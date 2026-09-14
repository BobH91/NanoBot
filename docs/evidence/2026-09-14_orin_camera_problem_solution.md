# Orin Camera Performance Problem and Verified Solution

## Status

**VERIFIED / LOCKED**

Date: 2026-09-14

Machine: Jetson Orin Nano (`Nanobot`)

Verification ID: `ORIN-CAM-720P30-PROBLEM-SOLUTION`

## Problem

The NanoBot Orin camera was configured for 1280×720 MJPG at 30 FPS.

The camera path was verified to sustain approximately 29.7–29.8 FPS with zero dropped frames.

A later runtime observation reported approximately 15.1 FPS after synchronization to commit `6af2bc8` and a restart of `nanobot-webrtc.service`.

The 15.1 FPS observation was preserved as historical evidence. A subsequent controlled service restart from a known-good state did **not** reproduce the 15.1 FPS condition.

Therefore, the 15.1 FPS observation is documented as an observed historical anomaly, not assigned an unproven cause.

## Verified Performance Issue

During controlled camera testing, the following OpenCV setting was found to reduce sustained capture performance:

`cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)`

Removing this forced buffer setting restored NanoBot capture to approximately 29.7 FPS with zero dropped frames.

## Verified Camera Configuration

- Device: `/dev/video0`
- Format: MJPG
- Resolution: 1280×720
- Configured FPS: 30
- JPEG quality: 85
- Startup timeout: 5 seconds
- Forced `CAP_PROP_BUFFERSIZE=1`: **not used**

## Capture Implementation

The NanoBot `FrameGrabber`:

1. Opens `/dev/video0` through V4L2.
2. Requests MJPG, 1280×720, and 30 FPS.
3. Reads frames continuously with `VideoCapture.read()`.
4. Updates the latest frame under a lock.
5. Counts successful frames and failed reads.
6. Calculates measured FPS from successful frames divided by elapsed monotonic time.

No artificial 15 FPS limiter is present in the capture loop.

## Controlled Restart Finding

A controlled restart of:

`nanobot-webrtc.service`

from the verified ~29.8 FPS state produced approximately 29.7–29.8 FPS with zero dropped frames.

**Finding:** restarting the service alone does not reproduce the historical 15.1 FPS condition.

## Final Verified Runtime

After repository synchronization to commit `87e7f6b`, the running Orin reported:

- Resolution: 1280×720
- Measured FPS: 29.7 FPS
- Dropped frames: 0
- Raspberry Pi link: true
- E-stop: false
- Servo pan: 0.0
- Servo tilt: 0.0
- Peers: 0

## Locked Setpoint

The current camera baseline is locked at:

**`/dev/video0` / MJPG / 1280×720 / 30 FPS configured / approximately 29.7–29.8 FPS measured / 0 drops**

No camera code, V4L2 control, or runtime configuration should be changed without an explicitly authorized controlled change.

## Historical Evidence

The original camera verification is recorded in:

`docs/evidence/2026-09-09_orin_camera_1280x720_30fps_verification.md`

The historical 15.1 FPS observation was preserved and committed as:

`87e7f6b docs: record post-restart camera runtime observation`

The exact preserved Orin documentation patch was verified against the working-tree diff before synchronization.

Preserved patch SHA-256:

`8b14f76695201acc42dfb051eeb3b61b3430f9cb196d0162c8ad4bf2ca6a9017`

## Conclusion

The verified camera performance problem was the forced OpenCV capture-buffer setting. Removing that setting restored the verified approximately 29.7–29.8 FPS capture rate with zero dropped frames.

The separate historical 15.1 FPS observation remains documented but has no assigned root cause because the condition was not reproduced by the controlled service-restart test.

The current camera state is verified, synchronized, and locked.
