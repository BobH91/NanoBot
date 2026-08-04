# Incident Note: Camera Device Drift (`/dev/video1` uncommitted change)

**Date:** 2026-08-03
**Node affected:** Jetson Orin Nano (`nodes/orin/camera.py`)
**Symptom:** NanoBot UI unreachable/unstable from iPad, iPhone, and Lenovo simultaneously.
**Status:** Resolved

---

## Summary

The Orin's `nodes/orin/camera.py` had an uncommitted local edit setting `DEVICE = "/dev/video1"`,
diverging from the committed value on `origin/main` (`/dev/video0`). `/dev/video1` on the attached
UVC camera has no usable capture formats (confirmed live via `v4l2-ctl -d /dev/video1
--list-formats-ext`, which returned zero formats under "Video Capture"). This caused
`nanobot-webrtc.service` to crash on every startup with `RuntimeError: Cannot open camera:
/dev/video1`, and systemd's `Restart=on-failure` (5s `RestartSec`) put it into a crash loop that
had accumulated **662 restarts** by the time it was caught. The loop's brief up-windows explain
why the UI intermittently loaded on some devices but never sustained a working connection.

## Timeline (reconstructed from file timestamps and git history — no assumptions)

| Date | Evidence | Inference |
|---|---|---|
| On/before Jul 12, 19:20 | `camera.py.failed-webrtc-repair` backup already shows `DEVICE = "/dev/video1"` | A `/dev/video1` troubleshooting attempt was already in progress by this point |
| Jul 14, 18:59 | `camera.py.before-video1-repair` backup shows `DEVICE = "/dev/video0"` | File had been reverted to the correct value sometime between Jul 12 and Jul 14, then a **second** `/dev/video1` attempt began (hence the backup name, taken immediately before that second edit) |
| Jul 14 onward | Live `camera.py` left at `DEVICE = "/dev/video1"`, never reverted, never committed | Cleanup step from the second attempt was never finished |
| Jul 14–16 (per prior session's reconciliation) | Reflog shows commits `c70e132` and `b9988e5`, both labeled "previously uncommitted," committing other stray mid-July repair work | This particular file's modification was not swept up in that reconciliation pass — it was a modified tracked file, not a new untracked file, and was evidently missed |
| Aug 3 (this session) | `git status` on Orin shows `camera.py` modified, `git diff origin/main` confirms the `/dev/video0` → `/dev/video1` divergence | Root cause identified |

## Fix Applied

```bash
git restore --source=origin/main -- nodes/orin/camera.py
sudo systemctl restart nanobot-webrtc.service
```

Confirmed via `v4l2-ctl` that `/dev/video0` is the camera's actual capture-capable node
(supports YUYV at multiple resolutions/framerates); `/dev/video1` does not.

## Why It Wasn't Caught Earlier

- The change was a **modification to an already-tracked file**, not a new untracked file. A
  `git status` glance that's scanning past ~25 untracked backup/evidence files from the same
  debugging era can easily miss a single `modified:` line at the top of the list.
- No `git status`/`git diff` check was run against the Orin's working tree between Jul 14 and
  this incident (three weeks) — nothing in the routine session workflow specifically re-verifies
  tracked-file cleanliness on remote nodes between sessions.
- Device-path troubleshooting was done via manual file edits and manual `.before-*`/`.failed-*`
  backups rather than git branches/stashes, so there was no forcing function (like a blocked
  merge or diff review) requiring the change to be explicitly committed or discarded before the
  session ended.

## Recommendations (not yet implemented)

1. Add a `git diff --stat` (not just `git status`) check for tracked-file modifications to the
   health-check script, run against all three nodes, so a lingering uncommitted change like this
   surfaces clearly instead of being buried among untracked files.
2. Consider a session-end habit (or simple script hook) that fails loudly if any node has
   modified-but-uncommitted tracked files when a debugging session closes.
3. Continue the still-open cleanup of ~25 untracked leftover files on the Orin
   (`*.before-*`, `*.failed-*`, `*.save`, stray `docs/evidence/` files from Jul 14–16) — flagged
   in the 2026-08-02 handoff and still outstanding.

## Related

- 2026-08-02 Session Handoff (SETPOINT-001 postmortem, Orin reconciliation)
- `docs/evidence/NanoBot_Drive_Bug_Postmortem_2026-08-01.md`
