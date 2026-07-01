FILE CONTENT — PROJECT_STATE.md
# NanoBot Project State (Verified Snapshot)

Last Updated: 2026-06-30

This document represents the **current verified runtime architecture** of NanoBot based on repository inspection.

It is intended as the **single source of truth for system understanding before UI or new architecture layers are added.**

---

# 1. SYSTEM OVERVIEW

NanoBot currently consists of three separate subsystems:

---

## 1.1 ACTIVE ROBOT CONTROL SYSTEM (PRODUCTION PATH)

This is the only system currently controlling the physical robot.

### Data Flow:

Orin Nano → Raspberry Pi → Motor Driver → Hardware

### Components:

- `nodes/orin/tcp_client.py`
- `nodes/pi/tcp_server.py`
- `nodes/pi/drive.py`

### Protocol:

```json
{
  "cmd": "drive",
  "throttle": float,
  "steering": float
}
Supported Commands:
drive
stop
estop
ping
Characteristics:
Real-time TCP communication
Simple JSON protocol
Rate-limited command sending (Orin)
Watchdog safety stop (Pi)
Immediate estop support
1.2 MOTOR CONTROL LAYER (PI HARDWARE INTERFACE)
File:
nodes/pi/drive.py
Responsibilities:
Differential drive mixing (throttle + steering)
Motor ramp smoothing
Deadband filtering
Exponential response curve
GPIO direction control (lgpio)
PCA9685 PWM control (I2C)
Emergency stop behavior
Thread-safe singleton driver
Hardware:
PCA9685 PWM driver (0x40)
GPIO 17 (left motor direction)
GPIO 27 (right motor direction)
1.3 PI TCP SERVER (EXECUTION GATEWAY)
File:
nodes/pi/tcp_server.py
Responsibilities:
Listens on 0.0.0.0:9000
Receives newline-delimited JSON commands
Dispatches commands to MotorDriver
Returns simple status responses
Behavior:
One client expected (Orin Nano)
Watchdog stops motors if client becomes inactive
Handles: drive, stop, estop, ping, quit
1.4 ORIN TCP CLIENT (CONTROL INTERFACE)
File:
nodes/orin/tcp_client.py
Responsibilities:
Maintains persistent TCP connection to Pi
Automatic reconnect logic
Keepalive ping system
Rate-limited drive command sending (20 Hz max)
Provides simple API:
drive(throttle, steering)
stop()
estop()
ping()
2. INACTIVE / EXPERIMENTAL SYSTEMS
2.1 v8.3 CONTROLLER SYSTEM (NOT CONNECTED TO HARDWARE)
Files:
nodes/controller.py
nodes/shared/protocol/v83_protocol.py
Features:
Structured command system
Command IDs (UUID)
ACK tracking
RESULT tracking
Pending command state management
Status:
NOT connected to Orin runtime path
NOT connected to Pi motor control system
Exists as a standalone control framework
2.2 NANOBUS (EXPERIMENTAL BROADCAST SYSTEM)
File:
nodes/shared/bus/nanobus.py
Behavior:
TCP broadcast relay
Receives JSON messages
Broadcasts to all connected clients
No schema enforcement
No control authority
Status:
Not used in robot control pipeline
Experimental / debugging tool only
3. COMMUNICATION ARCHITECTURE
Active Control Path:
Orin Nano
   ↓ TCP JSON (cmd protocol)
Raspberry Pi (tcp_server.py)
   ↓
MotorDriver (drive.py)
   ↓
PCA9685 + GPIO
   ↓
Motors
Inactive Systems:
controller.py → v8.3 protocol → (no hardware connection)
NanoBus → broadcast system → (no control role)
4. HARDWARE STACK (PI)
PCA9685 PWM driver (I2C address 0x40)
LGPIO GPIO control
Differential motor system
Motor ramp smoothing
Safety watchdog stop logic
5. SAFETY SYSTEMS

Active safety mechanisms:

Watchdog motor stop (TCP inactivity)
Emergency stop command (estop)
Motor ramp limiting (prevents sudden changes)
Client disconnect handling
6. SYSTEM BOUNDARIES
Raspberry Pi:
Motor control
Hardware interfacing
Safety enforcement
TCP execution server
Orin Nano:
Command generation
TCP client
Network control layer
Controller system:
Experimental logic layer
Not part of runtime control path
7. KEY ARCHITECTURAL TRUTH

NanoBot currently contains two parallel architectures:

ACTIVE SYSTEM (REAL ROBOT CONTROL)

Orin → Pi → Motors

EXPERIMENTAL SYSTEM (NOT CONNECTED)

controller.py → v8.3 protocol → (no hardware path)

8. IMPORTANT NOTES
The robot is currently controlled exclusively through the Orin → Pi TCP pipeline.
The v8.3 controller system is not part of the runtime execution path.
NanoBus is not integrated into robot control.
Motor control system is stable and production-ready.
9. PURPOSE OF THIS FILE

This document exists to:

Prevent architectural confusion
Establish a verified baseline before UI development
Ensure future changes are grounded in actual runtime behavior
Separate active vs experimental systems clearly
