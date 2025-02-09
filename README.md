# Exercise 2

This repo is built on this template: https://github.com/duckietown/template-ros/

In this exercise, we explore the fundamentals of ROS (Robot Operating System) including
topics, nodes, services, messages, and bags and dive
into the core principles of robotic kinematics and odometry.
Through hands-on tasks, we learned how robotic software components interact
and understand how robots move and track their position.

Part 1:

packages/my_package/src/my_publisher_node.py is a publisher ROS node that publishes message 'Hello from vbot!'


Launch it using 
$dts devel run -H ROBOT_NAME -L my-publisher

packages/my_package/src/my_subscriber_node.py is a subscriber node that listens to my_publisher_node.py


Launch it using
$dts devel run -H ROBOT_NAME -L my-subscriber

*./packages/my_package/src/camera_reader_node.py* is a subscriber node that subscribes to the topic /ROBOT_NAME/camera_node/image/compressed
Launch it using $dts devel run -R ROBOT_NAME -L camera-reader -X

