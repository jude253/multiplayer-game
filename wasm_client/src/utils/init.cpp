#include <SDL.h>
#include <SDL_ttf.h>
#include "defs.h"
#include "structs.h"
#include "gameObjects/clickSquare.h"
#include "common.h"

App app;
TTF_Font *font;

Color RED                =   {.r = 255, .g=0,   .b=0,   .a=255};
Color DARK_RED           =   {.r = 96,  .g=0,   .b=0,   .a=255};
Color BLUE               =   {.r = 0,   .g=0,   .b=255, .a=255};
Color GREEN              =   {.r = 0,   .g=255, .b=0,   .a=255};
Color WHITE              =   {.r = 255, .g=255, .b=255, .a=255};
Color BLACK              =   {.r = 0,   .g=0,   .b=0,   .a=255};
Color BACKGROUND_COLOR   =   {.r = 96,  .g=128, .b=255, .a=255};

void initSDL(void)
{
    int rendererFlags, windowFlags;

    rendererFlags = SDL_RENDERER_ACCELERATED;

    windowFlags = 0;

    // Initialize app data before game starts.
    app.gameStart = SDL_GetPerformanceCounter();
    app.frameStart = app.gameStart;
    app.secondsElapsed = 0;
    app.renderFrameSeconds = 0.0f;
    app.fps = 0.0f;
    app.squaresClickedCount = 0;

    for (int i = 0; i < 10; i++) {
        CLICK_SQUARES_LIST.push_back(createRandomClickSquare());
    }
    
    if (SDL_Init(SDL_INIT_VIDEO) < 0)
    {
        printf("Couldn't initialize SDL: %s\n", SDL_GetError());
        exit(1);
    }

    if (TTF_Init() < 0)
    {
        printf("Couldn't initialize SDL_ttf: %s\n", TTF_GetError());
        exit(1);
    }

    font = TTF_OpenFont("include/fonts/SourceCodePro-Regular.ttf", 24);
    if (!font){
        printf("Unable to get font: %s\n", TTF_GetError());
        return;
    }

    app.window = SDL_CreateWindow("CGameSandbox", SDL_WINDOWPOS_UNDEFINED,
        SDL_WINDOWPOS_UNDEFINED, SCREEN_WIDTH, SCREEN_HEIGHT, windowFlags
    );

    if (!app.window)
    {
        printf("Failed to open %d x %d window: %s\n", 
            SCREEN_WIDTH, SCREEN_HEIGHT, SDL_GetError()
        );
        exit(1);
    }

    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "linear");

    app.renderer = SDL_CreateRenderer(app.window, -1, rendererFlags);

    if (!app.renderer)
    {
        printf("Failed to create renderer: %s\n", SDL_GetError());
        exit(1);
    }
}