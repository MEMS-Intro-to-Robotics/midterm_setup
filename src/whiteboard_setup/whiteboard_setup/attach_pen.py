"""Attach the marker adapter to end_effector_link in MoveIt's planning scene, or
remove it with `--ros-args -p attach:=false`.

The attached object is the adapter and its collar (see station.py). It ends
21 mm short of the marker tip, so MoveIt does not count a pen-down pose as a
collision with the board, while the adapter itself still cannot be driven
into the board or the table. It is attached in the link's own frame, so the
arm's pose when you run this does not matter.
"""

import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import AttachedCollisionObject, CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from shape_msgs.msg import SolidPrimitive

from whiteboard_setup.scene_update import SceneUpdate, run
from whiteboard_setup.station import ADAPTER_CENTER_Z, ADAPTER_SIZE

LINK = "end_effector_link"
OBJECT_ID = "marker_adapter"
# Links the adapter may touch: the gripper holds it.
TOUCH_LINKS = [
    "end_effector_link", "dummy_link", "tool_frame", "gripper_base_link",
    "left_finger_prox_link", "left_finger_dist_link",
    "right_finger_prox_link", "right_finger_dist_link",
]


class AttachPen(SceneUpdate):
    def __init__(self) -> None:
        super().__init__("attach_pen", "")
        self.attach = bool(self.declare_parameter("attach", True).value)
        self.done_message = (f"Attached the marker adapter to {LINK}." if self.attach
                             else f"Removed the marker adapter from {LINK}.")

    def request(self) -> ApplyPlanningScene.Request:
        attached = AttachedCollisionObject(link_name=LINK)
        attached.object.id = OBJECT_ID
        attached.object.header.frame_id = LINK
        if self.attach:
            pose = Pose()
            pose.position.z = ADAPTER_CENTER_Z
            pose.orientation.w = 1.0
            attached.object.primitives = [
                SolidPrimitive(type=SolidPrimitive.BOX, dimensions=list(ADAPTER_SIZE))]
            attached.object.primitive_poses = [pose]
            attached.object.operation = CollisionObject.ADD
            attached.touch_links = TOUCH_LINKS
        else:
            attached.object.operation = CollisionObject.REMOVE
        scene = PlanningScene(is_diff=True)
        scene.robot_state.is_diff = True
        scene.robot_state.attached_collision_objects = [attached]
        return ApplyPlanningScene.Request(scene=scene)


def main() -> None:
    rclpy.init()
    run(AttachPen())


if __name__ == "__main__":
    main()
