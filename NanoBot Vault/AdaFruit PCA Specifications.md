AdaFruit PCA Specifications

7:26 PM

Searched the web

Searched the web

Here's a summary of the key specifications for the **Adafruit PCA9685 16-Channel PWM/Servo Driver**:

---

**Board / Physical**

- Dimensions (no headers): 2.5" × 1" × 0.1" (62.5 × 25.4 × 3 mm); weight ~5.5 g (9 g with headers and terminal block) [Adafruit](https://www.adafruit.com/product/815)

---

**PWM / Channels**

- 16 PWM output channels, all driven simultaneously over I2C using only 2 pins (SDA/SCL), with no additional host processor overhead [Adafruit](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all)
- 12-bit resolution per channel — the counter cycles 0–4095, and each channel has independently programmable ON and OFF tick points [DeepWiki](https://deepwiki.com/adafruit/Adafruit-PWM-Servo-Driver-Library/3-understanding-the-pca9685-hardware)
- All 16 channels share a single PWM frequency (you can't set different frequencies per channel)

---

**Frequency**

- Internal reference clock is 25 MHz (may vary slightly with temperature and manufacturing tolerances) [CircuitPython](https://docs.circuitpython.org/_/downloads/pca9685/en/3.3.4/pdf/)
- PWM frequency is user-configurable; typical use is 50 Hz for servos, up to ~1.6 kHz for LEDs/motors

---

**I2C Interface**

- 7-bit I2C address range 0x40–0x7F, selectable via solder jumpers — default is 0x40 (which matches your Nanobot setup) [Adafruit](https://www.adafruit.com/product/815)
- Supports Fast-mode Plus (Fm+) I2C up to 1 MHz, with bus capacitance support up to 4000 pF [DigiKey](https://www.digikey.com/en/htmldatasheets/production/1640697/0/0/1/pca9685-datasheet)

---

**Electrical**

- Supply voltage: 2.3 V to 5.5 V; I/O pins are 5.5 V tolerant [DigiKey](https://www.digikey.com/en/htmldatasheets/production/1640697/0/0/1/pca9685-datasheet)
- Output drivers: open-drain with 25 mA sink at 5 V, or totem-pole with 25 mA sink / 10 mA source at 5 V [DigiKey](https://www.digikey.com/en/htmldatasheets/production/1640697/0/0/1/pca9685-datasheet)
- Compatible with both 3.3 V and 5 V logic levels [Cirkit Designer](https://docs.cirkitdesigner.com/component/635df77c-89ab-5b97-3f92-8132f4ebf37c/adafruit-pca9685-pwm-servo-breakout)

---

**Typical Use Cases**

- Robotics, animatronics, LED dimming, and any application requiring multiple synchronized PWM outputs — and in your case, motor speed control via the MMD10A driver [Cirkit Designer](https://docs.cirkitdesigner.com/component/635df77c-89ab-5b97-3f92-8132f4ebf37c/adafruit-pca9685-pwm-servo-breakout)