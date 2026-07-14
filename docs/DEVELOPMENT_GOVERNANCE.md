# NanoBot Development Governance

## 1. Purpose

This document defines the development governance rules for the NanoBot robotics system.

The purpose of this document is to maintain:

- repository integrity,
- repeatable development practices,
- traceable changes,
- controlled multi-node synchronization,
- reliable milestone management.

---

## 2. Repository Authority Model

The NanoBot Git repository is the single source of truth.

Repository-controlled content represents the authoritative project state.

Device copies are working environments and must synchronize with the repository baseline.

Devices may contain temporary, generated, or machine-specific files that are not considered authoritative.

---

## 3. Development Workflow Rules

All development changes must follow this sequence:

1. Inspect current state.
2. Identify affected files and dependencies.
3. Propose changes.
4. Obtain authorization when required.
5. Modify files.
6. Verify behavior.
7. Document results.
8. Commit approved changes.

---

## 4. Inspection Before Modification

Files must be inspected before modification.

No changes should be made based only on assumptions, filenames, or previous versions.

Evidence from:

- repository contents,
- runtime output,
- device state,
- test results,

must guide development decisions.

---

## 5. Evidence Classification

Development discussions should separate:

### Facts

Directly observed information.

Examples:

- command output,
- file contents,
- commit hashes,
- test results.

### Evidence-Based Inference

A conclusion supported by observed evidence but not directly observed.

### Hypothesis

A possible explanation requiring validation.

---

## 6. Change Authorization

Repository-changing actions require authorization before execution.

Examples:

- creating files,
- modifying tracked files,
- deleting files,
- changing architecture,
- changing protocol behavior.

Analysis and recommendations do not modify repository state.

---

## 7. Verification Requirements

Changes must be verified before being considered complete.

Verification may include:

- file inspection,
- runtime testing,
- hardware testing,
- synchronization checks,
- commit verification.

---

## 8. Milestone Locking

Completed milestones are locked.

Locked milestones must not be reopened unless an explicit decision is made to revisit them.

A locked milestone represents a verified project state.

---

## 9. Multi-Node Development Rules

NanoBot nodes include:

- controller/development machines,
- Raspberry Pi nodes,
- Jetson Orin nodes.

Node-specific changes must remain consistent with the repository baseline.

---

## 10. Preservation and Recovery

Before risky changes:

- create preservation copies when appropriate,
- record current state,
- verify recovery path.

---

## 11. Commit Requirements

Commits should:

- describe the change clearly,
- represent a verified state,
- avoid mixing unrelated modifications.

---

## 12. Exceptions

Exceptions to this governance process must be explicitly identified and documented.

---

## 13. Documentation Maintenance

Documentation must remain synchronized with verified project state.

Documentation updates should be considered when:

- architecture changes,
- runtime behavior changes,
- milestones are completed,
- governance rules change,
- hardware configuration changes.

Documentation changes require the same inspection, verification, and commit process as code changes.
