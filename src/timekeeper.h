#pragma once
#include <Arduino.h>

void     timekeeperInit();
void     timekeeperLoop();          // gọi trong loop() — không blocking

uint32_t tkEpoch();                 // epoch hiện tại (GMT+7)
bool     tkTimeValid();             // đã có giờ chuẩn chưa
int      tkHour();
int      tkMinute();
int      tkSecond();
uint32_t tkJulianDay();             // ngày Julian để so sánh reset daily counter

// Gọi khi cần đồng bộ RTC từ NTP (tự động trong timekeeperLoop)
void     tkSyncRTC();
