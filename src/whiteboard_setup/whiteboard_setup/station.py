"""Geometry of the midterm whiteboard station, in base_link (meters).

These match the lab stations and the midterm handout: the arm on its mounting
plate and quick mount on a 60 x 30 in table, and a 40 in wide whiteboard against
the end of the table with its surface at x = 0.55 m. The marker adapter
dimensions come from the adapter CAD (intro-to-robotics-labs,
hardware/marker-adapter), expressed in end_effector_link.
"""

BOARD_X = 0.55  # board surface, ahead of base_link
BOARD_THICKNESS = 0.02
BOARD_WIDTH = 1.016  # 40 in
BOARD_HEIGHT = 0.914  # the part above the tabletop

QUICK_MOUNT_SIZE = (0.11, 0.11, 0.050)
PLATE_SIZE = (0.3048, 0.3048, 0.0127)  # 12 x 12 x 0.5 in
TABLE_TOP_Z = -(QUICK_MOUNT_SIZE[2] + PLATE_SIZE[2])  # -0.0627
TABLE_SIZE = (1.524, 0.762, 0.038)  # 60 x 30 in, long side toward the board
TABLE_CENTER_X = BOARD_X - TABLE_SIZE[0] / 2  # the table ends at the board

# The writing box from the handout, drawn on the board in Gazebo.
WRITING_BOX_Y = (-0.25, 0.25)
WRITING_BOX_Z = (0.04, 0.30)

# Gazebo places base_link this far above its ground plane (as in Labs 5 and 6).
GAZEBO_BASE_HEIGHT = 0.30
STATION_MODEL = "midterm_station"

# Marker adapter with its collar, in end_effector_link: 35 x 50 mm across,
# from the gripper palm (z = 77.6 mm) to the collar (z = 201.4 mm). The marker
# tip is at z = 222.2 mm, so the attached object ends 21 mm short of the tip and
# a pen-down pose is not a collision with the board.
ADAPTER_SIZE = (0.035, 0.050, 0.2014 - 0.0776)
ADAPTER_CENTER_Z = (0.2014 + 0.0776) / 2
MARKER_TIP_Z = 0.222

# A gap between the quick mount and base_link, so MoveIt does not report the
# arm's base touching its own mount (the same gap as Lab 6).
_GAP = 0.001


def planning_scene_boxes() -> dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]]:
    """Collision boxes for MoveIt: id -> (size, center), in base_link."""
    qx, qy, qz = QUICK_MOUNT_SIZE
    return {
        "whiteboard": ((BOARD_THICKNESS, BOARD_WIDTH, BOARD_HEIGHT),
                       (BOARD_X + BOARD_THICKNESS / 2, 0.0, TABLE_TOP_Z + BOARD_HEIGHT / 2)),
        "table": (TABLE_SIZE, (TABLE_CENTER_X, 0.0, TABLE_TOP_Z - TABLE_SIZE[2] / 2)),
        "mount_plate": (PLATE_SIZE, (0.0, 0.0, TABLE_TOP_Z + PLATE_SIZE[2] / 2)),
        "quick_mount": ((qx, qy, qz - _GAP),
                        (0.0, 0.0, TABLE_TOP_Z + PLATE_SIZE[2] + (qz - _GAP) / 2)),
    }


def _box(name: str, size: tuple[float, ...], center: tuple[float, ...], rgba: str,
         collide: bool = True, emissive: str = "0 0 0 1") -> str:
    x, y, z = center
    z += GAZEBO_BASE_HEIGHT
    sx, sy, sz = size
    geometry = f"<geometry><box><size>{sx} {sy} {sz}</size></box></geometry>"
    visual = (f"<visual name='{name}'><pose>{x} {y} {z} 0 0 0</pose>{geometry}"
              f"<material><ambient>{rgba}</ambient><diffuse>{rgba}</diffuse>"
              f"<emissive>{emissive}</emissive></material></visual>")
    if not collide:
        return visual
    return f"<collision name='{name}'><pose>{x} {y} {z} 0 0 0</pose>{geometry}</collision>{visual}"


def station_sdf() -> str:
    """The station as one static Gazebo model: table, plate, quick mount, and the
    board with the writing box outlined on it."""
    boxes = planning_scene_boxes()
    parts = [
        _box("table", *boxes["table"], "0.87 0.75 0.55 1"),
        _box("mount_plate", *boxes["mount_plate"], "0.8 0.81 0.83 1"),
        _box("quick_mount", QUICK_MOUNT_SIZE,
             (0.0, 0.0, TABLE_TOP_Z + PLATE_SIZE[2] + QUICK_MOUNT_SIZE[2] / 2), "0.05 0.05 0.05 1"),
        _box("board_frame", *boxes["whiteboard"], "0.55 0.55 0.58 1"),
        # The white writing surface, a millimeter in front of the frame. Gazebo's
        # default sun lights the back of the board, so the face glows to stay white.
        _box("board_surface", (0.001, BOARD_WIDTH - 0.03, BOARD_HEIGHT - 0.03),
             (BOARD_X - 0.0005, 0.0, TABLE_TOP_Z + BOARD_HEIGHT / 2), "0.97 0.97 0.97 1",
             collide=False, emissive="0.8 0.8 0.8 1"),
    ]
    # The writing box as four thin gray lines on the surface.
    (y0, y1), (z0, z1), width = WRITING_BOX_Y, WRITING_BOX_Z, 0.004
    x = BOARD_X - 0.0015
    for name, size, center in (
        ("box_left", (0.001, width, z1 - z0), (x, y0, (z0 + z1) / 2)),
        ("box_right", (0.001, width, z1 - z0), (x, y1, (z0 + z1) / 2)),
        ("box_bottom", (0.001, y1 - y0, width), (x, 0.0, z0)),
        ("box_top", (0.001, y1 - y0, width), (x, 0.0, z1)),
    ):
        parts.append(_box(name, size, center, "0.6 0.6 0.6 1", collide=False))
    return (f"<?xml version='1.0'?><sdf version='1.8'><model name='{STATION_MODEL}'>"
            f"<static>true</static><link name='station'>{''.join(parts)}</link></model></sdf>")
