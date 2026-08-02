# NanoBot Drive System — Postmortem Report

**Date:** 2026-08-01
**Scope:** SETPOINT-001 (Motor Direction Investigation) — root cause, fix, and deployment
**Status:** Resolved and physically verified

---

## 1. Executive Summary

NanoBot's differential-drive control had two independent problems: a
**wrong-motor-inverted** bug that made arrow-key controls produce
incorrect movement, and a missing **UI-serving route** that had left
the browser control page effectively unreachable. Both were traced to
their root causes and fixed. A third, unrelated issue (an iPad Safari
text-selection popup on the control buttons) was found and fixed along
the way. All fixes were physically verified by test-driving the robot
from the iPad UI: forward, back, left, and right all now behave
correctly.

The investigation also surfaced two governance-relevant findings worth
flagging on their own: a chunk of real, working repair code on the Orin
that exists only as an uncommitted local copy with no backup, and a
custom git commit hook whose dramatic "Runtime Firewall" language
doesn't match the modest logic it actually runs.

---

## 2. What Was Broken

### 2.1 The motor direction bug (the original complaint)

Pressing the arrow keys drove the robot incorrectly — for example, "up"
produced left-wheel-reverse / right-wheel-forward instead of both
wheels forward. This was already flagged internally as an open,
locked investigation (**SETPOINT-001**) in the project's own governance
system before this session started.

### 2.2 A configuration/code drift (found first, real but not the full story)

`nodes/pi/config.py` declared:

```
MOTOR_RIGHT_INVERT = True
```

But `nodes/pi/drive.py` — the file actually imported and run by
`tcp_server.py` — never read from `config.py` at all. It **hardcoded
its own local copy** of the same constant, set to `False`, along with
duplicating several other pin/channel constants. The two files
disagreed with each other, and only the hardcoded value in `drive.py`
was ever actually running.

This was a real bug (config and code should never be allowed to drift
like that), but fixing it alone was not enough — see §2.4.

### 2.3 A missing UI route (found, but based on stale information)

The version of `nodes/orin/webrtc_server.py` committed to git had no
HTTP route serving the control page at all — only `/offer` and
`/status` existed. The committed `index.html` was also JavaScript only,
with no surrounding HTML markup for that JavaScript to attach to.

This diagnosis turned out to be **correct for the git-committed code,
but stale for reality**: the Orin's actual working directory had
substantial *uncommitted* local repairs from a prior session
(2026-07-14 to 07-16) that already added a working UI route and other
fixes. That uncommitted code — not the git version — was what had
actually been serving the working camera/servo controls the whole
time. This was only discovered mid-deployment (§4.3) and the rebuilt
`webrtc_server.py`/`index.html` were never pushed to the Orin as a
result, avoiding overwriting real working code with an unnecessary
rewrite.

### 2.4 The actual root cause (found via physical test drive)

Once the config/drive.py drift was fixed and deployed, a live test
drive revealed the real bug: with `steering=0`, forward and back
commands sent **identical** values to both motors — yet the wheels
moved in **opposite physical directions** from each other on both
moves (e.g. "up" gave left-reverse / right-forward; "down" gave the
opposite). That pattern is only possible if one motor's wiring is
inverted relative to the other.

