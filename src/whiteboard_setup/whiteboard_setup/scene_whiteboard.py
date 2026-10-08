"""Add the whiteboard station to MoveIt's planning scene: the board, the table,
and the arm's mounting plate and quick mount, in base_link. The objects stay in
the planning scene until MoveIt restarts."""

import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive

from whiteboard_setup.station import planning_scene_boxes


class WhiteboardScene(Node):
    def __init__(self) -> None:
        super().__init__("whiteboard_scene")
        self.client = self.create_client(ApplyPlanningScene, "apply_planning_scene")
        self.timer = self.create_timer(1.0, self.try_apply)
        self.waiting_logged = False

    def try_apply(self) -> None:
        if not self.client.service_is_ready():
            if not self.waiting_logged:
                self.get_logger().info("Waiting for MoveIt (start MoveIt first)...")
                self.waiting_logged = True
            return
        self.timer.cancel()
        scene = PlanningScene(is_diff=True)
        for object_id, (size, center) in planning_scene_boxes().items():
            box = SolidPrimitive(type=SolidPrimitive.BOX, dimensions=list(size))
            pose = Pose()
            pose.position.x, pose.position.y, pose.position.z = center
            pose.orientation.w = 1.0
            obj = CollisionObject(id=object_id, operation=CollisionObject.ADD)
            obj.header.frame_id = "base_link"
            obj.primitives = [box]
            obj.primitive_poses = [pose]
            scene.world.collision_objects.append(obj)
        future = self.client.call_async(ApplyPlanningScene.Request(scene=scene))
        future.add_done_callback(self.done)

    def done(self, future) -> None:
        if future.result() is not None and future.result().success:
            self.get_logger().info(
                "Added the whiteboard, table, and arm mount to the planning scene.")
        else:
            self.get_logger().error("MoveIt did not accept the planning scene update.")
        raise SystemExit


def main() -> None:
    rclpy.init()
    node = WhiteboardScene()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
