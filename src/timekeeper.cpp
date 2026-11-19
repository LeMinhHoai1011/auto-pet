#include "timekeeper.h"
#include "config.h"
#include <WiFi.h>
#include <time.h>
#include <Wire.h>
#include <RTClib.h>

static RTC_DS1307 rtc;
static bool       rtcOK      = false;
static bool       ntpSynced  = false;
static uint32_t   lastNTPMs  = 0;
static const uint32_t NTP_RESYNC_MS = 3600000UL; // đồng bộ lại mỗi 1 giờ

void timekeeperInit() {
    Wire.begin(PIN_SDA, PIN_SCL);
    if (rtc.begin()) {
        rtcOK = true;
        if (!rtc.isrunning()) {
            // RTC chưa chạy — đặt thời gian compile tạm thời
            rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
        }
    } else {
        Serial.println("[TIME] RTC DS1307 not found");
    }
    // Cấu hình NTP
    configTime(GMT_OFFSET_S, DST_OFFSET_S, NTP_SERVER);
}

void timekeeperLoop() {
    if (!USE_WIFI) return;
    if (WiFi.status() != WL_CONNECTED) return;

    uint32_t now = millis();
    if (ntpSynced && (now - lastNTPMs) < NTP_RESYNC_MS) return;

    struct tm ti;
    if (getLocalTime(&ti, 100)) {
        ntpSynced = true;
        lastNTPMs = now;
        tkSyncRTC();
    }
}

void tkSyncRTC() {
    if (!rtcOK) return;
    struct tm ti;
    if (!getLocalTime(&ti, 100)) return;
    // Đồng bộ RTC từ NTP
    DateTime dt(ti.tm_year + 1900, ti.tm_mon + 1, ti.tm_mday,
                ti.tm_hour, ti.tm_min, ti.tm_sec);
    rtc.adjust(dt);
}

uint32_t tkEpoch() {
    // Ưu tiên NTP, dự phòng RTC
    if (ntpSynced) {
        time_t t;
        ::time(&t);
        return (uint32_t)t;
    }
    if (rtcOK) {
        DateTime dt = rtc.now();
        // RTC stores local wall time (written by tkSyncRTC). Return UTC epoch,
        // matching time() after NTP, so switching clocks cannot jump by 7 hours.
        int64_t utc = (int64_t)dt.unixtime() - GMT_OFFSET_S - DST_OFFSET_S;
        return utc > 0 ? (uint32_t)utc : 0;
    }
    return 0;
}

bool tkTimeValid() {
    return ntpSynced || rtcOK;
}

int tkHour() {
    if (ntpSynced) {
        struct tm ti;
        if (getLocalTime(&ti, 10)) return ti.tm_hour;
    }
    if (rtcOK) return rtc.now().hour();
    return -1;
}

int tkMinute() {
    if (ntpSynced) {
        struct tm ti;
        if (getLocalTime(&ti, 10)) return ti.tm_min;
    }
    if (rtcOK) return rtc.now().minute();
    return -1;
}

int tkSecond() {
    if (ntpSynced) {
        struct tm ti;
        if (getLocalTime(&ti, 10)) return ti.tm_sec;
    }
    if (rtcOK) return rtc.now().second();
    return 0;
}

uint32_t tkJulianDay() {
    // Trả về số ngày kể từ epoch để so sánh
    uint32_t ep = tkEpoch();
    if (ep == 0) return 0;
    return (uint32_t)(((int64_t)ep + GMT_OFFSET_S + DST_OFFSET_S) / 86400);
}
