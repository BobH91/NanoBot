# NanoBot Engineering Process Incident — 2026-09-28

**Project:** NanoBot  
**Incident type:** Engineering-process / troubleshooting-control failure  
**Primary systems involved:** Orin Nano, Raspberry Pi 5, motor-control path  
**Status:** Process corrective action required; motor investigation intentionally stopped pending a new evidence-based plan  
**GitHub source of truth:** `BobH91/NanoBot`

---

## 1. Executive Summary

On 2026-09-28, the NanoBot motor-control investigation entered a repeated diagnostic loop despite previously established evidence, locked setpoints, closed investigations, and explicit engineering rules.

The central process failure was not that a single command was technically dangerous. The larger failure was that the troubleshooting process stopped behaving like controlled engineering work. A new diagnostic command was proposed without first reconciling it against the existing evidence and the known-good historical baseline. The assistant then recognized that the command should not have been issued and retracted it, but the command had already been given to the user.

This caused:

- repeated investigation of areas that had already been checked;
- loss of confidence in the diagnostic process;
- unnecessary user effort and time;
- introduction of an unnecessary test step;
- confusion about what was actually known versus what was merely being explored;
- failure to consistently honor the user's standing engineering rules.

The user explicitly established that **all NanoBot work is engineering work, not casual conversation**. That requirement is now a permanent project-control rule.

The motor problem itself was **not resolved by MCT-005 or MCT-006**. The existing evidence establishes that the current physical behavior differs from the previously verified physical behavior, while the current Pi software still matches the known-good left-inversion implementation. The correct next step is therefore not another repeated software/TCP/service diagnostic. A new investigation must begin from the documented regression boundary and identify what changed between the prior physically verified state and the current physical state.

No motor wiring or software changes were made during this failed troubleshooting sequence.

---

## 2. Governing Engineering Principle

### Permanent rule

> **NanoBot work is an engineering activity, not casual conversation. Treat all NanoBot project inputs, commands, test results, evidence, setpoints, decisions, and troubleshooting steps as part of the engineering record and apply established engineering rules continuously. Never classify or handle NanoBot instructions as merely conversational context. Do not improvise or relax engineering guardrails based on conversational flow, and do not assume a conversational exchange permits speculative commands or repeated diagnostics.**

The following engineering rules remain mandatory:

1. Evidence first; no guessing.
2. Verify current state before making changes.
3. One controlled step at a time.
4. Use explicit setpoints.
5. Lock setpoints before testing.
6. Validate the result against the expected result.
7. Preserve evidence and hashes.
8. Do not modify unrelated NanoBot systems.
9. GitHub is the source of truth.
10. Do not change locked calibration without controlled recalibration and re-verification.
11. Do not reopen a fixed or closed investigation without regression evidence.
12. Before proposing a command, reconcile it against all relevant prior evidence and locked state.
13. Prefer the smallest genuinely new diagnostic step.
14. Do not repeat diagnostics merely because the latest conversation turn makes them seem relevant.
15. If evidence is inconclusive, explicitly mark the investigation inconclusive rather than manufacturing certainty.

---

## 3. Why the Process Failed

The assistant's failure came from treating the troubleshooting exchange too much like an interactive conversation and not enough like a controlled engineering state machine.

A conversational model naturally tends to respond to the most recent question or observation by proposing another potentially useful action. That behavior is appropriate for brainstorming or exploratory conversation, but it is inappropriate when a project has explicit locked baselines, completed investigations, evidence records, and controlled-test requirements.

The assistant should have maintained the following hierarchy:

**Existing verified evidence → locked setpoints → closed investigations → current state → gap analysis → only then a new test.**

Instead, the process temporarily became:

**latest observation → propose another diagnostic → reconsider it after issuance.**

That inversion is the core process error.

### What should have prevented the failure

The project already contained enough information to reject the proposed MCT-006 diagnostic before it was given:

