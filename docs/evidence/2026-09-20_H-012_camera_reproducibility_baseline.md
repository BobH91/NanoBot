# H-012 — Camera Setpoint Reproducibility Baseline

Date: 2026-09-20
Node: Orin
Service: nanobot-webrtc.service
MainPID: 937
Evidence Type: Read-only baseline
Status: VERIFIED

## Locked Setpoint A

- Device: /dev/video0
- Resolution: 1280x720
- Pixel format: MJPG
- Requested FPS: 30
- Gain: 64
- Auto exposure: 1 — Manual Mode
- Exposure time absolute: 110 reported
- Exposure dynamic framerate: 0
- Backlight compensation: 0

## Current Reported V4L2 State

- Gain: 192
- Auto exposure: 3 — Aperture Priority Mode
- Exposure time absolute: 667
- Exposure dynamic framerate: 1
- Backlight compensation: 0

## Current Capture State

- Device: /dev/video0
- Width: 1280
- Height: 720
- Pixel format: MJPG
- Configured frame rate: 30.000 FPS
- Read buffers: 0

## Current NanoBot Runtime State

- Frame count: 67870
- Drop count: 0
- Measured FPS: 15.0
- Width: 1280
- Height: 720
- Peers: 0
- RPi: true
- E-stop: false
- Servo pan: 0.0
- Servo tilt: 0.0

## Camera Ownership

- PID 937 owns /dev/video0
- PID 937 is nanobot-webrtc.service running nodes/orin/webrtc_server.py

## NanoBot Camera Source

- DEVICE = /dev/video0
- CAPTURE_FPS = 30
- JPEG_QUALITY = 85
- STARTUP_TIMEOUT = 5.0
- Source configures FOURCC, width, height, and FPS.
- Source does not enforce gain, auto exposure, exposure time, dynamic framerate, or backlight controls.

## Reproduction Procedure Evidence

The only preserved historical camera-control command located in repository documentation is:

    sudo v4l2-ctl -d /dev/video0 --set-ctrl=exposure_time_absolute=105

Historical documented result: requested 105, reported 110, verified locked exposure value 110.

Complete historical command-level procedures for the other locked controls were not preserved.

## Evidence Classification

Verified:
- Historical Setpoint A state is documented.
- Current V4L2 state is directly observed.
- Current capture format and configured FPS are directly observed.
- Current NanoBot measured runtime is directly observed.
- Current camera ownership is directly observed.
- NanoBot source does not currently enforce the locked V4L2 control values.

Unknown:
- Exact historical commands used to establish gain 64.
- Exact historical command used to establish auto-exposure 1.
- Exact historical command used to establish exposure dynamic framerate 0.
- Exact historical command used to establish backlight compensation 0.
- Exact mechanism responsible for the current controls returning to their present values.

Constraint:
Historical procedures must not be reconstructed from memory or inference.

## H-012 Significance

This baseline establishes the starting state for the controlled reproducibility investigation.

The current state demonstrates a difference between the historically verified/locked camera-control state and the currently reported camera-control state after service startup.

No corrective camera control was issued during collection of this baseline. No service restart or reboot was performed. No source code was changed.
