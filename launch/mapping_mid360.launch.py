#!/usr/bin/python3
# -- coding: utf-8 --

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    # Package paths
    config_file_dir = os.path.join(get_package_share_directory("fast_livo"), "config")
    rviz_config_file = os.path.join(get_package_share_directory("fast_livo"), "rviz_cfg", "fast_livo2.rviz")

    # MID360 + D435i config
    mid360_config_cmd = os.path.join(config_file_dir, "mid360.yaml")
    camera_config_cmd = os.path.join(config_file_dir, "camera_d435i.yaml")

    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="True",
        description="Whether to launch Rviz2",
    )

    mid360_config_arg = DeclareLaunchArgument(
        "mid360_params_file",
        default_value=mid360_config_cmd,
        description="Full path to the ROS2 parameters file to use for fast_livo2 nodes",
    )

    camera_config_arg = DeclareLaunchArgument(
        "camera_params_file",
        default_value=camera_config_cmd,
        description="Full path to the ROS2 parameters file to use for vikit_ros nodes",
    )

    use_respawn_arg = DeclareLaunchArgument(
        "use_respawn",
        default_value="True",
        description="Whether to respawn if a node crashes. Applied when composition is disabled.",
    )

    mid360_params_file = LaunchConfiguration("mid360_params_file")
    camera_params_file = LaunchConfiguration("camera_params_file")
    use_respawn = LaunchConfiguration("use_respawn")

    return LaunchDescription([
        use_rviz_arg,
        mid360_config_arg,
        camera_config_arg,
        use_respawn_arg,

        # For real hardware input, raw image is published directly by the camera driver.
        # No image_transport republish node is required.
        Node(
            package="fast_livo",
            executable="fastlivo_mapping",
            name="laserMapping",
            parameters=[
                mid360_params_file,
                camera_params_file,
            ],
            output="screen",
            respawn=use_respawn,
        ),

        Node(
            condition=IfCondition(LaunchConfiguration("use_rviz")),
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz_config_file],
            output="screen",
        ),
    ])
