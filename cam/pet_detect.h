#pragma once
#include <stdint.h>
#include <stddef.h>

struct PetResult {
    bool  detected;
    const char* label;      // "cat", "dog", "motion", "none"
    float confidence;       // 0.0 — 1.0
};

bool      petDetectInit();
PetResult petDetectRun(const uint8_t* buf, size_t len, int w, int h);
