# NanoBot Evidence Checkpoint
Date: 2026-07-15

## UI Route Pre-Repair Checkpoint

Machine:
NVIDIA Jetson Orin Nano (Nanobot)

Baseline:
v8.3-locked-baseline plus verified WebRTC camera repair

## Current Verified State

nanobot-webrtc.service:
ACTIVE

Port:
8080 LISTENING

Working endpoints:
GET /status
POST /offer

Camera:
Healthy

Raspberry Pi connection:
Verified by status endpoint

## Problem

Browser UI request:

GET /

returns:

404: Not Found

## Root Cause

webrtc_server.py creates aiohttp routes:

- POST /offer
- GET /status

No route exists for:

- GET /
- UI static files

UI file exists:

nodes/orin/ui/index.html

## Planned Repair

Add minimal HTTP route:

GET /

serves:

nodes/orin/ui/index.html

No WebRTC logic changes.
No camera changes.
No motor changes.

## Verification Required After Repair

1. Restart nanobot-webrtc.service.
2. Confirm GET / returns the UI.
3. Load browser interface.
4. Confirm WebRTC connection.
5. Continue to drive command verification.

## Status

Pre-repair checkpoint.

No code changes made.
No Git commit created.
