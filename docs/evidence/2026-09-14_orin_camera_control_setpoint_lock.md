# Orin Camera Control Setpoint Lock

**Status:** VERIFIED / LOCKED
**Date:** 2026-09-14
**Machine:** Orin Nano (`Nanobot`)
**Device:** `/dev/video0`
**Evidence ID:** `ORIN-CAM-CONTROL-SETPOINT-LOCK`

## Purpose

Record the verified runtime camera control setpoints established on Orin after controlled one-at-a-time changes and immediate verification.
## Locked camera control state

| Control | Locked/reported value | Verification |
|---|---:|---|
| `gain` | `64` | `v4l2-ctl --get-ctrl=gain` |
| `auto_exposure` | `1` (Manual Mode) | `v4l2-ctl --get-ctrl=auto_exposure` |
| `exposure_time_absolute` | `110` actual reported value | request `105` produced reported `110` |
| `exposure_dynamic_framerate` | `0` | `v4l2-ctl --get-ctrl=exposure_dynamic_framerate` |
## Exposure control verification

The camera/driver did not report the requested exposure value directly:

- request `110` -> reported `115`
- request `100` -> reported `105`
- request `105` -> reported `110`

Therefore the reproducible command for the locked **reported actual exposure of 110** is:

    sudo v4l2-ctl -d /dev/video0 --set-ctrl=exposure_time_absolute=105

The documented locked value is **actual reported exposure 110**; `105` is the verified driver command value.

The control range observed on Orin:

    min=1 max=10000 step=1 default=166 value=115
## Runtime verification

After applying the controls, Orin `/status` reported:

    {"camera":{"frame_count":51753,"drop_count":0,"fps_measured":29.9,"width":1280,"height":720},"servo":{"pan":0.0,"tilt":0.0},"rpi":false,"estop":false,"peers":0}

Final control verification:

    gain: 64
    auto_exposure: 1 (Manual Mode)
    exposure_time_absolute: 110
    exposure_dynamic_framerate: 0
## Capture configuration boundary

This control lock did not change the existing camera capture configuration:

- Device: `/dev/video0`
- Pixel format: MJPG
- Resolution: 1280x720
- Requested FPS: 30
- JPEG quality: 85
- No forced `cv2.CAP_PROP_BUFFERSIZE=1`

The existing capture configuration remains governed by the prior camera verification evidence.
## Lock rule

These camera control values are now a verified setpoint state.

No camera control, capture-format, resolution, FPS, or buffer configuration changes are to be made without an explicitly authorized controlled change followed by immediate verification and evidence recording.

## Historical anomaly boundary

The historical approximately 15.1 FPS observation remains documented separately. It was not reproduced by controlled restart from a known-good state, and no cause is assigned in this record.

This setpoint lock does not claim to identify the cause of that historical anomaly.

## Verification sequence

Controls were changed one at a time on Orin with immediate read-back verification. Runtime status was then verified at 1280x720, 29.9 FPS, and 0 drops, followed by a final read-back of all four controls.
