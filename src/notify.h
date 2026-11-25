#pragma once
#include <Arduino.h>

void notifyInit();
void notifyLoop();

// Gửi JSON event lên MQTT
void notifyEvent(const char* jsonStr);

// Gửi cảnh báo
void notifyAlert(const char* alertType, const char* message);

// Publish trạng thái cảm biến định kỳ
void notifyPublishState();

// Kiểm tra có lệnh feed từ xa đang chờ
bool     notifyHasPendingFeed();
float    notifyGetPendingGrams();
void     notifyClearPendingFeed();
bool     notifyTakePetFeed(float& grams, char (&requestId)[64]);
void     notifyPetFeedResult(const char* requestId, float actualGrams,
                             const char* reason = "dispense_finished");

// MQTT connected?
bool notifyMqttConnected();
