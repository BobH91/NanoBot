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


if __name__ == "__main__":
    test_ramp_write_holds_lock()
    test_estop_write_holds_lock()
