# NanoBot Issue Register

## Purpose

This document is the persistent repository record for NanoBot development issues, governance findings, process risks, and their resolution status.

The Issue Register exists to provide:

* Traceability of identified issues
* Ownership and status tracking
* Verification records
* Historical reference for development decisions

---

# Issue Status Definitions

| Status      | Meaning                                     |
| ----------- | ------------------------------------------- |
| OPEN        | Identified and awaiting action              |
| IN PROGRESS | Work has started                            |
| BLOCKED     | Cannot proceed until dependency is resolved |
| VERIFIED    | Resolution completed and verified           |
| CLOSED      | Archived after verification                 |

---

# Hardening Issues

## H-001 — Repository State Verification

**Category:** Process
**Status:** VERIFIED

**Description**

Ensure repository state is verified before development actions.

**Resolution**

Repository verification procedures established during milestone work.

**Verification**

Git status, commit verification, and tag validation performed during reconciliation milestones.

---

## H-002 — Multi-Node Synchronization Control

**Category:** Infrastructure
**Status:** VERIFIED

**Description**

Ensure Lenovo, Raspberry Pi, and NVIDIA Orin Nano nodes maintain a controlled repository state.

**Resolution**

Repository reconciliation and baseline verification completed.

**Verification**

All nodes verified against locked baseline commit.

---

## H-003 — Preservation Before Modification

**Category:** Process
**Status:** VERIFIED

**Description**

Preserve existing states before corrective actions.

**Resolution**

Preservation snapshots created before reconciliation operations.

**Verification**

Preservation directories recorded during milestone recovery process.

---

## H-004 — Single Source of Truth Enforcement

**Category:** Governance
**Status:** VERIFIED

**Description**

Repository remains the authoritative source for project state.

**Resolution**

Development workflow established around repository-first verification.

**Verification**

Git baseline and node synchronization checks completed.

---

## H-005 — Documentation Classification

**Category:** Documentation
**Status:** VERIFIED

**Description**

Inventory and classify project documentation.

**Resolution**

Documentation inventory completed during Milestone 4.5 Step 1.

**Verification**

Markdown inventory and classification completed.

---

## H-006 — Development Process Consistency

**Category:** Governance
**Status:** OPEN

**Description**

Establish formal development governance documentation.

**Related Gap**

G-001 Missing Development Governance Document

**Required Action**

Create and approve development governance documentation.

---

## H-007 — Persistent Issue Tracking

**Category:** Governance
**Status:** IN PROGRESS

**Description**

Create repository-local issue tracking documentation.

**Related Gap**

G-002 Missing Issue Register

**Resolution**

Creation of `docs/ISSUE_REGISTER.md`.

**Verification Required**

Confirm file exists in repository and is committed.

---

## H-008 — Machine-Local File Management

**Category:** Infrastructure
**Status:** OPEN

**Description**

Define rules for files that belong to individual machines and should not be synchronized.

**Related Gap**

G-003 Missing Machine-Local File Policy

**Required Action**

Create machine-local file policy documentation.

---

## H-009 — Development History Traceability

**Category:** Documentation
**Status:** VERIFIED

**Description**

Maintain historical records of major development decisions.

**Resolution**

Project history and milestone records maintained.

---

## H-010 — Recovery Procedure Documentation

**Category:** Reliability
**Status:** OPEN

**Description**

Document recovery and rollback procedures.

**Required Action**

Evaluate need for dedicated recovery documentation.

---

## H-011 — Process Compliance Check

**Category:** Governance
**Status:** IN PROGRESS

**Description**

Require a Process Compliance Check before any repository-changing recommendation or action.

**Requirement**

Every repository modification must verify:

* Authorization exists
* Correct milestone step reached
* Scope is defined
* Verification plan exists

**Verification**

Applied beginning with Milestone 4.5 development hardening.

---

# Change History

| Date       | Change                               | Verification                |
| ---------- | ------------------------------------ | --------------------------- |
| 2026-07-13 | Initial issue register authorization | Pending repository creation |

---

# Notes

This register is governed by the NanoBot development process.

Repository changes require:

1. Authorization
2. Process Compliance Check
3. Verification
4. Locking of completed steps
