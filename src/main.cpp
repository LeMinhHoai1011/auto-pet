#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "storage.h"
#include "timekeeper.h"
#include "sensors.h"
#include "feeder.h"
#include "schedule.h"
#include "display.h"
#include "notify.h"
#include "time_math.h"

// ─────────────────────────────────────────────
//  Trạng thái hệ thống
// ─────────────────────────────────────────────
enum SystemState {
    ST_INIT,
    ST_TIME_SYNC,
    ST_IDLE,
    ST_FEEDING,
    ST_STALE_ALERT,
    ST_DISCARD,
    ST_JAM_ERROR,
    ST_BRIDGE_ERROR
};

static SystemState  state        = ST_INIT;

// ─────────────────────────────────────────────
//  Kiểm tra giới hạn trước khi nhả
// ─────────────────────────────────────────────
static bool canFeed(FeedSource src) {
    NVSData& d = nvsGet();

    uint32_t day = tkJulianDay();
    if (day > 0 && day != d.lastFeedDay) {
        d.dailyFeedCount = 0;
        d.dailyGrams     = 0;
        d.lastFeedDay    = day;
        nvsMark();
    }

    if (d.dailyFeedCount >= DAILY_MAX_FEEDS) return false;
    if (d.dailyGrams     >= DAILY_MAX_GRAMS) return false;
    return true;
}

static bool canFeedVision() {
    if (!tkTimeValid()) return false;
    int h = tkHour();
    if (h >= NO_FEED_HOUR_START || h <= NO_FEED_HOUR_END) return false;

    NVSData& d = nvsGet();
    uint32_t ep = tkEpoch();
    if (d.lastFeedEpoch > 0 &&
        (ep <= d.lastFeedEpoch || ep - d.lastFeedEpoch < FEED_COOLDOWN_S)) return false;
    if (getBowlGrams() >= BOWL_EMPTY_G) return false;
    return canFeed(SRC_CAMERA);
}

// ─────────────────────────────────────────────
//  Build JSON event
// ─────────────────────────────────────────────
static const char* feedSourceName(FeedSource src) {
    static const char* names[] = {"schedule","camera","manual","remote"};
    if ((int)src < 0 || (int)src >= (int)(sizeof(names)/sizeof(names[0]))) return "unknown";
    return names[src];
}

static const char* eventLabel(const char* type) {
    if (strcmp(type, "fed") == 0)            return "Da cho an";
    if (strcmp(type, "skipped") == 0)        return "Bo qua (bat con du)";
    if (strcmp(type, "jam") == 0)            return "LOI: Ket thuc an";
    if (strcmp(type, "bridge") == 0)         return "LOI: Hat khong xuong";
    if (strcmp(type, "timeout") == 0)        return "LOI: Qua thoi gian";
    if (strcmp(type, "not_eaten") == 0)      return "Thu cung chua an";
    if (strcmp(type, "hopper_low") == 0)     return "Thung sap het";
    if (strcmp(type, "humidity_high") == 0)  return "Do am cao";
    if (strcmp(type, "stale_warn") == 0)     return "Thuc an co the thiu";
    if (strcmp(type, "stale_discard") == 0)  return "Thuc an thiu - da xu ly";
    if (strcmp(type, "interrupted_feed") == 0) return "Mat dien khi dang nha";
    return type;
}

static const char* srcLabel(FeedSource src) {
    static const char* labels[] = {"lich hen", "camera", "nut bam", "app/web"};
    if ((int)src < 0 || (int)src >= (int)(sizeof(labels)/sizeof(labels[0]))) return "khac";
    return labels[src];
}

