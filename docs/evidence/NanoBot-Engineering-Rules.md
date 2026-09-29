# NanoBot Engineering Rules

## Permanent Rule

**All NanoBot work is engineering work, not casual conversation.**

Treat every NanoBot instruction, command, test result, setpoint, observation, decision, and troubleshooting step as part of the engineering record.

Do not improvise or relax engineering controls because the interaction is conversational.

## Required Method

1. Evidence first; no guessing.
2. Verify current state before changes.
3. One controlled step at a time.
4. Use explicit setpoints.
5. Lock setpoints before testing.
6. Validate against the expected result.
7. Preserve evidence and hashes.
8. Do not change unrelated systems.
9. GitHub is the source of truth.
10. Do not alter locked calibration without controlled recalibration and re-verification.
11. Do not reopen a closed investigation without regression evidence.
12. Before every command, reconcile it against the complete existing evidence.
13. Prefer the smallest genuinely new diagnostic step.
14. Do not repeat diagnostics that already failed to produce new information.
15. If evidence is inconclusive, label it inconclusive.

## Command Gate

Before giving a command, answer internally:

- What exact unresolved question does this command answer?
- What evidence already exists?
- What new evidence will this command produce?
- What is the expected result?
- What will each possible result mean?
- Is the command safe?
- Does it alter hardware, software, configuration, or setpoints?
- Does it reopen a closed investigation?

If the answer is not clear, do not give the command.

## Physical Test Gate

Before a physical test:

1. Define the exact setpoint.
2. Define logical expected output.
3. Define physical expected output.
4. Confirm safety state.
5. Lock the setpoint.
6. Execute one test.
7. Stop.
8. Record the actual result.
9. Compare actual versus expected.
10. Decide the next step only after recording the result.

## Closed Investigation Gate

A closed investigation remains closed unless new evidence demonstrates a regression.

Required reopening statement:

> Regression evidence: [observation]
>
> Previously closed investigation: [ID]
>
> Reason reopening is justified: [specific evidence]

## Stop Rule

If a diagnostic step produces no new decision-relevant information, stop that branch.

Do not keep generating similar commands simply to continue the conversation.

## Permanent Principle

> **A NanoBot command is justified only when it is safe, evidence-based, and necessary to answer a specific unresolved engineering question.**
