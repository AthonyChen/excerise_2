#!/usr/bin/env python3

import rospy
import rosbag
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, LEDPattern
from sensor_msgs.msg import JointState
from std_srvs.srv import SetBool, SetBoolResponse
import numpy as np


class TrajectoryNode(DTROS):
    def __init__(self, node_name):
        super(TrajectoryNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)

        self.pub_wheels = rospy.Publisher("/duckiebot/wheels_driver_node/wheels_cmd", WheelsCmdStamped, queue_size=10)
        self.pub_led = rospy.Publisher("/duckiebot/led_emitter_node/led_pattern", LEDPattern, queue_size=10)
        self.sub_encoders = rospy.Subscriber("/duckiebot/joint_states", JointState, self.encoder_callback)

        self.odom_data = []
        self.bag = rosbag.Bag("duckiebot_odometry.bag", 'w')
        self.prev_encoder_left = 0
        self.prev_encoder_right = 0
        self.wheel_radius = 0.0318  # meters
        self.wheel_base = 0.1  # meters

    def encoder_callback(self, msg):
        left_ticks = msg.position[0]
        right_ticks = msg.position[1]

        d_left = (left_ticks - self.prev_encoder_left) * self.wheel_radius
        d_right = (right_ticks - self.prev_encoder_right) * self.wheel_radius

        d_center = (d_left + d_right) / 2.0

        self.odom_data.append(d_center)
        self.bag.write("odometry", d_center)

        self.prev_encoder_left = left_ticks
        self.prev_encoder_right = right_ticks

    def drive_straight(self, distance, speed=0.2):
        cmd = WheelsCmdStamped()
        cmd.vel_left = speed
        cmd.vel_right = speed
        traveled = 0
        rate = rospy.Rate(10)
        while traveled < distance:
            traveled += self.odom_data[-1] if self.odom_data else 0
            self.pub_wheels.publish(cmd)
            rate.sleep()
        cmd.vel_left = 0
        cmd.vel_right = 0
        self.pub_wheels.publish(cmd)

    def drive_arc(self, radius, speed=0.2):
        cmd = WheelsCmdStamped()
        cmd.vel_left = speed * (radius - self.wheel_base / 2) / radius
        cmd.vel_right = speed * (radius + self.wheel_base / 2) / radius
        traveled = 0
        target_distance = np.pi * radius / 2
        rate = rospy.Rate(10)
        while traveled < target_distance:
            traveled += self.odom_data[-1] if self.odom_data else 0
            self.pub_wheels.publish(cmd)
            rate.sleep()
        cmd.vel_left = 0
        cmd.vel_right = 0
        self.pub_wheels.publish(cmd)

    def use_leds(self, color):
        led_msg = LEDPattern()
        led_msg.color_list = [color] * 5
        self.pub_led.publish(led_msg)

    def run(self):
        rospy.sleep(2)
        self.use_leds("red")
        rospy.sleep(5)
        self.use_leds("blue")
        self.drive_straight(1.0)
        self.drive_arc(0.5)
        self.use_leds("red")
        rospy.sleep(5)
        self.bag.close()
        rospy.signal_shutdown("Task Complete")


if __name__ == '__main__':
    node = TrajectoryNode("trajectory_node")
    node.run()
    rospy.spin()