- the motor power was explicitly OFF;
- the wheels were physically confirmed off the ground;
- the current Pi source and hashes had already been verified;
- the current motor inversion implementation matched the historically verified correction;
- the TCP/software path had already been investigated;
- MCT-005 had already been closed as inconclusive/observability-limited;
- the historical physical behavior was known;
- the current physical behavior was known to contradict that historical behavior;
- no wiring or software change had occurred.

The correct engineering response was therefore to stop and identify the regression boundary, not invent another generic command-path test.

---

## 4. Established NanoBot Motor Baseline

### Historical physical verification — SETPOINT-001

The 2026-08-01 physical verification established:

- Forward/Up: both wheels forward.
- Reverse/Down: both wheels reverse.
- Left: robot turns left.
- Right: robot turns right.

The historical root cause was identified as a left/right inversion implementation mismatch.

The corrective change was:

- `MOTOR_LEFT_INVERT=False → True`
- `MOTOR_RIGHT_INVERT=False`
- left inversion applied in `drive.py`.

SETPOINT-001 was subsequently CLOSED and physically verified.

This historical evidence is authoritative unless new regression evidence demonstrates a change.

### Current authoritative wiring

MMD10A output terminals, left to right:

`M1B | M1A | M2A | M2B`

LEFT MOTOR:

- Red → M1B
- Yellow → M1A

RIGHT MOTOR:

- Red → M2A
- Yellow → M2B

Terminal polarity alone must not be used to infer a fault because mirror-mounted motors can require opposite physical polarity.

### Current motor safety state

At the end of the incident sequence:

- motor power: **OFF**
- no wiring changes authorized or performed
- no software changes authorized or performed

---

## 5. Current Physical Regression Evidence

During MCT-003, after motor power was deliberately turned ON at the reduced 4% UI setting, the observed behavior was:

| Command | Observed physical behavior |
|---|---|
| Forward | Left wheel reverse, right wheel forward |
| Back | Left wheel backward, right wheel backward |
| Left | Left wheel backward, right wheel backward |
| Right | Left wheel backward, right wheel forward |

Motor power was then turned OFF.

This contradicts the previously verified SETPOINT-001 behavior.

The existence of a physical regression is therefore established.

What is **not** established is the cause of that regression.

Possible cause categories remain open only as investigation categories, not conclusions:

- physical wiring or connector state;
- motor-driver channel state;
- motor-driver configuration/state;
- motor-side polarity or mechanical installation state;
- power-path behavior;
- another physical state change not yet identified.

No category should be selected without evidence.

---

## 6. Software State Already Verified

### Pi source state

Pi host:

`raspberrypi`

Git HEAD:

`b3a08bc`

Working tree:

clean

`drive.py` SHA256:

`dc09a08e5f01a05548cb95990cd0d1bb624ee248784b3decccc3de60fc595368`

`config.py` SHA256:

`dbb98f72fbb241ae20494af48d044b1b7b23d26f6fed43431d61a881432da5e1`

The Pi service was confirmed active and owning the GPIO resources.

### GPIO state

GPIO17 and GPIO27 were reported as active outputs in use by the production service.

A second standalone driver instance could not safely be created because the production service already owned the GPIO resources. The production service was therefore not stopped merely to instantiate a competing driver.

That was the correct safety behavior.

### Current `drive.py` logic

The relevant logic is:

```python
t = _shape(_clamp(throttle))
s = _shape(_clamp(steering))
left = _clamp(t + s * DIFFERENTIAL_MIX)
right = _clamp(t - s * DIFFERENTIAL_MIX)
phys_left = -left if MOTOR_LEFT_INVERT else left
phys_right = -right if MOTOR_RIGHT_INVERT else right
```

The motor writer uses:

- positive value → direction HIGH + duty magnitude;
- negative value → direction LOW + duty magnitude;
- zero → direction LOW + zero duty.

Current runtime constants include:

- `DEADBAND=0.04`
- `EXP_CURVE=2.0`
- `MAX_DUTY=0.95`
- `RAMP_RATE=2.0`
- `RAMP_INTERVAL=0.020`
- `DIFFERENTIAL_MIX=1.0`
- left invert = true
- right invert = false

### Configuration drift already identified

`config.py` contains different values for some control parameters, including:

