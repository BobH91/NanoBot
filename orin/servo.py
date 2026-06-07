
"""
servo.py — Nanobot pan/tilt servo driver (Orin Nano)
Hardware:
  PCA9685 #2  I2C bus 7, addr 0x40, 50 Hz
  CH0 → PAN  servo
  CH1 → TILT servo

Uses smbus2 directly — no Adafruit Blinka required.

Servo pulse range (standard):
  500 µs  = full counter-clockwise / down
  2500 µs = full clockwise / up
  1500 µs = centre

Angle convention:
  Pan  : -90 … +90  (negative = left,  positive = right)
  Tilt : -45 … +45  (negative = down,  positive = up)
"""

import threading
import time
import smbus2

# ──────────────────────────────────────────────
# Hardware constants
# ──────────────────────────────────────────────
I2C_BUS         = 7
PCA_ADDR        = 0x40
PWM_FREQ_HZ     = 50           # standard servo frequency

# PCA9685 registers
_MODE1          = 0x00
_PRESCALE       = 0xFE
_LED0_ON_L      = 0x06         # base register; each channel = base + 4*ch

# Servo pulse width limits (microseconds)
PULSE_MIN_US    = 500
PULSE_MAX_US    = 2500

# At 50 Hz: period = 20 000 µs
_PERIOD_US      = 1_000_000 / PWM_FREQ_HZ   # 20 000.0

# ──────────────────────────────────────────────
# Channel assignments
# ──────────────────────────────────────────────
CH_PAN          = 0
CH_TILT         = 1

# ──────────────────────────────────────────────
# Travel limits (degrees)
# ──────────────────────────────────────────────
PAN_MIN_DEG     = -90
PAN_MAX_DEG     =  90
TILT_MIN_DEG    = -45
TILT_MAX_DEG    =  45

# ──────────────────────────────────────────────
# Slew rate
# ──────────────────────────────────────────────
SLEW_RATE_DEG_S = 120.0        # max degrees per second
SLEW_INTERVAL   = 0.020        # 50 Hz slew loop


# ──────────────────────────────────────────────
# PCA9685 bare-metal driver (smbus2)
# ──────────────────────────────────────────────
class PCA9685:
    """Minimal PCA9685 driver over smbus2."""

    def __init__(self, bus: int, addr: int, freq_hz: float):
        self._bus  = smbus2.SMBus(bus)
        self._addr = addr
        self._init(freq_hz)

    def _write(self, reg: int, value: int) -> None:
        self._bus.write_byte_data(self._addr, reg, value)

    def _read(self, reg: int) -> int:
        return self._bus.read_byte_data(self._addr, reg)

    def _init(self, freq_hz: float) -> None:
        # Sleep mode to set prescaler
        self._write(_MODE1, 0x10)
        time.sleep(0.005)

        # Prescaler = round(25 MHz / (4096 * freq)) - 1
        prescale = round(25_000_000 / (4096 * freq_hz)) - 1
        self._write(_PRESCALE, prescale)

        # Wake, enable auto-increment
        self._write(_MODE1, 0x00)
        time.sleep(0.005)
        self._write(_MODE1, 0xA0)   # auto-increment + normal mode

    def set_pulse_us(self, channel: int, pulse_us: float) -> None:
        """Set a channel's ON time in microseconds (OFF = 0)."""
        ticks = int((pulse_us / _PERIOD_US) * 4096)
        ticks = max(0, min(4095, ticks))
        reg   = _LED0_ON_L + 4 * channel
        self._bus.write_i2c_block_data(self._addr, reg, [
            0x00, 0x00,             # ON  low, high
            ticks & 0xFF,           # OFF low
            (ticks >> 8) & 0x0F,   # OFF high
        ])

    def set_all_off(self) -> None:
        for ch in range(16):
            self.set_pulse_us(ch, 0)

    def close(self) -> None:
        self.set_all_off()
        self._bus.close()


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _deg_to_us(degrees: float, min_deg: float, max_deg: float) -> float:
    frac = (degrees - min_deg) / (max_deg - min_deg)
    return PULSE_MIN_US + frac * (PULSE_MAX_US - PULSE_MIN_US)


