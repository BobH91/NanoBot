#!/usr/bin/env python3
"""Hardware-independent tests for Pi motor output serialization."""

import sys
import types
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub hardware-only dependencies before importing drive.py.
lgpio = types.ModuleType("lgpio")
lgpio.gpiochip_open = lambda *_: 0
lgpio.gpio_claim_output = lambda *_: 0
lgpio.gpio_write = lambda *_: 0
lgpio.gpiochip_close = lambda *_: None
sys.modules["lgpio"] = lgpio

adafruit = types.ModuleType("adafruit_pca9685")
adafruit.PCA9685 = object
sys.modules["adafruit_pca9685"] = adafruit

board = types.ModuleType("board")
board.SCL = object()
board.SDA = object()
sys.modules["board"] = board

busio = types.ModuleType("busio")
busio.I2C = lambda *_: None
sys.modules["busio"] = busio

import drive


def make_driver():
    driver = drive.MotorDriver.__new__(drive.MotorDriver)
    driver._lock = threading.Lock()
    driver._target_left = 0.5
    driver._target_right = 0.5
    driver._cur_left = 0.0
    driver._cur_right = 0.0
    driver._running = True
    driver.applied = []

    def record_apply(left, right):
        assert driver._lock.locked(), "hardware write occurred outside motor lock"
        driver.applied.append((left, right))

    driver._apply = record_apply
    return driver


def test_ramp_write_holds_lock():
    driver = make_driver()

    def one_iteration_sleep(_):
        driver._running = False

    original_sleep = drive.time.sleep
    drive.time.sleep = one_iteration_sleep
    try:
        driver._ramp_loop()
    finally:
        drive.time.sleep = original_sleep

    assert len(driver.applied) == 1
    assert driver.applied[0] != (0.0, 0.0)
    print("PASS: ramp hardware write occurs under motor lock")


def test_estop_write_holds_lock():
    driver = make_driver()
    driver.estop()

    assert driver.applied == [(0.0, 0.0)]
    assert driver._target_left == driver._target_right == 0.0
    assert driver._cur_left == driver._cur_right == 0.0
    print("PASS: E-stop zero write occurs under motor lock")


class ObservedLock:
    """Lock wrapper that signals when the E-stop thread attempts acquisition."""

    def __init__(self, estop_waiting):
        self._lock = threading.Lock()
        self.estop_waiting = estop_waiting

    def acquire(self, *args, **kwargs):
        if threading.current_thread().name == "estop":
            self.estop_waiting.set()
        return self._lock.acquire(*args, **kwargs)

    def release(self):
        self._lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *_):
        self.release()

    def locked(self):
        return self._lock.locked()


def test_estop_waits_for_ramp_write_then_writes_zero():
    ramp_entered = threading.Event()
    release_ramp = threading.Event()
    estop_waiting = threading.Event()
    estop_done = threading.Event()

    driver = make_driver()
    driver._lock = ObservedLock(estop_waiting)
    driver.applied = []

    def controlled_apply(left, right):
        assert driver._lock.locked()
        if threading.current_thread().name == "ramp":
            ramp_entered.set()
            assert release_ramp.wait(2), "test did not release ramp write"
            driver.applied.append((left, right))
            driver._running = False
        else:
            driver.applied.append((left, right))

    driver._apply = controlled_apply

    original_sleep = drive.time.sleep
    drive.time.sleep = lambda _: None

    ramp = threading.Thread(
        target=driver._ramp_loop,
        name="ramp",
    )

    def run_estop():
        try:
            driver.estop()
        finally:
            estop_done.set()

    estop = threading.Thread(target=run_estop, name="estop")

    try:
        ramp.start()
        assert ramp_entered.wait(2), "ramp did not enter hardware write"

        estop.start()
        assert estop_waiting.wait(2), "E-stop did not attempt lock acquisition"

        assert not estop_done.is_set(), (
            "E-stop completed while ramp still held the motor lock"
        )

        release_ramp.set()

        ramp.join(2)
        estop.join(2)

        assert not ramp.is_alive(), "ramp thread did not stop"
        assert not estop.is_alive(), "E-stop thread did not finish"
        assert len(driver.applied) == 2
        assert driver.applied[-1] == (0.0, 0.0)
        assert driver._target_left == driver._target_right == 0.0
        assert driver._cur_left == driver._cur_right == 0.0

    finally:
        release_ramp.set()
        drive.time.sleep = original_sleep
        ramp.join(2)
        if estop.ident is not None:
            estop.join(2)

    print("PASS: E-stop waits for ramp write, then writes zero")


if __name__ == "__main__":
    test_ramp_write_holds_lock()
    test_estop_write_holds_lock()
    test_estop_waits_for_ramp_write_then_writes_zero()
