#include "schedule.h"
#include "config.h"
#include "timekeeper.h"
#include "sensors.h"
#include <Preferences.h>
#include "feeding_policy.h"

static Meal     meals[MAX_MEALS];
static bool     fired[MAX_MEALS] = {false};
static uint32_t lastDay          = 0;
static Preferences prefs;
struct ServedMeals {
    uint32_t day;
    uint16_t minutes[MAX_MEALS];
};
static ServedMeals served = {};

static bool wasServed(int idx) {
    uint16_t minute = meals[idx].hour * 60 + meals[idx].minute;
    for (int i = 0; i < MAX_MEALS; ++i)
        if (served.minutes[i] == minute) return true;
    return false;
}

void scheduleInit() {
    for (int i = 0; i < MAX_MEALS; ++i) fired[i] = false;
    prefs.begin("schedule", false);
    scheduleLoad();
    if (prefs.isKey("served_v1") && prefs.getBytesLength("served_v1") == sizeof(served)) {
        prefs.getBytes("served_v1", &served, sizeof(served));
        lastDay = served.day;
    } else {
        scheduleResetFired();
        lastDay = served.day;
    }
    scheduleLoop();
}

void scheduleLoad() {
    // Mặc định: 7:00 (30g) và 18:00 (30g)
    meals[0] = {7,  0, DEFAULT_PORTION_G, true};
    meals[1] = {18, 0, DEFAULT_PORTION_G, true};
    for (int i = 2; i < MAX_MEALS; i++)
        meals[i] = {0, 0, 0, false};

    for (int i = 0; i < MAX_MEALS; i++) {
        char key[12];
        snprintf(key, sizeof(key), "m%d", i);
        if (!prefs.isKey(key)) continue;
        uint32_t v = prefs.getUInt(key, 0);
        meals[i].hour    = (v >> 24) & 0xFF;
        meals[i].minute  = (v >> 16) & 0xFF;
        meals[i].grams   = ((v >> 1) & 0x7FFF) * 1.0f;
        meals[i].enabled = (v & 0x01);
    }
}

void scheduleSave() {
    for (int i = 0; i < MAX_MEALS; i++) {
        char key[12];
        snprintf(key, sizeof(key), "m%d", i);
        uint16_t g = (uint16_t)(meals[i].grams + 0.5f);
        if (g > 0x7FFF) g = 0x7FFF;
        uint32_t v = ((uint32_t)meals[i].hour  << 24) |
                     ((uint32_t)meals[i].minute << 16) |
                     ((uint32_t)g << 1) |
                     (meals[i].enabled ? 1 : 0);
        prefs.putUInt(key, v);
    }
}

void scheduleLoop() {
    // Reset fired flags khi sang ngày mới
    uint32_t day = tkJulianDay();
    if (day > lastDay) {
        scheduleResetFired();
        lastDay = day;
    }
}

void scheduleResetFired() {
    for (int i = 0; i < MAX_MEALS; i++) fired[i] = false;
    served.day = tkJulianDay();
    for (int i = 0; i < MAX_MEALS; ++i) served.minutes[i] = 0xFFFF;
    prefs.putBytes("served_v1", &served, sizeof(served));
}

int scheduleCheck() {
    if (!tkTimeValid()) return -1;
    if (served.day != tkJulianDay()) return -1;
    int h = tkHour();
    int m = tkMinute();
    if (h < 0) return -1;

    for (int i = 0; i < MAX_MEALS; i++) {
        if (!meals[i].enabled)   continue;
        if (fired[i] || wasServed(i)) continue;
        if (!withinMealWindow(h * 60 + m, meals[i].hour * 60 + meals[i].minute,
                              MEAL_WINDOW_MINUTES)) continue;
        return i;
    }
    return -1;
}

bool scheduleMarkFired(int idx) {
    if (idx < 0 || idx >= MAX_MEALS || !tkTimeValid()) return false;
    scheduleLoop();
    if (wasServed(idx)) { fired[idx] = true; return true; }
    for (int i = 0; i < MAX_MEALS; ++i) {
        if (served.minutes[i] != 0xFFFF) continue;
        served.minutes[i] = meals[idx].hour * 60 + meals[idx].minute;
        if (prefs.putBytes("served_v1", &served, sizeof(served)) != sizeof(served)) {
            served.minutes[i] = 0xFFFF;
            return false;
        }
        fired[idx] = true;
        return true;
    }
    return false;
}

Meal* scheduleGet() { return meals; }

void scheduleSet(int idx, Meal m) {
    if (idx >= 0 && idx < MAX_MEALS) meals[idx] = m;
}

void scheduleReplace(const Meal* replacement) {
    bool updatedFired[MAX_MEALS] = {};
    for (int i = 0; i < MAX_MEALS; ++i) {
        for (int j = 0; j < MAX_MEALS; ++j) {
            if (fired[j] && meals[j].hour == replacement[i].hour &&
                meals[j].minute == replacement[i].minute) updatedFired[i] = true;
        }
    }
    memcpy(meals, replacement, sizeof(meals));
    memcpy(fired, updatedFired, sizeof(fired));
    scheduleSave();
}

bool scheduleNextMeal(int& outHour, int& outMin, float& outGrams) {
    if (!tkTimeValid()) return false;
    int h = tkHour();
    int m = tkMinute();
    int nowMin = h * 60 + m;

    int bestDelta = INT_MAX;
    int bestIdx   = -1;

    for (int i = 0; i < MAX_MEALS; i++) {
        if (!meals[i].enabled) continue;
        int mealMin = meals[i].hour * 60 + meals[i].minute;
        int delta   = mealMin - nowMin;
        if (delta <= 0) delta += 1440; // ngày hôm sau
        if (delta < bestDelta) {
            bestDelta = delta;
            bestIdx   = i;
        }
    }
    if (bestIdx < 0) return false;
    outHour  = meals[bestIdx].hour;
    outMin   = meals[bestIdx].minute;
    outGrams = meals[bestIdx].grams;
    return true;
}
