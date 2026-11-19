#pragma once
#include <Arduino.h>

// ─────────────────────────────────────────────
//  Cấu trúc cache NVS (gom writes, chống mòn flash)
// ─────────────────────────────────────────────
struct NVSData {
    uint32_t lastFeedEpoch;      // epoch lần nhả gần nhất
    uint8_t  dailyFeedCount;     // số lần nhả hôm nay
    uint16_t dailyGrams;         // tổng gram nhả hôm nay
    uint32_t lastFeedDay;        // ngày Julian để reset bộ đếm
    uint32_t foodDispensedAt;    // epoch lần nhả vào bát gần nhất
    uint32_t lastTareTime;       // epoch lần tare gần nhất
    char     feedState[16];      // "done" hoặc "dispensing" (atomicity)
    float    feedTarget;         // gram mục tiêu (dùng khi mất điện giữa nhả)
    float    feedActual;         // gram thực tế đã nhả
};

// ─────────────────────────────────────────────
//  Khởi tạo / đọc / ghi
// ─────────────────────────────────────────────
void     storageInit();
NVSData& nvsGet();
void     nvsMark();                // đánh dấu dirty, sẽ flush sau
void     nvsFlush(bool force = false);  // ghi NVS nếu dirty + đủ interval

// ─────────────────────────────────────────────
//  LittleFS — hàng đợi sự kiện offline
// ─────────────────────────────────────────────
void     queueInit();
void     queuePush(const char* jsonEvent);  // thêm sự kiện vào /queue.log
bool     queueHasData();
String   queuePop();             // lấy 1 dòng (xóa luôn sau khi lấy)
void     queueClear();
int      queueCount();
