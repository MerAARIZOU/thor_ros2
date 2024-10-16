import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable, 
                            IncludeLaunchDescription, SetLaunchConfiguration)
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition


def generate_launch_description():
    
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_thor_gazebo = get_package_share_directory('thor_gazebo')
    install_thor_gazebo = get_package_prefix('thor_gazebo')
    gazebo_models_path = os.path.join(pkg_thor_gazebo, 'models')
    

    gazebo_plugins_name_path_install_dir = get_package_prefix("gazebo_plugins")
        

    gazebo_plugins_name = "gazebo_plugins"
    gazebo_plugins_name_path_install_dir = get_package_prefix(
        gazebo_plugins_name)


    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] = os.environ['GAZEBO_MODEL_PATH'] + ':' + install_thor_gazebo + \
            '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = install_thor_gazebo + \
            "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_thor_gazebo + '/lib' + ':' + \
            gazebo_plugins_name_path_install_dir + '/lib' + ':'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_thor_gazebo + '/lib' + ':' + gazebo_plugins_name_path_install_dir + \
            '/lib' + ':'

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    gzweb_arg = LaunchConfiguration('gzweb')
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py'),
        ),
        condition=IfCondition(gzweb_arg)  # Directly pass the condition
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        ),
        condition=UnlessCondition(gzweb_arg)  # Directly pass the condition
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=[os.path.join(pkg_thor_gazebo, 'worlds', 'empty.world'), ''],
            #default_value=[os.path.join(pkg_thor_gazebo, 'worlds', 'small_warehouse_classic.world'), ''],
            description='SDF world file'),
        DeclareLaunchArgument(
            'verbose', default_value='true',
            description='Set "true" to increase messages written to the terminal.'
        ),
        DeclareLaunchArgument(
            'gzweb',
            default_value='false',  # Set your default value here
            description='Launch Gazebo with gzweb'
        ),
        gzserver,
        gazebo
    ])