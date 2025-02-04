#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped

# Constants (Adjust for your Duckiebot)
WHEEL_RADIUS = 0.0318  # meters (Duckiebot wheel radius)
WHEEL_BASE = 0.05  # meters (distance between left and right wheels)
TICKS_PER_ROTATION = 135  # Encoder ticks per full wheel rotation
TURN_SPEED = 0.2  # Adjust speed for accuracy


class Turn90Node(DTROS):

    def __init__(self, node_name):
        super(Turn90Node, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)

        # Get vehicle name from environment
        self._vehicle_name = os.environ['VEHICLE_NAME']
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

    def callback_left(self, data):
        """ Left wheel encoder callback """
        if self._ticks_left_init is None:
            self._ticks_left_init = data.data
            self._ticks_left = 0
        else:
            self._ticks_left = data.data - self._ticks_left_init

    def callback_right(self, data):
        """ Right wheel encoder callback """
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

    def turn_90_degrees(self, direction=1):
        """
        Turns the Duckiebot 90 degrees in place.
        :param direction: 1 for left, -1 for right
        """
        # Reset encoder counters before each turn
        self.reset_encoders()

        # Compute required encoder ticks for 90-degree turn
        ticks_needed = round((WHEEL_BASE / (8 * WHEEL_RADIUS)) * TICKS_PER_ROTATION) + 11
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

    def run(self):
        # Allow time for encoders to initialize
        rospy.sleep(1)

        # Turn left 90 degrees
        self.turn_90_degrees(direction=1)

        # Turn right 90 degrees to return to original position
        self.turn_90_degrees(direction=-1)

        # Shutdown
        self.stop_robot()

    def stop_robot(self):
        """ Stop the Duckiebot and shut down subscribers """
        stop_command = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop_command)
        rospy.loginfo("Robot stopped.")

        # Unsubscribe from topics
        self.sub_left.unregister()
        self.sub_right.unregister()

        rospy.signal_shutdown("Task completed, shutting down.")


if __name__ == '__main__':
    node = Turn90Node(node_name='90turn')
    node.run()
    rospy.spin()