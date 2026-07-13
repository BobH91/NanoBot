# NanoBot Machine-Local File Policy

## 1. Purpose

This document defines the boundary between repository-controlled files and machine-local files.

The purpose of this policy is to prevent accidental inclusion of temporary, generated, or device-specific data into the NanoBot repository.

---

## 2. Repository-Controlled Files

Repository-controlled files are files required to reproduce, develop, test, or operate NanoBot.

Examples:

- source code,
- documentation,
- tests,
- hardware definitions,
- protocol definitions,
- configuration templates,
- deployment scripts.

---

## 3. Machine-Local Files

Machine-local files exist only on individual devices and are not considered project source.

Examples:

- editor metadata,
- cache files,
- temporary logs,
- generated runtime data,
- local credentials,
- device-specific temporary configuration.

---

## 4. Node-Specific Data

Each NanoBot node may contain local operational data.

Examples:

- runtime state,
- hardware calibration data,
- temporary diagnostics,
- local service files.

Node-local data must not replace repository-controlled configuration.

---

## 5. Secrets and Credentials

Sensitive data must remain machine-local.

Examples:

- passwords,
- private keys,
- tokens,
- personal credentials.

Secrets must not be committed to Git.

---

## 6. Generated Files

Generated files should not enter the repository unless they are explicitly required project artifacts.

Examples:

- compiled output,
- cache directories,
- temporary exports,
- generated metadata.

---

## 7. Review Before Adding Files

Before adding a new file to the repository, determine:

1. Is this required for NanoBot operation?
2. Should another developer or node receive this file?
3. Can this file be regenerated?
4. Does this file contain machine-specific information?

---

## 8. Recovery

If machine-local files are accidentally committed:

1. Identify the file.
2. Preserve required data.
3. Remove it from repository control.
4. Update policy or ignore rules if necessary.

---

## 9. Policy Maintenance

This policy should evolve as NanoBot hardware, software, and deployment methods change.
