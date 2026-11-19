#pragma once
#include <stdint.h>

// Receives observations, never assumes continued presence after messages stop.
class PresenceGate {
    uint32_t waitMs, gapMs, freshMs;
    uint32_t first = 0, last = 0;
    bool tracking = false;
public:
    PresenceGate(uint32_t wait, uint32_t gap, uint32_t fresh)
        : waitMs(wait), gapMs(gap), freshMs(fresh) {}
    void reset() { tracking = false; }
    void observe(bool valid, uint32_t now) {
        if (!valid) { reset(); return; }
        if (!tracking || uint32_t(now - last) > gapMs) first = now;
        last = now;
        tracking = true;
    }
    bool ready(uint32_t now) const {
        return tracking && uint32_t(now - last) <= freshMs &&
               uint32_t(last - first) >= waitMs;
    }
};

inline bool withinMealWindow(int nowMinute, int mealMinute, int windowMinutes) {
    return nowMinute >= mealMinute && nowMinute - mealMinute < windowMinutes;
}
