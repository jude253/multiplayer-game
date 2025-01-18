#pragma once

#define SCREEN_WIDTH   1280 / 2
#define SCREEN_HEIGHT  720 / 2

#define SCREEN_DIVISOR 10
#define GRID_HEIGHT SCREEN_HEIGHT / SCREEN_DIVISOR
#define GRID_WIDTH SCREEN_WIDTH / SCREEN_DIVISOR

#define TARGET_FPS 60
#define TARGET_SECONDS_PER_FRAME 1.0f/TARGET_FPS

#define GRAVITY 9.8 // m/s^2  -- Think about this as "adding depth"