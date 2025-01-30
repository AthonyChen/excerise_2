#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped
import math

# Constants
WHEEL_RADIUS = 0.0318  # Radius of the Duckiebot's wheels in meters
TICKS_PER_REVOLUTION = 135  # Number of encoder ticks per full wheel revolution
DISTANCE_PER_TICK = (2 * math.pi * WHEEL_RADIUS) / TICKS_PER_REVOLUTION  # Distance per tick in meters

# Target distance in meters
TARGET_DISTANCE = 1.25

class DriveDistanceNode(DTROS):

    def __init__(self, node_name):
        # Initialize the DTROS parent class
        super(DriveDistanceNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        
        # Initialize wheel control node
        self.wheel_control_node = WheelControlNode(node_name='wheel_control_node')
        
        # Initialize wheel encoder reader node
        self.encoder_reader_node = WheelEncoderReaderNode(node_name='wheel_encoder_reader_node')
        
        # Variables to store encoder ticks
        self.initial_ticks_left = None
        self.initial_ticks_right = None
        self.current_ticks_left = None
        self.current_ticks_right = None
        
        # Flag to indicate if the bot is moving forward or backward
        self.moving_forward = True

    def calculate_distance(self, initial_ticks, current_ticks):
        # Calculate the distance traveled based on encoder ticks
        return abs(current_ticks - initial_ticks) * DISTANCE_PER_TICK

    def run(self):
        # Wait for the encoder data to be available
        while self.encoder_reader_node._ticks_left is None or self.encoder_reader_node._ticks_right is None:
            rospy.sleep(0.1)
        
        # Record initial encoder ticks
        self.initial_ticks_left = self.encoder_reader_node._ticks_left
        self.initial_ticks_right = self.encoder_reader_node._ticks_right
        
        # Start moving forward
        self.wheel_control_node._vel_left = 0.5  # 50% throttle forward
        self.wheel_control_node._vel_right = 0.5  # 50% throttle forward
        
        while not rospy.is_shutdown():
            # Update current encoder ticks
            self.current_ticks_left = self.encoder_reader_node._ticks_left
            self.current_ticks_right = self.encoder_reader_node._ticks_right
            
            # Calculate distance traveled
            distance_left = self.calculate_distance(self.initial_ticks_left, self.current_ticks_left)
            distance_right = self.calculate_distance(self.initial_ticks_right, self.current_ticks_right)
            distance_traveled = (distance_left + distance_right) / 2  # Average distance
            
            rospy.loginfo(f"Distance traveled: {distance_traveled:.2f} meters")
            
            if self.moving_forward:
                if distance_traveled >= TARGET_DISTANCE:
                    # Stop the bot and prepare to move backward
                    self.wheel_control_node._vel_left = 0
                    self.wheel_control_node._vel_right = 0
                    rospy.sleep(1)  # Wait for 1 second
                    
                    # Record new initial ticks for backward movement
                    self.initial_ticks_left = self.encoder_reader_node._ticks_left
                    self.initial_ticks_right = self.encoder_reader_node._ticks_right
                    
                    # Start moving backward
                    self.wheel_control_node._vel_left = -0.5  # 50% throttle backward
                    self.wheel_control_node._vel_right = -0.5  # 50% throttle backward
                    self.moving_forward = False
            else:
                if distance_traveled >= TARGET_DISTANCE:
                    # Stop the bot
                    self.wheel_control_node._vel_left = 0
                    self.wheel_control_node._vel_right = 0
                    rospy.loginfo("Task completed!")
                    break
            
            rospy.sleep(0.1)

if __name__ == '__main__':
    # Create the node
    node = DriveDistanceNode(node_name='drive_distance_node')
    # Run the node
    node.run()
    # Keep the process from terminating
    rospy.spin()