static void logEvent(const char* type, FeedSource src, float grams,
                     float score = 0, float ageH = 0, float hum = 0) {
    char buf[200];
    const char* srcName = feedSourceName(src);
    if (score > 0)
        snprintf(buf, sizeof(buf),
            "{\"t\":%lu,\"type\":\"%s\",\"src\":\"%s\",\"g\":%.1f,\"age_h\":%.1f,\"hum\":%.0f,\"score\":%.2f}",
            (unsigned long)tkEpoch(), type, srcName, grams, ageH, hum, score);
    else
        snprintf(buf, sizeof(buf),
            "{\"t\":%lu,\"type\":\"%s\",\"src\":\"%s\",\"g\":%.1f}",
            (unsigned long)tkEpoch(), type, srcName, grams);

    Serial.printf(">> %s | Nguon: %s", eventLabel(type), srcLabel(src));
    if (grams > 0) Serial.printf(" | %.1fg", grams);
    Serial.println();
    queuePush(buf);
    notifyEvent(buf);
}

// ─────────────────────────────────────────────
//  Publish feeding result qua MQTT
// ─────────────────────────────────────────────
static void publishFeedingResult(FeedSource src, FeedResult res, float actual) {
    char buf[200];
    const char* resStr[] = {"ok","jam","bridge","timeout"};
    const char* rName = ((int)res >= 0 && (int)res < (int)(sizeof(resStr)/sizeof(resStr[0]))) ? resStr[res] : "unknown";
    snprintf(buf, sizeof(buf),
        "{\"t\":%lu,\"src\":\"%s\",\"result\":\"%s\",\"actual_g\":%.1f}",
        (unsigned long)tkEpoch(), feedSourceName(src), rName, actual);
    if (notifyMqttConnected()) {
        // Dùng PubSubClient trực tiếp qua extern nếu cần,
        // hoặc đơn giản dùng notifyEvent
        notifyEvent(buf);
    }
}

// ─────────────────────────────────────────────
//  Thực hiện nhả
// ─────────────────────────────────────────────
static void doFeed(float targetGrams, FeedSource src, int schedIdx) {
    NVSData& d  = nvsGet();
    float    bowlNow = getBowlGrams();

    // Bát còn ≥50% → bỏ qua (chỉ cho lịch)
    if ((src == SRC_SCHEDULE || src == SRC_CAMERA) && bowlNow >= targetGrams * BOWL_SKIP_RATIO) {
        logEvent("skipped", src, 0);
        if (schedIdx >= 0) scheduleMarkFired(schedIdx);
        return;
    }

    // Chỉ nhả phần còn thiếu
    float needed = targetGrams - bowlNow;
    if (needed <= 0) {
        if (schedIdx >= 0) scheduleMarkFired(schedIdx);
        logEvent("skipped", src, 0);
        return;
    }
    if (needed > DAILY_MAX_GRAMS - d.dailyGrams) return;

    // Stale lock
    if (stalenessScore() >= STALE_SCORE_LOCK) {
        Serial.println(">> Khong nha: thuc an cu con trong bat (thiu)");
        logEvent("skipped", src, 0);
        return;
    }

    // Claim this meal persistently before starting the motor. A reboot or jam
    // must not cause an automatic retry of a possibly partially dispensed meal.
    if (schedIdx >= 0 && !scheduleMarkFired(schedIdx)) {
        Serial.println(">> Khong the luu trang thai bua an; huy");
        return;
    }
    state = ST_FEEDING;

    float actual = 0;
    FeedResult res = feederDispense(needed, actual);

    uint32_t ep = tkEpoch();
    d.lastFeedEpoch   = ep;
    // A failed attempt with 0g did not put fresh food into the bowl.
    // Keep the oldest known food timestamp when topping up an existing bowl.
    if (actual > 0 && (d.foodDispensedAt == 0 || bowlNow < 0.3f))
        d.foodDispensedAt = ep;
    d.dailyFeedCount++;
    d.dailyGrams += (uint16_t)(actual + 0.5f);
    nvsMark();
    nvsFlush(true);

    resetPetDetection();

    if (schedIdx >= 0) scheduleMarkFired(schedIdx);

    publishFeedingResult(src, res, actual);

    if (res == FEED_OK) {
        logEvent("fed", src, actual);
        digitalWrite(PIN_LED, HIGH);
        delay(500);
        digitalWrite(PIN_LED, LOW);
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "");
        state = ST_IDLE;
    } else if (res == FEED_JAM) {
        logEvent("jam", src, actual);
        notifyAlert("jam", "Ket thuc an! Kiem tra may.");
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "LOI: Ket thuc an");
        for (int i = 0; i < 5; i++) {
            digitalWrite(PIN_BUZZER, HIGH); delay(200);
            digitalWrite(PIN_BUZZER, LOW);  delay(200);
        }
        state = ST_JAM_ERROR;
    } else if (res == FEED_TIMEOUT) {
        logEvent("timeout", src, actual);
        notifyAlert("jam", "Qua thoi gian nha thuc an. Kiem tra may.");
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "LOI: Qua thoi gian");
        state = ST_JAM_ERROR;
    } else if (res == FEED_BRIDGE) {
        logEvent("bridge", src, actual);
        notifyAlert("bridge", "Hat khong xuong! Kiem tra thung.");
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "LOI: Hat khong xuong");
        for (int i = 0; i < 3; i++) {
            digitalWrite(PIN_BUZZER, HIGH); delay(300);
            digitalWrite(PIN_BUZZER, LOW);  delay(300);
        }
        state = ST_BRIDGE_ERROR;
    }
}

