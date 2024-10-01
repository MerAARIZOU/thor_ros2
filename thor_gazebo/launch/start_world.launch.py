import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable, 
                            IncludeLaunchDescription, SetLaunchConfiguration)
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition


def generate_launch_description():
    
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_thor_gazebo = get_package_share_directory('thor_gazebo')
    install_thor_gazebo = get_package_prefix('thor_gazebo')
    install_thor_description = get_package_prefix('thor_description')

    gz_launch_path = os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
    gz_model_path = os.path.join(pkg_thor_gazebo, 'models')
    world_path = os.path.join(pkg_thor_gazebo, 'worlds', 'empty.world')
    gazebo_plugins_name_path_install_dir = get_package_prefix("gazebo_plugins")
    
    headless = LaunchConfiguration('headless')
    use_simulator = LaunchConfiguration('use_simulator')
    world = LaunchConfiguration('world')
    

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] = os.environ['GAZEBO_MODEL_PATH'] + ':' + install_thor_gazebo + \
            '/share' + ':' + gz_model_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = install_thor_gazebo + \
            "/share" + ':' + gz_model_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_thor_gazebo + '/lib' + ':' + \
            gazebo_plugins_name_path_install_dir + '/lib' + ':'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_thor_gazebo + '/lib' + ':' + gazebo_plugins_name_path_install_dir + \
            '/lib' + ':'
    
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        os.environ['GZ_SIM_RESOURCE_PATH'] = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + install_thor_gazebo + \
            '/share' + ':' + gz_model_path
        os.environ['GZ_SIM_RESOURCE_PATH'] = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + install_thor_description + \
        '/share' 
    else: 
        os.environ['GZ_SIM_RESOURCE_PATH'] = install_thor_gazebo + '/share' + ':' + gz_model_path
        os.environ['GZ_SIM_RESOURCE_PATH'] = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + install_thor_description + \
        '/share'

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_simulator',
            default_value='True',
            description='Whether to start Gazebo'),
        DeclareLaunchArgument(
            name = 'world',
            default_value= world_path,
            description='World to load into Gazebo'
        ),
        DeclareLaunchArgument(
            name='headless',
            default_value='False',
            description='Display the Gazebo GUI if False, otherwise run in headless mode'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_model_path),

        IncludeLaunchDescription( #gz_server
            PythonLaunchDescriptionSource(gz_launch_path),
            condition=IfCondition(use_simulator),
            launch_arguments={
                'gz_args': ['-r -s -v4 ',world],
                'on_exit_shutdown': 'True'
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={'gz_args': '-g -v4 '}.items(),
            condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless]))),
    ])