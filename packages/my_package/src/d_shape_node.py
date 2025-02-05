#!/usr/bin/env python3

import rospy
import rosbag
import os
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped
from std_msgs.msg import String  # ✅ Now publishing LED commands
from srv import SetLed

WHEEL_RADIUS = 0.0318  # meters (Duckiebot wheel radius)
WHEEL_BASE = 0.05  # meters (distance between left and right wheels)
TICKS_PER_ROTATION = 135  # Encoder ticks per full wheel rotation
TURN_SPEED = 0.1  # Adjust speed for accuracy

class DShapeNode(DTROS):
    def __init__(self):
        super(DShapeNode, self).__init__(node_name="d_shape_node", node_type=NodeType.GENERIC)

        # Get Duckiebot's name
        self._vehicle_name = os.environ["VEHICLE_NAME"]

        # Publisher for wheel movement
        self.pub_wheels = rospy.Publisher(f'/{self._vehicle_name}/wheels_driver_node/wheels_cmd', WheelsCmdStamped,
                                          queue_size=1)

        # Publisher for LED control ✅
        self.srv_leds = rospy.ServiceProxy('set_led', SetLed)

        # ROS Bag for odometry data
        #self.bag = rosbag.Bag('d_shape_odometry.bag', 'w')
        wheels_topic = f"/{self._vehicle_name}/wheels_driver_node/wheels_cmd"

        # Publisher for wheel commands
        self._publisher = rospy.Publisher(wheels_topic, WheelsCmdStamped, queue_size=1)

        # Encoder topics
        self._left_encoder_topic = f"/{self._vehicle_name}/left_wheel_encoder_node/tick"
        self._right_encoder_topic = f"/{self._vehicle_name}/right_wheel_encoder_node/tick"

        # Encoder tick tracking
        self._ticks_left_init = None
        self._ticks_right_init = None
        self._ticks_left = None
        self._ticks_right = None

        # Subscribers to wheel encoders
        self.sub_left = rospy.Subscriber(self._left_encoder_topic, WheelEncoderStamped, self.callback_left)
        self.sub_right = rospy.Subscriber(self._right_encoder_topic, WheelEncoderStamped, self.callback_right)

        self.rate = rospy.Rate(10)  # 10 Hz loop rate
        rospy.sleep(2)  # Wait for everything to initialize

    def callback_left(self, data):
        # log general information once at the beginning
        rospy.loginfo_once(f"Left encoder resolution: {data.resolution}")
        rospy.loginfo_once(f"Left encoder type: {data.type}")
        # store data value
        if self._ticks_left_init is None:
            self._ticks_left_init = data.data
            self._ticks_left = 0
        else:
            self._ticks_left = data.data - self._ticks_left_init

    def callback_right(self, data):
        # log general information once at the beginning
        rospy.loginfo_once(f"Right encoder resolution: {data.resolution}")
        rospy.loginfo_once(f"Right encoder type: {data.type}")
        # store data value
        if self._ticks_right_init is None:
            self._ticks_right_init = data.data
            self._ticks_right = 0
        else:
            self._ticks_right = data.data - self._ticks_right_init
    def reset_encoders(self):
        """ Reset encoder counters to track new movements """
        self._ticks_left_init = None
        self._ticks_right_init = None
        self._ticks_left = None
        self._ticks_right = None
        # Wait for encoder data to reinitialize
        rospy.loginfo("Resetting encoders...")
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            if self._ticks_left is not None and self._ticks_right is not None:
                break
            rate.sleep()
        rospy.loginfo("Encoders reset complete.")

    def set_led(self, color):
        """Publishes LED color changes to LEDNode."""
        self.srv_leds(color)
        rospy.loginfo(f"Requested LED color change to {color}")

    def move_wheels(self, left_vel, right_vel, duration):
        """Actively publishes movement commands at a controlled rate."""
        rospy.loginfo(f"Moving: Left = {left_vel}, Right = {right_vel} for {duration} seconds")
        self.reset_encoders()

        cmd = WheelsCmdStamped()
        cmd.vel_left = left_vel
        cmd.vel_right = right_vel

        distance_traveled = (2 * 3.14159 * 0.0318 * self._ticks_left) / 135
        distance = duration
        message = WheelsCmdStamped(vel_left=left_vel, vel_right=right_vel)
        self._publisher.publish(message)
        while not rospy.is_shutdown():
            if self._ticks_right is not None and self._ticks_left is not None:
                distance_traveled = (2 * 3.14159 * 0.0318 * self._ticks_left) / 135

            if distance_traveled >= distance:

                message = WheelsCmdStamped(vel_left=0, vel_right=0)
                self._publisher.publish(message)
                break
            rospy.loginfo(distance_traveled)
            rospy.loginfo(self._ticks_left)

        # Stop the robot after moving
        rospy.loginfo("Stopping robot")
        stop_command = WheelsCmdStamped(vel_left=0, vel_right=0)  # ✅ Correct Stop Command
        self.pub_wheels.publish(stop_command)
        rospy.sleep(0.5)  # Ensure stop command is received

    def turn_90_degrees(self, direction=1):
        """
        Turns the Duckiebot 90 degrees in place.
        :param direction: 1 for left, -1 for right
        """
        # Reset encoder counters before each turn
        self.reset_encoders()

        # Compute required encoder ticks for 90-degree turn
        ticks_needed = round((WHEEL_BASE / (8 * WHEEL_RADIUS)) * TICKS_PER_ROTATION)
        rospy.loginfo(f"Ticks needed for 90-degree turn: {ticks_needed}")

        # Command wheels to rotate in opposite directions
        turn_command = WheelsCmdStamped(
            vel_left=TURN_SPEED * direction,
            vel_right=-TURN_SPEED * direction
        )
        self._publisher.publish(turn_command)

        # Wait until the required ticks are reached
        rate = rospy.Rate(100)  # 10 Hz loop
        while not rospy.is_shutdown():
            if self._ticks_left is not None and self._ticks_right is not None:
                avg_ticks = (abs(self._ticks_left) + abs(self._ticks_right)) / 2
                rospy.loginfo(f"Current ticks: {avg_ticks}")

                if avg_ticks >= ticks_needed:
                    rospy.loginfo("90-degree turn complete.")
                    break

            self._publisher.publish(turn_command)
            rate.sleep()

        # Stop the robot
        stop_command = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop_command)
        rospy.sleep(1)  # Small delay to stabilize

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
        self.move_wheels(0.3, 0.3, 1.2)

        # Semi-circle turn (Clockwise)
        rospy.loginfo("Turning in Semi-Circle")
        self.turn_90_degrees(1)
        self.move_wheels(0.3,0.3,0.91)


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
