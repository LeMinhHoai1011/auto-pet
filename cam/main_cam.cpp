#include <Arduino.h>
#include <WiFi.h>
#include <esp_camera.h>
#include <esp_sleep.h>

#include "config_cam.h"
#include "camera_pins.h"
#include "pet_detect.h"
#include "mqtt_cam.h"
#include "config.h"
#include "secrets.h"

// ─────────────────────────────────────────────
//  Camera init — AI-Thinker ESP32-CAM + OV2640
// ─────────────────────────────────────────────
static bool cameraInit() {
    camera_config_t cfg = {};
    cfg.ledc_channel = LEDC_CHANNEL_0;
    cfg.ledc_timer   = LEDC_TIMER_0;
    cfg.pin_d0       = Y2_GPIO_NUM;
    cfg.pin_d1       = Y3_GPIO_NUM;
    cfg.pin_d2       = Y4_GPIO_NUM;
    cfg.pin_d3       = Y5_GPIO_NUM;
    cfg.pin_d4       = Y6_GPIO_NUM;
    cfg.pin_d5       = Y7_GPIO_NUM;
    cfg.pin_d6       = Y8_GPIO_NUM;
    cfg.pin_d7       = Y9_GPIO_NUM;
    cfg.pin_xclk     = XCLK_GPIO_NUM;
    cfg.pin_pclk     = PCLK_GPIO_NUM;
    cfg.pin_vsync    = VSYNC_GPIO_NUM;
    cfg.pin_href     = HREF_GPIO_NUM;
    cfg.pin_sccb_sda = SIOD_GPIO_NUM;
    cfg.pin_sccb_scl = SIOC_GPIO_NUM;
    cfg.pin_pwdn     = PWDN_GPIO_NUM;
    cfg.pin_reset    = RESET_GPIO_NUM;
    cfg.xclk_freq_hz = 20000000;
    cfg.pixel_format = PIXFORMAT_RGB565;
    cfg.frame_size   = FRAMESIZE_QQVGA;    // 160x120
    cfg.jpeg_quality = 12;
    cfg.fb_count     = 1;
    cfg.fb_location  = CAMERA_FB_IN_PSRAM;
    cfg.grab_mode    = CAMERA_GRAB_LATEST;

    esp_err_t err = esp_camera_init(&cfg);
    if (err != ESP_OK) {
        Serial.printf("[CAM] Init failed: 0x%x\n", err);
        return false;
    }

    // Tắt flash LED
    pinMode(PIN_FLASH_LED, OUTPUT);
    digitalWrite(PIN_FLASH_LED, LOW);

    Serial.println("[CAM] Camera ready (QQVGA 160x120 RGB565)");
    return true;
}

// ─────────────────────────────────────────────
//  WiFi — kết nối nhanh, timeout ngắn
// ─────────────────────────────────────────────
static bool wifiConnect() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > CAM_WIFI_TIMEOUT_MS) {
            Serial.println("[WIFI-CAM] Timeout");
            return false;
        }
        delay(200);
    }
    Serial.printf("[WIFI-CAM] Connected in %lums\n", millis() - start);
    return true;
}

// ─────────────────────────────────────────────
//  Đi ngủ
// ─────────────────────────────────────────────
static void goToSleep(uint64_t sleepUs) {
    esp_camera_deinit();
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);

    // PIR wake-up trên GPIO13 (HIGH = có chuyển động)
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_PIR_WAKE, 1);
    esp_sleep_enable_timer_wakeup(sleepUs);

    Serial.printf("[CAM] Sleep %llus...\n", sleepUs / 1000000ULL);
    Serial.flush();

    esp_deep_sleep_start();
}

// ─────────────────────────────────────────────
//  SETUP — chạy mỗi lần thức dậy
// ─────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    delay(100);

    esp_sleep_wakeup_cause_t reason = esp_sleep_get_wakeup_cause();
    bool pirWake = (reason == ESP_SLEEP_WAKEUP_EXT0);
    Serial.printf("\n[CAM] Boot — wake reason: %d (%s)\n",
                  reason, pirWake ? "PIR" : "timer/reset");

    // Chỉ xử lý khi PIR kích hoạt hoặc lần đầu boot
    if (reason == ESP_SLEEP_WAKEUP_TIMER) {
        Serial.println("[CAM] Timer wake — no motion, sleeping...");
        // Vẫn cấu hình PIR wake rồi ngủ lại
        esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_PIR_WAKE, 1);
        esp_sleep_enable_timer_wakeup(SLEEP_NO_MOTION_US);
        Serial.flush();
        esp_deep_sleep_start();
        return;
    }

    // ── Camera init ─────────────────────────
    if (!cameraInit()) {
        goToSleep(SLEEP_NO_MOTION_US);
        return;
    }

    // Bỏ 3 frame đầu (auto-exposure chưa ổn)
    for (int i = 0; i < 3; i++) {
        camera_fb_t* fb = esp_camera_fb_get();
        if (fb) esp_camera_fb_return(fb);
        delay(100);
    }

    // ── Nhận diện ───────────────────────────
    if (!petDetectInit()) {
        goToSleep(SLEEP_NO_MOTION_US);
        return;
    }

    bool petFound = false;
    float bestConf = 0;
    const char* bestLabel = "none";
    int votes = 0;

    for (int i = 0; i < CAPTURE_FRAMES; i++) {
        camera_fb_t* fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("[CAM] Capture failed");
            continue;
        }

        PetResult r = petDetectRun(fb->buf, fb->len, fb->width, fb->height);
        esp_camera_fb_return(fb);

        if (r.detected) {
            votes++;
            if (r.confidence > bestConf) {
                bestConf  = r.confidence;
                bestLabel = r.label;
            }
        }
        delay(80);
    }

    petFound = (votes >= CAPTURE_VOTE_MIN);

    Serial.printf("[CAM] Result: %s (votes=%d/%d, conf=%.0f%%)\n",
                  petFound ? bestLabel : "none",
                  votes, CAPTURE_FRAMES, bestConf * 100);

    // ── Gửi MQTT nếu phát hiện ─────────────
    if (petFound) {
        if (wifiConnect()) {
            mqttCamInit();
            mqttCamPublish(bestLabel, bestConf);
        }
        goToSleep(SLEEP_AFTER_DETECT_US);
    } else {
        goToSleep(SLEEP_NO_MOTION_US);
    }
}

void loop() {
    // Không bao giờ chạy tới đây — deep sleep reset CPU
}
