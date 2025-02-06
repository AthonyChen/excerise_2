#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

rosrun my_package led_service_node.py &

# launch subscriber
rosrun my_package d_shape_node.py

# wait for app to end
dt-launchfile-join