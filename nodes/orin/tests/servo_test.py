#!/usr/bin/env python3
"""Hardware-free tests for NanoBot servo limits and calibration."""

import sys
import types
import unittest
from pathlib import Path

# Allow importing servo.py without installing or accessing smbus2 hardware.
sys.modules.setdefault("smbus2", types.SimpleNamespace(SMBus=object))

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import servo


class ServoSafetyTests(unittest.TestCase):

    def test_tilt_travel_limits(self):
        self.assertEqual(servo.TILT_MIN_DEG, -30)
        self.assertEqual(servo.TILT_MAX_DEG, 10)

    def test_original_tilt_pulse_calibration_preserved(self):
        self.assertEqual(
            servo._deg_to_us(-45, servo.TILT_PULSE_MIN_DEG,
                             servo.TILT_PULSE_MAX_DEG), 500
        )
        self.assertEqual(
            servo._deg_to_us(45, servo.TILT_PULSE_MIN_DEG,
                             servo.TILT_PULSE_MAX_DEG), 2500
        )
        self.assertEqual(
            servo._deg_to_us(0, servo.TILT_PULSE_MIN_DEG,
                             servo.TILT_PULSE_MAX_DEG), 1500
        )

    def test_new_tilt_limits_map_inside_original_pulse_range(self):
        low = servo._deg_to_us(
            servo.TILT_MIN_DEG,
            servo.TILT_PULSE_MIN_DEG,
            servo.TILT_PULSE_MAX_DEG
        )
        high = servo._deg_to_us(
            servo.TILT_MAX_DEG,
            servo.TILT_PULSE_MIN_DEG,
            servo.TILT_PULSE_MAX_DEG
        )
        self.assertAlmostEqual(low, 833.333333, places=5)
        self.assertAlmostEqual(high, 1722.222222, places=5)
        self.assertGreater(low, 500)
        self.assertLess(high, 2500)

    def test_tilt_command_clamping(self):
        self.assertEqual(servo._clamp(-100, servo.TILT_MIN_DEG,
                                      servo.TILT_MAX_DEG), -30)
        self.assertEqual(servo._clamp(100, servo.TILT_MIN_DEG,
                                      servo.TILT_MAX_DEG), 10)
        self.assertEqual(servo._clamp(0, servo.TILT_MIN_DEG,
                                      servo.TILT_MAX_DEG), 0)

    def test_independent_slew_rates(self):
        pan_step = servo.PAN_SLEW_RATE_DEG_S * servo.SLEW_INTERVAL
        tilt_step = servo.TILT_SLEW_RATE_DEG_S * servo.SLEW_INTERVAL
        self.assertAlmostEqual(pan_step, 2.4)
        self.assertAlmostEqual(tilt_step, 0.6)
        self.assertAlmostEqual(pan_step / tilt_step, 4.0)

    def test_scan_rows_within_tilt_limits(self):
        import config
        rows = config.SCAN_TILT_ROWS_DEG
        self.assertEqual(rows, (-30, -15, 0, 5, 10))
        self.assertTrue(all(
            config.TILT_MIN_DEG <= angle <= config.TILT_MAX_DEG
            for angle in rows
        ))


if __name__ == "__main__":
    unittest.main(verbosity=2)
