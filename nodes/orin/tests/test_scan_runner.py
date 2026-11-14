import math
import os
import sys
import tempfile
import time
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import config
from scan_map import ScanRunner, build_stops

TEST_PAN_SIGN = -1
TEST_TILT_SIGN = 1
config.SCAN_PAN_SIGN = TEST_PAN_SIGN
config.SCAN_TILT_SIGN = TEST_TILT_SIGN
config.SCAN_SETTLE_S = 0.0
config.SCAN_FRESH_MARGIN_S = 0.0
config.SCAN_RESULT_TIMEOUT_S = 0.5
config.SCAN_ARRIVE_TIMEOUT_S = 1.0

TAGS = {7: (1.0, 2.0, 0.3), 9: (-1.5, 1.0, 0.0)}   # true grid X, Y, Z (m)
HALF_H = math.radians(24.9)
HALF_V = math.radians(14.7)


class FakeServos:
    def __init__(self):
        self.pan = 6.7
        self.tilt = -14.7
        self.commands = []

    def set(self, pan, tilt):
        self.commands.append((pan, tilt))
        self.pan, self.tilt = pan, tilt

    def get_position(self):
        return {"pan": self.pan, "tilt": self.tilt}


def grid_to_camera(X, Y, Z, pan_deg, tilt_deg):
    p, t = math.radians(pan_deg), math.radians(tilt_deg)
    right = X * math.cos(p) - Y * math.sin(p)
    fwd = X * math.sin(p) + Y * math.cos(p)
    up = Z
    z = fwd * math.cos(t) + up * math.sin(t)
    y = fwd * math.sin(t) - up * math.cos(t)
    return right, y, z


def make_get_result(servos):
    def get_result():
        pan = TEST_PAN_SIGN * servos.pan
        tilt = TEST_TILT_SIGN * servos.tilt
        tags = []
        for tag_id, (X, Y, Z) in TAGS.items():
            x, y, z = grid_to_camera(X, Y, Z, pan, tilt)
            if z > 0 and abs(math.atan2(x, z)) < HALF_H and abs(math.atan2(y, z)) < HALF_V:
                tags.append(SimpleNamespace(
                    tag_id=tag_id, hamming=0, decision_margin=50.0,
                    x_m=x, y_m=y, z_m=z))
        return SimpleNamespace(
            frame_time=time.monotonic() + 1.0, tags=tuple(tags), error=None)
    return get_result


def wait_done(runner, timeout=20.0):
    end = time.monotonic() + timeout
    while runner.is_running():
        assert time.monotonic() < end, "scan did not finish"
        time.sleep(0.02)


def test_build_stops():
    stops = build_stops()
    assert len(stops) == 50, len(stops)
    assert stops[0] == (-90, -30), stops[0]
    assert stops[9] == (90, -30), stops[9]
    assert stops[10] == (90, -15), stops[10]
    print("PASS: build_stops (50 stops, serpentine)")


def test_full_scan():
    servos = FakeServos()
    with tempfile.TemporaryDirectory() as tmp:
        runner = ScanRunner(servos, make_get_result(servos), lambda: False, log_dir=tmp)
        ok, msg = runner.start()
        assert ok, msg
        wait_done(runner)
        st = runner.status()
        assert st["state"] == "done", st
        found = {t["tag_id"]: t for t in st["tags"]}
        assert set(found) == {7, 9}, sorted(found)
        for tag_id, (X, Y, Z) in TAGS.items():
            t = found[tag_id]
            assert abs(t["X_m"] - X) < 1e-3, (tag_id, t)
            assert abs(t["Y_m"] - Y) < 1e-3, (tag_id, t)
            assert abs(t["Z_m"] - Z) < 1e-3, (tag_id, t)
            assert t["n"] >= 2, (tag_id, t)
            assert t["X_std_m"] < 1e-3 and t["Y_std_m"] < 1e-3, (tag_id, t)
        assert servos.get_position() == {"pan": 6.7, "tilt": -14.7}
        assert st["csv"] and os.path.isfile(st["csv"]), st
        with open(st["csv"]) as handle:
            header = handle.readline().strip()
        assert header.startswith("stop,pan_deg,tilt_deg,tag_id"), header
    print("PASS: full scan recovers both tag positions, restores servos, writes CSV")


def test_refuses_when_estop():
    servos = FakeServos()
    runner = ScanRunner(servos, make_get_result(servos), lambda: True)
    ok, msg = runner.start()
    assert (not ok) and "e-stop" in msg, (ok, msg)
    assert runner.status()["state"] == "idle"
    print("PASS: start refused while e-stop is active")


def test_stop_mid_scan():
    servos = FakeServos()
    config.SCAN_SETTLE_S = 0.2
    try:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ScanRunner(servos, make_get_result(servos), lambda: False, log_dir=tmp)
            ok, msg = runner.start()
            assert ok, msg
            time.sleep(0.3)
            runner.stop()
            wait_done(runner)
            st = runner.status()
            assert st["state"] == "stopped", st
            assert servos.get_position() == {"pan": 6.7, "tilt": -14.7}
    finally:
        config.SCAN_SETTLE_S = 0.0
    print("PASS: stop request ends the scan and restores servos")


def test_estop_mid_scan():
    servos = FakeServos()
    flag = [False]
    config.SCAN_SETTLE_S = 0.2
    try:
        with tempfile.TemporaryDirectory() as tmp:
            runner = ScanRunner(servos, make_get_result(servos), lambda: flag[0], log_dir=tmp)
            ok, msg = runner.start()
            assert ok, msg
            time.sleep(0.3)
            runner.estop()
            # Simulate an immediate server reset while the scan unwinds.
            flag[0] = False
            wait_done(runner)
            st = runner.status()
            assert st["state"] == "error" and "e-stop" in st["error"], st
            assert servos.commands, "scan never issued a servo command"
            assert servos.commands[-1] != (6.7, -14.7), (
                "E-stop incorrectly commanded restoration", servos.commands
            )
    finally:
        config.SCAN_SETTLE_S = 0.0
    print("PASS: e-stop mid-scan aborts the scan")


def main():
    test_build_stops()
    test_full_scan()
    test_refuses_when_estop()
    test_stop_mid_scan()
    test_estop_mid_scan()
    print("ALL PASS (5 tests)")


if __name__ == "__main__":
    main()
