Claude finished the response

## You said: MMD 10 A Dual Channel Motor Controller Specifications

MMD 10 A Dual Channel Motor Controller Specifications

7:29 PM

## Claude responded: Here's a summary of the Cytron MDD10A specifications, which is the dual-channel motor driver you're using on the Nanobot:

Searched the web

Searched the web

Here's a summary of the Cytron MDD10A specifications, which is the dual-channel motor driver you're using on the Nanobot:

**Power**

- Motor supply voltage: 5V to 30V (Rev 2.0) [BOTLAND](https://botland.store/drivers-for-dc-motors/15818-cytron-mdd10a-dual-channel-30v-10a-motor-controller-5904422350444.html)
- Continuous current: 10A per channel; Peak current: 30A per channel (momentary, ~10 seconds) [Cytron](https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels)

**Control Interface**

- Logic voltage: 3.3V and 5V compatible (PWM and DIR inputs), so it works with Arduino, Raspberry Pi, and similar microcontrollers [BOTLAND](https://botland.store/drivers-for-dc-motors/15818-cytron-mdd10a-dual-channel-30v-10a-motor-controller-5904422350444.html)
- Supports both sign-magnitude and locked-antiphase PWM signal modes [Makers Electronics](https://makerselectronics.com/product/cytron-mdd10a-dc-motor-driver-dual/)
- Note: supports TTL PWM from a microcontroller — not RC receiver PWM [Makers Electronics](https://makerselectronics.com/product/cytron-mdd10a-dc-motor-driver-dual/)
- PWM frequency up to 20 kHz [Makermotor](https://makermotor.com/pn00218-cyt4-cytron-dual-channel-10a-dc-motor-driver-mdd10a/)

**Hardware Design**

- Fully NMOS H-Bridge for better efficiency — no heat sink required [Makermotor](https://makermotor.com/pn00218-cyt4-cytron-dual-channel-10a-dc-motor-driver-mdd10a/)
- Solid-state components only (no mechanical relays), giving faster response and longer life [Makers Electronics](https://makerselectronics.com/product/cytron-mdd10a-dc-motor-driver-dual/)
- Includes regenerative braking [Opencircuit](https://opencircuit.shop/product/10amp-5v-30v-dc-motor-driver-2-channels)
- Includes overcurrent protection, undervoltage lockout, and thermal shutdown [Cytron](https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels)

**Onboard Features**

- Two onboard push buttons per channel for manual motor testing without a microcontroller [Makers Electronics](https://makerselectronics.com/product/cytron-mdd10a-dc-motor-driver-dual/)
- LED indicators showing current flow direction per channel
- Board dimensions: 84.5mm × 62mm [Makers Electronics](https://makerselectronics.com/product/cytron-mdd10a-dc-motor-driver-dual/)

**Important Note** Use a battery (not a switching power supply alone) when driving inductive loads like brushed DC motors. Switching power supplies may shut down when they detect regenerative current from the motor. If a switching supply is needed, connect a battery of the same voltage in parallel to absorb that regenerative current. [Makers Electronics](https://makerselectronics.com/product/cytron-mdd10a-dc-motor-driver-dual/)

This matches your setup well — the RPi5 driving PWM via PCA9685 at 1kHz and DIR signals via GPIO fits within the MDD10A's control interface specs.