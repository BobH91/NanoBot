# Orin Camera Performance — Verified Problem and Solution

## Status

**VERIFIED / LOCKED**

Date: 2026-09-14  
Machine: Jetson Orin Nano (`Nanobot`)  
Verification ID: `ORIN-CAM-720P30-PROBLEM-SOLUTION`

## Verified Camera Baseline

- Device: `/dev/video0`
- Format: MJPG
- Resolution: 1280×720
- Configured FPS: 30
- Measured FPS: approximately 29.7–29.8 FPS
- Dropped frames: 0
- JPEG quality: 85
- Forced OpenCV `CAP_PROP_BUFFERSIZE=1`: **not used**

## Verified Performance Problem

During controlled testing, forcing:

`cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)`

reduced sustained camera capture performance.

Removing that forced buffer setting restored approximately 29.7–29.8 FPS with zero dropped frames.

No artificial 15 FPS limiter exists in the NanoBot camera capture loop.

## Historical 15.1 FPS Observation

A separate runtime observation reported approximately 15.1 FPS.

A subsequent controlled restart of `nanobot-webrtc.service` from a verified approximately 29.8 FPS state produced approximately 29.7–29.8 FPS with zero dropped frames.

Therefore, the historical 15.1 FPS observation remains documented as an anomaly with **no assigned cause**.

## Locked State

The camera baseline is locked at:

**`/dev/video0` / MJPG / 1280×720 / 30 FPS configured / approximately 29.7–29.8 FPS measured / 0 drops**

No camera code, V4L2 control, or runtime configuration should be changed without an explicitly authorized controlled change.

## Authoritative Engineering Record

Full evidence is maintained in the NanoBot Git repository:

`docs/evidence/2026-09-14_orin_camera_problem_solution.md`

Git commit:

`76bcdd0`

Commit message:

`docs: record Orin camera problem and verified solution`

## Historical Evidence

Original camera verification:

`docs/evidence/2026-09-09_orin_camera_1280x720_30fps_verification.md`

Historical 15.1 FPS observation:

`87e7f6b`

Preserved documentation patch SHA-256:

`8b14f76695201acc42dfb051eeb3b61b3430f9cb196d0162c8ad4bf2ca6a9017`
