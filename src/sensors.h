#pragma once
#include <Arduino.h>

void sensorsInit();
void sensorsLoop();
void sensorsPollWeight(); // Weight only: safe during dispensing, no auto-tare.

// ── Loadcell HX711 ──────────────────────────
float    getBowlGrams();          // gram đã lọc nhiễu (stable)
float    getBowlGramsRaw();       // gram sau median filter (phản hồi nhanh)
void     tareBowl();
void     sensorsAutoTare();
#if WOKWI_SIM
void     sensorsAddVirtualGrams(float g);
#endif

// ── HC-SR04 — mức thức ăn thùng ─────────────
float    getHopperCm();
int      getHopperPct();

// ── DHT22 — độ ẩm & nhiệt độ ────────────────
float    getHumidity();
float    getTemperature();

// ── Pet detection (từ RPi qua MQTT) ─────────
void     setPetDetected(bool detected);
bool     isPetPresent();
int      getPetConfirmCount();
void     resetPetDetection();

// ── Nút thủ công ────────────────────────────
bool     isButtonPressed();

// ── Stale food score ────────────────────────
float    stalenessScore();

// ── Cảnh báo chống spam ─────────────────────
bool     canAlert(const char* alertType);
void     markAlert(const char* alertType);
