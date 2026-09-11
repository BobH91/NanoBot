# Orin Camera 1280×720 / 30 FPS Verification and Freeze

**Status:** VERIFIED / FROZEN
**Date:** 2026-09-09
**Machine:** Jetson Orin Nano (`Nanobot`)
**Repository:** `~/NanoBot`

## Verification ID

`ORIN-CAM-720P30-VERIFIED`

## Camera Configuration

The Logitech 720p USB camera is configured for:

- Device: `/dev/video0`
- Pixel format: MJPG
- Resolution: 1280×720
- Requested frame rate: 30 FPS
- JPEG quality: 85
- Startup timeout: 5.0 seconds

## Verification Results

Direct V4L2 capture verified that the camera can sustain approximately 29.8 FPS at 1280×720 MJPG.

NanoBot `FrameGrabber` verification after removal of the forced OpenCV buffer-size setting:

- Frames captured: 300
- Dropped frames: 0
- Measured rate: approximately 29.7 FPS
- Width: 1280
- Height: 720

A subsequent running `nanobot-webrtc.service` status check reported:

- `frame_count`: 744
- `drop_count`: 0
- `fps_measured`: 29.8 FPS
- `width`: 1280
- `height`: 720
- `rpi`: true
- `estop`: false
- `peers`: 0

## Controlled Change

The following forced OpenCV capture-buffer setting was removed from `nodes/orin/camera.py`:

`cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)`

Testing showed that retaining this forced setting reduced sustained OpenCV capture performance. After its removal, NanoBot capture returned to approximately 29.7 FPS with zero dropped frames.

## Frozen Setpoint

The following camera configuration is frozen for the current NanoBot camera baseline:

- Device: `/dev/video0`
- Format: MJPG
- Resolution: 1280×720
- Frame rate: 30 FPS
- Buffer size: No forced `CAP_PROP_BUFFERSIZE` setting

Do not change this camera configuration without a new controlled verification.

## Separate Observation

During camera testing, OpenCV/V4L2 output repeatedly reported messages of the form:

`Corrupt JPEG data: N extraneous bytes before marker`

These messages did not prevent sustained approximately 29.7–29.8 FPS capture or produce dropped frames in the verification tests.

This observation is recorded separately and is **not** treated as a reason to change the verified camera configuration.

## Verification Conclusion

The Orin Nano camera path is verified at 1280×720 MJPG / 30 FPS.

The camera configuration is frozen pending a separately authorized and controlled change.

## Reproducible Post-Restart Runtime Observation — 2026-09-10

After synchronization to commit `6af2bc8` and restart of `nanobot-webrtc.service`, the running NanoBot status endpoint reported a stable measured capture rate of 15.1 FPS.

Two status samples taken 10 seconds apart reported:

- Sample 1: `frame_count` 4583, `fps_measured` 15.1 FPS
- Sample 2: `frame_count` 4734, `fps_measured` 15.1 FPS
- Frame-count increase: 151 frames over 10 seconds
- Calculated interval rate: 15.1 FPS
- `drop_count`: 0
- Resolution: 1280×720
- `rpi`: true
- `estop`: false
- `peers`: 0

The `/snapshot` endpoint also returned HTTP 200 with a valid 1280×720 JPEG after the restart.

This is a reproducible runtime observation and does not change the frozen camera configuration of 1280×720 MJPG / 30 FPS. The discrepancy between this observed 15.1 FPS runtime rate and the earlier approximately 29.7–29.8 FPS verification is recorded for separate controlled investigation.
