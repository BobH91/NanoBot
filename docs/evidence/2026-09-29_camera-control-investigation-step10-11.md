# NanoBot Camera Control Investigation — Steps 10–11

Date: 2026-09-29
Machine: Nanobot
Role: Orin Nano
Motor power: OFF

## STEP 10 — System-Level Camera Control Trace

Read-only searches were performed for explicit camera-control setters in:

- `/etc/systemd/system`
- `/etc/systemd`
- `/etc/udev/rules.d`
- `/lib/udev/rules.d`
- `/etc/cron.d`
- `/etc/cron.daily`
- `/etc/cron.hourly`
- `/etc/cron.weekly`

Search patterns included:

- `v4l2-ctl`
- `auto_exposure`
- `exposure_time_absolute`
- `exposure_dynamic_framerate`
- `backlight_compensation`
- `video0`

Result:

No matching systemd, udev, or cron/timer camera-control configuration was found.

## STEP 11 — Camera Ownership

Host:
`Nanobot`

Camera device:
`/dev/video0`

Device:
`crw-rw----+ 1 root video 81, 0`

Owning process:
PID `936`

Process:
`python`

User:
`bob`

`lsof` confirmed:

`python 936 bob 6u CHR 81,0 /dev/video0`

WebRTC service:
`active`

WebRTC MainPID:
`936`

Conclusion:

`/dev/video0` is currently owned by the NanoBot WebRTC process.

## Runtime Camera State

Resolution:
1280×720

Measured FPS:
23.8

Frame drops:
0

AprilTag worker:
alive

AprilTag result:
available

AprilTag detector runtime:
19.91 ms

Peers:
0

Raspberry Pi connection:
true

E-stop:
false

## LOCKED CAMERA SETPOINTS

These setpoints remain locked and were NOT changed during Steps 10–11:

- Resolution: 1280×720
- Pixel format: MJPG
- Target FPS: 30
- Gain: 64
- Auto exposure: 1
- Exposure time absolute: 110
- Exposure dynamic framerate: 0
- Backlight compensation: 0
- JPEG quality: 85

## CURRENT OBSERVED V4L2 CONTROL STATE

Previously verified during Step 6:

- Auto exposure: 3
- Exposure time absolute: 419
- Exposure dynamic framerate: 1

These differ from the locked setpoints.

## ENGINEERING GATE

Established:

1. Active NanoBot camera source contains no explicit V4L2 control setters.
2. NanoBot systemd service configuration contains no explicit V4L2 control setters.
3. OS systemd/udev/cron searches found no explicit camera-control setters.
4. `/dev/video0` is currently owned by NanoBot WebRTC PID 936.
5. Current camera performance is approximately 23.8 FPS with zero reported frame drops.

Unknown remaining:

What establishes or changes the observed V4L2 control state.

Decision:

Do NOT modify camera controls at this stage.

Do NOT launch a second camera reader while PID 936 owns `/dev/video0`.

Next authorized investigation:

Controlled camera service lifecycle experiment, beginning with a pre-stop baseline capture.

Motor testing remains blocked. Motor power remains OFF.
