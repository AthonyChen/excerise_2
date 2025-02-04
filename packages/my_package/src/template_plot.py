#!/usr/bin/env python3

import rospy
import rosbag
import matplotlib.pyplot as plt
import numpy as np


def plot_trajectory(bag_file):
    bag = rosbag.Bag(bag_file, 'r')
    odom_data = []

    for topic, msg, t in bag.read_messages(topics=['odometry']):
        odom_data.append(msg)

    bag.close()

    x, y = [0], [0]
    theta = 0

    for d in odom_data:
        x_new = x[-1] + d * np.cos(theta)
        y_new = y[-1] + d * np.sin(theta)
        x.append(x_new)
        y.append(y_new)

    plt.plot(x, y, marker='o', label='D-trajectory')
    plt.xlabel('X Position (m)')
    plt.ylabel('Y Position (m)')
    plt.title('Duckiebot D-Shaped Trajectory')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == '__main__':
    rospy.init_node('plot_trajectory')
    plot_trajectory('duckiebot_odometry.bag')
