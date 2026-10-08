"""Add the whiteboard station to MoveIt's planning scene: the board, the table,
and the arm's mounting plate and quick mount, in base_link."""

import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from shape_msgs.msg import SolidPrimitive

from whiteboard_setup.scene_update import SceneUpdate, run
from whiteboard_setup.station import planning_scene_boxes


class WhiteboardScene(SceneUpdate):
    def __init__(self) -> None:
        super().__init__("whiteboard_scene",
                         "Added the whiteboard, table, and arm mount to the planning scene.")

    def request(self) -> ApplyPlanningScene.Request:
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
        return ApplyPlanningScene.Request(scene=scene)


def main() -> None:
    rclpy.init()
    run(WhiteboardScene())


if __name__ == "__main__":
    main()
