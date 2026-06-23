# =============================================================================
# config.py  —  Nanobot Orin Nano constants
# All other modules import from here. Never hardcode addresses or IPs.
# =============================================================================

# Network
NANO_IP       = "192.168.4.90"
RPI_IP        = "192.168.4.153"
LAPTOP_IP     = "192.168.4.14"
RPI_TCP_PORT  = 9000            # TCP port on RPi — send drive commands here

WEBRTC_HOST   = "0.0.0.0"      # listen on all interfaces
WEBRTC_PORT   = 8080            # browser connects to http://192.168.4.90:8080

# Camera
CAMERA_DEVICE = "/dev/video0"   # Logitech 720p USB
CAMERA_WIDTH  = 960
CAMERA_HEIGHT = 544
CAMERA_FPS    = 30
CAMERA_FOURCC = "MJPG"

# PCA9685 #2  (I2C → pan/tilt servos)
# Wiring: Nano I2C → PCA9685 addr 0x40 @ 50 Hz
# CH0 = PAN servo    CH1 = TILT servo
PCA_ADDRESS   = 0x40  # confirmed
PCA_I2C_BUS   = 7
PCA_FREQ_HZ   = 50

PCA_CH_PAN    = 0
PCA_CH_TILT   = 1

# Servo pulse widths (microseconds)
SERVO_MIN_US  = 500             # ~-90°
SERVO_MID_US  = 1500            # center
SERVO_MAX_US  = 2500            # ~+90°

# Pan/tilt range (degrees from center)
PAN_MIN_DEG   = -90
PAN_MAX_DEG   =  90
PAN_CENTER    =   0
PAN_STEP_DEG  =   5             # degrees per button tick

TILT_MIN_DEG  = -45
TILT_MAX_DEG  =  45
TILT_CENTER   =   0
TILT_STEP_DEG =   5

# WebRTC DataChannel names
DC_CONTROL    = "control"       # browser → Nano: JSON commands
DC_TELEMETRY  = "telemetry"     # Nano → browser: JSON status
