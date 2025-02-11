#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

rosrun my_package led_service_node.py &

# launch subscriber
rosrun my_package reverse_parking.py

# wait for app to end
dt-launchfile-join