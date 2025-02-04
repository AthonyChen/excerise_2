#!/usr/bin/env python3

import rospy
import rosbag
import os
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped
from std_msgs.msg import String  # ✅ Now publishing LED commands


class DShapeNode(DTROS):
    def __init__(self):
        super(DShapeNode, self).__init__(node_name="d_shape_node", node_type=NodeType.GENERIC)

        # Get Duckiebot's name
        self._vehicle_name = os.environ["VEHICLE_NAME"]

        # Publisher for wheel movement
        self.pub_wheels = rospy.Publisher(f'/{self._vehicle_name}/wheels_driver_node/wheels_cmd', WheelsCmdStamped,
                                          queue_size=1)

        # Publisher for LED control ✅
        self.pub_leds = rospy.Publisher(f'/{self._vehicle_name}/led_control', String, queue_size=1)

        # Subscribers for wheel encoders
        rospy.Subscriber(f'/{self._vehicle_name}/left_wheel_encoder_node/tick', WheelEncoderStamped,
                         self.encoder_callback)
        rospy.Subscriber(f'/{self._vehicle_name}/right_wheel_encoder_node/tick', WheelEncoderStamped,
                         self.encoder_callback)

        # ROS Bag for odometry data
        #self.bag = rosbag.Bag('d_shape_odometry.bag', 'w')

        self.rate = rospy.Rate(10)  # 10 Hz loop rate
        rospy.sleep(2)  # Wait for everything to initialize

    def encoder_callback(self, msg):
        """Save encoder data to ROS bag."""
        #self.bag.write(f'/{self._vehicle_name}/encoder_data', msg)
        pass
    def set_led(self, color):
        """Publishes LED color changes to LEDNode."""
        self.pub_leds.publish(color)
        rospy.loginfo(f"Requested LED color change to {color}")

    def move_wheels(self, left_vel, right_vel, duration):
        """Actively publishes movement commands at a controlled rate."""
        rospy.loginfo(f"Moving: Left = {left_vel}, Right = {right_vel} for {duration} seconds")

        cmd = WheelsCmdStamped()
        cmd.vel_left = left_vel
        cmd.vel_right = right_vel

        distance_traveled = (2 * 3.14159 * 0.0318 * self._ticks_left) / 135
        start_time = rospy.Time.now().to_sec()

        while rospy.Time.now().to_sec() - start_time < duration:
            self.pub_wheels.publish(cmd)
            self.rate.sleep()  # Maintain consistent publishing rate

        # Stop the robot after moving
        rospy.loginfo("Stopping robot")
        stop_command = WheelsCmdStamped(vel_left=0, vel_right=0)  # ✅ Correct Stop Command
        self.pub_wheels.publish(stop_command)
        rospy.sleep(0.5)  # Ensure stop command is received

    def execute(self):
        rospy.loginfo("Starting D-Shape Execution...")

        # State 1: Stop (Red)
        rospy.loginfo("State 1: Stop")
        self.set_led("red")  # ✅ Now publishes to `led_control`
        rospy.sleep(5)

        # State 2: Move in "D" Shape (Blue)
        rospy.loginfo("State 2: Moving in D-shape")
        self.set_led("blue")  # ✅ Set LED to blue for moving

        # Move forward 1 meter
        rospy.loginfo("Moving Forward")
        self.move_wheels(0.3, 0.3, 3)

        # Semi-circle turn (Clockwise)
        rospy.loginfo("Turning in Semi-Circle")
        self.move_wheels(0.2, -0.2, 3)

        # State 3: Return to Start (Red)
        rospy.loginfo("State 3: Returning to Start")
        self.set_led("red")  # ✅ Set LED back to red
        rospy.sleep(5)

        # Close the ROS bag
        #self.bag.close()
        rospy.loginfo("D-Shape Execution Completed!")


if __name__ == '__main__':
    node = DShapeNode()
    node.execute()
