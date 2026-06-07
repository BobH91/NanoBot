
"""
drive.py — Nanobot motor driver (RPi 5)
Hardware:
  PCA9685 #1  I2C bus 1, addr 0x40, 1000 Hz
  CH0 → MMD10A PWM1 (left motor)
  CH1 → MMD10A PWM2 (right motor)
  GPIO 17 → DIR1 (left)   [rpi-lgpio]
  GPIO 27 → DIR2 (right)  [rpi-lgpio]

Differential drive notes:
  Motors are mirror-mounted → forward = LEFT forward + RIGHT reverse.
  MOTOR_RIGHT_INVERT = False compensates so callers always pass
  positive throttle = forward, positive steer = right.

Coordinate convention (caller's frame):
  throttle  : -1.0 … +1.0   (+1 = forward)
  steering  : -1.0 … +1.0   (+1 = right turn)
"""

import time
import threading
import lgpio 
from adafruit_pca9685 import PCA9685
import board
import busio

# ──────────────────────────────────────────────
# Hardware constants
# ──────────────────────────────────────────────
I2C_FREQ_HZ        = 1_000          # PCA9685 PWM frequency
PCA_ADDR           = 0x40
CH_LEFT            = 0              # PCA9685 channel for left  PWM
CH_RIGHT           = 1              # PCA9685 channel for right PWM
GPIO_DIR_LEFT      = 17             # lgpio GPIO for left  direction
GPIO_DIR_RIGHT     = 27             # lgpio GPIO for right direction

MOTOR_RIGHT_INVERT = False          # mirrors physical mounting

# ──────────────────────────────────────────────
# Tuning parameters
# ──────────────────────────────────────────────
DEADBAND           = 0.04           # |input| below this → 0 (fraction of full scale)
EXP_CURVE          = 2.0            # exponent for response curve (1 = linear)
MAX_DUTY           = 0.95           # cap duty cycle (fraction of full scale)
RAMP_RATE          = 2.0            # max change in duty per second (0…1 scale)
RAMP_INTERVAL      = 0.020          # ramp update period, seconds (50 Hz)
DIFFERENTIAL_MIX   = 1.0           # how much steering bleeds into opposite motor (0…1)

# PCA9685 full-scale tick count
_PCA_MAX_TICKS     = 0xFFFF         # 16-bit


# ──────────────────────────────────────────────
# Helper: signal shaping
# ──────────────────────────────────────────────

def _apply_deadband(value: float, band: float) -> float:
    """Return 0 inside deadband, rescaled outside so output is continuous."""
    if abs(value) < band:
        return 0.0
    sign = 1.0 if value > 0 else -1.0
    return sign * (abs(value) - band) / (1.0 - band)


def _apply_exp_curve(value: float, exp: float) -> float:
    """Apply exponential response curve, preserving sign."""
    return (abs(value) ** exp) * (1.0 if value >= 0 else -1.0)


def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _shape(raw: float) -> float:
    """Full shaping pipeline: deadband → exp curve → clamp."""
    v = _apply_deadband(raw, DEADBAND)
    v = _apply_exp_curve(v, EXP_CURVE)
    return _clamp(v)


# ──────────────────────────────────────────────
# Motor driver class
# ──────────────────────────────────────────────

