from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    LaunchConfiguration, Command, PathJoinSubstitution, FindExecutable
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    use_gz = LaunchConfiguration("use_gz")
    entity = LaunchConfiguration("entity")
    x = LaunchConfiguration("x"); y = LaunchConfiguration("y"); z = LaunchConfiguration("z")
    R = LaunchConfiguration("R"); P = LaunchConfiguration("P"); Y = LaunchConfiguration("Y")
    base_frame = LaunchConfiguration("base_frame")

    urdf_xacro = PathJoinSubstitution([
        FindPackageShare("whiteboard_setup"), "urdf", "whiteboard_setup.urdf.xacro"
    ])

    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", urdf_xacro]),
        value_type=str,
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    spawn_gz = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", entity, "-topic", "robot_description",
            "-x", x, "-y", y, "-z", z, "-R", R, "-P", P, "-Y", Y,
        ],
        output="screen",
        condition=IfCondition(use_gz),
    )

    spawn_classic = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", entity, "-topic", "robot_description",
            "-x", x, "-y", y, "-z", z, "-R", R, "-P", P, "-Y", Y,
        ],
        output="screen",
        condition=UnlessCondition(use_gz),
    )

    # NEW: add the MoveIt Planning Scene boxes (same pose/rotation)
    scene_node = Node(
        package="whiteboard_setup",
        executable="whiteboard_scene",
        name="whiteboard_scene",
        parameters=[{
            "base_frame": base_frame,  # usually "base_link"
            "x": x, "y": y, "z": z,
            "yaw": Y,
            # you can override sizes/offsets here if needed:
            # "base_size": [0.3048, 0.9144, 0.062],
            # "panel_size": [0.3048, 0.0286, 0.6096],
            # "panel_offset_xyz": [0.00, 0.668, 0.0381],
        }],
    )

    # Exit the launch once the scene node finishes
    shutdown_when_done = RegisterEventHandler(
        OnProcessExit(target_action=scene_node, on_exit=[EmitEvent(event=Shutdown())])
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_gz", default_value="true"),
        DeclareLaunchArgument("entity", default_value="whiteboard"),
        DeclareLaunchArgument("x", default_value="-0.1524"),
        DeclareLaunchArgument("y", default_value="0.1524"),
        DeclareLaunchArgument("z", default_value="0.2373"),
        DeclareLaunchArgument("R", default_value="0.0"),
        DeclareLaunchArgument("P", default_value="0.0"),
        DeclareLaunchArgument("Y", default_value="-1.5708"),
        DeclareLaunchArgument("base_frame", default_value="world"),

        rsp,
        spawn_gz,
        spawn_classic,
        scene_node,
        shutdown_when_done,
    ])

