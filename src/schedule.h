#pragma once
#include <Arduino.h>

struct Meal {
    uint8_t hour;
    uint8_t minute;
    float   grams;
    bool    enabled;
};

void   scheduleInit();
void   scheduleLoop();              // gọi trong loop()

// Trả về index cữ nào cần nhả ngay (−1 nếu không có)
int    scheduleCheck();

// Persist a meal claim before starting motor; false if NVS write fails.
bool   scheduleMarkFired(int idx);

// Lấy/đặt lịch
Meal*  scheduleGet();               // con trỏ tới mảng MAX_MEALS
void   scheduleSet(int idx, Meal m);
void   scheduleReplace(const Meal* replacement);
void   scheduleSave();
void   scheduleLoad();

// Cữ tiếp theo (giờ, phút) — để hiển thị OLED
bool   scheduleNextMeal(int& outHour, int& outMin, float& outGrams);

// Reset fired flags lúc nửa đêm
void   scheduleResetFired();
