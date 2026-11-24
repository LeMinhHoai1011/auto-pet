#include "feeder.h"
#include "config.h"
#include "sensors.h"
#include "storage.h"
#include "display.h"
#include <AccelStepper.h>

static AccelStepper stepper(AccelStepper::DRIVER, PIN_STEP, PIN_DIR);
static bool busy = false;

// ── Encoder ISR ─────────────────────────────
static volatile long encCount = 0;

static void IRAM_ATTR encISR_A() {
    int a = digitalRead(PIN_ENC_A);
    int b = digitalRead(PIN_ENC_B);
    encCount += (a == b) ? 1 : -1;
}

volatile long encoderGetCount() { return encCount; }
void encoderResetCount() { encCount = 0; }

// ─────────────────────────────────────────────
void feederInit() {
    stepper.setMaxSpeed(STEPPER_MAX_SPEED);
    stepper.setAcceleration(STEPPER_ACCEL);

    pinMode(PIN_EN, OUTPUT);
    digitalWrite(PIN_EN, HIGH); // disable motor khi idle

    pinMode(PIN_ENC_A, INPUT_PULLUP);
    pinMode(PIN_ENC_B, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), encISR_A, CHANGE);
}

bool feederIsBusy() { return busy; }

// ── Quay stepper 1 đợt, trả về số xung encoder đếm được ──
static long stepperRunDose(int steps) {
    encoderResetCount();

    digitalWrite(PIN_EN, LOW); // bật motor
    stepper.move(steps);
    while (stepper.distanceToGo() != 0) {
        stepper.run();
        sensorsPollWeight();
        yield();
    }
    delay(50); // chờ encoder bắt kịp
    long enc = abs(encoderGetCount());
#if WOKWI_SIM
    // The current Wokwi diagram has no encoder. Simulate only its pulses;
    // the dispensed grams must still come from the actual HX711 input.
    enc = abs(steps);
#endif
    return enc;
}

static void stepperOff() {
    stepper.stop();
    digitalWrite(PIN_EN, HIGH);
}

// ─────────────────────────────────────────────
//  Nhả theo gram — stepper + encoder + loadcell
//
//  Vòng lặp:
//    1. Quay stepper N steps
//    2. Đọc encoder → trục có quay?
//    3. Đọc loadcell → cân tăng?
//    4. Đủ gram → dừng
//    5. Encoder = 0 → kẹt cơ học → đảo chiều 1 lần
//    6. Encoder OK, cân = 0 → hạt không xuống (vòm/hết)
// ─────────────────────────────────────────────
FeedResult feederDispense(float targetGrams, float& actualGrams) {
    busy = true;

    NVSData& d = nvsGet();
    strncpy(d.feedState, "dispensing", sizeof(d.feedState) - 1);
    d.feedTarget = targetGrams;
    nvsFlush(true);

    float startGrams = getBowlGramsRaw();
    actualGrams = 0;

    int noIncDoses  = 0;   // đợt loadcell không tăng
    int noEncDoses  = 0;   // đợt encoder không quay
    int bridgeDoses = 0;   // đợt encoder OK + loadcell = 0
    bool reversed   = false;

    FeedResult result = FEED_OK;
    uint32_t feedStartMs = millis();
    const uint32_t FEED_TIMEOUT_MS = 60000;
    Serial.printf(">> Bat dau nha %.1fg thuc an...\r\n", targetGrams);
#if WOKWI_SIM
    // Ước tính gram mỗi dose dựa trên steps (Wokwi không có loadcell thật)
    const float gramsPerDose = 5.0f;
    Serial.println(">> (Wokwi: virtual loadcell - tu dong tinh gram)");
#endif

    while (true) {
        if ((millis() - feedStartMs) > FEED_TIMEOUT_MS) {
            result = FEED_TIMEOUT;
            break;
        }
        float prevGrams = getBowlGramsRaw();

        long enc = stepperRunDose(STEPPER_STEPS_PER_DOSE);

#if WOKWI_SIM
        // Mô phỏng thức ăn rơi vào bát: mỗi dose cộng thêm gram
        sensorsAddVirtualGrams(gramsPerDose);
#endif

        // Chờ cân ổn định
        uint32_t pauseStart = millis();
        do {
            sensorsPollWeight();
            delay(1);
        } while (millis() - pauseStart < STEPPER_DOSE_PAUSE_MS);

        float nowGrams = getBowlGramsRaw();
        actualGrams = nowGrams - startGrams;
        dispState.bowlGrams = nowGrams;
        displayLoop();
        Serial.printf("   Bat: %.1fg | Da nha: %.1fg / %.1fg\r\n",
                      nowGrams, actualGrams, targetGrams);

        if (actualGrams >= targetGrams) {
            result = FEED_OK;
            break;
        }

        float delta = nowGrams - prevGrams;

        // ── Trường hợp 1: Encoder không quay → kẹt cơ học ──
        if (enc < ENC_MIN_PULSES) {
            noEncDoses++;
            if (noEncDoses >= 2) {
                if (!reversed) {
                    // Thử đảo chiều 1 lần
                    reversed = true;
                    noEncDoses = 0;
                    stepperRunDose(-STEPPER_REVERSE_STEPS);
                    delay(200);
                    continue;
                }
                // Đã đảo chiều rồi mà vẫn kẹt
                result = FEED_JAM;
                break;
            }
            continue;
        }
        noEncDoses = 0;

        // ── Trường hợp 2: Trục quay, loadcell = 0 → hạt không xuống ──
        if (nowGrams < 0.3f) {
            bridgeDoses++;
            if (bridgeDoses >= JAM_DOSES) {
                result = FEED_BRIDGE;
                break;
            }
            continue;
        }
        bridgeDoses = 0;

        // ── Trường hợp 3: Trục quay, loadcell tăng ít → nghi kẹt mềm ──
        if (delta < JAM_THRESHOLD_G) {
            noIncDoses++;
            if (noIncDoses >= JAM_DOSES) {
                if (!reversed) {
                    reversed = true;
                    noIncDoses = 0;
                    stepperRunDose(-STEPPER_REVERSE_STEPS);
                    delay(200);
                    continue;
                }
                result = FEED_JAM;
                break;
            }
        } else {
            noIncDoses = 0;
        }
    }

    stepperOff();

    d.feedActual = actualGrams;
    strncpy(d.feedState, "done", sizeof(d.feedState) - 1);
    nvsFlush(true);

    busy = false;
    return result;
}
