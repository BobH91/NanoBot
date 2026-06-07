#!/usr/bin/env python3
"""
i2c_scan.py — Scan I2C bus 1.  Expected: 0x40 (PCA9685 #1)
Run: python3 /home/pi/nanobot/tests/i2c_scan.py
"""
import smbus2, sys

BUS = 1
print(f"Scanning I2C bus {BUS} ...")
try:
    bus = smbus2.SMBus(BUS)
except FileNotFoundError:
    sys.exit(f"ERROR: /dev/i2c-{BUS} not found. Reboot after enabling I2C.")

found = []
for addr in range(3, 128):
    try:
        bus.read_byte(addr)
        found.append(addr)
    except Exception:
        pass
bus.close()

if found:
    for a in found:
        tag = "  ← PCA9685 #1  ✓" if a == 0x40 else ""
        print(f"  0x{a:02X}{tag}")
else:
    print("  No devices found. Check wiring and confirm reboot after I2C enable.")

if 0x40 not in found:
    print("\nFAIL — 0x40 not found.")
    print("  Check: SDA→pin3  SCL→pin5  3.3V on VCC  GND connected")
    sys.exit(1)
else:
    print("\nPASS — PCA9685 responding on 0x40.")
