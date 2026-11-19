#include "sensors.h"
#include "config.h"
#include "storage.h"
#include "timekeeper.h"
#include "feeding_policy.h"
#include "time_math.h"
#include <HX711.h>
#include <DHT.h>

static HX711 scale;
static DHT   dht(PIN_DHT, DHT22);

// ── Nút ────────────────────────────────────
static bool     btnLast        = HIGH;
static bool     btnStable      = HIGH;
static uint32_t btnMs          = 0;
static bool     btnFired       = false;
static const uint32_t BTN_DEBOUNCE_MS = 50;

// ── Pet detection từ RPi ───────────────────
static bool     petDetected    = false;
static int      petConfirmCnt  = 0;
static PresenceGate presence(PET_WAIT_MS, PET_OBSERVATION_GAP_MS, PET_OBSERVATION_TTL_MS);

// ── Cảnh báo anti-spam ─────────────────────
static uint32_t alertLastMs[6] = {0};
static const char* alertKeys[] = {
    "hopper_low", "humidity_high", "jam", "bridge",
    "not_eaten", "stale"
};

// ── DHT cache ──────────────────────────────
static float    lastHum  = 50.0f;
static float    lastTemp = 25.0f;
static uint32_t dhtMs    = 0;
static const uint32_t DHT_INTERVAL_MS = 10000;

// ── Lọc nhiễu loadcell ─────────────────────
static void sensorsUpdateLoadcell();
static float    lcBuf[LC_FILTER_SIZE] = {0};
static int      lcBufIdx    = 0;
static bool     lcBufFull   = false;
static float    lcFiltered  = 0;
static float    lcStable    = 0;
static float    lcPrevious  = 0;
static int      lcStableCnt = 0;
static uint32_t lcLastMs    = 0;

// ─────────────────────────────────────────────
void sensorsInit() {
    scale.begin(PIN_HX711_DT, PIN_HX711_SCK);
#if WOKWI_SIM
    // Wokwi: 420 raw counts/kg = 0.42 counts/g.
    scale.set_scale(0.42f);
#else
    scale.set_scale(LOADCELL_CALIBRATION);
#endif

    // Chờ HX711 sẵn sàng với timeout (tránh treo trong Wokwi)
    uint32_t t0 = millis();
    while (!scale.is_ready() && (millis() - t0) < 3000) {
        delay(10);
    }
    if (scale.is_ready()) {
        scale.tare();
        Serial.println("[SENSOR] HX711 tare OK");
    } else {
        Serial.println("[SENSOR] HX711 not ready — skipped tare");
    }

    pinMode(PIN_TRIG, OUTPUT);
    pinMode(PIN_ECHO, INPUT);

    dht.begin();

    pinMode(PIN_BUTTON, INPUT_PULLUP);
    Serial.println("[SENSOR] Init done");
}

// ─────────────────────────────────────────────
void sensorsLoop() {
    uint32_t now = millis();

    // ── DHT đọc không chặn ──────────────────
    if (now - dhtMs > DHT_INTERVAL_MS) {
        float h = dht.readHumidity();
        float t = dht.readTemperature();
        if (!isnan(h)) lastHum  = h;
        if (!isnan(t)) lastTemp = t;
        dhtMs = now;
    }

    // ── Nút debounce ────────────────────────
    bool btnCur = digitalRead(PIN_BUTTON);
    if (btnCur != btnLast) {
        btnMs   = now;
        btnLast = btnCur;
    }
    if ((now - btnMs) > BTN_DEBOUNCE_MS && btnCur != btnStable) {
        btnStable = btnCur;
        if (btnStable == LOW) btnFired = true;
    }

    // ── Loadcell lọc nhiễu ──────────────────
    sensorsUpdateLoadcell();

    // ── Auto-tare ───────────────────────────
    sensorsAutoTare();
}

// ─────────────────────────────────────────────
//  Lọc nhiễu loadcell: median → spike reject → stable
// ─────────────────────────────────────────────
static float lcMedian() {
    int n = lcBufFull ? LC_FILTER_SIZE : lcBufIdx;
    if (n == 0) return 0;
    float tmp[LC_FILTER_SIZE];
    memcpy(tmp, lcBuf, n * sizeof(float));
    for (int i = 0; i < n - 1; i++)
        for (int j = i + 1; j < n; j++)
            if (tmp[j] < tmp[i]) { float t = tmp[i]; tmp[i] = tmp[j]; tmp[j] = t; }
    return tmp[n / 2];
}

