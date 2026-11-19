#pragma once
#include <Arduino.h>

// ─────────────────────────────────────────────
//  CHÂN GPIO — STEPPER + ENCODER
// ─────────────────────────────────────────────
#define PIN_STEP         13   // A4988 STEP
#define PIN_DIR          27   // A4988 DIR
#define PIN_EN           25   // A4988 ENABLE (LOW = on)
#define PIN_ENC_A        34   // Encoder channel A (interrupt)
#define PIN_ENC_B        35   // Encoder channel B (interrupt)

// ─────────────────────────────────────────────
//  CHÂN GPIO — CẢM BIẾN
// ─────────────────────────────────────────────
#define PIN_HX711_DT     16
#define PIN_HX711_SCK     4
#define PIN_TRIG          5   // HC-SR04
#define PIN_ECHO         18
#define PIN_DHT          15

// ─────────────────────────────────────────────
//  CHÂN GPIO — TƯƠNG TÁC
// ─────────────────────────────────────────────
#define PIN_BUTTON       32   // INPUT_PULLUP
#define PIN_BUZZER       23
#define PIN_LED           2
#define PIN_SDA          21
#define PIN_SCL          22

// ─────────────────────────────────────────────
//  CỜ BẬT/TẮT MODULE
// ─────────────────────────────────────────────
#define USE_WIFI          1
#define WOKWI_SIM         1   // 1: WiFi "Wokwi-GUEST", bỏ WiFiManager
// Manual HX711 testing: delay jam/bridge checks, still stop at target or timeout.
#define WOKWI_FEED_GRACE_MS 30000UL

// ─────────────────────────────────────────────
//  CHẾ ĐỘ XỬ LÝ THỨC ĂN THIU
// ─────────────────────────────────────────────
// 0 = chỉ cảnh báo (alert only)
// 1 = cảnh báo + chờ nút xác nhận
// 2 = tự động đổ
#define AUTO_DISCARD_MODE 0

// ─────────────────────────────────────────────
//  LỊCH ĂN
// ─────────────────────────────────────────────
#define MAX_MEALS         6
#define DEFAULT_PORTION_G 30.0f
#define DAILY_MAX_FEEDS   6
#define DAILY_MAX_GRAMS   150

// ─────────────────────────────────────────────
//  COOLDOWN & PHÁT HIỆN
// ─────────────────────────────────────────────
#define FEED_COOLDOWN_S   7200   // 2 tiếng (epoch-based)
#define VISION_CONFIRM_FRAMES 5  // RPi phải gửi N khung hình liên tiếp có pet
#define PET_WAIT_MS           5000
#define PET_OBSERVATION_GAP_MS 1500
#define PET_OBSERVATION_TTL_MS 1500
#define PET_MIN_CONFIDENCE    0.70f
#define MEAL_WINDOW_MINUTES   30
#define BOWL_EMPTY_G      5.0f   // dưới ngưỡng = bát gần hết
#define BOWL_SKIP_RATIO   0.5f   // còn ≥50% khẩu phần → bỏ qua cữ
#define NO_FEED_HOUR_START 23
#define NO_FEED_HOUR_END    5

// ─────────────────────────────────────────────
//  THỨC ĂN THIU (STALE FOOD)
// ─────────────────────────────────────────────
#define STALE_BASE_H      12.0f
#define STALE_HUM60_H      8.0f
#define STALE_HUM70_H      4.0f
#define STALE_TEMP30_MULT  0.75f
#define STALE_SCORE_WARN   1.0f
#define STALE_SCORE_LOCK   1.5f
#define STALE_CHECK_MS    (30UL * 60 * 1000)
#define NOT_EATEN_H        4

// ─────────────────────────────────────────────
//  CẢM BIẾN NGƯỠNG
// ─────────────────────────────────────────────
#define HOPPER_LOW_PCT    20
#define HOPPER_HEIGHT_CM  20.0f
#define HUM_HIGH_PCT      70
#define ALERT_COOLDOWN_S  21600  // 1 cảnh báo / 6 tiếng

// ─────────────────────────────────────────────
//  STEPPER & NHẢ THỨC ĂN
// ─────────────────────────────────────────────
#define STEPPER_MAX_SPEED    800    // steps/sec
#define STEPPER_ACCEL        400    // steps/sec^2
#define STEPPER_STEPS_PER_DOSE 200  // steps mỗi đợt nhả
#define STEPPER_DOSE_PAUSE_MS 300   // nghỉ giữa đợt để cân ổn định
#define STEPPER_REVERSE_STEPS 100   // steps đảo chiều khi kẹt

#define JAM_THRESHOLD_G   0.5f  // tăng < 0.5g/đợt = nghi kẹt
#define JAM_DOSES          3    // N đợt liên tiếp không tăng → kẹt
#define ENC_MIN_PULSES     10   // encoder phải đếm >= N xung/đợt, dưới = trục không quay

#define LOADCELL_CALIBRATION 420.0f

// ─────────────────────────────────────────────
//  LỌC NHIỄU LOADCELL
// ─────────────────────────────────────────────
#define LC_FILTER_SIZE      7
#define LC_SPIKE_G          15.0f
#define LC_STABLE_COUNT     3
#define LC_STABLE_DELTA_G   2.0f
#define LC_READ_INTERVAL_MS 200

// ─────────────────────────────────────────────
//  AUTO-TARE LOADCELL
// ─────────────────────────────────────────────
#define TARE_BOWL_THRESHOLD  1.0f
#define TARE_INTERVAL_S     600

// ─────────────────────────────────────────────
//  NVS / LittleFS
// ─────────────────────────────────────────────
#define NVS_WRITE_INTERVAL_S 60
#define QUEUE_FILE      "/queue.log"
#define QUEUE_MAX_BYTES 51200
#define QUEUE_MAX_EVENTS 50

// ─────────────────────────────────────────────
//  WIFI / MQTT
// ─────────────────────────────────────────────
#define WIFI_RETRY_BASE_S   5
#define WIFI_RETRY_MAX_S   300
#define MQTT_DEVICE_ID     "device01"
#define MQTT_TOPIC_PREFIX  "petfeeder/" MQTT_DEVICE_ID "/"

// MQTT topics nhận lệnh từ RPi / Server
#define MQTT_CMD_FEED      MQTT_TOPIC_PREFIX "command"
#define MQTT_VISION_PET    MQTT_TOPIC_PREFIX "vision/pet_detected"

// MQTT topics gửi đi
#define MQTT_PUB_STATUS    MQTT_TOPIC_PREFIX "status"
#define MQTT_PUB_EVENT     MQTT_TOPIC_PREFIX "event"
#define MQTT_PUB_SENSOR    MQTT_TOPIC_PREFIX "sensor/weight"
#define MQTT_PUB_HOPPER    MQTT_TOPIC_PREFIX "sensor/food_level"
#define MQTT_PUB_ENV       MQTT_TOPIC_PREFIX "sensor/env"
#define MQTT_PUB_FEEDING   MQTT_TOPIC_PREFIX "feeding"
#define MQTT_PUB_ALERT     MQTT_TOPIC_PREFIX "alert"

// ─────────────────────────────────────────────
//  TIMEOUT CHỜ CÂN ỔN ĐỊNH
// ─────────────────────────────────────────────
#define WEIGH_STABLE_TIMEOUT_MS 5000  // ms chờ cân ổn định trước khi timeout

// ─────────────────────────────────────────────
//  TIMEZONE & NTP
// ─────────────────────────────────────────────
#define NTP_SERVER    "pool.ntp.org"
#define GMT_OFFSET_S  25200       // GMT+7
#define DST_OFFSET_S  0
