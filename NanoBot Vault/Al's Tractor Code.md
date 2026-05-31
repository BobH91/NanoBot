#include <Arduino.h>

/*
 * steer_test.cpp
 * Steering motor + potentiometer test with PID control
 * - PWM scales naturally with distance (high when far, low when close)
 * - On timeout: increments PWM_MIN by 10 and retries from beginning
 * - Stops after MAX_CYCLES complete cycles or PWM_MIN hits PWM_MAX
 *
 * Hardware:
 *   IBT-2: RPWM=5, LPWM=6
 *   Pot:   A9
 *   LED:   13 (built-in)
 *
 * Calibration from bench measurements:
 *   Hard right = 197, Straight = 446, Hard left = 815
 *
 * PWM scaling explanation:
 *   kp=1.0, error=250 (far away) -> output=250 -> near PWM_MAX
 *   kp=1.0, error=80  (mid range) -> output=80  -> passes through
 *   kp=1.0, error=15  (close)     -> output=15  -> floored to PWM_MIN
 *   error <= DEADBAND              -> motor stops
 */

// Built-in LED
#define LED_PIN 13

// IBT-2 pins
const int RPWM = 5;
const int LPWM = 6;

// Pot pin
const int POT_PIN = A9;

// Measured calibration values
const int POT_RIGHT  = 197;
const int POT_CENTER = 446;
const int POT_LEFT   = 815;

// Control settings
const int   DEADBAND        = 10;
int         PWM_MIN         = 160;   // Variable: increments on timeout
const int   PWM_MAX         = 255;
const int   PWM_MIN_START   = 160;   // Starting floor
const int   PWM_MIN_STEP    = 10;    // Increment on each timeout
const unsigned long HOLD_TIME    = 10000;  // 10 seconds hold at each position
const unsigned long MOVE_TIMEOUT = 10000;  // 10 seconds max to reach target

// Stop after this many complete cycles (hard right + center = 1 cycle)
const int MAX_CYCLES = 3;

// PID gains
// kp=1.0 means: error=250 -> PWM=250 (near max), error=80 -> PWM=80, error=15 -> floored to PWM_MIN
float kp = 1.0;   // CHANGED: was 0.8, raised so output spans full PWM range
float ki = 0.05;
float kd = 0.1;

// PID state variables
float pid_error      = 0;
float pid_last_error = 0;
float pid_error_sum  = 0;
unsigned long pid_last_time = 0;

// Last PWM for printing
int last_pwm = 0;

// Cycle tracking
int  cycleCount = 0;
bool testDone   = false;

// Test sequence
const int NUM_TARGETS = 3;

const int targets[NUM_TARGETS] = {
    POT_RIGHT,   // hard right = 197
    POT_CENTER,  // center = 446
    POT_LEFT     // hard left = 815   ← NEW
};

const char* targetNames[NUM_TARGETS] = {
    "hard right",
    "center",
    "hard left"   // ← NEW
};


int           currentTarget   = 0;
unsigned long holdStart       = 0;
unsigned long moveStart       = 0;
bool          holdingPosition = false;

// LED heartbeat state
bool          ledState  = false;
unsigned long lastBlink = 0;

// Trajectory logging
unsigned long lastTrajLog = 0;
const unsigned long TRAJ_LOG_INTERVAL = 100;

void stopMotor() {
    analogWrite(RPWM, 0);
    analogWrite(LPWM, 0);
}

void resetPID() {
    pid_error      = 0;
    pid_last_error = 0;
    pid_error_sum  = 0;
    pid_last_time  = millis();
}

void resetTest() {
    currentTarget   = 0;
    holdingPosition = false;
    cycleCount      = 0;
    moveStart       = 0;
    lastTrajLog     = 0;
    resetPID();
}

// PID drive toward target, returns true when on target
bool driveToTarget(int target) {
    int pot = analogRead(POT_PIN);
    pid_error = target - pot;

    // Log trajectory every 100ms
    unsigned long now = millis();
    if (now - lastTrajLog >= TRAJ_LOG_INTERVAL) {
        Serial.print("  moving  pot=");
        Serial.print(pot);
        Serial.print("  target=");
        Serial.print(target);
        Serial.print("  error=");
        Serial.print((int)pid_error);
        Serial.print("  pwm=");
        Serial.println(last_pwm);
        lastTrajLog = now;
    }

    // On target - stop
    if (abs(pid_error) <= DEADBAND) {
        stopMotor();
        return true;
    }

    // Time delta
    float dt = (now - pid_last_time) / 1000.0f;
    if (dt <= 0) dt = 0.01f;
    pid_last_time = now;

    // Integral with anti-windup
    pid_error_sum += pid_error * dt;
    pid_error_sum = constrain(pid_error_sum, -200.0f, 200.0f);

    // Derivative
    float d_error = (pid_error - pid_last_error) / dt;
    pid_last_error = pid_error;

    // PID output - naturally high when far, low when close
    float output = kp * pid_error +
                   ki * pid_error_sum +
                   kd * d_error;

    // Clamp PWM - floor keeps motor moving near target, ceiling prevents damage
    int pwm = constrain(abs((int)output), PWM_MIN, PWM_MAX);
    last_pwm = pwm;

    if (output > 0) {
        analogWrite(RPWM, 0);
        analogWrite(LPWM, pwm);
    } else {
        analogWrite(LPWM, 0);
        analogWrite(RPWM, pwm);
    }
    return false;
}

