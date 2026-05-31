[[Debug pins 2]]

Tell the new chat this: Nanobot robot debug — drive arrow mapping wrong Stack:

- RPi5 (`pi@192.168.4.153`) runs `drive.py`
    - `tcp_server.py` (port 9000)
- Orin Nano (`bob@192.168.4.90`) runs `webrtc_server.py` (port 8080) + `tcp_client.py`
- UI is WebRTC, served from Nano at `http://192.168.4.90:8080/` Hardware constants in `drive.py` (current state): python

```
CH_LEFT            = 0
CH_RIGHT           = 1
GPIO_DIR_LEFT      = 27
GPIO_DIR_RIGHT     = 17
MOTOR_RIGHT_INVERT = False
```

What the RPi logs show arriving for each button:

- Up → `throttle=+0.5, steering=0.0` → robot turns right (should go forward)
- Down → `throttle=-0.5, steering=0.0` → robot goes forward (should go reverse)
- Right → `throttle=+0.15, steering=+0.5` → right turn ✓
- Left → `throttle=+0.15, steering=-0.5` → goes forward (should turn left) Conclusion so far: The UI is sending correct values. The bug is in `drive.py` — the DIR pins or channel assignments are still mismatched with the physical wiring. Next step is to try swapping `GPIO_DIR_LEFT=27` and `GPIO_DIR_RIGHT=17`. Hardware notes:
    
- Motors are mirror-mounted — right motor needs inversion for forward
- PCA9685 at I2C 0x40, 1kHz
- DIR pins use `rpi-lgpio` That gives the new chat everything it needs to pick up exactly where we left off.

Show more

May 18

Here's a clean handoff message you can paste into a new chat:

---

**Nanobot robot debug — drive arrow mapping wrong**

**Stack:**

- RPi5 (`pi@192.168.4.153`) runs `drive.py` + `tcp_server.py` (port 9000)
- Orin Nano (`bob@192.168.4.90`) runs `webrtc_server.py` (port 8080) + `tcp_client.py`
- UI is WebRTC, served from Nano at `http://192.168.4.90:8080/`

**Hardware constants in `drive.py` (current state):**

python

```python
CH_LEFT            = 0
CH_RIGHT           = 1
GPIO_DIR_LEFT      = 27
GPIO_DIR_RIGHT     = 17
MOTOR_RIGHT_INVERT = False
```

**What the RPi logs show arriving for each button:**

- Up → `throttle=+0.5, steering=0.0` → robot turns right (should go forward)
- Down → `throttle=-0.5, steering=0.0` → robot goes forward (should go reverse)
- Right → `throttle=+0.15, steering=+0.5` → right turn ✓
- Left → `throttle=+0.15, steering=-0.5` → goes forward (should turn left)

**Conclusion so far:** The UI is sending correct values. The bug is in `drive.py` — the DIR pins or channel assignments are still mismatched with the physical wiring. Next step is to try swapping `GPIO_DIR_LEFT=27` and `GPIO_DIR_RIGHT=17`.

**Hardware notes:**

- Motors are mirror-mounted — right motor needs inversion for forward
- PCA9685 at I2C 0x40, 1kHz
- DIR pins use `rpi-lgpio`

---

I'll also update my notes to reflect where things stand — the DIR pin swap is the next thing to test.

Used 2 tools

Used 2 tools

Notes updated. Paste that block into the new chat and it'll have full context to continue right where you left off.