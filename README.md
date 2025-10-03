---

# Midterm: Optional Whiteboard & Pen Setup (Physical Robot)

If you choose to run your midterm on the **physical Kinova Gen3 Lite**, you’ll need to set up the environment so MoveIt knows about the **whiteboard** and the **pen** the robot will be holding.

---

## 1. Spawn the Whiteboard

Start the whiteboard (static object in Gazebo, matching collision boxes in MoveIt):

```bash
ros2 launch whiteboard_setup spawn_whiteboard.launch.py
```

This ensures your planning scene matches the physical setup with the board in front of the robot.

---

## 2. Attach the Pen (MoveIt only)

The robot will be holding a simulated pen (25 mm diameter × 150 mm tall) in MoveIt.
This is only added to the **planning scene** — it is not spawned into Gazebo to avoid physics engine complications.

Run:

```bash
ros2 run whiteboard_setup attach_pen
```

This attaches the pen to the robot’s `end_effector_link`, so it follows the gripper when planning motions.

⚠️ **Important:** Do this **before moving the robot**.
If you attach after moving, the pen will be in the wrong place relative to the arm.

To remove the pen later:

```bash
ros2 run whiteboard_setup attach_pen --ros-args -p attach:=false
```

---

## 3. Key Notes

* The pen is allowed to contact the gripper fingers (so you won’t get collision errors).
* Dimensions are slightly larger than the actual marker so that planning is conservative.
* If you are only running your midterm in **simulation**, you do not need this setup.

---

✅ With both steps complete, your MoveIt planning scene will accurately reflect the real robot holding a pen in front of the whiteboard.

---