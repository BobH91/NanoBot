# Orin Camera Recovery Checkpoint — 2026-09-14

**Status:** VERIFIED RECOVERY CHECKPOINT
**Machine:** Orin Nano (`Nanobot`)
**Repository source of truth:** Lenovo `~/NanoBot`

## Recovery Verification

Following the observed 15 FPS camera condition, the Orin camera was restored through a controlled V4L2 setpoint test.

Verified runtime state after restarting `nanobot-webrtc.service`:

- Device: `/dev/video0`
- Pixel format: MJPG
- Resolution: 1280×720
- Configured frame rate: 30 FPS
- Measured frame rate: 29.9 FPS
- Dropped frames: 0
- Auto exposure: `1` — Manual Mode
- Exposure time: `115`
- Gain: `192` — observed, not locked as a new setpoint
- Exposure dynamic framerate: `1` — observed, not locked as a new setpoint
- NanoBot service: running

## Controlled Recovery Sequence

Before restarting NanoBot, the camera controls were:

- Auto exposure: `1` — Manual Mode
- Exposure time: `110`
- Gain: `192`
- Exposure dynamic framerate: `1`

After starting `nanobot-webrtc.service`, the verified runtime controls were:

- Auto exposure: `1` — Manual Mode
- Exposure time: `115`
- Gain: `192`
- Exposure dynamic framerate: `1`

The resulting NanoBot runtime status reported 29.9 FPS with zero dropped frames at 1280×720.

## Setpoint Lock Boundary

The previously locked capture baseline remains unchanged:

**`/dev/video0` / MJPG / 1280×720 / 30 FPS configured / approximately 29.7–29.8 FPS measured / 0 drops**

This checkpoint does not create a new exact exposure-control lock.

Exposure `110` was restored before service startup, but the camera reported `115` after startup. Therefore `110` is not claimed here as a persistent runtime lock.

Gain `192` and exposure dynamic framerate `1` are recorded as observed runtime values only. They are not promoted to locked setpoints by this checkpoint.

## Historical 15 FPS Observation

The historical approximately 15.1 FPS condition was not reproduced during this controlled recovery.

No root cause is assigned to the historical 15 FPS observation by this checkpoint.

## Conclusion

**Recovery verified.**

The Orin camera returned to approximately 30 FPS measured operation with zero dropped frames after restoration of Manual exposure mode and exposure control.

No camera code or capture configuration was changed during this recovery checkpoint.

This document records the verified recovery state and preserves the distinction between the existing locked capture baseline and observed V4L2 control values.