- `MOTOR_LEFT_INVERT=True`
- `MOTOR_RIGHT_INVERT=False`
- `DEADBAND=0.05`
- `RAMP_RATE=0.10`
- `EXP_CURVE=2.0`

This is documented code/config drift. It was **not changed during this incident** and must not be casually modified as a troubleshooting shortcut.

---

## 7. UI / Command-Path Evidence

The Orin UI uses a DataChannel named `control`.

Commands include:

- Forward: `{cmd:'drive', throttle:speed(), steering:0.0}`
- Back: `{cmd:'drive', throttle:-speed(), steering:0.0}`
- Left: `{cmd:'drive', throttle:speed()*0.3, steering:-speed()}`
- Right: `{cmd:'drive', throttle:speed()*0.3, steering:speed()}`
- release: stop
- e-stop: `{cmd:'estop'}`

Pointer control repeats drive commands every 100 ms while held and stops on release.

At the intentionally reduced 4% setting:

- forward = +0.04 throttle
- back = -0.04 throttle
- left = +0.012 throttle, -0.04 steering
- right = +0.012 throttle, +0.04 steering

The drive shaping deadband means 4% is at the runtime deadband boundary. It is therefore not a useful motion-power setpoint for future diagnostic work.

This fact is useful, but it does **not** explain the observed direction reversal when wheel motion actually occurred.

---

## 8. MCT-005 — Command-Path Investigation

MCT-005 investigated whether the Orin-to-Pi command path was responsible for the physical discrepancy.

### Verified path

`webrtc_server.py`:

- receives `cmd == "drive"`;
- calls `client.drive(throttle=..., steering=...)`.

`tcp_client.py`:

- sends commands over persistent TCP to `192.168.4.153:9000`;
- uses `sendall`;
- drive/stop/estop are transmitted over the connection.

`tcp_server.py`:

- receives newline-delimited JSON;
- parses the command;
- pets the watchdog;
- dispatches the command;
- calls `drv.set(...)`;
- sends a JSON response.

The dispatch implementation logs the received command and calls the production driver.

### Important observability limitation

The Orin client `drive()` path ultimately returned the connection state rather than the Pi command response. Therefore, a returned `True` primarily established that the TCP connection remained connected; it did not independently prove that the Pi driver executed the requested command.

A direct `_send_recv` test did return:

`{'status':'ok'}`

However, later journal observations did not provide matching production `DRIVE` lines for the exact test window. This created an observability ambiguity.

### MCT-005 disposition

MCT-005 was closed as:

**INCONCLUSIVE / OBSERVABILITY-LIMITED**

The following were established:

- no software changes;
- no wiring changes;
- production service active;
- TCP ownership/listening established;
- Orin received a successful status response;
- production driver remained at zero in the observed journal window;
- repeated journal/process investigation was no longer producing new evidence.

The investigation was intentionally deferred rather than endlessly repeated.

That closure should have remained authoritative unless new regression evidence appeared.

---

## 9. MCT-006 — Process Failure

MCT-006 began after the physical regression remained unexplained.

Precondition evidence established:

- hostname `raspberrypi`;
- production Pi service active;
- GPIO17/27 in use;
- Git HEAD `b3a08bc`;
- clean working tree;
- source hashes unchanged;
- wheels physically off the ground;
- motor power OFF.

A proposed diagnostic was then generated using a 20% throttle setpoint.

The assistant later recognized that the diagnostic was not sufficiently justified and that the expected physical interpretation initially given was wrong.

The user nevertheless executed the command.

The command printed:

- throttle `0.200`
- steering `0.000`
- logical left/right `+0.200`
- expected physical left `-0.200` before shaping/ramp
- expected physical right `+0.200` before shaping/ramp
- motor power OFF

No physical motion occurred because motor power remained OFF.

### Why this was a process failure

The problem was not that the command moved the robot. It did not.

The problem was that the command should never have been issued in that form because:

