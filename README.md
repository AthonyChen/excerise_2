# Exercise 2

This repository is built on the following template: [Duckietown Template-ROS](https://github.com/duckietown/template-ros/).

In this exercise, we explore the fundamentals of ROS (Robot Operating System), including topics, nodes, services, messages, and bags. We also dive into the core principles of robotic kinematics and odometry.  

Through hands-on tasks, we learn how robotic software components interact and how robots move and track their position.

---

## Part 1: Basic ROS Nodes

### Publisher Node
📌 **File:** `packages/my_package/src/my_publisher_node.py`  
📝 **Description:** This is a ROS publisher node that publishes the message:  
> *"Hello from vbot!"*

▶ **Launch Command:**
```bash
dts devel run -H ROBOT_NAME -L my-publisher
```

### Subscriber Node
📌 **File:** `packages/my_package/src/my_subscriber_node.py`  
📝 **Description:** This is a subscriber node that listens to messages from `my_publisher_node.py`.

▶ **Launch Command:**
```bash
dts devel run -H ROBOT_NAME -L my-subscriber
```

### Camera Reader Node
📌 **File:** `packages/my_package/src/camera_reader_node.py`  
📝 **Description:** This subscriber node subscribes to the topic `/ROBOT_NAME/camera_node/image/compressed` to receive camera images.

▶ **Launch Command:**
```bash
dts devel run -H ROBOT_NAME -L camera-reader -X
```

---

## Part 2: Robot Movement

### Drive Distance Node
📌 **File:** `packages/my_package/src/drive_distance_node.py`  
📝 **Description:** Moves the Duckiebot forward for **1.25 meters** and then backward for **1.25 meters**.

▶ **Launch Command:**
```bash
dts devel run -H ROBOT_NAME -L drive-distance
```

### 90° Turn Node
📌 **File:** `packages/my_package/src/90turn.py`  
📝 **Description:** Rotates the Duckiebot **90 degrees (π/2 radians) clockwise** on the spot, then rotates it back to **0 degrees (0 radians) counterclockwise**.

▶ **Launch Command:**
```bash
dts devel run -H ROBOT_NAME -L 90turn
```

---

## Part 3: D-Shaped Path Navigation

📌 **File:** `packages/my_package/src/d_shape_node.py`  
📝 **Description:** Controls the Duckiebot to follow a **D-shaped** path using **wheel encoder odometry**.

### **State 1: Stop**
- The robot remains stationary for **5 seconds**.
- LED lights set to a chosen color for this state.

### **State 2: Tracing the "D" Path**
- LED lights switch to another color.
- The robot follows a **D-shaped path**:
  1. **Straight Segment:** Moves forward **1 meter**.
  2. **Semi-Circular Segment:** Performs a **clockwise semi-circle** to form the curved part of the "D".
- LED lights remain consistent throughout this state.

### **State 3: Return to Start**
- The robot moves back to the **starting position and orientation**.
- It waits for **5 seconds** at the starting position.
- LED lights revert to the **State 1** color.

▶ **Launch Command:**
```bash
dts devel run -H ROBOT_NAME -L d-shape
```

---

## 🚀 Running the Exercises
Replace `ROBOT_NAME` with your actual robot's name in the commands.

Happy coding! 🤖🎯
```
