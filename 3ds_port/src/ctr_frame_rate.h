#ifndef CTR_FRAME_RATE_H
#define CTR_FRAME_RATE_H
#include <stdbool.h>
#include <stdint.h>

/* Call once per submitted frame, using one consistent clock boundary.
 * Never substitutes a target rate, clamps a low value, or smooths a stall. */
typedef struct {
    uint64_t start, gameMark;
    unsigned frames;
    bool initialized;
    float shown, game;
} CtrFrameRate;

static inline void CtrFrameRate_Add(CtrFrameRate *rate, uint64_t tick,
                                    uint64_t gameFrame, uint64_t frequency)
{
    if (!rate->initialized || tick < rate->start || gameFrame < rate->gameMark)
    {
        rate->start = tick;
        rate->gameMark = gameFrame;
        rate->frames = 0;
        rate->initialized = true;
        return;
    }
    ++rate->frames;
    uint64_t elapsed = tick - rate->start;
    if (elapsed >= frequency && frequency)
    {
        rate->shown = (float)(rate->frames * (double)frequency / elapsed);
        rate->game = (float)((gameFrame - rate->gameMark) * (double)frequency / elapsed);
        rate->start = tick;
        rate->gameMark = gameFrame;
        rate->frames = 0;
    }
}
#endif
