# NanoBot Evidence Checkpoint

Date:
2026-07-16

## WebRTC Offer 500 Setpoint

Machine:
NVIDIA Jetson Orin Nano (Nanobot)

## Milestone State

Milestone:
5.2 UI/WebRTC Runtime Verification

## Completed Before This Setpoint

### HTTP UI

Verified:

GET /

Result:

200 OK

UI file:

nodes/orin/ui/index.html

Browser:
NanoBot control interface loads successfully.

---

### WebRTC Service

Service:

nanobot-webrtc.service

State:

ACTIVE (running)

---

### Camera

Verified through:

GET /status

Current:

- frame_count increasing
- fps_measured approximately 15 FPS
- resolution 960x544
- drop_count 0

Camera subsystem:
PASS

---

### Raspberry Pi Connection

Status endpoint reports:

rpi:
true

Pi communication:
PASS

---

## Current Failure

Browser loads UI but video does not appear.

Browser network shows:

POST /offer

Result:

HTTP 500 Internal Server Error

---

## Investigation Boundary

The failure is isolated to:

nodes/orin/webrtc_server.py

Function:

offer_handler()

No changes planned yet.

---

## Protected Systems

Do not modify:

- camera.py
- tcp_client.py
- Pi drive system
- UI layout
- systemd service
- HTTP routing

These are currently verified working.

---

## Next Planned Action

Add temporary exception visibility around offer_handler only.

Purpose:

Capture traceback causing HTTP 500.

No functional repair yet.

---

## Status

Diagnostic checkpoint.

System preserved before WebRTC negotiation debugging.