static void sensorsUpdateLoadcell() {
    uint32_t now = millis();
    if ((now - lcLastMs) < LC_READ_INTERVAL_MS) return;
    lcLastMs = now;

#if WOKWI_SIM
    static uint32_t diagnosticMs = 0;
    bool diagnosticDue = now - diagnosticMs >= 2000;
#endif
    if (!scale.is_ready()) {
#if WOKWI_SIM
        if (diagnosticDue) {
            diagnosticMs = now;
            Serial.println("[HX711] NOT READY: check DT/SCK wiring");
        }
#endif
        return;
    }
    long counts = scale.read();
    float raw = (counts - scale.get_offset()) / scale.get_scale();
#if WOKWI_SIM
    if (diagnosticDue) {
        diagnosticMs = now;
        Serial.printf("[HX711] raw=%ld tare=%ld factor=%.2f grams=%.1f\n",
                      counts, scale.get_offset(), scale.get_scale(), raw);
    }
#endif
    raw = max(0.0f, raw);

    // Median rejects isolated spikes without locking out real weight changes.

    lcBuf[lcBufIdx] = raw;
    lcBufIdx = (lcBufIdx + 1) % LC_FILTER_SIZE;
    if (lcBufIdx == 0) lcBufFull = true;

    lcFiltered = lcMedian();

    if (fabsf(lcFiltered - lcPrevious) < LC_STABLE_DELTA_G) {
        lcStableCnt++;
    } else {
        lcStableCnt = 0;
    }
    if (lcStableCnt >= LC_STABLE_COUNT) {
        lcStable = lcFiltered;
    }
    lcPrevious = lcFiltered;
}

void sensorsPollWeight() { sensorsUpdateLoadcell(); }

float getBowlGrams()    { return lcStable; }
float getBowlGramsRaw() { return lcFiltered; }

void tareBowl() {
    scale.tare();
    lcStable = 0;
    lcFiltered = 0;
    lcPrevious = 0;
    lcBufIdx = 0;
    lcBufFull = false;
    lcStableCnt = 0;
    NVSData& d = nvsGet();
    d.lastTareTime = tkEpoch();
    nvsMark();
}

void sensorsAutoTare() {
    NVSData& d  = nvsGet();
    uint32_t ep = tkEpoch();
    if (ep == 0) return;
    if (getBowlGrams() < TARE_BOWL_THRESHOLD &&
        ep > d.lastTareTime &&
        (ep - d.lastTareTime) > TARE_INTERVAL_S) {
        tareBowl();
    }
}

// ─────────────────────────────────────────────
float getHopperCm() {
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);
    long dur = pulseIn(PIN_ECHO, HIGH, 30000);
    return dur * 0.0343f / 2.0f;
}

int getHopperPct() {
    float cm = getHopperCm();
    if (cm <= 0 || cm > HOPPER_HEIGHT_CM) return 0;
    int pct = (int)((1.0f - cm / HOPPER_HEIGHT_CM) * 100.0f);
    return constrain(pct, 0, 100);
}

// ─────────────────────────────────────────────
float getHumidity()    { return lastHum;  }
float getTemperature() { return lastTemp; }

// ─────────────────────────────────────────────
//  Pet detection — RPi gửi qua MQTT
// ─────────────────────────────────────────────
void setPetDetected(bool detected) {
    presence.observe(detected, millis());
    if (detected) {
        petConfirmCnt++;
        if (petConfirmCnt >= VISION_CONFIRM_FRAMES)
            petDetected = true;
    } else {
        petConfirmCnt = 0;
        petDetected   = false;
    }
}

bool isPetPresent()       { return presence.ready(millis()); }
int  getPetConfirmCount() { return petConfirmCnt; }
void resetPetDetection()  { petConfirmCnt = 0; petDetected = false; presence.reset(); }

// ─────────────────────────────────────────────
bool isButtonPressed() {
    if (btnFired) {
        btnFired = false;
        return true;
    }
    return false;
}

// ─────────────────────────────────────────────
float stalenessScore() {
    NVSData& d = nvsGet();
    if (d.foodDispensedAt == 0) return 0.0f;

    float ageH   = (float)epochElapsed(tkEpoch(), d.foodDispensedAt) / 3600.0f;
    float hum    = getHumidity();
    float temp   = getTemperature();
    float thresh = STALE_BASE_H;

    if (hum > 70)      thresh = STALE_HUM70_H;
    else if (hum > 60) thresh = STALE_HUM60_H;
    if (temp > 30)     thresh *= STALE_TEMP30_MULT;

    return ageH / thresh;
}

// ─────────────────────────────────────────────
//  Chống spam cảnh báo
// ─────────────────────────────────────────────
static int alertIndex(const char* type) {
    for (int i = 0; i < 6; i++)
        if (strcmp(alertKeys[i], type) == 0) return i;
    return -1;
}

bool canAlert(const char* alertType) {
    int idx = alertIndex(alertType);
    if (idx < 0) return true;
    return (millis() - alertLastMs[idx]) > (uint32_t)(ALERT_COOLDOWN_S * 1000UL);
}

void markAlert(const char* alertType) {
    int idx = alertIndex(alertType);
    if (idx < 0) return;
    alertLastMs[idx] = millis();
}
