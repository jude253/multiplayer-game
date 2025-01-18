#include <SDL.h>
#include "defs.h"
#include "math.h"
/*
Need a better approach for this stuff.  It's too confusing, and it's not
working how I would think it would work.

https://stackoverflow.com/questions/288739/generate-random-numbers-uniformly-over-an-entire-range
*/
int randIntInRange(int min, int max) {
    double rand_double = ((double) rand() / (RAND_MAX+1)) * (min-max+1) + min;
    return (int) rand_double;
}


/*
https://stackoverflow.com/questions/7560114/random-number-c-in-some-range
*/
SDL_Point getRandomPoint(void) {
    SDL_Point point;
    point.x = GRID_HEIGHT + rand() % (SCREEN_WIDTH - GRID_HEIGHT + 1);
    point.y = GRID_HEIGHT + rand() % (SCREEN_HEIGHT - GRID_HEIGHT + 1);
    return point;
}