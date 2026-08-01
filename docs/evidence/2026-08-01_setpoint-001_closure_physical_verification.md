# SETPOINT-001 Closure — Physical Test Drive Confirms Fix

Date:
2026-08-01

## Investigation

SETPOINT-001 (Motor Direction Investigation, `docs/SETPOINT_LOCKS.md`).

## Summary

The original evidence entry (2026-07-30) reconciled a `config.py` /
`drive.py` drift around `MOTOR_RIGHT_INVERT`, but a subsequent physical
test drive (iPad UI, 2026-07-31) showed that fix was incomplete: with
`steering=0`, forward and back commands sent identical values to both
motors, yet the wheels moved in opposite physical directions from each
other on both moves. This ruled out a right-only invert problem and
pointed at the left motor instead.

Root cause identified: `drive.py` had never implemented any inversion
logic for the left motor. `config.py` declared `MOTOR_LEFT_INVERT`, but
nothing in `drive.py` read it — only `MOTOR_RIGHT_INVERT` was ever
applied in `_apply()`. The physical wiring asymmetry between the two
motors is on the left side, not the right.

## Fix

- `nodes/pi/config.py`: `MOTOR_LEFT_INVERT` corrected `False -> True`.
  `MOTOR_RIGHT_INVERT` remains `False` (unchanged, was already correct).
- `nodes/pi/drive.py`: added `MOTOR_LEFT_INVERT = config.MOTOR_LEFT_INVERT`
  and a `phys_left` calculation in `_apply()`, mirroring the existing
  `phys_right` logic. `_write_motor()` for `CH_LEFT` now receives
  `phys_left` instead of the raw `left` value.

## Physical Verification (2026-08-01, iPad UI)

| Command | Expected            | Observed             | Match |
|---------|----------------------|-----------------------|-------|
| Up      | both wheels forward  | both wheels forward   | Yes   |
| Down    | both wheels reverse  | both wheels reverse   | Yes   |
| Left    | turn left            | turn left             | Yes   |
| Right   | turn right           | turn right            | Yes   |

All four directions confirmed correct via live test drive.

## Related fix (same session, unrelated to motor direction)

iPad Safari was triggering its text-selection/callout popup on
long-press of control buttons. Fixed by adding `-webkit-touch-callout:
none` (plus `-webkit-user-select: none` / `user-select: none`) to the
UI stylesheet. Applied to both the git-tracked `nodes/orin/ui/index.html`
and, separately, the actual local (uncommitted) `index.html` running on
the Orin — see "Open follow-up" below regarding why these are two
different files.

## Status

SETPOINT-001 is CLOSED. Root cause confirmed, fix applied, physically
verified on hardware.

## Open follow-up (not part of this setpoint, flagged for separate attention)

During deployment it was discovered that the Orin (`/home/bob/NanoBot`)
has substantial **uncommitted local changes** to `nodes/orin/webrtc_server.py`,
`nodes/orin/camera.py`, and `nodes/orin/ui/index.html` — the product of
an apparent repair session dated 2026-07-14 to 2026-07-16 (see the
`.before-*` / `.failed-*` backup files and several untracked
`docs/evidence/2026-07-1*` files sitting in that working directory).
This local version is the one actually running the WebRTC service and
serving the control page today; it already includes a `/` route
(`ui_handler`) and other fixes that the git-committed version — and an
earlier rebuild attempted in this SETPOINT-001 session — lacked. That
earlier rebuild was not deployed to the Orin once this was discovered,
avoiding overwriting working, undocumented local repair work.

This uncommitted work should be reviewed and properly committed in its
own dedicated session, since it currently exists in only one place (the
Orin's disk) with no backup. Recommend treating this as its own
Constitution-governed change: inventory the diffs, evaluate against
Setpoint Lock process, and commit deliberately rather than as a
byproduct of an unrelated fix.
