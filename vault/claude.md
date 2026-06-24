# Nanobot — Project Context

## Boards

### RPi 5 (motor control)
IP 192.168.4.153 | OS Bookworm 64-bit | user pi

### Orin Nano (high-level control)
IP 192.168.4.90 | OS JetPack (Ubuntu 20/22) | user bob

## Python
System-wide only. NO virtual environments.
RPi:  pip3 install <pkg> --break-system-packages
Orin: pip3 install <pkg> --break-system-packages
      (fall back to --user if --break-system-packages rejected)

## Hardware — RPi 5
PCA9685 #1  I2C bus-1  addr 0x40  1000 Hz
  CH0 → MMD10A PWM1  (left motor speed)
  CH1 → MMD10A PWM2  (right motor speed)
rpi-lgpio digital output (direction, NOT PWM):
  GPIO27 / pin13 → MMD10A DIR1  (left)
  GPIO17 / pin11 → MMD10A DIR2  (right)
NO dtoverlay=pwm-2chan in /boot/firmware/config.txt
Diff drive: Barbie motors mirrored. Forward = LEFT fwd + RIGHT rev.
MOTOR_RIGHT_INVERT = False in config.py.

## Hardware — Orin Nano
PCA9685 #2  I2C bus-7  addr 0x40  50 Hz
  CH0 → PAN servo   (-90° to +90°,  center 1500us)
  CH1 → TILT servo  (-45° to +45°,  center 1500us)
  V+ powered from separate 5V BEC rail
Camera: Logitech 720p USB  /dev/video0  960x540 MJPG 30fps

## Network
WebRTC server 0.0.0.0:8080  ← browser (iPad/Safari) connects here
TCP client (Orin) → RPi 192.168.4.153:9000  (drive commands)
CAT6 between boards

## WebRTC
Library: aiortc
DC 'control'   browser→Nano  {cmd, throttle, steer, pan, tilt}
DC 'telemetry' Nano→browser  {pan_deg, tilt_deg, throttle, steer, state}
E-STOP: latching, cleared only by {"cmd":"RESET"}
Servo moves during E-STOP; drive commands blocked.

## Files — RPi
/home/pi/nanobot/config.py       constants
/home/pi/nanobot/drive.py        motor control
/home/pi/nanobot/tcp_server.py   command receiver
/home/pi/nanobot/tests/          test scripts
/home/pi/nanobot/logs/           runtime logs

## Files — Orin
/home/bob/nanobot/config.py          constants
/home/bob/nanobot/webrtc_server.py   main server
/home/bob/nanobot/camera.py          OpenCV capture
/home/bob/nanobot/servo.py           pan/tilt control
/home/bob/nanobot/tcp_client.py      relay to RPi
/home/bob/nanobot/ui/index.html      browser UI
/home/bob/nanobot/tests/             test scripts
/home/bob/nanobot/logs/              runtime logs
