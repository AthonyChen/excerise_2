#!/usr/bin/env python3

import rospy
import os
from duckietown_msgs.msg import LEDPattern  # ✅ Now listens for LED commands
from std_msgs.msg import ColorRGBA
from my_package.srv import SetLed, SetLedResponse

color_map = {
    "red": [1.0, 0.0, 0.0],
    "blue": [0.0, 0.0, 1.0],
}

# Get Duckiebot's name
vehicle_name = os.environ["VEHICLE_NAME"]

color_list = [ColorRGBA()] * 5

def led_callback(msg):
    """
    Callback function to set LEDs based on received color command.
    """
    color = msg.color

    if color == 'shutdown':
        s.shutdown("Task completed, shutting down service.")
        rospy.signal_shutdown('Task completed, shutting down node.')
        return SetLedResponse(False)

    if color not in ["red", "blue"]:
        rospy.logwarn(f"Invalid color '{color}'. Only 'red' and 'blue' are supported.")
        return

    for i in color_list:
        i.r = color_map[color][0]
        i.g = color_map[color][1]
        i.b = color_map[color][2]
        i.a = 0.2

    pattern = LEDPattern()
    pattern.rgb_vals = color_list  # Set all LEDs to the same color
    led_pub.publish(pattern)
    rospy.loginfo(f"LEDs set to {color}")
    return SetLedResponse(True)

if __name__ == '__main__':
    rospy.init_node('led_service_node')
    led_pub = rospy.Publisher('/csc22928/led_emitter_node/led_pattern', LEDPattern, queue_size=1)
    s = rospy.Service('set_led', SetLed, led_callback)
    rospy.loginfo("LED pattern service is ready.")
    rospy.spin()