void setup() {
    pinMode(LED_PIN, OUTPUT);
    pinMode(RPWM, OUTPUT);
    pinMode(LPWM, OUTPUT);
    stopMotor();

    // 3 fast blinks = setup ran
    for (int i = 0; i < 3; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);
        delay(100);
    }

    delay(45000);  // Wait for RPi serial to be ready
    Serial.begin(115200);
    while (!Serial && millis() < 3000);

    resetPID();

    Serial.println("Steer PID logging test starting...");
    Serial.print("kp="); Serial.print(kp);
    Serial.print("  ki="); Serial.print(ki);
    Serial.print("  kd="); Serial.println(kd);
    Serial.print("PWM_MIN="); Serial.print(PWM_MIN);
    Serial.print("  PWM_MAX="); Serial.println(PWM_MAX);
    Serial.print("Will run "); Serial.print(MAX_CYCLES);
    Serial.print(" cycles, timeout="); Serial.print(MOVE_TIMEOUT / 1000);
    Serial.println("s per move.");
    Serial.print("First target: ");
    Serial.print(targetNames[0]);
    Serial.print("  pot target=");
    Serial.println(targets[0]);
}

void loop() {
    unsigned long now = millis();

    // LED heartbeat
    if (now - lastBlink >= 500) {
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
        lastBlink = now;
    }

    // Test complete - just blink
    if (testDone) {
        return;
    }

    if (!holdingPosition) {
        // Record when this move started
        if (moveStart == 0) moveStart = now;

        // Kill timer - increment PWM_MIN and retry if stuck
        if (now - moveStart >= MOVE_TIMEOUT) {
            stopMotor();
            int stuckPot = analogRead(POT_PIN);
            Serial.print(">>> TIMEOUT moving to: ");
            Serial.print(targetNames[currentTarget]);
            Serial.print("  stuck at pot=");
            Serial.print(stuckPot);
            Serial.print("  PWM_MIN was=");
            Serial.println(PWM_MIN);

            PWM_MIN += PWM_MIN_STEP;

            if (PWM_MIN >= PWM_MAX) {
                testDone = true;
                Serial.print("PWM_MIN reached PWM_MAX=");
                Serial.println(PWM_MAX);
                Serial.println("=== Test stopped: motor cannot reach target. ===");
                return;
            }

            Serial.print("Retrying with PWM_MIN=");
            Serial.println(PWM_MIN);
            resetTest();
            Serial.print("Restarting from target: ");
            Serial.print(targetNames[0]);
            Serial.print("  pot target=");
            Serial.println(targets[0]);
            return;
        }

        bool onTarget = driveToTarget(targets[currentTarget]);

        if (onTarget) {
            moveStart       = 0;
            holdingPosition = true;
            holdStart       = now;
            resetPID();
            Serial.print(">>> Reached: ");
            Serial.print(targetNames[currentTarget]);
            Serial.print("  pot=");
            Serial.print(analogRead(POT_PIN));
            Serial.print("  pwm=");
            Serial.println(last_pwm);
        }

    } else {
        // Holding - print every 2 seconds
        static unsigned long lastPrint = 0;
        if (now - lastPrint >= 2000) {
            Serial.print("    Holding ");
            Serial.print(targetNames[currentTarget]);
            Serial.print("  pot=");
            Serial.print(analogRead(POT_PIN));
            Serial.print("  PWM_MIN=");
            Serial.println(PWM_MIN);
            lastPrint = now;
        }

        if (now - holdStart >= HOLD_TIME) {
            // Increment cycle count when center target completed
            if (currentTarget == 1) {
                cycleCount++;
                Serial.print("--- Cycle ");
                Serial.print(cycleCount);
                Serial.print(" of ");
                Serial.print(MAX_CYCLES);
                Serial.print(" complete  PWM_MIN=");
                Serial.println(PWM_MIN);

                if (cycleCount >= MAX_CYCLES) {
                    stopMotor();
                    testDone = true;
                    Serial.println("=== Test complete. Motor stopped. ===");
                    return;
                }
            }

            currentTarget   = (currentTarget + 1) % NUM_TARGETS;
            holdingPosition = false;
            moveStart       = 0;
            resetPID();
            lastTrajLog = 0;
            Serial.print("Moving to: ");
            Serial.print(targetNames[currentTarget]);
            Serial.print("  pot target=");
            Serial.println(targets[currentTarget]);
        }
    }
}