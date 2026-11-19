#include "schedule.h"
#include <Preferences.h>
#include <assert.h>

bool Preferences::failWrites = false;
std::map<std::string, std::vector<unsigned char>> Preferences::data;
static uint32_t day = 100;
static int minuteOfDay = 419;
bool tkTimeValid() { return day > 0; }
uint32_t tkJulianDay() { return day; }
int tkHour() { return minuteOfDay / 60; }
int tkMinute() { return minuteOfDay % 60; }
int tkSecond() { return 30; }

int main() {
    scheduleInit();
    assert(scheduleCheck() == -1);
    minuteOfDay = 420;
    assert(scheduleCheck() == 0);
    assert(scheduleMarkFired(0));
    assert(scheduleCheck() == -1);
    scheduleInit(); // reload persistent state, same day
    assert(scheduleCheck() == -1);
    Meal replacement[6] = {};
    replacement[3] = {7, 0, 30, true};
    scheduleReplace(replacement);
    assert(scheduleCheck() == -1); // reordered slot cannot repeat
    ++day;
    scheduleLoop();
    assert(scheduleCheck() == 3);
    Preferences::failWrites = true;
    assert(!scheduleMarkFired(3)); // do not start motor if claim cannot persist
    assert(scheduleCheck() == 3);
    Preferences::failWrites = false;
    assert(scheduleMarkFired(3));
    assert(scheduleCheck() == -1);
    ++day;
    scheduleLoop();
    minuteOfDay = 450;
    assert(scheduleCheck() == -1);
    puts("Schedule persistence, reboot, reorder and write-failure tests passed");
}
