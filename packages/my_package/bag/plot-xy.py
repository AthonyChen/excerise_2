import rosbag
import numpy as np
import sys
import matplotlib.pyplot as plt

def get_robot_frame(vl, vr, l):
    return np.array([
        [vr / 2.0 + vl / 2.0],
        [0.0],
        [vr / l - vl / l],
    ])

def get_r_inv(theta):
    return np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1],
    ])

if len(sys.argv) != 2:
    print("Usage: python plot-xy.py <bagfile>")
    sys.exit(1)

try:
    bag = rosbag.Bag(sys.argv[1])
except FileNotFoundError:
    print("Could not find bag file '{}'".format(sys.argv[1]))
    sys.exit(1)

# All measurements are in meters
axle_len = 10
radius = 3.18
global_angle = 0
x_last, y_last = 0.0, 0.0
trajectory_x = [0.0]
trajectory_y = [0.0]
previous_time = None
vel_left, vel_right = 0.0, 0.0

for topic, msg, t in bag.read_messages(topics=['/csc22928/wheels_driver_node/wheels_cmd_executed']):
    current_time = msg.header.stamp.secs + msg.header.stamp.nsecs / 1e9

    if previous_time is None:
        previous_time = current_time
        vel_left, vel_right = msg.vel_left * 100, msg.vel_right * 100  # Velocity is in m/s.
        continue

    dt = current_time - previous_time
    previous_time = current_time

    robot_frame = get_robot_frame(vel_left, vel_right, axle_len)
    r_inverse = get_r_inv(global_angle)
    initial_frame = r_inverse @ robot_frame

    x_last += initial_frame[0][0].item() * dt
    y_last += initial_frame[1][0].item() * dt
    global_angle += initial_frame[2][0].item() * dt
    vel_left, vel_right = msg.vel_left * 100, msg.vel_right * 100  # Velocity is in m/s.

    trajectory_x.append(x_last)
    trajectory_y.append(y_last)

plt.plot(trajectory_x, trajectory_y, label="Duckiebot Path", color='blue')
plt.scatter(trajectory_x[0], trajectory_y[0], color='green', label="Start")  # Start point
plt.scatter(trajectory_x[-1], trajectory_y[-1], color='red', label="End")  # End point
plt.xlabel("X Position (cm)")
plt.ylabel("Y Position (cm)")
plt.title("Duckiebot Trajectory - Reverse Parking")
plt.legend()
plt.grid()
plt.show()

bag.close()
