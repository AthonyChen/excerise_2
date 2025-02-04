#!/usr/bin/env python3

import rospy
import os
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import LEDPattern, String  # ✅ Now listens for LED commands

class LEDNode(DTROS):
    def __init__(self):
        super(LEDNode, self).__init__(node_name="led_node", node_type=NodeType.GENERIC)

        # Get Duckiebot's name
        self._vehicle_name = os.environ["VEHICLE_NAME"]

        # Publisher for LED patterns
        self.led_pub = rospy.Publisher(f'/{self._vehicle_name}/led_emitter_node/led_pattern', LEDPattern, queue_size=1)

        # Subscriber to listen for LED color commands
        self.led_sub = rospy.Subscriber(f'/{self._vehicle_name}/led_control', String, self.led_callback)

        rospy.loginfo("LED Node Ready")

    def led_callback(self, msg):
        """
        Callback function to set LEDs based on received color command.
        """
        color = msg.data.lower()

        if color not in ["red", "blue"]:
            rospy.logwarn(f"Invalid color '{color}'. Only 'red' and 'blue' are supported.")
            return

        pattern = LEDPattern()
        pattern.color_list = [color] * 5  # Set all LEDs to the same color
        pattern.color_mask = [1] * 5  # Enable all LEDs
        self.led_pub.publish(pattern)
        rospy.loginfo(f"LEDs set to {color}")

if __name__ == '__main__':
    node = LEDNode()
    rospy.spin()
