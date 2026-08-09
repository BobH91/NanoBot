# NanoBot Incident Report — 2026-08-08

**Prepared for sharing.** UI became unreachable from the iPad; root cause traced to a
side-effect of the 2026-08-05 cleanup session. Fixed and verified working.

---

## TL;DR

The iPad could not find/connect to the robot. Root cause: `nanobot-webrtc.service` was
crash-looping on startup because a required log directory (`nodes/orin/logs/`) no longer
existed — it had been deleted during a prior cleanup session as apparent clutter, without
realizing the running code depends on it existing at startup. Recreating the directory and
restarting the service resolved the issue immediately. **Drive controls and pan/tilt servo
controls have both been confirmed working since the fix.**

---

## What Was Broken

- iPad reported it could not find the robot's server.
- `nanobot-webrtc.service` on the Jetson Orin Nano was crash-looping — restart counter had
  climbed into the tens of thousands of attempts by the time this was caught.
- Exact error from service logs:
  `FileNotFoundError: [Errno 2] No such file or directory: '/home/bob/NanoBot/nodes/orin/logs/webrtc_server.log'`
- Root cause: the service's logging setup writes to a file inside `nodes/orin/logs/`, but that
  directory had been deleted on 2026-08-05 during a repository cleanup pass. At the time, the
  directory appeared empty and unused (it contained only a single empty log file) and was judged
  safe to remove — that judgment didn't account for the running code needing the directory itself
  to exist at every startup, independent of what was in it.

## How It Was Fixed

1. Diagnosed via live service logs (`journalctl`) — found the exact `FileNotFoundError` and its
   source line in `webrtc_server.py`.
2. Recreated the missing directory (`mkdir -p nodes/orin/logs`) and restarted the service.
3. Confirmed the service came up clean — `active (running)`, camera initialized, no crash.
4. Verified via the actual browser UI: drive controls and pan/tilt servo controls both confirmed
   working.
5. **In progress / pending confirmation:** a code change was made so the service automatically
   creates the `logs/` directory itself at startup if it's ever missing again (`os.makedirs(...,
   exist_ok=True)` added just before the logging configuration), so this specific failure mode
   cannot recur even if the directory is deleted again in the future. This change still needs to
   be verified and committed to GitHub.

## Why It Happened

This was a direct consequence of a decision made during the prior cleanup session: a directory
was judged safe to delete based on its *contents* (one empty file) without checking whether any
running code *depended on the directory itself existing*, separate from its contents. That
distinction wasn't accounted for at the time.

## Recommendation

- Once the self-healing code change above is confirmed and committed, consider adding a tracked
  placeholder file (e.g. `.gitkeep`) inside `nodes/orin/logs/` so the directory is preserved by
  git itself going forward, rather than relying solely on the code's runtime `os.makedirs` call.
- Before deleting any directory during future cleanup passes, grep the codebase for references
  to that path first, not just inspect its contents.

## Note — Servo Behavior Discrepancy (unresolved detail)

Earlier the same day, isolated hardware tests sending direct PWM pulses to the pan (Channel 0)
and tilt (Channel 1) servo channels showed no physical movement, which had pointed toward a
possible wiring/power issue separate from this service crash. Servos are now confirmed working
through the actual UI following this fix. It's not yet established with direct evidence whether
the earlier non-response was related to the service's crash-loop state at the time, or was a
separate, now-resolved condition. Flagged for awareness, not currently blocking anything.

---

*Report generated from live diagnostic evidence (service logs, direct verification through the
UI) — no assumptions.*
