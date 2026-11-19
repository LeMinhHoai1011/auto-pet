#pragma once

void mqttCamInit();
bool mqttCamPublish(const char* petLabel, float confidence);
