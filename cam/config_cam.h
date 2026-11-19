#pragma once

// ─────────────────────────────────────────────
//  ESP32-CAM — Cấu hình riêng module camera
// ─────────────────────────────────────────────

// PIR wake-up (GPIO13 — dùng chung HSYNC camera, an toàn khi deep sleep)
#define PIN_PIR_WAKE            13
#define PIN_FLASH_LED            4

// Deep sleep
#define SLEEP_NO_MOTION_US      (60ULL * 1000000ULL)   // 60s nếu không có PIR
#define SLEEP_AFTER_DETECT_US   (10ULL * 1000000ULL)   // 10s sau khi detect (chống spam)

// Nhận diện
#define PET_CONFIDENCE_MIN      0.70f
#define CAPTURE_FRAMES          3       // chụp N frame, vote đa số
#define CAPTURE_VOTE_MIN        2       // cần >= 2/3 frame có pet

// WiFi timeout khi kết nối để gửi MQTT
#define CAM_WIFI_TIMEOUT_MS     10000

// Frame differencing (khi không có TFLite model)
#define MOTION_PIXEL_THRESH     30      // chênh lệch pixel coi là thay đổi
#define MOTION_AREA_PCT         8       // % diện tích thay đổi → có chuyển động

// Model input (khi dùng TFLite)
#define MODEL_INPUT_W           96
#define MODEL_INPUT_H           96
#define MODEL_INPUT_CH          1       // grayscale

// Số class output
#define CLASS_BACKGROUND        0
#define CLASS_CAT               1
#define CLASS_DOG               2
#define NUM_CLASSES             3
