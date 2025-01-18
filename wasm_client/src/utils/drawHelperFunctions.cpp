#include <SDL.h>
#include "init.h"
#include "defs.h"
#include "input.h"

void setRenderDrawColor(Color color) {
    SDL_SetRenderDrawColor(app.renderer, 
    color.r, 
    color.g, 
    color.b, 
    color.a
    );
}

void drawVertLine(int x, int y, int h) {
    SDL_RenderDrawLine(app.renderer, x, y, x, y+h);
}

void drawRect(int x, int y) {
    SDL_Rect rect;
    rect.x = x;
    rect.y = y;
    rect.w = GRID_WIDTH;
    rect.h = GRID_HEIGHT;
    
    SDL_RenderDrawRect(app.renderer, &rect);
}

/*
Draw vertically parallel trapezoid from x_lt to x_rt-- Left to Right.
*/
void drawVerticalTrapezoid(
    int x_lt, int y_lt, int x_rt, int y_rt,
    int x_lb, int y_lb, int x_rb, int y_rb
    ) {
    int y_t;
    int y_b;
    for (int x = x_lt; x < x_rt; x++) {
        y_t = (int)(((float)(y_rt - y_lt) / (float)(x_rt - x_lt))*(float)(x-x_lt) + y_lt);
        y_b = (int)(((float)(y_rb - y_lb) / (float)(x_rb - x_lb))*(float)(x-x_lb) + y_lb);
        SDL_RenderDrawLine(app.renderer, x, y_t, x, y_b);
    }
    
}
