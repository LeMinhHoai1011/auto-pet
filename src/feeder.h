#pragma once
#include <Arduino.h>

enum FeedResult {
    FEED_OK,
    FEED_JAM,         // encoder OK nhưng loadcell không tăng, hoặc encoder không quay
    FEED_BRIDGE,      // trục quay mà loadcell = 0 (hạt không xuống)
    FEED_TIMEOUT      // cân không ổn định quá thời gian chờ
};

enum FeedSource {
    SRC_SCHEDULE,
    SRC_CAMERA,    // RPi camera detection qua MQTT
    SRC_MANUAL,
    SRC_REMOTE     // lệnh từ app/server qua MQTT
};

void       feederInit();
FeedResult feederDispense(float targetGrams, float& actualGrams);
bool       feederIsBusy();

// Encoder — gọi từ ISR, đọc từ feeder
volatile long encoderGetCount();
void         encoderResetCount();
