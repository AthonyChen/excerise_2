#!/bin/bash

source /environment.sh  # Load Duckietown environment

# Initialize launch file
dt-launchfile-init

# Launch the LED service node
rosrun my_package led_service_node.py &

# Launch the main control node
rosrun my_package d_shape_node.py

# Wait for app to end
dt-launchfile-join
