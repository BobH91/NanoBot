#!/usr/bin/env python3
"""
i2c_scan.py — Scan I2C buses for PCA9685 #2  (addr 0x40)
Run: python3 /home/bob/nanobot/tests/i2c_scan.py
Expected: 0x40 on bus 1 or bus 7
"""
import smbus2, sys

found_on = None
for bus_num in [1, 7]:
    try:
        bus = smbus2.SMBus(bus_num)
        found = []
        for addr in range(3, 128):
            try:
                bus.read_byte(addr)
                found.append(addr)
            except Exception:
                pass
        bus.close()
        if found:
            print(f"Bus {bus_num}:")
            for a in found:
                tag = "  ← PCA9685 #2  ✓" if a == 0x40 else ""
                print(f"  0x{a:02X}{tag}")
            if 0x40 in found:
                found_on = bus_num
        else:
            print(f"Bus {bus_num}: no devices.")
    except FileNotFoundError:
        print(f"Bus {bus_num}: not available.")

if found_on:
    print(f"\nPASS — PCA9685 on bus {found_on}.")
    print(f"  → Set PCA_I2C_BUS = {found_on} in config.py if not already set.")
else:
    print("\nFAIL — 0x40 not found on any bus.")
    print("  Check SDA/SCL wiring and 3.3V on PCA VCC.")
    sys.exit(1)
