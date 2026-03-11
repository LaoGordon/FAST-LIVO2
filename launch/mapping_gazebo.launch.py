#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAST-LIVO2 Gazebo 仿真启动文件
用于 quadruped_ws Gazebo 仿真环境下的 SLAM 建图

用法:
  ros2 launch fast_livo mapping_gazebo.launch.py [use_rviz:=True]
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    # 获取包路径
    pkg_share = get_package_share_directory('fast_livo')

    # 配置文件
    # 仿真环境使用专用的外参配置 (mid360_sim.yaml 和 camera_sim.yaml)
    # 这些文件中的外参是根据 xacro 机器人模型计算的
    config_file = os.path.join(pkg_share, 'config', 'mid360_sim.yaml')
    camera_config_file = os.path.join(pkg_share, 'config', 'camera_sim.yaml')
    rviz_config_file = os.path.join(pkg_share, 'rviz_cfg', 'fast_livo2.rviz')
    
    # 参数声明
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='False',
        description='Whether to launch RViz2'
    )
    
    use_respawn_arg = DeclareLaunchArgument(
        'use_respawn',
        default_value='False',
        description='Whether to respawn if a node crashes'
    )
    
    use_rviz = LaunchConfiguration('use_rviz')
    use_respawn = LaunchConfiguration('use_respawn')
    
    # FAST-LIVO2 节点
    fastlivo_node = Node(
        package='fast_livo',
        executable='fastlivo_mapping',
        name='laserMapping',
        parameters=[
            config_file,
            camera_config_file,
            {'use_sim_time': True},  # 关键：使用仿真时间
        ],
        output='screen',
        respawn=use_respawn,
    )

    # RViz2 节点（可选）
    rviz_node = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen',
    )
    
    return LaunchDescription([
        use_rviz_arg,
        use_respawn_arg,
        fastlivo_node,
        rviz_node,
    ])