# ──────────────────────────────────────────────
# Servo driver
# ──────────────────────────────────────────────
class ServoDriver:
    """
    Thread-safe pan/tilt servo driver for Nanobot.

    Usage
    -----
    servos = ServoDriver()
    servos.set_pan(45)
    servos.set_tilt(-20)
    servos.set(pan=0, tilt=0)
    servos.centre()
    servos.close()
    """

    def __init__(self):
        self._pca  = PCA9685(I2C_BUS, PCA_ADDR, PWM_FREQ_HZ)
        self._lock = threading.Lock()

        self._cur_pan     = 0.0
        self._cur_tilt    = 0.0
        self._target_pan  = 0.0
        self._target_tilt = 0.0

        self._write_pan(0.0)
        self._write_tilt(0.0)

        self._running = True
        self._thread  = threading.Thread(target=self._slew_loop, daemon=True)
        self._thread.start()

    # ── Public API ──────────────────────────────

    def set_pan(self, degrees: float) -> None:
        with self._lock:
            self._target_pan = _clamp(degrees, PAN_MIN_DEG, PAN_MAX_DEG)

    def set_tilt(self, degrees: float) -> None:
        with self._lock:
            self._target_tilt = _clamp(degrees, TILT_MIN_DEG, TILT_MAX_DEG)

    def set(self, pan: float, tilt: float) -> None:
        self.set_pan(pan)
        self.set_tilt(tilt)

    def centre(self) -> None:
        self.set(0.0, 0.0)

    def nudge_pan(self, delta: float) -> None:
        with self._lock:
            self._target_pan = _clamp(
                self._target_pan + delta, PAN_MIN_DEG, PAN_MAX_DEG)

    def nudge_tilt(self, delta: float) -> None:
        with self._lock:
            self._target_tilt = _clamp(
                self._target_tilt + delta, TILT_MIN_DEG, TILT_MAX_DEG)

    def get_position(self) -> dict:
        with self._lock:
            return {"pan": self._cur_pan, "tilt": self._cur_tilt}

    def close(self) -> None:
        self._running = False
        self._thread.join(timeout=1.0)
        self.centre()
        time.sleep(0.3)
        self._pca.close()

    # ── Slew loop ───────────────────────────────

    def _slew_loop(self) -> None:
        max_step = SLEW_RATE_DEG_S * SLEW_INTERVAL
        while self._running:
            time.sleep(SLEW_INTERVAL)
            with self._lock:
                self._cur_pan  = self._step(self._cur_pan,  self._target_pan,  max_step)
                self._cur_tilt = self._step(self._cur_tilt, self._target_tilt, max_step)
                cp, ct = self._cur_pan, self._cur_tilt
            self._write_pan(cp)
            self._write_tilt(ct)

    @staticmethod
    def _step(current: float, target: float, max_step: float) -> float:
        diff = target - current
        if abs(diff) <= max_step:
            return target
        return current + max_step * (1.0 if diff > 0 else -1.0)

    # ── Hardware write ───────────────────────────

    def _write_pan(self, degrees: float) -> None:
        us = _deg_to_us(degrees, PAN_MIN_DEG, PAN_MAX_DEG)
        self._pca.set_pulse_us(CH_PAN, us)

    def _write_tilt(self, degrees: float) -> None:
        us = _deg_to_us(degrees, TILT_MIN_DEG, TILT_MAX_DEG)
        self._pca.set_pulse_us(CH_TILT, us)

    # ── Context manager ──────────────────────────

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ──────────────────────────────────────────────
# Singleton (used by webrtc_server.py)
# ──────────────────────────────────────────────
_servos: ServoDriver | None = None
_servos_lock = threading.Lock()


def get_servos() -> ServoDriver:
    global _servos
    with _servos_lock:
        if _servos is None:
            _servos = ServoDriver()
    return _servos


def shutdown_servos() -> None:
    global _servos
    with _servos_lock:
        if _servos is not None:
            _servos.close()
            _servos = None


# ──────────────────────────────────────────────
# CLI smoke test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    print("Nanobot servo.py — smoke test (smbus2, I2C bus 7)")
    print("  Centring …")
    with ServoDriver() as s:
        s.centre()
        time.sleep(1.0)

        print("  Pan right 45° …")
        s.set_pan(45)
        time.sleep(1.0)

        print("  Pan left 45° …")
        s.set_pan(-45)
        time.sleep(1.0)

        print("  Centre pan, tilt up 30° …")
        s.set(pan=0, tilt=30)
        time.sleep(1.0)

        print("  Tilt down 30° …")
        s.set_tilt(-30)
        time.sleep(1.0)

        print("  Return to centre …")
        s.centre()
        time.sleep(1.0)

    print("Done — hardware released.")
    sys.exit(0)
