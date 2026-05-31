
## You said: Nanobot robot debug — drive arrow mapping wrong

Nanobot robot debug — drive arrow mapping wrong Stack:

- RPi5 (`pi@192.168.4.153`) runs `drive.py`
    - `tcp_server.py` (port 9000)
- Orin Nano (`bob@192.168.4.90`) runs `webrtc_server.py` (port 8080) + `tcp_client.py`
- UI is WebRTC, served from Nano at `http://192.168.4.90:8080/` Hardware constants in `drive.py` (current state): python

```
CH_LEFT            = 0
CH_RIGHT           = 1
GPIO_DIR_LEFT      = 27
GPIO_DIR_RIGHT     = 17
MOTOR_RIGHT_INVERT = False
```

What the RPi logs show arriving for each button:

- Up → `throttle=+0.5, steering=0.0` → robot turns right (should go forward)
- Down → `throttle=-0.5, steering=0.0` → robot goes forward (should go reverse)
- Right → `throttle=+0.15, steering=+0.5` → right turn ✓
- Left → `throttle=+0.15, steering=-0.5` → goes forward (should turn left) Conclusion so far: The UI is sending correct values. The bug is in `drive.py` — the DIR pins or channel assignments are still mismatched with the physical wiring. Next step is to try swapping `GPIO_DIR_LEFT=27` and `GPIO_DIR_RIGHT=17`. Hardware notes:
    
- Motors are mirror-mounted — right motor needs inversion for forward
- PCA9685 at I2C 0x40, 1kHz
- DIR pins use `rpi-lgpio` I'll also update my notes to reflect where things stand — the DIR pin swap is the next thing to test. Used 2 tools Used 2 tools Notes updated. Paste that block into the new chat and it'll have full context to continue right where you left off.

Show more

May 18

## Claude responded: Got it, notes are updated.

Got it, notes are updated. Here's a clean summary of where things stand and what to try next:

---

**Current symptoms → diagnosis**

|Button|Expected|Actual|Implication|
|---|---|---|---|
|Up|Forward|Turns right|Left motor not driving forward, or channels swapped|
|Down|Reverse|Goes forward|Direction logic inverted on one/both motors|
|Right|Right turn|Right turn ✓|Right side at least partially correct|
|Left|Left turn|Goes forward|Left motor behaving like right motor|

The pattern — especially Left acting like forward — strongly suggests the DIR pins are crossed: GPIO 17 is wired to the left motor physically but assigned as `GPIO_DIR_RIGHT` in code (or vice versa).

---

**Next test: swap the DIR pin assignments**

python

```python
GPIO_DIR_LEFT  = 17   # was 27
GPIO_DIR_RIGHT = 27   # was 17
```

Leave everything else unchanged for now. Retest all four arrows and note what changes.

---

**If that fixes direction but Left/Right are still swapped:**

python

```python
CH_LEFT  = 1   # was 0
CH_RIGHT = 0   # was 1
```

**If forward/reverse are still inverted after the DIR swap:**

python

```python
MOTOR_RIGHT_INVERT = True
```

or add a `MOTOR_LEFT_INVERT` if you don't have one yet.

---

Work through one change at a time so you can isolate which axis (DIR pin vs PWM channel vs invert flag) fixes each symptom. Good luck with the test — report back what the four buttons do after the swap.