// ─────────────────────────────────────────────
//  Stale food check
// ─────────────────────────────────────────────
static uint32_t lastStaleCheckMs = 0;

static void checkStaleness() {
    uint32_t now = millis();
    if (now - lastStaleCheckMs < STALE_CHECK_MS) return;
    lastStaleCheckMs = now;

    float score = stalenessScore();
    dispState.staleScore = score;

    if (score < STALE_SCORE_WARN) return;
    if (!canAlert("stale")) return;

    NVSData& d  = nvsGet();
    float ageH  = (float)epochElapsed(tkEpoch(), d.foodDispensedAt) / 3600.0f;
    float hum   = getHumidity();

    if (AUTO_DISCARD_MODE == 2) {
        state = ST_DISCARD;
        logEvent("stale_discard", SRC_SCHEDULE, getBowlGrams(), score, ageH, hum);
        // Không có servo bát nữa — chỉ cảnh báo + khóa nhả
        d.foodDispensedAt = 0;
        nvsMark();
        markAlert("stale");
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "Thuc an thiu - da khoa");
        state = ST_IDLE;
    } else if (AUTO_DISCARD_MODE == 1) {
        state = ST_STALE_ALERT;
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "Nhan nut de xac nhan");
        digitalWrite(PIN_BUZZER, HIGH); delay(500); digitalWrite(PIN_BUZZER, LOW);
        markAlert("stale");
    } else {
        logEvent("stale_warn", SRC_SCHEDULE, 0, score, ageH, hum);
        notifyAlert("stale", "Thuc an co the da thiu! Kiem tra bat.");
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "! Thuc an thiu");
        digitalWrite(PIN_BUZZER, HIGH); delay(300); digitalWrite(PIN_BUZZER, LOW);
        markAlert("stale");
    }
}

// ─────────────────────────────────────────────
//  Kiểm tra cảm biến môi trường
// ─────────────────────────────────────────────
static uint32_t lastNotEatenCheckMs = 0;

static void checkEnvironment() {
    if (getHopperPct() < HOPPER_LOW_PCT && canAlert("hopper_low")) {
        logEvent("hopper_low", SRC_SCHEDULE, 0);
        notifyAlert("hopper_low", "Thuc an sap het! Bo sung them.");
        markAlert("hopper_low");
    }

    if (getHumidity() > HUM_HIGH_PCT && canAlert("humidity_high")) {
        logEvent("humidity_high", SRC_SCHEDULE, 0);
        notifyAlert("humidity_high", "Do am cao! Thay goi hut am.");
        markAlert("humidity_high");
    }

    uint32_t now = millis();
    if (now - lastNotEatenCheckMs > 1800000UL) {
        lastNotEatenCheckMs = now;
        NVSData& d = nvsGet();
        if (d.foodDispensedAt > 0 && tkTimeValid()) {
            float ageH = (float)epochElapsed(tkEpoch(), d.foodDispensedAt) / 3600.0f;
            if (ageH >= NOT_EATEN_H && getBowlGrams() > BOWL_EMPTY_G &&
                canAlert("not_eaten")) {
                logEvent("not_eaten", SRC_SCHEDULE, getBowlGrams());
                notifyAlert("not_eaten", "Thu cung chua an! Kiem tra suc khoe.");
                markAlert("not_eaten");
            }
        }
    }
}

