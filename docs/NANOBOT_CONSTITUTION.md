# NanoBot Constitution

Version: 1.0

Status: ACTIVE

## Article 1 — Source of Truth

GitHub is the single engineering source of truth for NanoBot.

All permanent engineering artifacts shall exist in the Git repository.

Obsidian is the documentation interface for repository-based documentation.

Syncthing synchronizes working copies between machines but is not authoritative.

Runtime state is temporary and shall not replace committed engineering records.

---

## Article 2 — Engineering Process

All NanoBot engineering work shall follow the documented engineering process.

The process exists to prevent uncontrolled changes, assumptions, and loss of project knowledge.

---

## Article 3 — Setpoint Locks

A Setpoint Lock defines a controlled engineering investigation.

A Setpoint Lock shall define:

- the engineering question
- locked constraints
- verified facts
- allowed actions
- forbidden actions

A locked setpoint is a binding engineering constraint until explicitly closed or replaced.

---

## Article 4 — Evidence Before Change

Inspection precedes modification.

Unknowns shall be reduced through evidence before changes are proposed.

Assumptions shall not replace measurements or verification.

---

## Article 5 — Smallest Safe Change

When a change is required, only the smallest change necessary to test the current hypothesis shall be made.

---

## Article 6 — Milestone Completion

A completed milestone requires:

- verified evidence
- documented result
- Git commit
- synchronization to GitHub

before the next milestone begins.

---

## Article 7 — Recoverability

Another engineer shall be able to reconstruct NanoBot using only:

- the Git repository
- committed documentation
- recorded evidence

without relying on conversation history.

---

## Article 8 — Governance Freeze

Governance exists to support engineering.

New governance documents shall not be created unless an existing process deficiency prevents effective engineering work.

The priority is building NanoBot.

---

## Article 9 — Amendment

This Constitution may only be changed through an explicit Git commit documenting the reason for the amendment.
