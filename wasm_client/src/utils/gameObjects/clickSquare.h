#pragma once
#include <SDL.h>
#include "../structs.h"
#include <vector>

class ClickSquare {

public:
    Color color;  // RGBA color
    SDL_Rect drawRect;  // Actual Rect used to draw onscreen.  Update with other attributes.
    int l;  // Edge length
    Point position;  // (x,y) upper left corner float coordinates -- truncate before drawing.
    Point velocity;  // (x,y) float velocity components
    Point acceleration;  // (x,y) float velocity components
    Uint64 drawTime;  // Draw time-- intended to be set by SDL_GetPerformanceCounter()

};

void drawClickSquare(App app, ClickSquare clickSquare);
ClickSquare createClickSquare(int x, int y, int l, Color color);

extern std::vector<ClickSquare> CLICK_SQUARES_LIST;
ClickSquare createRandomClickSquare();
bool deleteClickSquareIfClicked();