// ─────────────────────────────────────────────
//  Publish sensor state định kỳ
// ─────────────────────────────────────────────
static uint32_t lastStatePublishMs = 0;

static uint32_t lastStatusPrintMs = 0;

static void publishStatePeriodic() {
    uint32_t now = millis();
    if (now - lastStatePublishMs < 5000UL) return;
    lastStatePublishMs = now;
    notifyPublishState();

    if (now - lastStatusPrintMs >= 10000UL) {
        lastStatusPrintMs = now;
        Serial.printf("-- Bat: %.0fg | Thung: %d%% | Am: %.0f%% | Nhiet: %.1fC",
            getBowlGrams(), getHopperPct(), getHumidity(), getTemperature());
        if (notifyMqttConnected())
            Serial.print(" | MQTT: OK");
        else
            Serial.print(" | MQTT: Mat ket noi");
        if (dispState.cooldownSec > 0) {
            uint32_t s = dispState.cooldownSec;
            Serial.printf(" | Cho %um%us nua", (unsigned)(s/60), (unsigned)(s%60));
        }
        Serial.println();
    }
}

// ─────────────────────────────────────────────
//  Cập nhật DisplayState
// ─────────────────────────────────────────────
static void updateDisplay() {
    int h = tkHour(), m = tkMinute(), s = tkSecond();
    if (h >= 0)
        snprintf(dispState.timeStr, sizeof(dispState.timeStr),
                 "%02d:%02d:%02d", h, m, s);
    else
        strncpy(dispState.timeStr, "--:--:--", sizeof(dispState.timeStr));

    dispState.wifiOK        = (WiFi.status() == WL_CONNECTED);
    dispState.mqttOK        = notifyMqttConnected();
    dispState.bowlGrams     = getBowlGrams();
    dispState.hopperPct     = getHopperPct();
    dispState.humidity      = getHumidity();
    dispState.staleScore    = stalenessScore();

    NVSData& d = nvsGet();
    uint32_t ep = tkEpoch();
    if (ep > 0 && d.lastFeedEpoch > 0) {
        uint32_t elapsed = epochElapsed(ep, d.lastFeedEpoch);
        dispState.cooldownSec = (elapsed < FEED_COOLDOWN_S)
                                 ? (FEED_COOLDOWN_S - elapsed) : 0;
    } else {
        dispState.cooldownSec = 0;
    }

    int nh = -1, nm = -1; float ng = 0;
    if (scheduleNextMeal(nh, nm, ng)) {
        dispState.nextMealH = nh;
        dispState.nextMealM = nm;
        dispState.nextMealG = ng;
    } else {
        dispState.nextMealH = -1;
    }
}

// ─────────────────────────────────────────────
//  WiFi — kết nối không blocking
// ─────────────────────────────────────────────
static uint32_t wifiRetryMs  = 0;
static uint32_t wifiRetryS   = WIFI_RETRY_BASE_S;

static void wifiTask() {
    if (!USE_WIFI) return;
    if (WiFi.status() == WL_CONNECTED) {
        wifiRetryS = WIFI_RETRY_BASE_S;
        return;
    }
    uint32_t now = millis();
    if (now - wifiRetryMs < wifiRetryS * 1000UL) return;
    wifiRetryMs = now;

#if WOKWI_SIM
    WiFi.begin("Wokwi-GUEST", "");
#else
    WiFi.begin();
#endif

    Serial.printf(">> WiFi: Dang ket noi... thu lai sau %lus\r\n", wifiRetryS);
    wifiRetryS = min(wifiRetryS * 2, (uint32_t)WIFI_RETRY_MAX_S);
}

