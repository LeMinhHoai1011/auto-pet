#include "storage.h"
#include "config.h"
#include <Preferences.h>
#include <LittleFS.h>

static Preferences prefs;
static NVSData     cache;
static bool        dirty        = false;
static uint32_t    lastFlushMs  = 0;
static bool        lfsOk        = false;

// ─────────────────────────────────────────────
//  NVS
// ─────────────────────────────────────────────
void storageInit() {
    prefs.begin("petfeeder", false);

    cache.lastFeedEpoch   = prefs.getUInt("lastFeed", 0);
    cache.dailyFeedCount  = prefs.getUChar("dayCount", 0);
    cache.dailyGrams      = prefs.getUShort("dayGrams", 0);
    cache.lastFeedDay     = prefs.getUInt("feedDay", 0);
    cache.foodDispensedAt = prefs.getUInt("dispensedAt", 0);
    cache.lastTareTime    = prefs.getUInt("lastTare", 0);
    cache.feedTarget      = prefs.isKey("feedTarget") ? prefs.getFloat("feedTarget", 0) : 0.0f;
    cache.feedActual      = prefs.isKey("feedActual") ? prefs.getFloat("feedActual", 0) : 0.0f;

    if (prefs.isKey("feedState")) {
        String fsStr = prefs.getString("feedState", "done");
        strncpy(cache.feedState, fsStr.c_str(), sizeof(cache.feedState) - 1);
    } else {
        strncpy(cache.feedState, "done", sizeof(cache.feedState) - 1);
    }
    cache.feedState[sizeof(cache.feedState) - 1] = '\0';

    dirty = false;

#if WOKWI_SIM
    // Wokwi không load partitions.bin tự động → skip LittleFS im lặng
    lfsOk = false;
    Serial.println(">> Bo nho: che do mo phong (khong luu queue)");
#else
    lfsOk = LittleFS.begin(false);
    if (!lfsOk) {
        Serial.println(">> Bo nho: dinh dang lai...");
        if (LittleFS.format()) {
            lfsOk = LittleFS.begin(false);
        }
    }
    if (!lfsOk) Serial.println("!! Bo nho: khong kha dung, hang doi tat");
#endif
}

NVSData& nvsGet() { return cache; }

void nvsMark() { dirty = true; }

void nvsFlush(bool force) {
    if (!dirty) return;
    uint32_t now = millis();
    if (!force && (now - lastFlushMs) < (NVS_WRITE_INTERVAL_S * 1000UL)) return;

    prefs.putUInt("lastFeed",    cache.lastFeedEpoch);
    prefs.putUChar("dayCount",   cache.dailyFeedCount);
    prefs.putUShort("dayGrams",  cache.dailyGrams);
    prefs.putUInt("feedDay",     cache.lastFeedDay);
    prefs.putUInt("dispensedAt", cache.foodDispensedAt);
    prefs.putUInt("lastTare",    cache.lastTareTime);
    prefs.putFloat("feedTarget", cache.feedTarget);
    prefs.putFloat("feedActual", cache.feedActual);
    prefs.putString("feedState", cache.feedState);

    dirty       = false;
    lastFlushMs = now;
}

// ─────────────────────────────────────────────
//  LittleFS — hàng đợi sự kiện
// ─────────────────────────────────────────────
void queueInit() {
    // LittleFS đã mount trong storageInit()
}

void queuePush(const char* jsonEvent) {
    if (!lfsOk) return;
    // Kiểm tra giới hạn kích thước
    File f = LittleFS.open(QUEUE_FILE, "r");
    if (f) {
        size_t sz = f.size();
        f.close();
        if (sz >= QUEUE_MAX_BYTES) {
            Serial.println(">> Hang doi day, xoa su kien cu nhat");
            // Đọc tất cả, bỏ dòng đầu, ghi lại
            File fr = LittleFS.open(QUEUE_FILE, "r");
            String buf = "";
            fr.readStringUntil('\n'); // bỏ dòng đầu
            while (fr.available()) buf += (char)fr.read();
            fr.close();
            File fw = LittleFS.open(QUEUE_FILE, "w");
            fw.print(buf);
            fw.close();
        }
    }
    File fa = LittleFS.open(QUEUE_FILE, "a");
    if (fa) {
        fa.println(jsonEvent);
        fa.close();
    }
}

bool queueHasData() {
    if (!lfsOk) return false;
    if (!LittleFS.exists(QUEUE_FILE)) return false;
    File f = LittleFS.open(QUEUE_FILE, "r");
    if (!f) return false;
    bool has = f.size() > 0;
    f.close();
    return has;
}

String queuePop() {
    if (!lfsOk) return "";
    if (!LittleFS.exists(QUEUE_FILE)) return "";
    File f = LittleFS.open(QUEUE_FILE, "r");
    if (!f) return "";

    String first = f.readStringUntil('\n');
    String rest  = "";
    while (f.available()) rest += (char)f.read();
    f.close();

    File fw = LittleFS.open(QUEUE_FILE, "w");
    fw.print(rest);
    fw.close();

    first.trim();
    return first;
}

void queueClear() {
    if (!lfsOk) return;
    if (LittleFS.exists(QUEUE_FILE))
        LittleFS.remove(QUEUE_FILE);
}

int queueCount() {
    if (!lfsOk) return 0;
    if (!LittleFS.exists(QUEUE_FILE)) return 0;
    File f = LittleFS.open(QUEUE_FILE, "r");
    if (!f) return 0;
    int count = 0;
    while (f.available()) {
        f.readStringUntil('\n');
        count++;
    }
    f.close();
    return count;
}
