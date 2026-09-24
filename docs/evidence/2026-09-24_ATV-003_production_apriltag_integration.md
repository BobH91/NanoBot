# ATV-003 — Production AprilTag Integration Verification

**Date:** 2026-09-24
**Machine:** Orin Nano (`Nanobot`)
**Repository HEAD:** `1652a12`
**Status:** PASS

## Purpose

Verify the complete production AprilTag path:

Camera → FrameGrabber → `_apriltag_loop` → `AprilTagWorker` → C-002 calibration → AprilTag detector → `/status`

This verification establishes production integration and short-term repeatability.
It does **not** establish absolute AprilTag distance accuracy.

## Locked Setpoints

- Camera: `/dev/video0`
- Image: `1280 × 720`
- Tag family: `tag36h11`
- Tag ID: `0`
- Tag size: `0.150 m`
- Calibration: C-002
- C-002 SHA-256:
  `9babdf22e7a20ae309ad84930e41b8c3b3f3f882f75a82d2a5f8542579793230`
- Python runtime:
  `/home/bob/nanobot-apriltag-venv/bin/python`
- Detector configuration: ATV-002 verified configuration

## Integrated Source

### `nodes/orin/apriltag_worker.py`

SHA-256:

`6eedbe36f1a743717bf450163686c0449d58756b1176b46bd32b414360a6ed40`

### `nodes/orin/webrtc_server.py`

SHA-256:

`832fcfffda75172d24c526647ed256e0f8ff1150d4c9c02ea8b6e309de36234f`

The AprilTag worker operates as a thread inside the service process and
does not open the camera independently.

## Step 36 — 60-Second Production Retest

Service MainPID:

`35157`

The service remained active throughout the test.

### Results

| Measurement | Result |
|---|---:|
| HTTP samples | 60/60 |
| Valid AprilTag results | 60/60 |
| Tag detected | 60/60 |
| Tag ID 0 | 60/60 |
| Hamming 0 | 60/60 |
| Worker alive | 60/60 |
| Errors | 0 |
| Detector runtime minimum | 66.850 ms |
| Detector runtime maximum | 92.356 ms |
| Detector runtime mean | 78.183 ms |
| Distance minimum | 1.175268 m |
| Distance maximum | 1.176022 m |
| Distance mean | 1.175636 m |
| Distance spread | 0.000754 m / 0.754 mm |
| Camera FPS minimum | 14.9 |
| Camera FPS maximum | 15.2 |
| Camera drops minimum | 0 |
| Camera drops maximum | 0 |

Every one of the 60 samples reported:

- `detected=True`
- `tag_id=0`
- `hamming=0`
- `worker_alive=True`
- `error=null`
- `drop_count=0`

## Result

**ATV-003 PASS — Production AprilTag integration verified.**

The complete production path operated continuously for 60 seconds with:

- 60/60 successful HTTP status samples
- 60/60 successful AprilTag results
- 60/60 Tag 0 detections
- 60/60 hamming-zero detections
- zero worker errors
- zero request errors
- zero camera frame drops
- stable pose output

The measured distance varied by only 0.754 mm during this fixed-camera
test, demonstrating strong short-term production repeatability.

## Accuracy Limitation

The camera/tag geometry was not changed or measured against a controlled
physical reference during this test.

Therefore the approximately 1.176 m distance **must not be treated as an
absolute-accuracy result**.

C-004 remains the controlled absolute-distance experiment and remains:

`COMPLETED_ABSOLUTE_ACCURACY_NOT_ESTABLISHED`

No correction factor or recalibration was introduced.

## Camera Performance Observation

The camera operated at approximately 15 FPS with zero reported frame drops.

The previously documented camera-control persistence gap remains separate
from ATV-003. No camera-control changes were made during this verification.

## WebRTC Scope

No WebRTC regression was identified.

The previously verified WebRTC fix remains closed and was not reopened.

## Governance

No source-code or camera-configuration changes were made during Step 36.

The Orin repository remained at Git HEAD `1652a12`.

The ATV-003 integration source and evidence are not yet committed to the
Lenovo source-of-truth.

## Milestone Conclusion

ATV-003 production AprilTag integration is verified and may proceed to the
evidence-transfer and source-of-truth commit stage.

The remaining camera ~15 FPS issue is a separate known setpoint-persistence
gap and is not an ATV-003 failure.

Absolute AprilTag distance accuracy remains unestablished.
