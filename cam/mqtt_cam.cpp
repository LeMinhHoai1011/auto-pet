#include "mqtt_cam.h"
#include "config.h"
#include "secrets.h"

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

static WiFiClient   camWifi;
static PubSubClient mqtt(camWifi);

void mqttCamInit() {
    mqtt.setServer(MQTT_HOST, MQTT_PORT);
    mqtt.setBufferSize(256);
}

bool mqttCamPublish(const char* petLabel, float confidence) {
    if (WiFi.status() != WL_CONNECTED) return false;

    // Kết nối MQTT (đồng bộ, 1 lần duy nhất mỗi wake cycle)
    if (!mqtt.connected()) {
        if (!mqtt.connect("esp32cam-01", MQTT_USER, MQTT_PASS)) {
            Serial.printf("[MQTT-CAM] Connect failed rc=%d\n", mqtt.state());
            return false;
        }
    }

    JsonDocument doc;
    doc["detected"]   = true;
    doc["pet"]        = petLabel;
    doc["confidence"] = confidence;
    // No calibrated waiting-zone detector exists yet. Motion/classification
    // alone cannot authorize feeding.
    doc["in_zone"] = false;
    doc["src"]        = "esp32cam";

    char buf[128];
    serializeJson(doc, buf, sizeof(buf));

    bool ok = mqtt.publish(MQTT_VISION_PET, buf);
    mqtt.loop();
    delay(50);

    Serial.printf("[MQTT-CAM] %s → %s\n", ok ? "OK" : "FAIL", buf);

    mqtt.disconnect();
    return ok;
}
