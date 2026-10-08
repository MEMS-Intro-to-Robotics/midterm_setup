# Midterm whiteboard station

The `whiteboard_setup` package provides the midterm simulation and the whiteboard
station for Gazebo and MoveIt. It is built into the course Kinova image at
`/opt/kortex_ws`, with these commands:

| Command | What it does |
|---|---|
| `kinova-midterm` | Simulation: Gazebo with the Gen3 Lite and its controllers, the whiteboard station, and two nodes that add the station and the marker holder to MoveIt's planning scene whenever MoveIt starts |
| `kinova-whiteboard` | Adds the board, the table, and the arm's mounting plate and quick mount to Gazebo and to MoveIt's planning scene, then exits (`gazebo:=false` on the real arm) |
| `kinova-pen` | Attaches the marker adapter to `end_effector_link` in MoveIt's planning scene, then exits |

## Simulation

Run each command in its own container terminal, in this order:

1. `kinova-midterm` starts Gazebo, the arm's controllers, and the station.
2. `kinova-sim-moveit` starts MoveIt and RViz. When MoveIt is running, the
   `kinova-midterm` terminal reports that the station and the marker adapter were
   added to the planning scene. After a MoveIt restart they are added again.
3. Your program.

## Real arm

There is no Gazebo. Start MoveIt with `kinova-moveit`, then:

```bash
kinova-whiteboard gazebo:=false
kinova-pen
```

Run both again after restarting MoveIt. To remove the adapter from the planning
scene:

```bash
ros2 run whiteboard_setup attach_pen --ros-args -p attach:=false
```

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
