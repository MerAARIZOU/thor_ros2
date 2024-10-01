# Copyright 2023 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, AppendEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.parameter_descriptions import ParameterValue

from launch_ros.actions import Node


def generate_launch_description():
    # Configure ROS nodes for launch

    # Setup project paths
    pkg_project_bringup = get_package_share_directory('thor_gazebo')
    pkg_project_description = get_package_share_directory('thor_description')
    urdf_filename = 'thor_urdf.xacro'
    world_file_path = 'worlds/empty.world'
    default_urdf_model_path = PathJoinSubstitution([pkg_project_description, 'urdf', urdf_filename])
    world_path = os.path.join(pkg_project_bringup, world_file_path)
    ros_gz_bridge_config = os.path.join(pkg_project_bringup, 'config/ros_gz_bridge.yaml')

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Load the SDF file from "description" package
    sdf_file  =  os.path.join(pkg_project_description, 'urdf', 'thor.sdf')
    with open(sdf_file, 'r') as infp:
        robot_desc = infp.read()

    
    # For publishing and controlling the robot pose, we need joint states of the robot
    # Configure the robot model by adjusting the joint angles using the GUI slider
    
    jsp_gui = DeclareLaunchArgument(
        name='jsp_gui', 
        default_value='true', 
        choices=['true', 'false'],
        description='Flag to enable joint_state_publisher_gui')

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=IfCondition(LaunchConfiguration('jsp_gui')))
 
    # Depending on gui parameter, either launch joint_state_publisher or joint_state_publisher_gui
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('jsp_gui')))
    
    robot_description_content = ParameterValue(Command(['xacro ', LaunchConfiguration('urdf_model')]), value_type=str)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'), 
            'robot_description': robot_description_content}])

    robot_name = LaunchConfiguration('robot_name')
    
    # Visualize in RViz
    rviz = Node(
       package='rviz2',
       executable='rviz2',
       arguments=['-d', os.path.join(pkg_project_description, 'rviz', 'thor_view_description.rviz')],
       condition=IfCondition(LaunchConfiguration('rviz'))
    )

    ros_gz_sim_package = get_package_share_directory('ros_gz_sim')
    gz_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim_package, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': PathJoinSubstitution([
            pkg_project_description ,
            'urdf',
            "thor.sdf",
        ])}.items(),)
    
    
    urdf_model_path = DeclareLaunchArgument(
        name='urdf_model', 
        default_value=default_urdf_model_path, 
        description='Absolute path to robot urdf file')
    
    use_sim_time = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='True',
        description='Use simulation (Gazebo) clock if true')
    
    
    simulator = DeclareLaunchArgument(
        name='headless',
        default_value='False',
        description='Display the Gazebo GUI if False, otherwise run in headless mode'
    )
    
    use_robot_state_pub = DeclareLaunchArgument(
        name='use_robot_state_pub',
        default_value='True',
        description='Whether to start the robot state publisher')
    
    
    world = DeclareLaunchArgument(
        name='world',
        default_value=world_path,
        description='Full path to the world model file to load')
    
    x = DeclareLaunchArgument(
        name='x',
        default_value='0.0',
        description='x component of initial position, meters')
    
    y = DeclareLaunchArgument(
        name='y',
        default_value='0.0',
        description='y component of initial position, meters')
    
    z = DeclareLaunchArgument(
        name='z',
        default_value='0.05',
        description='z component of initial position, meters')
    
    roll = DeclareLaunchArgument(
        name='roll',
        default_value='0.0',
        description='roll angle of initial orientation, radians')
    
    pitch = DeclareLaunchArgument(
        name='pitch',
        default_value='0.0',
        description='pitch angle of initial orientation, radians')
    
    yaw = DeclareLaunchArgument(
        name='yaw',
        default_value='0.0',
        description='yaw angle of initial orientation, radians')
    
    set_env_vars_resources = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        'models')
    
    gazebo_client = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-g -v4 '}.items(),)
    
    gazebo_ros_spawner = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
        '-name', robot_name,
        '-topic', 'robot_description',
        '-x', x,
        '-y', y,
        '-z', z,
        '-R', roll,
        '-P', pitch,
        '-Y', yaw
        ],
        output='screen') 
    
    gazebo_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': ros_gz_bridge_config,
        }],
        output='screen')  

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Open RViz.'),
        DeclareLaunchArgument(
            name='robot_name',
            default_value='thor',
            description='The name for the robot'),
        simulator,
        urdf_model_path,
        use_robot_state_pub,
        use_sim_time,
        world,
        x,
        y,
        z,
        roll,
        pitch,
        yaw,
        set_env_vars_resources,
        gz_node,
        gazebo_client,
        jsp_gui,
        joint_state_publisher,
        robot_state_publisher,
        rviz,
        gazebo_ros_spawner,
        gazebo_ros_bridge  
    ])