# NanoBot Camera Control Enforcement — Runtime Verification

Date: 2026-09-29
Machine: Orin Nano (`Nanobot`)
Test: Step 20C — Runtime Enforcement Test
Status: PASS

## Purpose

Verify that NanoBot automatically restores the locked camera control state
when the camera starts in a drifted device state.

## Pre-start state

With `nanobot-webrtc.service` stopped and `/dev/video0` unowned:

- gain: 192
- auto_exposure: 3 (Aperture Priority Mode)
- exposure_time_absolute: 115
- exposure_dynamic_framerate: 1
- backlight_compensation: 0

The drifted state was already present after the attempted manual injection;
the failed manual write was not treated as evidence of successful injection.

## Runtime enforcement result

NanoBot was started normally.

Service:
- active

Camera owner:
- PID 13145

Post-start controls:

- gain: 64
- auto_exposure: 1 (Manual Mode)
- exposure_time_absolute: 120
- exposure_dynamic_framerate: 0
- backlight_compensation: 0

## Camera performance

- resolution: 1280x720
- measured FPS: 29.8
- frame drops: 0

## AprilTag / system state

- AprilTag worker alive: true
- result available: true
- detected: false
- Raspberry Pi connection: true
- e-stop: false
- servo pan: 0.0
- servo tilt: 0.0
- WebRTC peers: 0

## Engineering conclusion

PASS.

NanoBot successfully enforced the locked camera controls at startup and
restored the drifted gain, auto-exposure mode, and dynamic-framerate controls.
Camera operation remained approximately 30 FPS with zero drops.

The camera driver reported an effective exposure value of 120 when NanoBot
requested 115. This is recorded as observed driver behavior and is not treated
as a new failure or reason to change the verified implementation.

No additional camera-control investigation is warranted from this test.

Motor power remained OFF throughout the test.

## Source

Camera implementation hash at Step 20C:

`952fe41ccf772f9086dfd56483548d9b6faf1fb7c722f774a97581c19d9f72cd`

## Safety

Motor power remained OFF.
