"""Midterm simulation: Gazebo with the Gen3 Lite and the whiteboard station.

    ros2 launch whiteboard_setup midterm_sim.launch.py     (alias: kinova-midterm)

Starts, in this terminal:
  1. Gazebo with the Kinova Gen3 Lite and its controllers (the same launch as
     Lab 5, with the arguments filled in);
  2. the whiteboard station in Gazebo: the table, the arm's mounting plate and
     quick mount, and the board with the writing box outlined;
  3. two nodes that add the station and the marker holder to MoveIt's planning
     scene as soon as MoveIt is running, and again each time MoveIt restarts.

Start MoveIt and RViz separately, in their own terminal, with kinova-sim-moveit.
"""

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from whiteboard_setup.station import STATION_MODEL, station_sdf

# Gazebo's default camera starts far from the arm. This view looks at the arm and
# the board from behind the arm's right side.
CAMERA_POSE = ("pose: {position: {x: -0.75, y: -1.05, z: 1.05}, "
               "orientation: {x: -0.0588, y: 0.1468, z: 0.3672, w: 0.9166}}")


def generate_launch_description() -> LaunchDescription:
    kinova = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("kortex_bringup"), "/launch/kortex_sim_control.launch.py"]),
        launch_arguments={
            "sim_gazebo": "true",
            "robot_type": "gen3_lite",
            "gripper": "gen3_lite_2f",
            "robot_name": "gen3_lite",
            "dof": "6",
            "launch_rviz": "false",
            "use_sim_time": "true",
            "robot_controller": "joint_trajectory_controller",
        }.items(),
    )
    station = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-string", station_sdf(), "-name", STATION_MODEL, "-allow_renaming", "false"],
        output="screen",
    )
    scene = Node(package="whiteboard_setup", executable="whiteboard_scene", output="screen",
                 parameters=[{"watch": True, "use_sim_time": True}])
    pen = Node(package="whiteboard_setup", executable="attach_pen", output="screen",
               parameters=[{"watch": True, "use_sim_time": True}])
    camera = ExecuteProcess(
        cmd=["bash", "-c",
             "for i in $(seq 30); do gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera "
             "--reptype gz.msgs.Boolean --timeout 2000 "
             f"--req '{CAMERA_POSE}' 2>/dev/null | grep -q true && exit 0; sleep 2; done"],
    )
    return LaunchDescription([
        kinova,
        # Gazebo needs a few seconds before it accepts new models.
        TimerAction(period=5.0, actions=[station]),
        TimerAction(period=8.0, actions=[camera, scene, pen]),
    ])
