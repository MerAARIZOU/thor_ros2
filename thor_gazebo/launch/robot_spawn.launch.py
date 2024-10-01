import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable, 
                            IncludeLaunchDescription, SetLaunchConfiguration)
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition


def generate_launch_description():

    pkg_thor_description = get_package_share_directory('thor_description')
    pkg_thor_gazebo = get_package_share_directory('thor_gazebo')
    urdf_model_path = os.path.join(pkg_thor_description, 'urdf', 'thor.urdf')
    default_ros_gz_bridge_config_file_path = os.path.join(pkg_thor_gazebo, 'config', 'ros_gz_bridge.yaml')

    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub', default='true')
    use_sim_time = LaunchConfiguration('use_sim_time')
    urdf_model = LaunchConfiguration('urdf_model')
    robot_name = LaunchConfiguration('robot_name')
    with open(urdf_model_path, 'r') as infp:
        robot_description_content = infp.read()
    
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    roll = LaunchConfiguration('roll')
    pitch = LaunchConfiguration('pitch')
    yaw = LaunchConfiguration('yaw')
    

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        condition=IfCondition(use_robot_state_pub),
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time, 
            'robot_description': robot_description_content}],
        arguments=[urdf_model_path])
    
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher')
    
    robot_file_arg = DeclareLaunchArgument('robot_file', default_value='$(find-pkg-share thor_description)/urdf/thor.urdf')    
    
    gazebo_ros_spawner = Node(
        name='thor_spawn_entity',
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity',
                   robot_name,
                   '-x', x, 
                   '-y', y, 
                   '-z', z,
                   '-R', roll, 
                   '-P', pitch, 
                   '-Y', yaw,
                   '-topic', '/robot_description'
                   ],
        output='screen')
    
    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': default_ros_gz_bridge_config_file_path,
        }],
        output='screen'
  )  
    
    return LaunchDescription([
        robot_file_arg,
        DeclareLaunchArgument(
            name='robot_name',
            default_value='thor',
            description='The name for the robot'),
        DeclareLaunchArgument(
            name='use_robot_state_pub',
            default_value='True',
            description='Whether to start the robot state publisher'),
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            name='urdf_model', 
            default_value=urdf_model_path, 
            description='Absolute path to robot urdf file'),
        robot_state_publisher, 
        joint_state_publisher,     
        DeclareLaunchArgument(
            name='x',
            default_value='0.0',
            description='x component of initial position, meters'),
        DeclareLaunchArgument(
            name='y',
            default_value='0.0',
            description='y component of initial position, meters'),
        DeclareLaunchArgument(
            name='z',
            default_value='0.05',
            description='z component of initial position, meters'),
        DeclareLaunchArgument(
            name='roll',
            default_value='0.0',
            description='roll angle of initial orientation, radians'),
        DeclareLaunchArgument(
            name='pitch',
            default_value='0.0',
            description='pitch angle of initial orientation, radians'),
        DeclareLaunchArgument(
            name='yaw',
            default_value='0.0',
            description='yaw angle of initial orientation, radians'),
        gazebo_ros_spawner
    ])