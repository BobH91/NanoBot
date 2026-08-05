# NanoBot Evidence Checkpoint
Date: 2026-07-14

## WebRTC Camera Repair

Machine:
NVIDIA Jetson Orin Nano (Nanobot)

Baseline:
v8.3-locked-baseline
Commit:
87e4a6e7194ae27d2741e2feb9ae32b599d077a3

## Problem Found

nanobot-webrtc.service failed because:

RuntimeError:
Cannot open camera: /dev/video0

Evidence:
- /dev/video0 did not exist
- USB camera appeared as:
  /dev/video1
  /dev/video2

## Repair

Updated:
nodes/orin/camera.py

Changed camera device:
FROM:
 /dev/video0

TO:
 /dev/video1

## Verification

systemd:
nanobot-webrtc.service ACTIVE

Port:
8080 LISTENING

Status endpoint:
camera frame_count increasing
fps_measured ~15 FPS
drop_count 0

## Additional Finding

Git staging anomaly discovered.

Cause:
.nod_identity was modified and previously staged as deletion.

Evidence:
git reflog showed no destructive history operation.

Recovery:
git restore --staged .node_identity

Current action:
restore original file before further development.

## Lesson

Create intermediate checkpoints before:
- git restore
- git checkout
- git add
- git rm
- service changes
- code replacement operations
