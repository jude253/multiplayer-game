
#include <string.h>
#include "utils/init.h"
#include "utils/draw.h"
#include "utils/input.h"
#include "utils/defs.h"
#include <SDL.h>
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif


void handleFrameStart(void) {
    Uint64 frameStart = SDL_GetPerformanceCounter();
    float frameStartToStartSeconds = (float)(frameStart - app.frameStart) / 
                                     (float)SDL_GetPerformanceFrequency();

    app.secondsElapsed = (Uint64)((float)(frameStart - app.frameStart) / 
                                  (float)SDL_GetPerformanceFrequency());
    
    // Calculate fps from frame start to frame start. Hopefully this
    // will allow accurate frame calculation also in emscripten on web.
    app.fps = 1.0f/frameStartToStartSeconds;
    // SDL_Log("FPS=%f", app.fps);

    // Overwrite previous frame start with current frame start
    app.frameStart = frameStart;
}

void handleFrameEnd(void) {
    Uint64 renderEnd = SDL_GetPerformanceCounter();

    // Calculate how long it took to render current frame
    app.renderFrameSeconds = (float)(renderEnd - app.frameStart) / 
                             (float)SDL_GetPerformanceFrequency();
    
    // If not running in emscipten, delay start of next frame to target FPS:
#ifndef __EMSCRIPTEN__
    SDL_Delay(
        // Needs to be in MS
        floor((TARGET_SECONDS_PER_FRAME - app.renderFrameSeconds)*1000.0f)
    );
#endif
}

void renderFrame(void) {
    
    handleFrameStart();

    prepareScene();

    doInput();

    presentScene();

    handleFrameEnd();
    
}


int main(int argc, char *argv[])
{
    memset(&app, 0, sizeof(App));

    initSDL();

    // atexit(cleanup);  // <- I don't know what this is for... Maybe saving?
    
    #ifdef __EMSCRIPTEN__
    // Docs: https://emscripten.org/docs/api_reference/emscripten.h.html#c.emscripten_set_main_loop
    emscripten_set_main_loop(renderFrame, 0, 1);
    #else
    while (1) { renderFrame(); }
    #endif
    return 0;
}