1. it did not answer a clearly identified unresolved question;
2. it was not derived from a new evidence gap;
3. it was not reconciled against the historical physical baseline;
4. it did not advance the investigation beyond MCT-005;
5. the expected physical interpretation was initially incorrect;
6. it introduced another loop into an investigation already recognized as repetitive.

This is the exact behavior the project's engineering-control rules are intended to prevent.

---

## 10. Why the User Experienced This as “Going Around in Circles”

The repetition was real.

The project had already established:

- the historical correct motor behavior;
- the historical software correction;
- the current software state;
- the current hashes;
- the active production service;
- the GPIO ownership;
- the TCP architecture;
- the command path;
- the limitations of the existing observability;
- the physical regression;
- the absence of authorized software or wiring changes.

Once those facts were established, repeating generic TCP/service/source checks did not materially narrow the cause.

The investigation needed to transition from **software-path verification** to **regression-boundary identification**.

That transition did not happen quickly enough.

---

## 11. Root Process Cause

### Primary cause

**Failure to maintain engineering-state continuity across conversational turns.**

The assistant did not consistently treat previously verified evidence and closed investigations as authoritative constraints on subsequent actions.

### Contributing causes

1. **Conversation-driven troubleshooting** — responding to the latest observation instead of the complete engineering state.
2. **Insufficient evidence-gating** — a proposed command was not required to answer a specific unresolved question before being issued.
3. **Failure to distinguish “possible” from “necessary.”**
4. **Failure to preserve closed-investigation boundaries.**
5. **Incorrect command expectation** in MCT-006.
6. **Over-investigation of an observability-limited path.**
7. **No mandatory pre-command reconciliation checklist.**

---

## 12. What Was Done Correctly

Even during the process failure, several safety controls worked:

- motor power was kept OFF during software investigation;
- wheels were physically confirmed off the ground before later physical work;
- no unverified wiring change was made;
- no software source was modified during the incident;
- no production GPIO-owning service was stopped merely to run a competing driver instance;
- existing hashes were preserved;
- the known-good motor inversion was not casually changed;
- the WebRTC investigation was not reopened;
- AprilTag was not modified;
- camera calibration was not changed;
- the motor investigation was eventually stopped rather than continuing indefinitely.

These controls should remain in place.

---

## 13. Corrective Engineering Controls

### Control 1 — Evidence Gate

Before every proposed command, explicitly identify:

- unresolved question;
- existing evidence relevant to that question;
- what new evidence the command will produce;
- exact expected result;
- what decision will follow each possible result.

If the command does not change the information state, do not issue it.

### Control 2 — Closed-Investigation Gate

A closed investigation may only be reopened when there is explicit regression evidence.

Required format:

> **Regression evidence:** [new observation]  
> **Previously closed investigation affected:** [ID]  
> **Why the new observation invalidates or reopens the boundary:** [specific reason]

### Control 3 — Setpoint Gate

Before a physical test:

1. define setpoint;
2. define expected logical output;
3. define expected physical output;
4. verify safety state;
5. lock the setpoint;
6. execute one test;
7. stop;
8. record result.

### Control 4 — Command Validation Gate

The assistant must internally validate a proposed command before presenting it to the user.

Minimum checks:

- Is it necessary?
- Is it new?
- Is it safe?
- Is the expected result correct?
- Does it conflict with a locked baseline?
- Does it reopen a closed investigation?
- Does it require a physical action?
- Does it modify anything?

If any answer is unresolved, do not issue the command.

### Control 5 — One-Step Rule

One controlled step means one step that answers one specific question.

Do not bundle exploratory commands merely because they are convenient.

### Control 6 — Stop Condition

If a test produces no new information, stop the diagnostic branch rather than adding another similar test.

---

## 14. Required Future Investigation Method

The motor investigation should resume only from the known regression boundary.

### Known-good state

SETPOINT-001 physical behavior was verified on 2026-08-01.

### Current bad state

MCT-003 produced behavior inconsistent with SETPOINT-001.

### Known unchanged state

Current Pi software and hashes match the established implementation.

### Therefore the next investigation objective

Identify **what changed between the last known-good physical state and the current physical state**.

The investigation should be organized around a controlled comparison of physical state, not another generic command-path loop.

