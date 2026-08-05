# NanoBot Evidence Checkpoint
Date: 2026-07-15

## WebRTC UI Route Investigation

Machine:
NVIDIA Jetson Orin Nano (Nanobot)

Baseline:
v8.3-locked-baseline plus verified WebRTC camera repair

## Verified Runtime State

nanobot-webrtc.service:

ACTIVE

Port:
8080 LISTENING

Status endpoint:
GET /status returns healthy camera status

Offer endpoint:
POST /offer exists

## Investigation

Problem:

Browser UI returns:

GET /

404: Not Found

Evidence:

UI file exists:

nodes/orin/ui/index.html

Search performed in:

nodes/orin/webrtc_server.py

Checked for:

- root route
- static file route
- FileResponse
- add_static
- add_routes

Result:

No route exists to serve the UI.

## Additional Verification

Backend functionality confirmed:

webrtc_server.py contains:

- WebRTC video handling
- DataChannel command handling
- drive command dispatch
- tcp_client integration

Drive command path exists:

Browser
→ WebRTC DataChannel
→ webrtc_server.py
→ tcp_client.py
→ Raspberry Pi TCP port 9000

## Current Diagnosis

The WebRTC backend is operational.

The missing component is HTTP serving of:

nodes/orin/ui/index.html

The browser cannot load the operator interface until a root UI route is added.

## Next Action

Inspect application initialization and route registration.

Implement the smallest possible repair:

GET /

serves:

nodes/orin/ui/index.html

Verification required after repair:

- Browser loads UI
- WebRTC connection establishes
- Drive commands tested
- Raspberry Pi receives commands

## Status

Checkpoint only.

No code changes made.
No Git commit created.
Repository unchanged.
