# NanoBot Progress Report — 2026-08-06

**Prepared for sharing.** Status of infrastructure verification, plus an in-progress hardware
investigation into non-responsive pan/tilt servos.

---

## TL;DR

Project infrastructure (GitHub, Syncthing, Obsidian vault) was fully verified across all three
NanoBot machines and confirmed clean, in sync, and stable. Separately, a **new issue was found**:
the camera's pan/tilt servos are not responding to commands, despite video and drive-motor
controls working correctly. Diagnosis is in progress; current evidence points to a hardware
connection or power issue rather than a software bug. **Not yet resolved.**

---

## What's Good — Infrastructure Verified Stable

| Area | Status |
|---|---|
| GitHub | All three machines (Lenovo, Pi, Orin) confirmed identical, at commit `9596865`, no modified or untracked files |
| Syncthing | Active and responding on all three machines |
| Obsidian vault | `.obsidian/` config folder present and intact on the Lenovo (previously recovered on 2026-08-01, holding steady since) |

No drift, no sync issues, nothing broken on the project infrastructure side.

---

## What's Broken — Pan/Tilt Servos Not Responding

**Symptom:** Video feed and drive (motor) controls work correctly in the browser UI. Pan/tilt
camera servo controls do not move the camera at all.

**Diagnosis so far:**

1. Confirmed via live service logs that pan/tilt commands from the browser UI *are* reaching the
   server correctly (`nudge_pan` commands logged with correct values).
2. Confirmed the server's command dispatch code correctly routes these commands into the servo
   control module (`servo.py`) — no bug found in the dispatch logic.
3. Confirmed `servo.py` has never been modified since its very first commit to GitHub — and
   project history explicitly recorded pan/tilt servos as "confirmed working live" as recently as
   2026-08-02. Since the code hasn't changed since then, this rules out a code regression.
4. Ran the module's built-in hardware smoke test directly (bypassing the browser/UI entirely) —
   it completed without errors, but a servo that is **not** the camera's pan/tilt servo was
   observed moving.
5. Ran isolated, direct hardware tests sending PWM pulses straight to Channel 0 (pan) and
   Channel 1 (tilt) on the servo controller board — both completed without any Python errors,
   but **no physical movement was observed on either channel**.

**Current working hypothesis:** This looks like a physical hardware issue — most likely a loose
or disconnected servo cable, or a missing/disconnected servo power supply to the controller
board — rather than a software problem. The controller chip is clearly receiving and accepting
commands without error (proven by the lack of any exception across every test), which is
consistent with the servos simply not being powered or connected, not with a code fault.

## How It Will Be Fixed (next steps, not yet done)

1. Physically inspect the camera servo cable connections on the PCA9685 controller board —
   confirm they're firmly seated in the correct channel headers.
2. Confirm the servo controller board has an active, separate power supply for the servos
   themselves (distinct from the logic/I2C connection to the Orin).
3. Re-run the isolated channel tests after any physical fix to confirm resolution.
4. Verify end-to-end through the actual browser UI once hardware-level movement is confirmed.

---

*Report generated from live diagnostic evidence (service logs, direct hardware tests, git
history) — no assumptions. The servo issue remains open as of this report.*
