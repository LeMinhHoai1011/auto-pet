#pragma once
#include <stdint.h>

// Epoch time can move backwards after NTP sync; unlike millis it must not wrap.
inline uint32_t epochElapsed(uint32_t now, uint32_t since) {
    return since > 0 && now >= since ? now - since : 0;
}
