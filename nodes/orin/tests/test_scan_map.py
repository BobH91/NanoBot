import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from scan_map import camera_to_grid

TOL = 1e-9
c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))

CASES = [
    # name, (x, y, z) camera frame, pan, tilt, expected (X, Y, Z)
    ("straight ahead",              (0, 0, 2), 0,   0,  (0, 2, 0)),
    ("pan right 90",                (0, 0, 2), 90,  0,  (2, 0, 0)),
    ("pan left 90",                 (0, 0, 2), -90, 0,  (-2, 0, 0)),
    ("tag right of axis",           (1, 0, 2), 0,   0,  (1, 2, 0)),
    ("tag below axis",              (0, 1, 2), 0,   0,  (0, 2, -1)),
    ("tilt up 30",                  (0, 0, 2), 0,   30, (0, 2 * c30, 2 * s30)),
    ("pan right 90, tag at right",  (1, 0, 0), 90,  0,  (0, -1, 0)),
]


def main():
    for name, (x, y, z), pan, tilt, exp in CASES:
        got = camera_to_grid(x, y, z, pan, tilt)
        for g, e in zip(got, exp):
            assert abs(g - e) < TOL, f"{name}: got {got}, expected {exp}"
    ref = math.sqrt(0.4**2 + 0.3**2 + 2.5**2)
    for pan in (-80, -20, 0, 35, 90):
        for tilt in (-30, 0, 15, 30):
            gx, gy, gz = camera_to_grid(0.4, -0.3, 2.5, pan, tilt)
            assert abs(math.sqrt(gx*gx + gy*gy + gz*gz) - ref) < TOL
    print(f"PASS: {len(CASES)} direction cases + distance check")


if __name__ == "__main__":
    main()
