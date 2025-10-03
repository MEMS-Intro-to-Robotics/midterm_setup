#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose
from shape_msgs.msg import SolidPrimitive
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene

def quat_from_yaw(yaw):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))

class WhiteboardScene(Node):
    def __init__(self):
        super().__init__("whiteboard_scene")

        # Frames & rotation
        self.declare_parameter("base_frame", "world")   # publish into 'world' so RViz matches Gazebo
        self.declare_parameter("yaw", -1.5708)          # 90° right by default

        # Geometry (from your URDF)
        self.declare_parameter("base_size",  [0.3048, 0.9144, 0.062])
        self.declare_parameter("panel_size", [0.3048, 0.0286, 0.6096])

        # Absolute centers in world (your RViz targets)
        self.declare_parameter("wb_base_center",  [0.3048, 0.0,   -0.0311])
        self.declare_parameter("wb_panel_center", [0.5142, 0.0,    0.3047])

        # Read params
        self.base_frame    = self.get_parameter("base_frame").get_parameter_value().string_value
        self.yaw           = float(self.get_parameter("yaw").value)
        self.base_size     = [float(v) for v in self.get_parameter("base_size").value]
        self.panel_size    = [float(v) for v in self.get_parameter("panel_size").value]
        self.base_center   = [float(v) for v in self.get_parameter("wb_base_center").value]
        self.panel_center  = [float(v) for v in self.get_parameter("wb_panel_center").value]

        # Service client
        self.cli = self.create_client(ApplyPlanningScene, "apply_planning_scene")
        self.timer = self.create_timer(0.5, self.try_apply)  # retry until service is ready

    def _box_obj(self, obj_id, size_xyz, center_xyz, yaw):
        prim = SolidPrimitive(type=SolidPrimitive.BOX)
        prim.dimensions = list(size_xyz)  # [x, y, z]

        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = center_xyz
        qx, qy, qz, qw = quat_from_yaw(yaw)
        pose.orientation.x = qx
        pose.orientation.y = qy
        pose.orientation.z = qz
        pose.orientation.w = qw

        obj = CollisionObject()
        obj.id = obj_id
        obj.header.frame_id = self.base_frame
        obj.primitives = [prim]
        obj.primitive_poses = [pose]
        obj.operation = CollisionObject.ADD
        return obj

    def try_apply(self):
        if not self.cli.wait_for_service(timeout_sec=0.1):
            self.get_logger().info("Waiting for MoveIt 'apply_planning_scene'...")
            return

        base_obj  = self._box_obj("wb_base",  self.base_size,  tuple(self.base_center),  self.yaw)
        panel_obj = self._box_obj("wb_panel", self.panel_size, tuple(self.panel_center), self.yaw)

        scene = PlanningScene()
        scene.is_diff = True
        scene.world.collision_objects = [base_obj, panel_obj]

        req = ApplyPlanningScene.Request(scene=scene)
        future = self.cli.call_async(req)

        def done_cb(_):
            ok = future.result() and getattr(future.result(), "success", False)
            if ok:
                self.get_logger().info("Whiteboard added to Planning Scene.")
            else:
                self.get_logger().warn("Failed to apply Planning Scene.")
            rclpy.shutdown()

        future.add_done_callback(done_cb)
        self.timer.cancel()

def main():
    rclpy.init()
    node = WhiteboardScene()
    try:
        rclpy.spin(node)
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()
