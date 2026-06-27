# =============================================================================
# config.py  —  Nanobot RPi 5 constants
# Import from here — never hardcode pins or addresses elsewhere.
# =============================================================================

# Network
TCP_HOST     = "0.0.0.0"
TCP_PORT     = 9000
NANO_IP      = "192.168.4.90"
RPI_IP       = "192.168.4.153"
LAPTOP_IP    = "192.168.4.14"

# PCA9685 #1  (I2C-1 → MMD10A)
# Wiring: GPIO2/pin3=SDA  GPIO3/pin5=SCL → PCA9685 addr 0x40 @ 1000 Hz
PCA_I2C_BUS  = 1
PCA_ADDRESS  = 0x40
PCA_FREQ_HZ  = 1000
PCA_CH_LEFT  = 0               # CH0 → MMD10A PWM1  (left motor)
PCA_CH_RIGHT = 1               # CH1 → MMD10A PWM2  (right motor)

# Direction pins — rpi-lgpio digital output ONLY (not PWM)
# BCM numbering.  NO dtoverlay=pwm-2chan in config.txt.
GPIO_DIR_LEFT  = 17            # BCM17 / physical pin 11 → MMD10A DIR1
GPIO_DIR_RIGHT = 27            # BCM27 / physical pin 13 → MMD10A DIR2
DIR_FWD = 1
DIR_REV = 0

# Differential drive — Barbie motors mounted mirrored
MOTOR_LEFT_INVERT  = False
MOTOR_RIGHT_INVERT = True      # right motor mounted mirrored — inverted

# Tuning
DEADBAND     = 0.05
RAMP_RATE    = 0.10
EXP_CURVE    = 2.0
MAX_THROTTLE = 1.0
PWM_FULL_OFF = 0
PWM_FULL_ON  = 4095
