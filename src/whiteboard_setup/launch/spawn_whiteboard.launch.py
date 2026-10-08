"""Add the midterm whiteboard station: the board, the table, and the arm's mount.

In simulation, start Gazebo and MoveIt first (as in Lab 5), then:

    ros2 launch whiteboard_setup spawn_whiteboard.launch.py

This puts the station in Gazebo and the same objects in MoveIt's planning scene,
then exits. On the real arm, where there is no Gazebo, add gazebo:=false.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from whiteboard_setup.station import STATION_MODEL, station_sdf


def generate_launch_description() -> LaunchDescription:
    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-string", station_sdf(), "-name", STATION_MODEL, "-allow_renaming", "false"],
        output="screen",
        condition=IfCondition(LaunchConfiguration("gazebo")),
    )
    scene = Node(package="whiteboard_setup", executable="whiteboard_scene", output="screen")
    return LaunchDescription([
        DeclareLaunchArgument("gazebo", default_value="true",
                              description="Also add the station to Gazebo (false on the real arm)"),
        spawn,
        scene,
        RegisterEventHandler(OnProcessExit(target_action=scene,
                                           on_exit=[EmitEvent(event=Shutdown())])),
    ])
