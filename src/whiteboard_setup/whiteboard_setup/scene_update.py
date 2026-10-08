"""Shared logic for the nodes that add objects to MoveIt's planning scene.

A node waits for MoveIt's apply_planning_scene service, applies its update, and
exits. With the parameter watch:=true it keeps running instead and applies the
update again each time MoveIt restarts, because a restarted MoveIt starts with
an empty planning scene.
"""

import rclpy
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.node import Node


class SceneUpdate(Node):
    def __init__(self, name: str, done_message: str) -> None:
        super().__init__(name)
        self.watch = bool(self.declare_parameter("watch", False).value)
        self.done_message = done_message
        self.client = self.create_client(ApplyPlanningScene, "apply_planning_scene")
        self.applied = False
        self.pending = False
        self.waiting_logged = False
        self.timer = self.create_timer(1.0, self.tick)

    def request(self) -> ApplyPlanningScene.Request:
        raise NotImplementedError

    def tick(self) -> None:
        if not self.client.service_is_ready():
            if self.applied:
                self.get_logger().info("MoveIt stopped; this is added again when it restarts.")
                self.applied = False
            if not self.waiting_logged:
                self.get_logger().info("Waiting for MoveIt to start...")
                self.waiting_logged = True
            return
        if self.applied or self.pending:
            return
        self.pending = True
        self.client.call_async(self.request()).add_done_callback(self.done)

    def done(self, future) -> None:
        self.pending = False
        if future.result() is not None and future.result().success:
            self.applied = True
            self.waiting_logged = False
            self.get_logger().info(self.done_message)
        else:
            self.get_logger().error("MoveIt did not accept the planning scene update.")
        if not self.watch:
            raise SystemExit


def run(node: SceneUpdate) -> None:
    try:
        rclpy.spin(node)
    except (SystemExit, KeyboardInterrupt):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
