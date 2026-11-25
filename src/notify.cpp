#include "notify.h"
#include "config.h"
#include "storage.h"
#include "sensors.h"
#include "timekeeper.h"
#include "schedule.h"
#include <math.h>

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

static WiFiClient   mqttWiFi;
static PubSubClient mqtt(mqttWiFi);
static uint32_t     mqttLastRetryMs = 0;
static uint32_t     mqttRetryS      = 5;

// Lệnh feed từ xa (MQTT command hoặc app)
static bool  pendingFeed   = false;
static float pendingGrams  = 0;
static float pendingPetGrams = 0;
static uint32_t pendingPetUntil = 0;
static uint32_t pendingPetReceivedMs = 0;
static char pendingPetId[64] = {};
static char lastPetId[64] = {};

#include "secrets.h"

#if WOKWI_SIM
// Docker broker on the computer running the Wokwi private gateway.
static const char* const mqttHost = "host.wokwi.internal";
static const int mqttPort = WOKWI_MQTT_PORT;
#else
static const char* const mqttHost = MQTT_HOST;
static const int mqttPort = MQTT_PORT;
#endif

// ─────────────────────────────────────────────
//  MQTT callback — nhận lệnh từ RPi / Server / App
// ─────────────────────────────────────────────
static void mqttCallback(char* topic, byte* payload, unsigned int len) {
    char buf[1024];
    if (len >= sizeof(buf)) return;
    memcpy(buf, payload, len);
    buf[len] = '\0';

    Serial.printf(">> Nhan lenh: %s\r\n", buf);

    // ── RPi gửi pet detected ────────────────
    // topic: petfeeder/device01/vision/pet_detected
    // payload: {"detected":true,"pet":"dog","confidence":0.92}
    if (strstr(topic, "vision/pet_detected")) {
        JsonDocument doc;
        if (deserializeJson(doc, buf) == DeserializationError::Ok) {
            const char* pet = doc["pet"] | "";
            float confidence = doc["confidence"] | 0.0f;
            bool detected = (doc["detected"] | false) &&
                (doc["in_zone"] | false) &&
                (strcmp(pet, "cat") == 0 || strcmp(pet, "dog") == 0) &&
                isfinite(confidence) && confidence >= PET_MIN_CONFIDENCE && confidence <= 1;
            setPetDetected(detected);
        } else {
            resetPetDetection();
        }
        return;
    }

    // ── Lệnh feed từ server/app ─────────────
    // topic: petfeeder/device01/command
    // payload: {"command":"FEED","amount":80}
    //          {"command":"SCHEDULE","meals":[...]}
    //          {"command":"TARE"}
    //          {"command":"STATUS"}
    if (strstr(topic, "command")) {
        JsonDocument doc;
        if (deserializeJson(doc, buf) != DeserializationError::Ok) return;

        const char* cmd = doc["cmd"] | doc["command"] | "";

        if (strcmp(cmd, "FEED") == 0) {
            float g = doc["g"] | doc["amount"] | DEFAULT_PORTION_G;
            if (g >= 1 && g <= DAILY_MAX_GRAMS) {
                pendingFeed  = true;
                pendingGrams = g;
            }
        } else if (strcmp(cmd, "PET_FEED") == 0) {
            const char* id = doc["id"] | "";
            float g = doc["g"] | 0.0f;
            uint32_t until = doc["until"] | 0UL;
            if (strlen(id) != 32 || strspn(id, "0123456789abcdef") != 32) {
                Serial.println(">> PET_FEED bo qua: invalid_id");
                return;
            }
            if (strcmp(id, lastPetId) == 0 || strcmp(id, pendingPetId) == 0) {
                Serial.println(">> PET_FEED bo qua: duplicate");
                return;
            }
            if (pendingPetId[0] || g < 1 || g > DAILY_MAX_GRAMS || !isfinite(g) || !until) {
                notifyPetFeedResult(id, 0, pendingPetId[0] ? "busy" : "invalid_request");
                return;
            }
#if !WOKWI_SIM
            uint32_t now = tkEpoch();
            if (!tkTimeValid() || until < now || until - now > 15) {
                Serial.printf(">> PET_FEED UTC: ESP32=%lu until=%lu\r\n",
                              (unsigned long)now, (unsigned long)until);
                notifyPetFeedResult(id, 0, "clock_or_expiry");
                return;
            }
#endif
            strlcpy(pendingPetId, id, sizeof(pendingPetId));
            pendingPetGrams = g;
            pendingPetUntil = until;
            pendingPetReceivedMs = millis();
            Serial.printf(">> PET_FEED da xep hang: %.1fg\r\n", g);
        } else if (strcmp(cmd, "SCHEDULE") == 0) {
            JsonArrayConst incoming = doc["meals"].as<JsonArrayConst>();
            if (incoming.isNull() || incoming.size() > MAX_MEALS) return;
            Meal updated[MAX_MEALS] = {};
            int count = 0;
            // Validate the entire replacement before changing live state.
            for (JsonObjectConst item : incoming) {
                if (!item["h"].is<int>() || !item["m"].is<int>() ||
                    !item["g"].is<float>()) return;
                int h = item["h"], m = item["m"];
                float g = item["g"];
                if (h < 0 || h > 23 || m < 0 || m > 59 ||
                    !isfinite(g) || g < 1 || g > DAILY_MAX_GRAMS) return;
                updated[count++] = {(uint8_t)h, (uint8_t)m, g, true};
            }
            scheduleReplace(updated);
            Serial.printf(">> Lich an: cap nhat %d cua an\r\n", count);
        } else if (strcmp(cmd, "TARE") == 0) {
            tareBowl();
        } else if (strcmp(cmd, "STATUS") == 0) {
            notifyPublishState();
        }
    }
}

