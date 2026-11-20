#include <assert.h>
#include <stdio.h>
#include "ctr_frame_rate.h"

int main(void)
{
    CtrFrameRate presentation = {0}, workEnd = {0}, stalled = {0};
    const uint64_t hz = 1000000, period = 16715;
    for (unsigned frame = 0; frame <= 60; ++frame)
    {
        uint64_t tick = frame * period;
        CtrFrameRate_Add(&presentation, tick, frame, hz);
        /* Background work varies after submission, without missing VBlank. */
        CtrFrameRate_Add(&workEnd, tick + (frame == 60 ? 6000 : 0), frame, hz);
        CtrFrameRate_Add(&stalled, tick + (frame == 60 ? 20000 : 0), frame, hz);
    }
    assert(presentation.shown > 59.8f && presentation.shown < 59.9f);
    assert(workEnd.shown < 59.6f);
    assert(stalled.shown < 59.0f); /* Actual cadence loss must remain visible. */
    assert(presentation.game == presentation.shown);
    puts("Frame-rate clock boundary: post-submit work cannot invent a presentation dip; actual stalls remain visible");
    return 0;
}
