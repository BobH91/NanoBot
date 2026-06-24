
# NanoBot Sync Rules (LOCKED ARCHITECTURE)

## 1. Repository Purpose
This repository contains TWO systems:

### A. Software Layer (EXECUTION)
Path:
- /software/

Contains:
- Pi runtime code
- Orin runtime code
- networking, control, vision, servo logic

RULE:
- All robot execution code MUST live here
- No code outside /software/

---

### B. Knowledge Layer (VAULT)
Path:
- /vault/

Contains:
- Obsidian notes
- hardware research
- design docs
- AI chats
- system knowledge graphs

RULE:
- All documentation MUST live here
- No execution code allowed here

---

## 2. Folder Ownership Rules

### software/
- Python, C++, scripts that run on devices
- Pi / Orin runtime logic

### vault/
- Markdown only (.md)
- Logs, research, MOCs, design notes
- No executable code

### docs/
- System-level architecture docs only
- High-level design (not runtime code)

### hardware/
- Specifications, datasheets, wiring notes

### scripts/
- Dev tooling, automation scripts (non-runtime)

### ai_chats/
- Archived development conversations only

### tests/
- Unit/integration test files only

---

## 3. Git Rules

- Always commit from repository root
- Never commit:
  - videos
  - large binaries
  - temporary logs
- Always verify with:
  git status
  git ls-files

---

## 4. Sync Rules (CRITICAL)

### GitHub sync:
- software/
- vault/
- docs/
- hardware/
- scripts/
- ai_chats/
- tests/

### NOT recommended for GitHub long-term:
- large media files (future rule)

---

## 5. Device Sync Model (Future)
- Lenovo = MASTER Git repo
- Pi = runtime clone (software only execution)
- Orin = runtime clone (software + vision)
- Vault sync = Syncthing (eventual optimization)

---

## 6. Golden Rule

> Git tracks structure and knowledge.  
> Devices execute behavior.

Never mix execution runtime with vault knowledge structure.
