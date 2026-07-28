# NanoBot Setpoint Locks

This document records active NanoBot investigation constraints.

A locked setpoint is an engineering constraint.

It is not a conversation note or temporary suggestion.

While ACTIVE:
- Investigation remains inside the defined boundary.
- Changes outside the boundary require explicit release or modification of the setpoint.
- Evidence must be collected before corrective action is taken.

Git is the source of truth for locked setpoints.

---

## SETPOINT-001 — Motor Direction Investigation

Status: ACTIVE

Date: 2026-07-27

## Investigation Question

Why does the running NanoBot command path not produce the expected right-wheel physical direction?

---

## Locked Constraints

Until SETPOINT-001 is released:

DO NOT:

- Modify `nodes/pi/drive.py` motor logic.
- Change `MOTOR_RIGHT_INVERT`.
- Swap motor wiring.
- Change motor connections.
- Change trims.
- Change ramp values.
- Change deadband.
- Change PWM frequency.
- Introduce tuning changes.
- Add corrective compensation.

---

## Verified Facts

- `nanobot-pi.service` is the active Raspberry Pi motor service.
- Git repository is the source of truth.
- Current investigation concerns the command-to-hardware path only.
- Previous wheel movement was observed during earlier testing.
- The previous working behavior is a known reference state.
- The working state must be recovered from Git history and evidence, not memory.

---

## Allowed Actions

Only the following actions are allowed:

- Inspect source files.
- Inspect Git history.
- Inspect service state.
- Inspect runtime logs.
- Compare working and non-working states.
- Collect evidence.
- Document findings.

---

## Forbidden Actions

While SETPOINT-001 is ACTIVE:

- No fix attempts.
- No code modifications.
- No tuning changes.
- No hardware changes.
- No architecture changes.

Any proposed change must first explain:

1. What unknown it reduces.
2. Why it stays inside this setpoint boundary.
3. What evidence supports the change.

---

## Release Criteria

SETPOINT-001 can only be released when:

- The cause of the right-wheel direction discrepancy is identified.
- Evidence is recorded.
- A controlled change is proposed.
- The change is reviewed before implementation.