// ─────────────────────────────────────────────
//  setup() / loop()
// ─────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    Serial.println("\n========================================");
    Serial.println("  May cho thu cung an tu dong v3.0");
    Serial.println("========================================");

    pinMode(PIN_BUZZER, OUTPUT);
    pinMode(PIN_LED,    OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
    digitalWrite(PIN_LED,    LOW);

    storageInit();
    displayInit();

    // Kiểm tra mất điện giữa nhả
    NVSData& d = nvsGet();
    if (strcmp(d.feedState, "dispensing") == 0) {
        Serial.printf("!! Phat hien mat dien khi dang nha %.1fg!\r\n", d.feedTarget);
        logEvent("interrupted_feed", SRC_SCHEDULE, d.feedTarget);
        strncpy(d.feedState, "done", sizeof(d.feedState) - 1);
        nvsMark(); nvsFlush(true);
        snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "! Mat dien khi nha");
    }

    timekeeperInit();
    sensorsInit();
    feederInit();
    scheduleInit();
    queueInit();
    notifyInit();

#if USE_WIFI && WOKWI_SIM
    WiFi.begin("Wokwi-GUEST", "");
#elif USE_WIFI
    WiFi.mode(WIFI_STA);
    WiFi.begin();
#endif

    state = ST_TIME_SYNC;
    Serial.println(">> He thong san sang!");
}

void loop() {
    // ── Luôn chạy dù có mạng hay không ──────
    sensorsLoop();
    scheduleLoop();
    timekeeperLoop();
    nvsFlush();

#if USE_WIFI
    wifiTask();
#endif
    notifyLoop();
    publishStatePeriodic();

    // ── State machine ────────────────────────
    switch (state) {

        case ST_INIT:
            state = ST_TIME_SYNC;
            break;

        case ST_TIME_SYNC:
            if (tkTimeValid()) state = ST_IDLE;
            break;

        case ST_IDLE: {
            updateDisplay();
            displayLoop();
            checkStaleness();
            checkEnvironment();

            // 1. Kiểm tra lịch
            int idx = scheduleCheck();
            if (idx >= 0 && isPetPresent() && canFeedVision()) {
                Meal* meals = scheduleGet();
                doFeed(meals[idx].grams, SRC_CAMERA, idx);
                break;
            }

            // 2. Camera RPi phát hiện thú cưng qua MQTT
            // Camera presence alone never authorizes a meal outside its window.

            // 3. Nút thủ công
            if (isButtonPressed() && canFeed(SRC_MANUAL)) {
                Meal* m = scheduleGet();
                float portion = (m[0].enabled && m[0].grams > 0) ? m[0].grams : DEFAULT_PORTION_G;
                doFeed(portion, SRC_MANUAL, idx);
                break;
            }

            // 4. Lệnh feed từ xa (app/server qua MQTT)
            if (notifyHasPendingFeed() && canFeed(SRC_REMOTE)) {
                float g = notifyGetPendingGrams();
                notifyClearPendingFeed();
                doFeed(g, SRC_REMOTE, idx);
                break;
            }

            break;
        }

        case ST_STALE_ALERT:
            updateDisplay();
            displayLoop();
            if (isButtonPressed()) {
                state = ST_DISCARD;
            }
            break;

        case ST_DISCARD: {
            NVSData& d = nvsGet();
            float g    = getBowlGrams();
            float ageH = (d.foodDispensedAt > 0)
                         ? (float)epochElapsed(tkEpoch(), d.foodDispensedAt) / 3600.0f : 0;
            logEvent("stale_discard", SRC_MANUAL, g,
                     stalenessScore(), ageH, getHumidity());
            d.foodDispensedAt = 0;
            nvsMark();
            snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "Thuc an thiu - xac nhan");
            resetPetDetection();
            state = ST_IDLE;
            break;
        }

        case ST_JAM_ERROR:
        case ST_BRIDGE_ERROR:
            updateDisplay();
            displayLoop();
            if (isButtonPressed()) {
                snprintf(dispState.errorMsg, sizeof(dispState.errorMsg), "");
                state = ST_IDLE;
            }
            break;

        default:
            break;
    }
}
