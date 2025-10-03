#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose
from shape_msgs.msg import SolidPrimitive
from moveit_msgs.msg import CollisionObject, AttachedCollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene



def quat_from_rpy(roll, pitch, yaw):
    cr, sr = math.cos(roll/2), math.sin(roll/2)
    cp, sp = math.cos(pitch/2), math.sin(pitch/2)
    cy, sy = math.cos(yaw/2), math.sin(yaw/2)
    qw = cr*cp*cy + sr*sp*sy
    qx = sr*cp*cy - cr*sp*sy
    qy = cr*sp*cy + sr*cp*sy
    qz = cr*cp*sy - sr*sp*cy
    return (qx, qy, qz, qw)


class AttachPen(Node):
    """
    Attaches (or removes) a cylinder to the Kinova Gen3 Lite end effector in MoveIt.
    The cylinder axis is along +Z of the provided pose, which is expressed in the ee_link frame.
    """
    def __init__(self):

        super().__init__("attach_pen")

        # Target link to attach to (MoveIt link name)
        self.declare_parameter("ee_link", "end_effector_link")

        # Object identity / action
        self.declare_parameter("object_id", "pen_cyl")
        self.declare_parameter("attach", True)   # False -> detach

        # Cylinder geometry (meters): height and diameter (you set diameter=0.025)
        self.declare_parameter("height", 0.150)
        self.declare_parameter("diameter", 0.025)  # 25 mm diameter
        # Pose of the cylinder center relative to ee_link
        self.declare_parameter("x", 0.00)
        self.declare_parameter("y", 0.00)
        self.declare_parameter("z", 0.155)
        self.declare_parameter("roll", 0.0)
        self.declare_parameter("pitch", 0.0)
        self.declare_parameter("yaw", 0.0)


        self.declare_parameter("touch_links", [
            "end_effector_link",
            "tool_frame",                  # if present in your setup
            "gripper_base_link",           # or "2f_gripper_base_link"
            "left_finger_link",            # e.g., "finger_left_link"
            "right_finger_link",           # e.g., "finger_right_link"
            "left_inner_finger_link",      # inner pads if they exist
            "right_inner_finger_link",
        ])

        self.touch_links = [str(v) for v in self.get_parameter("touch_links").value]

        # Read params
        self.ee_link   = self.get_parameter("ee_link").get_parameter_value().string_value
        self.object_id = self.get_parameter("object_id").get_parameter_value().string_value
        self.attach    = bool(self.get_parameter("attach").value)

        self.height   = float(self.get_parameter("height").value)
        self.diameter = float(self.get_parameter("diameter").value)
        self.radius   = self.diameter / 2.0

        self.pos = (
            float(self.get_parameter("x").value),
            float(self.get_parameter("y").value),
            float(self.get_parameter("z").value),
        )
        self.rpy = (
            float(self.get_parameter("roll").value),
            float(self.get_parameter("pitch").value),
            float(self.get_parameter("yaw").value),
        )
        self.touch_links = [str(v) for v in self.get_parameter("touch_links").value]

        # Service
        self.cli = self.create_client(ApplyPlanningScene, "apply_planning_scene")
        self.timer = self.create_timer(0.5, self._tick)

    def _tick(self):
        if not self.cli.wait_for_service(timeout_sec=0.1):
            self.get_logger().info("Waiting for MoveIt 'apply_planning_scene'...")
            return

        req = self._make_attach_request() if self.attach else self._make_detach_request()
        fut = self.cli.call_async(req)
        fut.add_done_callback(self._done)
        self.timer.cancel()

    def _make_attach_request(self):
        # Build the collision shape (MoveIt expects [height, radius] for CYLINDER)
        cyl = SolidPrimitive(type=SolidPrimitive.CYLINDER)
        cyl.dimensions = [self.height, self.radius]

        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = self.pos
        qx, qy, qz, qw = quat_from_rpy(*self.rpy)
        pose.orientation.x = qx
        pose.orientation.y = qy
        pose.orientation.z = qz
        pose.orientation.w = qw

        # Define the collision object in the ee_link frame
        co = CollisionObject()
        co.id = self.object_id
        co.header.frame_id = self.ee_link
        co.primitives = [cyl]
        co.primitive_poses = [pose]
        co.operation = CollisionObject.ADD

        # Wrap as an attached object
        aco = AttachedCollisionObject()
        aco.link_name = self.ee_link
        aco.object = co
        aco.touch_links = self.touch_links  # can be empty

        # Build planning scene diff
        scene = PlanningScene()
        scene.is_diff = True
        scene.robot_state.is_diff = True
        scene.robot_state.attached_collision_objects = [aco]
        return ApplyPlanningScene.Request(scene=scene)

    def _make_detach_request(self):
        # Remove the attached object by ID
        aco = AttachedCollisionObject()
        aco.link_name = self.ee_link
        aco.object = CollisionObject()
        aco.object.id = self.object_id
        aco.object.operation = CollisionObject.REMOVE

        scene = PlanningScene()
        scene.is_diff = True
        scene.robot_state.is_diff = True
        scene.robot_state.attached_collision_objects = [aco]
        return ApplyPlanningScene.Request(scene=scene)

    def _done(self, fut):
        ok = fut.result() and getattr(fut.result(), "success", False)
        if ok:
            self.get_logger().info(
                f"{'Attached' if self.attach else 'Detached'} '{self.object_id}' to '{self.ee_link}'."
            )
        else:
            self.get_logger().warn("ApplyPlanningScene request failed.")
        rclpy.shutdown()


def main():
    rclpy.init()
    node = AttachPen()
    try:
        rclpy.spin(node)
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
