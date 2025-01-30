#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped

# throttle and direction for each wheel
THROTTLE_LEFT = 0.5  # 50% throttle
DIRECTION_LEFT = 1  # forward
THROTTLE_RIGHT = 0.5  # 30% throttle
DIRECTION_RIGHT = 1


class WheelControlNode(DTROS):

    def __init__(self, node_name):
        # initialize the DTROS parent class
        super(WheelControlNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        # static parameters
        self._vehicle_name = os.environ['VEHICLE_NAME']
        wheels_topic = f"/{self._vehicle_name}/wheels_driver_node/wheels_cmd"
        # form the message
        self._vel_left = THROTTLE_LEFT * DIRECTION_LEFT
        self._vel_right = THROTTLE_RIGHT * DIRECTION_RIGHT
        # construct publisher
        self._publisher = rospy.Publisher(wheels_topic, WheelsCmdStamped, queue_size=1)

        self._left_encoder_topic = f"/{self._vehicle_name}/left_wheel_encoder_node/tick"
        self._right_encoder_topic = f"/{self._vehicle_name}/right_wheel_encoder_node/tick"
        # temporary data storage
        self._ticks_left_init = None
        self._ticks_right_init = None
        self._ticks_left = None
        self._ticks_right = None
        # construct subscriber
        self.sub_left = rospy.Subscriber(self._left_encoder_topic, WheelEncoderStamped, self.callback_left)
        self.sub_right = rospy.Subscriber(self._right_encoder_topic, WheelEncoderStamped, self.callback_right)

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

    def run(self):
        # publish 10 messages every second (10 Hz)
        rate = rospy.Rate(10)

        distance = 1.25
        distance_traveled = 0
        rospy.loginfo(self._ticks_left)
        message = WheelsCmdStamped(vel_left=self._vel_left, vel_right=self._vel_right)
        bool1 = False
        while not rospy.is_shutdown():
            if self._ticks_right is not None and self._ticks_left is not None:
                distance_traveled = (2 * 3.14159 * 0.0318 * self._ticks_left) / 135

            if distance_traveled >= distance:

                message = WheelsCmdStamped(vel_left=-0.5, vel_right=-0.5)
                self._publisher.publish(message)
                bool1 = True
            if distance_traveled <= 0 and bool1:
                stop = WheelsCmdStamped(vel_left=0, vel_right=0)
                self._publisher.publish(stop)
                break

            rospy.loginfo(distance_traveled)
            rospy.loginfo(self._ticks_left)
            self._publisher.publish(message)
            rate.sleep()

        self.stop_robot()

    def on_shutdown(self):
        stop = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop)

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
    # create the node
    node = WheelControlNode(node_name='wheel_control_node')
    # run node
    node.run()
    # keep the process from terminating
    rospy.spin()
