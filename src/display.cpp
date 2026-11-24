#include "display.h"
#include "config.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

static Adafruit_SSD1306 oled(128, 64, &Wire, -1);
static uint32_t lastRefreshMs = 0;
static const uint32_t REFRESH_MS = 1000;

DisplayState dispState = {};

void displayInit() {
    Wire.begin(PIN_SDA, PIN_SCL);
    if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("!! Man hinh OLED: khong tim thay");
        return;
    }
    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setTextColor(SSD1306_WHITE);
    oled.setCursor(0, 0);
    oled.println("Pet Feeder v3");
    oled.println("Stepper + Camera");
    oled.display();
}

void displayLoop() {
    uint32_t now = millis();
    if (now - lastRefreshMs < REFRESH_MS) return;
    lastRefreshMs = now;

    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setTextColor(SSD1306_WHITE);

    // Dòng 1: Giờ + trạng thái mạng
    oled.setCursor(0, 0);
    oled.print(dispState.timeStr);
    oled.print(dispState.wifiOK ? " W+" : " W-");
    oled.print(dispState.mqttOK ? " M+" : " M-");

    // Dòng 2: Bát + thùng
    oled.setCursor(0, 10);
    oled.printf("Bat:%.0fg Thung:%d%%", dispState.bowlGrams, dispState.hopperPct);

    // Dòng 3: Độ ẩm
    oled.setCursor(0, 20);
    oled.printf("Am:%.0f%%", dispState.humidity);

    // Dòng 4: Cữ tiếp theo / cooldown
    oled.setCursor(0, 30);
    if (dispState.cooldownSec > 0) {
        uint32_t s = dispState.cooldownSec;
        uint32_t h = s / 3600; s %= 3600;
        uint32_t m = s / 60;
        oled.printf("Cho %uh%02um nua", h, m);
    } else if (dispState.nextMealH >= 0) {
        oled.printf("Ke: %02d:%02d %.0fg",
            dispState.nextMealH, dispState.nextMealM, dispState.nextMealG);
    }

    // Dòng 5: Stale warning
    oled.setCursor(0, 40);
    if (dispState.staleScore >= STALE_SCORE_WARN) {
        oled.print("! Thuc an thiu");
    }

    // Dòng 6: Lỗi
    if (dispState.errorMsg[0] != '\0') {
        oled.setCursor(0, 54);
        oled.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
        oled.print(dispState.errorMsg);
        oled.setTextColor(SSD1306_WHITE);
    }

    oled.display();
}
