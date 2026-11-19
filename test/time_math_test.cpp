#include "time_math.h"
#include <assert.h>
#include <stdio.h>
int main() {
    assert(epochElapsed(1795065764u, 1795090887u) == 0);
    assert(epochElapsed(0, 1795090887u) == 0);
    assert(epochElapsed(1795065764u, 0) == 0);
    assert(epochElapsed(1795065764u, 1795065764u) == 0);
    assert(epochElapsed(1795069364u, 1795065764u) == 3600);
    puts("Epoch regression, missing clock and normal aging tests passed");
}
