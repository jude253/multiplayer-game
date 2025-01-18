#include <SDL.h>
#include <SDL_ttf.h>
#include "init.h"
#include "drawHelperFunctions.h"
#include "defs.h"
#include "input.h"
#include "gameObjects/clickSquare.h"
#include <string>

void drawDebugGrid(void) {
    setRenderDrawColor(WHITE);
    for (int i = 0; i < SCREEN_DIVISOR; i++) {
        for (int j = 0; j < SCREEN_DIVISOR; j++) {
            drawRect(i*GRID_WIDTH, j*GRID_HEIGHT);
        }
    }
}

void drawBorder(void) {

    // Top
    setRenderDrawColor(BLACK);
    SDL_Rect top;
    top.x = 0;
    top.y = 0;
    top.w = SCREEN_WIDTH;
    top.h = GRID_HEIGHT;
    SDL_RenderFillRect(app.renderer, &top);

    // Bottom
    SDL_Rect bottom;
    bottom.x = 0;
    bottom.y = SCREEN_HEIGHT-GRID_HEIGHT;
    bottom.w = SCREEN_WIDTH;
    bottom.h = GRID_HEIGHT;
    SDL_RenderFillRect(app.renderer, &bottom);

    
    // Sides:
    setRenderDrawColor(DARK_RED);
    
    // Left
    drawVerticalTrapezoid(
        0, 0,             GRID_WIDTH, GRID_HEIGHT,
        0, SCREEN_HEIGHT, GRID_WIDTH, SCREEN_HEIGHT-GRID_HEIGHT
    );

    // Right
    drawVerticalTrapezoid(
        SCREEN_WIDTH-GRID_WIDTH, GRID_HEIGHT,               SCREEN_WIDTH, 0,
        SCREEN_WIDTH-GRID_WIDTH, SCREEN_HEIGHT-GRID_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
    );
}

void prepareScene(void)
{
    setRenderDrawColor(BACKGROUND_COLOR);
    SDL_RenderClear(app.renderer);
}


void renderText(int x, int y, std::string text) {
    SDL_Color white = {255, 255, 255};
    SDL_Surface *surface = TTF_RenderText_Solid(font, text.c_str(), white);
    SDL_Texture *texture = SDL_CreateTextureFromSurface(app.renderer, surface);
    int textWidth = surface->w;
    int textHeight = surface->h;
    SDL_FreeSurface(surface);
    SDL_Rect rect;
    rect.x = x;
    rect.y = y;
    rect.w = textWidth;
    rect.h = textHeight;
    SDL_RenderCopy(app.renderer, texture, NULL, &rect);
}

void renderFPS(void) {
    std::string writeOnScreen = "FPS=";
    writeOnScreen.append(std::to_string((int)app.fps));
    renderText(0, SCREEN_HEIGHT-GRID_HEIGHT, writeOnScreen);
}

void renderSquaresClicked(void) {
    std::string writeOnScreen ="Squares Clicked=";
    writeOnScreen.append(std::to_string((int)app.squaresClickedCount));
    renderText(0, 0, writeOnScreen);
}

void presentScene(void)
{   
    drawDebugGrid();
    
    SDL_Rect mouse_rect;
    mouse_rect.x = app.mousePosition.x - 5;
    mouse_rect.y = app.mousePosition.y - 5;
    mouse_rect.w = 10;
    mouse_rect.h = 10;

    SDL_RenderDrawRect(app.renderer, &mouse_rect);
    
    for (int i = 0; i < CLICK_SQUARES_LIST.size(); i++) {
        ClickSquare cs = CLICK_SQUARES_LIST[i];
        drawClickSquare(app, cs);
    }
    drawBorder();
    renderFPS();
    renderSquaresClicked();
    SDL_RenderPresent(app.renderer);
}