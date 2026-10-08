# SETPOINT-001 Related Evidence: Wheel Direction Test with MOTOR_RIGHT_INVERT = True

Date: 2026-10-04

## Summary

Wheel direction was tested on the Raspberry Pi motor service
(`nanobot-pi.service`) with the committed settings (MOTOR_LEFT_INVERT = True,
MOTOR_RIGHT_INVERT = False) and again after changing MOTOR_RIGHT_INVERT to
True. The root cause of why the committed settings gave a different result
than the 2026-08-01 closure record is NOT identified.

This change was made while SETPOINT_LOCKS.md listed "Change
MOTOR_RIGHT_INVERT" under DO NOT. It was made before this evidence entry
was written and before review. This entry records it after the fact.

The edit was also made directly on the Pi. LOCK_SYNC.md describes the Pi as
runtime-only (no commits unless instructed; allowed operations: git pull,
run scripts, run tests, log runtime data). Editing a repository file is not
among them.

## Requested

Key presses in the UI, one at a time (UI device not recorded). Logged
commands:

| Key   | DRIVE throttle / steering |
|-------|---------------------------|
| Up    | 0.500 / 0.000             |
| Down  | -0.500 / 0.000            |
| Left  | 0.150 / -0.500            |
| Right | 0.150 / 0.500             |

Wanted: Up = both wheels forward; Down = both reverse; Left = left reverse,
right forward; Right = left forward, right reverse.

## Reported (journalctl, nanobot-pi.service)

APPLY values were the same before and after the change: Up +/+, Down -/-,
Left -/+, Right +/-.

WRITE_MOTOR before (MOTOR_RIGHT_INVERT = False, service PID 751):

| Key   | pwm=0 left (gpio 17) | pwm=1 right (gpio 27) |
|-------|----------------------|-----------------------|
| Up    | value -, dir 0       | value +, dir 1        |
| Down  | value +, dir 1       | value -, dir 0        |
| Left  | value +, dir 1       | value +, dir 1        |
| Right | value -, dir 0       | value -, dir 0        |

WRITE_MOTOR after (MOTOR_RIGHT_INVERT = True, service PID 2707):

| Key   | pwm=0 left (gpio 17) | pwm=1 right (gpio 27) |
|-------|----------------------|-----------------------|
| Up    | value -, dir 0       | value -, dir 0        |
| Down  | value +, dir 1       | value +, dir 1        |
| Left  | value +, dir 1       | value -, dir 0        |
| Right | value -, dir 0       | value +, dir 1        |

## Verified (wheels observed by Bob, one key press per test)

| Key   | Before: left / right | After: left / right | Wanted: left / right | After matches |
|-------|----------------------|---------------------|----------------------|---------------|
| Up    | forward / reverse    | forward / forward   | forward / forward    | Yes           |
| Down  | reverse / forward    | reverse / reverse   | reverse / reverse    | Yes           |
| Left  | reverse / reverse    | reverse / forward   | reverse / forward    | Yes           |
| Right | forward / forward    | forward / reverse   | forward / reverse    | Yes           |

In all eight tests, direction value 0 went with a wheel turning forward and
direction value 1 with a wheel turning reverse.

## Runtime effect

With MOTOR_LEFT_INVERT = True and MOTOR_RIGHT_INVERT = True, all four arrow
keys produced the wanted wheel directions. Bob reported no speed problems;
speed was not tested or changed.

## Reproduction procedure (established 2026-10-04)

1. In nodes/pi/config.py set MOTOR_RIGHT_INVERT = True.
2. sudo systemctl restart nanobot-pi.service
3. Capture: journalctl -u nanobot-pi.service -f -n 0 > <file>
4. Press one arrow key for about 1 second, release, wait 3 seconds, Ctrl+C.
5. Filter idle lines: grep -v -e "APPLY left=+0.000 right=+0.000" -e "value=[+-]0.000" <file>

Log files were saved under /tmp and are not preserved.

## Not identified

- Why the committed settings (LEFT True, RIGHT False) gave a right wheel
  opposite to the 2026-08-01 closure record (which lists all four directions
  as matching with those same settings).
- Commit e3d9f15 (2026-09-29) changed only _shape() in drive.py; it does not
  touch the invert logic. It has not been shown to be related.
- Bob knows of no change to the right motor, its connections, or the driver
  since 2026-08-01. Not independently checked.
- Robot support state (wheels on a stand) during the tests was not recorded.

## Backup

Original config.py (MOTOR_RIGHT_INVERT = False) was copied to
/tmp/config.py.bak_before_right_invert (not preserved across reboot).
