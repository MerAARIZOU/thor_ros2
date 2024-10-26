# Thor Robotic Arm    
<br>
This work is my contribution of a ROS2 package to manipulate a simulated **Thor Robotic Arm** with Gazebo.
**Thor Robotic Arm** is an Open source 3D printable 06DoF Arm developed by Àngel L.M.. More details can be found in the [official website](http://thor.angel-lm.com/) 

# Thor Robotic Arm: Gazebo Classic + Rviz2 + MoveIt!
<br>

1. [Description](##description)
2. [Packages](##packages)
3. [Dependencies](##dependencies)
4. [Quick Start](##quick-start)
5. [Tutorials](##tutorials)
6. [Related Ressources](##related-ressources)

## 1. Description
This work describes a set of ROS2 packages that can simulate and control the Thor 06DoF robotic arm. The simulation is done with Gazebo Classic and the code was tested with the Humble distrubution.
## 2. Packages
  - `thor_description`: xacro description of the URDF robot model.
  - `thor_gazebo`: simulation of the robot on Gazebo Classic.
  - `thor_moveit`: configuration files to enable MoveIt functionnalities.
## 3. Dependencies
  - `controller_manager`
  - `gripper_controllers`
  - `ros2_control`
  - `ros2_controllers`
  - `trajectory_msgs`
  - `xacro`
## 4. Quick Start
  1. Visualise Thor on Rviz2:
     `ros2 launch thor_description thor_view_description.launch.py`
  2. Launch an empty world simulation:
     `ros2 launch thor_gazebo simple.launch.xml`
## 5. Tutorials
## 6. Related Ressources