No candidate cause should be declared until evidence identifies it.

---

## 15. Current Investigation Boundary

At incident close:

| Item | State |
|---|---|
| Motor power | OFF |
| Motor wiring | Not changed during incident |
| Pi code | Not changed during incident |
| Pi Git HEAD | `b3a08bc` |
| Pi working tree | Clean |
| `drive.py` hash | `dc09a08e5f01a05548cb95990cd0d1bb624ee248784b3decccc3de60fc595368` |
| `config.py` hash | `dbb98f72fbb241ae20494af48d044b1b7b23d26f6fed43431d61a881432da5e1` |
| Historical motor baseline | SETPOINT-001 verified |
| Current physical behavior | Contradicts SETPOINT-001 |
| MCT-005 | Closed inconclusive / observability-limited |
| MCT-006 | Stopped due process error |
| WebRTC investigation | Closed; do not reopen without regression evidence |
| AprilTag | Not involved in this motor investigation |
| Camera | Separate known persistence issue; not to be mixed into motor investigation |

---

## 16. Separate Camera Finding — Do Not Mix Into Motor Investigation

During the same general period, the Orin camera showed a separate known persistence problem:

- approximately 16.8 FPS observed;
- 1280×720;
- 0 drops;
- V4L2 controls after reboot included gain 192, auto exposure 3 / Aperture Priority, exposure 598 inactive, dynamic framerate 1, backlight 0;
- `camera.py` sets device, FourCC, resolution, and FPS but does not enforce the V4L2 controls;
- existing persistence-gap evidence already documents this issue.

This camera issue must remain separate from the motor investigation.

It is not evidence that the motor regression is caused by the camera.

Likewise, the camera issue must not be used to reopen the completed AprilTag or WebRTC investigations without specific regression evidence.

---

## 17. Accountability Record

The assistant acknowledges the following engineering-process failures:

1. It failed to consistently honor the project's explicit engineering rules.
2. It treated the troubleshooting flow too much like conversational exploration.
3. It proposed a command before establishing that the command answered a genuinely new engineering question.
4. It initially supplied an incorrect expected interpretation for the command.
5. It corrected itself only after the command had already been presented.
6. It repeated diagnostic categories that had already been substantially investigated.
7. It failed to preserve the user's time and confidence as engineering resources.

The user was correct to identify the pattern as similar to an earlier troubleshooting loop.

The corrective action is procedural, not merely verbal: the evidence-gating controls in this document are to be used in future NanoBot work.

---

## 18. Permanent Engineering Rule for NanoBot

> **Do not give the user a NanoBot command unless the command has first been validated against the current engineering record, locked setpoints, known-good baselines, safety state, and closed-investigation boundaries.**

A command is not justified merely because it might produce information.

It must produce **new, decision-relevant information**.

---

## 19. Final Disposition

**Incident disposition:** Process failure documented.  
**Motor regression disposition:** Unresolved; investigation intentionally stopped at the established regression boundary.  
**Software changes:** None.  
**Wiring changes:** None.  
**Motor power at close:** OFF.  
**Further work:** Requires a new controlled investigation plan based on the known-good-to-current physical regression boundary.

This report is the canonical record of the 2026-09-28 engineering-process incident.

---

## 20. Related Evidence

Historical motor evidence:

- `docs/evidence/2026-08-01_setpoint-001_closure_physical_verification.md`
- `docs/evidence/NanoBot_Drive_Bug_Postmortem_2026-08-01.md`

Motor investigation:

- MCT-001 through MCT-006 engineering records from the 2026-09-28 investigation

Camera / ATV-004:

- `docs/evidence/ATV-004-final-state-2026-09-24_133050.txt`
- SHA256: `a671be3a2432834254f25b39d7c588057cb717885b5cb8e5f0d8e354f84de287`
- `docs/evidence/2026-09-20_camera_setpoint_persistence_gap.md`

WebRTC:

- Git commit `1652a12` — `Fix WebRTC browser peer reconnect lifecycle`

AprilTag:

- ATV-003 production AprilTag engineering record
- ATV-004 camera dynamic frame-rate record

---

## 21. Document Control

**Document:** NanoBot Engineering Process Incident — 2026-09-28  
**Purpose:** Permanent engineering-process record and corrective-control reference  
**Authority:** NanoBot engineering record  
**Source of truth:** GitHub repository  
**Obsidian role:** Engineering knowledge / operational reference  
**Status:** Final for this incident; future corrections require explicit revision history

---

## 22. Preventing Recurrence: From Rules to Enforced Gates

The incident demonstrated that written rules and remembered instructions are not sufficient by themselves. The failure occurred because the established rules existed, but they were not reliably enforced at the point where the next diagnostic command was generated.

The corrective principle is therefore:

> **NanoBot engineering rules must function as gates, not reminders.**

### 22.1 Persistent Engineering Control

NanoBot engineering controls must exist as authoritative project artifacts, not only as conversational or remembered instructions.

- GitHub remains the engineering source of truth.
- Obsidian mirrors the engineering record and operational knowledge.
- The engineering rules document is a persistent control reference.
- A new conversational turn does not reset the established engineering state.

### 22.2 Mandatory Pre-Command Gate

Before issuing any NanoBot command, the assistant must establish:

1. **Purpose** — What exact unknown does this command resolve?
2. **Prior evidence** — Has that question already been answered?
3. **Regression check** — Am I reopening something previously closed?
4. **Safety** — Can this affect hardware, software, calibration, or locked setpoints?
5. **Expected result** — What result is expected?
6. **Decision consequence** — What will change depending on the result?

If these conditions cannot be established, the command must not be issued.

### 22.3 Closed Investigations Become Constraints

Previously resolved investigations are treated as closed engineering states unless new regression evidence exists.

Examples:

- WebRTC investigation: closed; do not reopen without regression evidence.
- Camera calibration: locked; do not alter without controlled recalibration and re-verification.
- AprilTag production integration: established baseline; do not modify during unrelated motor investigation.
- Motor SETPOINT-001: historically physically verified; treat that physical evidence as authoritative baseline evidence.

### 22.4 No Diagnostic Loops

When a diagnostic produces no new actionable evidence, the investigation must not continue by generating another variation of substantially the same test.

The required state is:

**NO NEW EVIDENCE → STOP**

The next diagnostic must address a genuinely different unresolved question.

### 22.5 Regression Investigation Pattern

For a regression, the investigation should follow this structure:

```text
KNOWN-GOOD
     ↓
CURRENT-BAD
     ↓
WHAT CHANGED?
     ↓
SMALLEST TEST THAT DISTINGUISHES THE POSSIBILITIES
```

It must not devolve into an open-ended sequence of unrelated checks.

### 22.6 Command Justification

Every proposed command must have an explicit engineering justification:

> **Run this because it distinguishes A from B.**

A command must not be issued merely because it might reveal something or because it is the next conversational troubleshooting idea.

### 22.7 Evidence-Based Stop Condition

If the evidence is insufficient to determine the next action, the assistant must state exactly what remains unknown and identify the single next evidence requirement. It must not improvise another troubleshooting branch.

### 22.8 Engineering Record Overrides Conversational Momentum

NanoBot work is engineering work. The latest conversational message does not override:

- locked setpoints;
- prior PASS results;
- closed investigations;
- safety constraints;
- previous failed diagnostic branches;
- known-good physical evidence; or
- established engineering decisions.

The assistant must carry the engineering state forward continuously.

### 22.9 Required Action Sequence

The governing sequence for NanoBot work is:

**Evidence → State → Purpose → Safety → Command → Result → Decision → Record**

If this sequence cannot be maintained, the process stops rather than improvising.

### 22.10 Accountability Principle

The user should not have to catch the assistant violating these controls. Maintaining the engineering process is the assistant's responsibility when acting as the NanoBot engineering assistant.

The purpose of these controls is not to create additional paperwork. Their purpose is to prevent repeated diagnostics, unsafe or unnecessary commands, loss of established evidence, and conversational drift from the engineering state.