class MotorDriver:
    """
    Thread-safe motor driver for Nanobot's differential drive.

    Usage
    -----
    driver = MotorDriver()
    driver.set(throttle=0.5, steering=0.0)   # half speed forward
    driver.stop()
    driver.close()
    """

    def __init__(self):
        # I2C + PCA9685
        i2c = busio.I2C(board.SCL, board.SDA)
        self._pca = PCA9685(i2c, address=PCA_ADDR)
        self._pca.frequency = I2C_FREQ_HZ

        # lgpio
        self._gpio_handle = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self._gpio_handle, GPIO_DIR_LEFT,  0)
        lgpio.gpio_claim_output(self._gpio_handle, GPIO_DIR_RIGHT, 0)

        # Ramp state  (target and current duty for each motor, range -1…+1)
        self._lock         = threading.Lock()
        self._target_left  = 0.0
        self._target_right = 0.0
        self._cur_left     = 0.0
        self._cur_right    = 0.0

        # Start ramp thread
        self._running = True
        self._ramp_thread = threading.Thread(target=self._ramp_loop, daemon=True)
        self._ramp_thread.start()

    # ── Public API ──────────────────────────────

    def set(self, throttle: float, steering: float) -> None:
        """
        Set desired motion.

        Parameters
        ----------
        throttle : float  -1…+1   (+1 = forward)
        steering : float  -1…+1   (+1 = turn right)
        """
        t = _shape(_clamp(throttle))
        s = _shape(_clamp(steering))

        # Differential mix
        left  = _clamp(t + s * DIFFERENTIAL_MIX)
        right = _clamp(t - s * DIFFERENTIAL_MIX)

        with self._lock:
            self._target_left  = left
            self._target_right = right

    def stop(self) -> None:
        """Immediately command zero speed (targets set to 0; ramp still applies)."""
        with self._lock:
            self._target_left  = 0.0
            self._target_right = 0.0

    def estop(self) -> None:
        """Emergency stop: cut output immediately, bypassing ramp."""
        with self._lock:
            self._target_left  = 0.0
            self._target_right = 0.0
            self._cur_left     = 0.0
            self._cur_right    = 0.0
        self._apply(0.0, 0.0)

    def close(self) -> None:
        """Release hardware resources."""
        self._running = False
        self._ramp_thread.join(timeout=1.0)
        self.estop()
        self._pca.deinit()
        lgpio.gpiochip_close(self._gpio_handle)

    # ── Ramp loop ───────────────────────────────

    def _ramp_loop(self) -> None:
        max_step = RAMP_RATE * RAMP_INTERVAL
        while self._running:
            time.sleep(RAMP_INTERVAL)
            with self._lock:
                self._cur_left  = self._step(self._cur_left,  self._target_left,  max_step)
                self._cur_right = self._step(self._cur_right, self._target_right, max_step)
                cl, cr = self._cur_left, self._cur_right
            self._apply(cl, cr)

    @staticmethod
    def _step(current: float, target: float, max_step: float) -> float:
        diff = target - current
        if abs(diff) <= max_step:
            return target
        return current + max_step * (1.0 if diff > 0 else -1.0)

    # ── Hardware write ───────────────────────────

    def _apply(self, left: float, right: float) -> None:
        """
        Write direction and duty cycle to hardware.

        Positive value → forward for that side.
        MOTOR_RIGHT_INVERT flips the physical right-motor direction signal.
        """
        # Physical direction: right motor wired mirror-image
        phys_right = -right if MOTOR_RIGHT_INVERT else right

        self._write_motor(CH_LEFT,  GPIO_DIR_LEFT,  left)
        self._write_motor(CH_RIGHT, GPIO_DIR_RIGHT, phys_right)

    def _write_motor(self, pwm_ch: int, dir_gpio: int, value: float) -> None:
        """
        Write one motor channel.

        value > 0 → forward  (DIR = HIGH, duty = |value|)
        value < 0 → reverse  (DIR = LOW,  duty = |value|)
        value = 0 → brake    (DIR = LOW,  duty = 0)
        """
        duty = min(abs(value), MAX_DUTY)
        direction = 1 if value > 0 else 0

        lgpio.gpio_write(self._gpio_handle, dir_gpio, direction)

        ticks = int(duty * _PCA_MAX_TICKS)
        self._pca.channels[pwm_ch].duty_cycle = ticks

    # ── Context manager support ──────────────────

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ──────────────────────────────────────────────
# Convenience singleton (used by tcp_server.py)
# ──────────────────────────────────────────────
_driver: MotorDriver | None = None
_driver_lock = threading.Lock()


def get_driver() -> MotorDriver:
    global _driver
    with _driver_lock:
        if _driver is None:
            _driver = MotorDriver()
    return _driver


def shutdown_driver() -> None:
    global _driver
    with _driver_lock:
        if _driver is not None:
            _driver.close()
            _driver = None


# ──────────────────────────────────────────────
# CLI smoke-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    print("Nanobot drive.py — smoke test")
    print("  Ramping forward 0→50% over 1 s …")
    with MotorDriver() as drv:
        drv.set(throttle=0.5, steering=0.0)
        time.sleep(1.5)

        print("  Turning right …")
        drv.set(throttle=0.3, steering=0.5)
        time.sleep(1.0)

        print("  Stopping …")
        drv.stop()
        time.sleep(0.5)

    print("Done — hardware released.")
    sys.exit(0)
