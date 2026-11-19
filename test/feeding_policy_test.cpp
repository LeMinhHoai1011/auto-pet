#include "feeding_policy.h"
#include <assert.h>
#include <stdio.h>

int main() {
    PresenceGate gate(5000, 1500, 1500);
    assert(!gate.ready(0));
    gate.observe(true, 0);
    gate.observe(true, 1000);
    gate.observe(false, 1500); // walks through the zone, then leaves
    assert(!gate.ready(6000));
    gate.observe(true, 10000);
    gate.observe(true, 11000);
    gate.observe(true, 12000);
    gate.observe(true, 13000);
    gate.observe(true, 14000);
    assert(!gate.ready(14999)); // wall time alone is not proof of dwell
    gate.observe(true, 15000);
    assert(gate.ready(15000));
    assert(!gate.ready(16501)); // stale camera data cannot dispense
    gate.observe(true, 17000); // gap restarts dwell
    assert(!gate.ready(17000));
    gate.reset();
    assert(!gate.ready(17000));
    uint32_t nearWrap = UINT32_MAX - 2000;
    for (uint32_t dt = 0; dt <= 5000; dt += 1000) gate.observe(true, nearWrap + dt);
    assert(gate.ready(nearWrap + 5000));
    assert(!withinMealWindow(419, 420, 30)); // before 07:00
    assert(withinMealWindow(420, 420, 30));
    assert(withinMealWindow(449, 420, 30));
    assert(!withinMealWindow(450, 420, 30)); // expires 07:30
    puts("Presence and meal-window tests passed");
}
