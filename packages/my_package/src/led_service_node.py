#!/usr/bin/env python3

import rospy
import os
from duckietown_msgs.msg import LEDPattern, String  # ✅ Now listens for LED commands
from std_msgs.msg import ColorRGBA

color_map = {
    "red": [1.0, 0.0, 0.0],
    "blue": [0.0, 0.0, 1.0],
}

# Get Duckiebot's name
vehicle_name = os.environ["VEHICLE_NAME"]

# Publisher for LED patterns
led_pub = rospy.Publisher('~led_pattern', LEDPattern, queue_size=1)

color_list = [ColorRGBA()] * 5

def led_callback(msg):
    """
    Callback function to set LEDs based on received color command.
    """
    color = msg.data.lower()

    if color not in ["red", "blue"]:
        rospy.logwarn(f"Invalid color '{color}'. Only 'red' and 'blue' are supported.")
        return

    for i in color_list:
        i.r = color_map[color][0]
        i.g = color_map[color][1]
        i.b = color_map[color][2]
        i.a = 1.0

    pattern = LEDPattern()
    pattern.rgb_vals = color_list  # Set all LEDs to the same color
    led_pub.publish(pattern)
    rospy.loginfo(f"LEDs set to {color}")

if __name__ == '__main__':
    rospy.init_node('led_service_node')
    s = rospy.Service('set_led', LEDPattern, led_callback)
    rospy.loginfo("LED pattern service is ready.")
    rospy.spin()
