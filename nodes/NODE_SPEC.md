# NanoBot Node Spec v5 (AUTHORITATIVE)

## GLOBAL RULES

- Pi = motion + control execution node
- Orin = vision + sensor + AI node
- Lenovo = controller + architecture node
- shared = ONLY reusable libraries / protocols

---

## PI NODE RULES

Allowed:
- nodes/pi/**

Responsibilities:
- motor control
- GPIO / hardware interface
- TCP server (robot control)

Blocked:
- vision / camera code
- UI / web server
- controller logic
- AI processing

---

## ORIN NODE RULES

Allowed:
- nodes/orin/**

Responsibilities:
- camera pipeline
- servo control
- AI inference
- web UI / streaming

Blocked:
- direct motor drive control
- robot base control logic

---

## SHARED RULES

Allowed ONLY:
- reusable libraries
- communication protocols
- configs

STRICTLY BLOCKED:
- test files (*.txt, test scripts)
- node-specific logic
- hardware control code

---

## CONTROLLER NODE (LENOVO)

Allowed:
- everything in repo

Responsibilities:
- system architecture
- deployment control
- validation enforcement
- git governance

---

## VIOLATION POLICY

Any file that does not match this spec:
→ MUST be blocked at commit time
