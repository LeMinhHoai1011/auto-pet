#pragma once
#include <Arduino.h>

void displayInit();
void displayLoop();

struct DisplayState {
    char     timeStr[9];       // "HH:MM:SS"
    bool     wifiOK;
    bool     mqttOK;
    float    bowlGrams;
    int      hopperPct;
    float    humidity;
    int      nextMealH;
    int      nextMealM;
    float    nextMealG;
    uint32_t cooldownSec;
    float    staleScore;
    char     errorMsg[32];
};

extern DisplayState dispState;
