# NanoBot Milestone 6.x — Orin → Pi Drive Path Verification

Date:
2026-07-24

## Objective

Verify the motor control path outside the browser/UI layer.

Path tested:

Orin Nano
    ↓ TCP JSON command
Raspberry Pi NanoBot service
    ↓
Motor driver
    ↓
MMD10A motor controller
    ↓
Wheels

## Ownership Resolution

Previous issue:

Two motor services existed:

- /home/pi/nanobot/nanobot-drive.service
- /home/pi/NanoBot/nanobot-pi.service

This created duplicate GPIO ownership.

Resolution:

Final owner:
- Repository: /home/pi/NanoBot
- Service: nanobot-pi.service

Legacy service:
- nanobot-drive.service stopped

## Verification

Passed:

- GPIO ownership conflict identified
- Legacy motor service stopped
- NanoBot motor service started
- GPIO17/GPIO27 successfully claimed by NanoBot service
- Pi TCP server listening on port 9000
- Orin TCP client configured for Raspberry Pi
- Orin → Pi ping verified
- Drive command verified
- Forward movement verified
- Stop command verified

## Result

Milestone 6.x drive communication path is operational.

Next milestone may extend control outward to UI/browser.

No WebRTC or browser control changes included.
