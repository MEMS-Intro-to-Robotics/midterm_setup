# Midterm whiteboard station

The `whiteboard_setup` package adds the midterm whiteboard station to Gazebo and to
MoveIt's planning scene, and attaches the marker adapter to the gripper in MoveIt.
It is built into the course Kinova image at `/opt/kortex_ws`, with two commands:

| Command | What it does |
|---|---|
| `kinova-whiteboard` | Adds the board, the table, and the arm's mounting plate and quick mount to Gazebo and to MoveIt's planning scene, then exits |
| `kinova-pen` | Attaches the marker adapter to `end_effector_link` in MoveIt's planning scene, then exits |

## Geometry

All values are in `base_link`, in meters, and match the lab stations and the midterm
handout:

- The board surface is the plane x = 0.55. The board is 1.016 m (40 in) wide and
  0.914 m tall above the tabletop.
- The table is 60 x 30 in, with its end at the board. The tabletop is 0.0627 m below
  `base_link` (the mounting plate and quick mount, as in Lab 6).
- The writing box, y from -0.25 to 0.25 and z from 0.04 to 0.30, is outlined on the
  board in Gazebo.
- The marker adapter, with its collar, spans z = 0.0776 to 0.2014 in
  `end_effector_link`. The marker tip is at z = 0.222, so the attached object ends
  21 mm short of the tip and a pen-down pose is not a collision with the board.

`whiteboard_setup/station.py` holds these values.

## Simulation

Start Gazebo and MoveIt as in Lab 5. Then, in another container terminal:

```bash
kinova-whiteboard
kinova-pen
```

Run both again after restarting MoveIt; the planning scene starts empty. Gazebo keeps
the station until it restarts.

## Real arm

There is no Gazebo, so add `gazebo:=false`:

```bash
kinova-whiteboard gazebo:=false
kinova-pen
```

To remove the adapter from the planning scene:

```bash
ros2 run whiteboard_setup attach_pen --ros-args -p attach:=false
```
