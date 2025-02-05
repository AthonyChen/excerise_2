#!/usr/bin/env python3

import os
import rospy
import math
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped

# 
WHEEL_RADIUS = 0.0318  # Radius of the Duckiebot's wheels in meters
TICKS_PER_REVOLUTION = 135  # Number of encoder ticks per full wheel revolution
DISTANCE_PER_TICK = (2 * math.pi * WHEEL_RADIUS) / TICKS_PER_REVOLUTION  # Distance per tick in meters

TARGET_DISTANCE = 0.4555

class ArcNode(DTROS):

    def __init__(self, node_name):
        super(ArcNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        
        self._vehicle_name = os.environ['VEHICLE_NAME']
        
        self._vel_left = 0.0
        self._vel_right = 0.0
        
        self._ticks_left = None
        self._ticks_right = None
        self.initial_ticks_left = None
        self.initial_ticks_right = None
                
        self.wheels_topic = f"/{self._vehicle_name}/wheels_driver_node/wheels_cmd"
        self._publisher = rospy.Publisher(self.wheels_topic, WheelsCmdStamped, queue_size=1)
        
        self.left_encoder_topic = f"/{self._vehicle_name}/left_wheel_encoder_node/tick"
        self.right_encoder_topic = f"/{self._vehicle_name}/right_wheel_encoder_node/tick"
        self.sub_left = rospy.Subscriber(self.left_encoder_topic, WheelEncoderStamped, self.callback_left)
        self.sub_right = rospy.Subscriber(self.right_encoder_topic, WheelEncoderStamped, self.callback_right)

    def callback_left(self, data):
        rospy.loginfo_once(f"Left encoder resolution: {data.resolution}")
        rospy.loginfo_once(f"Left encoder type: {data.type}")
        self._ticks_left = data.data

    def callback_right(self, data):
        rospy.loginfo_once(f"Right encoder resolution: {data.resolution}")
        rospy.loginfo_once(f"Right encoder type: {data.type}")
        self._ticks_right = data.data

    def calculate_distance(self, initial_ticks, current_ticks):
        return abs(current_ticks - initial_ticks) * DISTANCE_PER_TICK

    def run(self):
        while self._ticks_left is None or self._ticks_right is None:
            rospy.sleep(0.1)
        
        self.initial_ticks_left = self._ticks_left
        self.initial_ticks_right = self._ticks_right
        
        self._vel_left = 0.708  # 50% throttle forward
        self._vel_right = 0.5  # 50% throttle forward
        
        # Publish wheel commands at 10 Hz
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            # Publish wheel commands
            message = WheelsCmdStamped(vel_left=self._vel_left, vel_right=self._vel_right)
            self._publisher.publish(message)
            
            # Update current encoder ticks
            current_ticks_left = self._ticks_left
            current_ticks_right = self._ticks_right
            
            # Calculate distance traveled
            distance_left = self.calculate_distance(self.initial_ticks_left, current_ticks_left)
            distance_right = self.calculate_distance(self.initial_ticks_right, current_ticks_right)
            distance_traveled = (distance_left + distance_right) / 2  # Average distance
            
            rospy.loginfo(f"Distance traveled: {distance_traveled:.2f} meters")
            
            if distance_traveled >= TARGET_DISTANCE:
                self._vel_left = 0
                self._vel_right = 0

                message = WheelsCmdStamped(vel_left=self._vel_left, vel_right=self._vel_right)
                self._publisher.publish(message)
        
                rospy.loginfo("Task completed!")
                message = WheelsCmdStamped(vel_left=self._vel_left, vel_right=self._vel_right)
                self._publisher.publish(message)
                break
            
            rate.sleep()

    def on_shutdown(self):
        # Stop the bot when the node is shut down
        stop_message = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop_message)

if __name__ == '__main__':
    # Create the node
    node = ArcNode(node_name='arc_node')
    # Run the node
    node.run()
    # Keep the process from terminating
    rospy.spin()