// ─────────────────────────────────────────────
//  MQTT connect
// ─────────────────────────────────────────────
static void mqttConnect() {
    if (WiFi.status() != WL_CONNECTED) return;
    uint32_t now = millis();
    if (now - mqttLastRetryMs < mqttRetryS * 1000UL) return;
    mqttLastRetryMs = now;

    if (mqtt.connect(MQTT_DEVICE_ID, MQTT_USER, MQTT_PASS,
                     MQTT_PUB_STATUS, 0, true, "offline")) {
        resetPetDetection();
        Serial.println(">> MQTT: Da ket noi thanh cong");
        mqttRetryS = 5;

        // Online
        mqtt.publish(MQTT_PUB_STATUS, "online", true);

        // Subscribe lệnh từ server/app
        char sub1[80];
        snprintf(sub1, sizeof(sub1), "%scommand", MQTT_TOPIC_PREFIX);
        mqtt.subscribe(sub1);

        // Subscribe vision từ RPi
        char sub2[80];
        snprintf(sub2, sizeof(sub2), "%svision/#", MQTT_TOPIC_PREFIX);
        mqtt.subscribe(sub2);

        notifyPublishState();

        Serial.println(">> MQTT: Dang lang nghe lenh tu server/app");
    } else {
        Serial.printf(">> MQTT: Loi ket noi (ma=%d). Thu lai sau %lus\r\n",
                      mqtt.state(), mqttRetryS);
        mqttRetryS = min(mqttRetryS * 2, (uint32_t)300);
    }
}

// ─────────────────────────────────────────────
//  Flush offline queue
// ─────────────────────────────────────────────
static void flushQueue() {
    if (!mqtt.connected()) return;
    if (!queueHasData()) return;

    String lines[16];
    int count = 0;
    String line;
    while (count < 16 && (line = queuePop()).length() > 0) {
        lines[count++] = line;
    }
    for (int i = 0; i < count; i++) {
        mqtt.publish(MQTT_PUB_EVENT, lines[i].c_str());
        delay(10);
    }
}

// ─────────────────────────────────────────────
//  Public API
// ─────────────────────────────────────────────
void notifyInit() {
    mqtt.setServer(mqttHost, mqttPort);
    Serial.printf(">> MQTT Broker: %s:%d\r\n", mqttHost, mqttPort);
    mqtt.setCallback(mqttCallback);
    mqtt.setBufferSize(1152);
}

void notifyLoop() {
    if (!mqtt.connected()) mqttConnect();
    if (mqtt.connected()) {
        mqtt.loop();
        flushQueue();
    }
}

void notifyEvent(const char* jsonStr) {
    if (mqtt.connected()) {
        mqtt.publish(MQTT_PUB_EVENT, jsonStr);
    }
}

void notifyAlert(const char* alertType, const char* message) {
    char jsonStr[256];
    snprintf(jsonStr, sizeof(jsonStr),
        "{\"t\":%lu,\"type\":\"%s\",\"msg\":\"%s\"}",
        (unsigned long)tkEpoch(), alertType, message);

    Serial.printf("!! CANH BAO: %s - %s\r\n", alertType, message);
    queuePush(jsonStr);

    if (mqtt.connected()) {
        mqtt.publish(MQTT_PUB_ALERT, jsonStr);
    }
}

void notifyPublishState() {
    if (!mqtt.connected()) return;

    // Weight
    char buf[128];
    snprintf(buf, sizeof(buf), "{\"bowl_g\":%.1f}", getBowlGrams());
    mqtt.publish(MQTT_PUB_SENSOR, buf);

    // Hopper
    snprintf(buf, sizeof(buf), "{\"hopper_pct\":%d}", getHopperPct());
    mqtt.publish(MQTT_PUB_HOPPER, buf);

    // Environment
    snprintf(buf, sizeof(buf), "{\"humidity\":%.1f,\"temp\":%.1f}",
             getHumidity(), getTemperature());
    mqtt.publish(MQTT_PUB_ENV, buf);
}

bool  notifyHasPendingFeed()   { return pendingFeed; }
float notifyGetPendingGrams()  { return pendingGrams; }
void  notifyClearPendingFeed() { pendingFeed = false; pendingGrams = 0; }

bool notifyTakePetFeed(float& grams, char (&requestId)[64]) {
    if (!pendingPetId[0]) return false;
    strlcpy(requestId, pendingPetId, sizeof(requestId));
    pendingPetId[0] = '\0';
    bool expired = millis() - pendingPetReceivedMs > 10000UL;
#if !WOKWI_SIM
    expired = expired || !tkTimeValid() || tkEpoch() > pendingPetUntil;
#endif
    if (expired) {
        notifyPetFeedResult(requestId, 0, "expired_in_queue");
        return false;
    }
    strlcpy(lastPetId, requestId, sizeof(lastPetId));
    grams = pendingPetGrams;
    return true;
}

void notifyPetFeedResult(const char* requestId, float actualGrams, const char* reason) {
    char buf[192];
    snprintf(buf, sizeof(buf),
             "{\"type\":\"pet_feed_result\",\"id\":\"%s\",\"actual_g\":%.1f,\"reason\":\"%s\"}",
             requestId, actualGrams, reason);
    Serial.printf(">> PET_FEED %s: %s (%.1fg)\r\n", requestId, reason, actualGrams);
    notifyEvent(buf);
}

bool notifyMqttConnected() { return mqtt.connected(); }
