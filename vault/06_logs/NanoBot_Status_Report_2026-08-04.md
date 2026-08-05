# NanoBot Status Report — 2026-08-04

**Prepared for sharing.** Summary of tonight's incident, the fix applied, and current system
status across all three NanoBot nodes.

---

## TL;DR

The NanoBot browser UI (video + controls) went down across all client devices (iPad, iPhone,
Lenovo). Root cause: an old, uncommitted local edit on the robot's vision computer pointed the
camera driver at the wrong device path, crashing the video service in a restart loop. Fixed by
restoring the correct value from the authoritative GitHub repo. **System is now fully operational
and verified stable across all three machines.**

---

## What Was Broken

- UI failed to connect from all three client devices at once (iPad: "can't find server";
  iPhone/Lenovo: page loaded but couldn't connect).
- Root cause: `nanobot-webrtc.service` on the Jetson Orin Nano (the robot's vision/control
  computer) was crash-looping — it had restarted **662 times** trying and failing to start.
- The failure: the camera driver code (`camera.py`) had an uncommitted local edit pointing at
  `/dev/video1`, a camera device path with no usable video-capture capability. This edit dated
  back to a troubleshooting attempt from mid-July that was never fully cleaned up or committed to
  GitHub, so it sat undetected for about three weeks.

## How It Was Fixed

1. Diagnosed via live service logs (`journalctl`) — found the exact crash: `RuntimeError: Cannot
   open camera: /dev/video1`.
2. Verified directly on the hardware (`v4l2-ctl`) which camera device path is actually
   functional: `/dev/video0`.
3. Compared the Orin's local file against the correct, committed version on GitHub — confirmed
   the mismatch.
4. Restored the correct file from GitHub (`git restore --source=origin/main`) and restarted the
   service.
5. Verified live: video and controls confirmed working in-browser (Firefox, Lenovo) after the fix.
6. Wrote a full incident report with timeline, committed to the project vault for future
   reference.
7. Improved the project's health-check script to specifically flag this class of issue (an
   uncommitted change to a tracked file) going forward, so it surfaces immediately instead of
   hiding among routine debug-session leftovers.

## Current Status — All Systems

| Node | Git status | Sync status |
|---|---|---|
| **Lenovo** (dev machine / controller) | Clean, up to date with GitHub `main` | Syncthing active |
| **Raspberry Pi 5** (motor control) | Clean, up to date with GitHub `main` | Syncthing active |
| **Jetson Orin Nano** (vision/control) | Clean (no uncommitted changes to tracked files), up to date with GitHub `main` | Syncthing active |

- **GitHub**: all three machines confirmed in sync with `origin/main`, no divergence.
- **NanoBot vault** (project documentation): incident report and updated health-check tooling
  committed and pushed.
- **Syncthing**: active and responding on all three machines.
- **Overall stability**: no outstanding drift or crash conditions detected as of the last
  health check run tonight.

## Known Non-Urgent Housekeeping (does not affect operation)

- ~31 old backup/troubleshooting files from a mid-July debugging session are still sitting
  untracked on the Orin (harmless, just clutter — cleanup planned for a future session).
- A small test script (`drive_logic_test.py`) remains untracked on the Lenovo, pending a
  decision on whether to commit or discard it.

---

*Report generated from live diagnostic evidence (service logs, git history, hardware queries)
during tonight's debugging session — no assumptions, everything below was independently verified.*
