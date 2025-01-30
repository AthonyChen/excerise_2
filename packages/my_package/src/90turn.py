#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped

# Constants (Adjust for your Duckiebot)
WHEEL_RADIUS = 0.0318  # meters (Duckiebot wheel radius)
WHEEL_BASE = 0.05  # meters (distance between left and right wheels)
TICKS_PER_ROTATION = 135  # Encoder ticks per full wheel rotation
TURN_SPEED = 0.3  # Adjust speed for accuracy


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

    def turn_90_degrees(self, direction=1):
        """
        Turns the Duckiebot 90 degrees in place.
        :param direction: 1 for left, -1 for right
        """

        # Compute required encoder ticks for 90-degree turn
        ticks_needed = (WHEEL_BASE / (8 * WHEEL_RADIUS)) * TICKS_PER_ROTATION
        rospy.loginfo(f"Ticks needed for 90-degree turn: {ticks_needed}")

        # Command wheels to rotate in opposite directions
        turn_command = WheelsCmdStamped(
            vel_left=TURN_SPEED * direction,
            vel_right=-TURN_SPEED * direction
        )
        self._publisher.publish(turn_command)

        # Wait until the required ticks are reached
        rate = rospy.Rate(10)  # 10 Hz loop
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
        rospy.sleep(2)  # Give encoders time to initialize

        # Step 1: Turn 90 degrees (Left)
        self.turn_90_degrees(direction=1)

        # Step 2: Stop briefly
        rospy.sleep(1)

        # Step 3: Turn back to 0 degrees (Right)
        self.turn_90_degrees(direction=-1)

        # Step 4: Stop the Duckiebot
        self.stop_robot()

    def stop_robot(self):
        """ Stop the Duckiebot and shut down subscribers """
        stop_command = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop_command)
        rospy.loginfo("Robot stopped.")

        # Unsubscribe from topics to prevent lingering processes
        self.sub_left.unregister()
        self.sub_right.unregister()

        # Shutdown ROS properly
        rospy.signal_shutdown("Task completed, shutting down.")


if __name__ == '__main__':
    node = Turn90Node(node_name='turn_90_node')
    node.run()
    rospy.spin()
