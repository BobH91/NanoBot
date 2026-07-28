# NanoBot Engineering Process

Version: 1.0

Status: ACTIVE

## 1. Define the Objective

Every engineering effort begins with a clearly defined question or goal.

---

## 2. Create a Setpoint

A Setpoint defines the current engineering objective.

Example:

Determine why a previously verified subsystem no longer operates.

---

## 3. Create a Setpoint Lock

When investigation requires fixed conditions, create a Setpoint Lock.

The lock must define:

- question
- constraints
- verified facts
- allowed actions
- forbidden actions

The lock must be committed before investigation continues.

---

## 4. Investigation Rules

While a Setpoint Lock is active:

Allowed:

- inspect files
- compare versions
- review logs
- collect measurements
- document evidence

Forbidden:

- changing unrelated systems
- tuning parameters
- modifying code without justification
- expanding scope without updating the lock

---

## 5. Evidence Classification

All findings should be classified as:

Observation:
What was directly seen.

Verified Fact:
Confirmed by evidence.

Unknown:
Not yet determined.

Conclusion:
A decision supported by evidence.

---

## 6. Change Control

Changes require:

1. isolated unknown
2. proposed hypothesis
3. smallest safe change
4. verification
5. documentation
6. commit

---

## 7. Git Discipline

Before work:

- verify branch
- verify synchronization
- verify repository state

After verified milestones:

- commit
- push
- synchronize machines

---

## 8. Runtime Principle

Running systems are temporary.

Git records the intended engineering state.

---

## 9. Process Improvement

The engineering process itself may be improved only when a demonstrated failure exists.

The purpose of process is to enable building NanoBot.