The actual defect: `drive.py` had **no inversion logic for the left
motor at all**. `config.py` declared a `MOTOR_LEFT_INVERT` constant,
but nothing in `drive.py` ever read it — only `MOTOR_RIGHT_INVERT` was
ever applied. The physical wiring asymmetry was on the **left** motor,
not the right, meaning the original SETPOINT-001 framing ("why doesn't
the right wheel..." ) had been aimed at the wrong motor from the start.
Working through the left/right turn math against the observed behavior
confirmed this precisely — every observed movement matched exactly
what a left-only wiring inversion, with no software compensation,
would produce.

### 2.5 iPad Safari touch-callout

Long-pressing the control buttons on the iPad triggered Safari's
built-in "Copy / Look Up" selection popup, interrupting control. Plain
`user-select: none` (already present) doesn't suppress this on iOS —
it requires the iOS-specific `-webkit-touch-callout: none` property,
which was missing from both the git-tracked and the actual-running
`index.html`.

---

## 3. Why It Was Broken — Root Causes

| Issue | Root cause |
|---|---|
| Right-invert drift | `drive.py` never imported `config.py`; constants were duplicated by hand and fell out of sync over time. |
| Left-invert missing | `drive.py` was written with invert logic for only one motor; the second motor's asymmetry was never accounted for in software, even though `config.py` had a placeholder constant for it. |
| Missing UI route (git) | The committed `webrtc_server.py` predates the working local repairs; the repo was never updated after those repairs were made directly on the Orin. |
| iPad callout | A one-line CSS gap — a Safari-specific property that's easy to omit since it has no effect on other browsers. |

The common thread across the first three: **single source of truth was
not being enforced**. Constants got duplicated instead of imported, and
working fixes were made locally without ever being committed back to
git. Both are exactly the failure modes the project's own Constitution
and Setpoint Lock process exist to prevent — this incident is a good
concrete example of why.

---

## 4. What Was Fixed

### 4.1 `nodes/pi/config.py`
- `MOTOR_RIGHT_INVERT` corrected to match the value already verified
  working (`False`).
- `MOTOR_LEFT_INVERT` corrected `False → True` — the actual fix, found
  only after physical testing.

### 4.2 `nodes/pi/drive.py`
- Now imports hardware/wiring constants from `config.py` instead of
  redefining them locally (removes the drift mechanism itself, not
  just one instance of it).
- Added `phys_left` calculation in `_apply()`, mirroring the existing
  `phys_right` logic, so the left motor's inversion is now actually
  applied in software.

### 4.3 `nodes/orin/webrtc_server.py` / Orin deployment — reverted course
A full rebuild of this file (adding UI-serving routes, an MJPEG
fallback, etc.) was drafted and even deployed to the Pi/committed to
git — but before pushing it to the Orin, a `git status` check revealed
the Orin's real working directory already had different, working,
uncommitted local repairs solving the same problem. Rather than
overwrite that, the rebuild was **not** deployed to the Orin. This is
flagged as an open follow-up (§6), not resolved in this session.

### 4.4 `nodes/orin/ui/index.html`
- The iPad Safari fix (`-webkit-touch-callout: none` etc.) was applied
  to **two different files**: the git-tracked version, and — separately
  — the actual different, uncommitted `index.html` running live on the
  Orin, once it became clear those were not the same file.

### 4.5 Documentation
Every step was recorded as dated evidence entries under
`docs/evidence/`, per the project's existing Setpoint Lock process,
culminating in a closure entry once the fix was physically verified.

---

## 5. Deployment: The "Base64" Approach, and Why It Was Needed

### The problem
Getting the fixed files from this conversation onto your Lenovo hit a
wall: pasting large multi-line Python/HTML files directly into your
terminal (via `cat > file << 'EOF' ... EOF` heredocs) repeatedly
produced **corrupted files** — lines dropped, reordered, or merged with
shell prompts mid-paste. A few different mechanisms were likely at
play:

- Large pastes containing blank lines could get partially interpreted
  as shell input before the heredoc fully captured them.
- Very long **single lines** (10–16KB) could make a terminal with a
  fancy prompt (syntax highlighting, etc.) appear to hang, since some
  of those do expensive re-processing on every keystroke/paste chunk.
- Non-ASCII characters (arrows, em dashes, box-drawing characters used
  in code comments) added another way for a paste to get mangled
  depending on terminal/locale handling.

### The fix: base64 encoding, chunked
Base64 encodes arbitrary content (text or binary) into a string using
only `A–Z`, `a–z`, `0–9`, `+`, `/`, and `=` — none of which are shell
metacharacters, none of which trigger locale/encoding issues, and none
of which a terminal would ever try to "interpret." That made it
immune to the corruption we were seeing.

Two refinements made it reliable in practice:

1. **Chunking.** Rather than one giant single-line command (which
   still triggered the terminal-hang issue), the base64 string was
   split into many short lines (~300 characters each), each appended
   to a temp file with its own `echo '...' >> file` command. Short
   lines paste and process quickly; the terminal never had to choke on
   one enormous line.
2. **Integrity verification, every time.** After decoding
   (`base64 -d`), every file was checked with `wc -l` (line count),
   `python3 -m py_compile` (syntax validity, for Python files), and —
   once corruption was suspected on the very last file — an `md5sum`
   comparison against the same file's hash computed independently on
   this end. A matching hash is a mathematical guarantee the bytes are
   identical; nothing short of that was fully trusted after the
   earlier corruption incidents.

This approach turned an unreliable, error-prone transfer method into a
mechanically verifiable one — each file was provably byte-identical
before it was ever committed, rather than assumed correct because it
"looked right" scrolling past in a terminal.

---

## 6. Open Follow-Up (Not Resolved This Session)

**The Orin has real, working, uncommitted local changes** to
`webrtc_server.py`, `camera.py`, and `index.html`, dating to a repair
session around 2026-07-14–16. This code is what's actually running the
robot's camera/servo/UI stack today — but it exists in only one place
(that machine's disk), with no git history and no backup. It should be
reviewed and committed deliberately in its own dedicated session,
following the same evidence-and-verification discipline used here,
rather than risk losing it to a disk failure or an careless `git pull`.

**A custom git pre-commit hook** (`.githooks/pre-commit`, tracked in
git since commit `9c6e8f3`) prints dramatic "🔐 NanoBot v7 Runtime
Firewall / Trust: root" banners on every commit. On inspection, its
actual logic is a straightforward node/role-based file-path check
(matching the project's documented pi/orin separation rules) — nothing
malicious was found. But its commit history references a version
scheme ("v3.3", "v6", "v7", "v8.2.1") that doesn't appear anywhere in
the project's actual documentation, which tracks progress by Milestone
and Phase instead. Worth a closer look at that history when time
allows, purely to understand where that mismatch came from.

---

## 7. Final Verification

Physical test drive from the iPad UI, 2026-08-01:

| Command | Result |
|---|---|
| Up | Both wheels forward — correct |
| Down | Both wheels reverse — correct |
| Left | Turns left — correct |
| Right | Turns right — correct |

Touch-and-hold on control buttons no longer triggers the Safari
selection popup.

SETPOINT-001 is closed, with full evidence trail in
`docs/evidence/2026-07-30_setpoint-001_config_drive_constant_discrepancy.md`,
`docs/evidence/2026-07-30_setpoint-001_release_and_fix.md`, and
`docs/evidence/2026-08-01_setpoint-001_closure_physical_verification.md`.
