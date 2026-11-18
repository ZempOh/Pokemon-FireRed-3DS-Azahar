"""Exercise the actual world eligibility function with native weather states."""
from pathlib import Path
import subprocess, tempfile
source=(Path(__file__).resolve().parents[1]/'src/voxel/voxel_world.c').read_text()
start=source.index('bool VoxelWorld_ClimateAllowed(void)')
end=source.index('\nVoxelWeatherClass VoxelWorld_Weather',start)
harness='''#include <assert.h>
#include <stdbool.h>
#define PLATFORM_3DS
enum { WEATHER_NONE, WEATHER_SUNNY_CLOUDS, WEATHER_SUNNY, WEATHER_RAIN,
       WEATHER_SNOW, WEATHER_FOG_HORIZONTAL, WEATHER_VOLCANIC_ASH,
       WEATHER_SANDSTORM, WEATHER_FOG_DIAGONAL, WEATHER_UNDERWATER,
       WEATHER_SHADE, WEATHER_DROUGHT, WEATHER_DOWNPOUR };
static unsigned current;
static unsigned GetCurrentWeather(void) { return current; }
'''+source[start:end]+'''
int main(void) {
    for(current=WEATHER_NONE;current<=WEATHER_SUNNY;current++)
        assert(VoxelWorld_ClimateAllowed());
    for(current=WEATHER_RAIN;current<=WEATHER_DOWNPOUR;current++)
        assert(!VoxelWorld_ClimateAllowed());
}
'''
with tempfile.TemporaryDirectory() as d:
    c=Path(d)/'weather.c'; exe=Path(d)/'weather.exe';c.write_text(harness)
    subprocess.run(['gcc','-std=c99','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('weather gate: daylight allowed, native effects preserved')
