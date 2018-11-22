import logging
import math
import re
import subprocess
import sys

import click

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)-15s %(message)s')
verbosity_levels = [logging.INFO, logging.DEBUG]


@click.command()
@click.option('-e', '--event-file', required=True,
              type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
              help='Path to device event file.')
@click.option('-d', '--dispatcher', default=None,
              type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
              help='Path to dispatcher script.')
@click.option('-v', 'verbose', count=True, help='Logging verbosity.')
def listen(event_file, dispatcher, verbose):
    log.setLevel(verbosity_levels[min(verbose, len(verbosity_levels) - 1)])

    accum_dx, accum_dy = None, None
    p = None

    try:
        p = subprocess.Popen(['stdbuf', '-o', 'L', 'libinput', 'debug-events', '--device', event_file],
                             stdout=subprocess.PIPE, stderr=sys.stderr)
        while not p.poll():
            line = p.stdout.readline().decode('utf-8')
            m = re.search(
                '^ (?P<file>event\d+)\s+(?P<event>GESTURE_\w+)\s+\+(?P<time>\d+\.\d+)s\s+(?P<fingers>\d+)(?:\s+(?P<dx>-?\d+\.\d+)/\s*(?P<dy>-?\d+\.\d+))?',
                line)

            if m:
                file, event, time, fingers, dx, dy = m.groups()
                time = float(time)
                fingers = int(fingers)

                if event == 'GESTURE_SWIPE_BEGIN':
                    accum_dx = 0
                    accum_dy = 0
                elif event == 'GESTURE_SWIPE_UPDATE':
                    dx = float(dx)
                    dy = float(dy)

                    accum_dx += dx
                    accum_dy += dy
                elif event == 'GESTURE_SWIPE_END':
                    # angle     = angle of gesture direction with 0 degrees being up
                    # distance  = distance between gesture start and end (mouse acceleration account for)
                    # deviation = deviation in degrees to the nearest 90 degree angle
                    # direction = direction of gesture starting from 0 being up going clockwise to 3 pointing left
                    angle = round((math.degrees(math.atan2(accum_dy, accum_dx)) + 90) % 360)
                    distance = round(math.sqrt(accum_dx ** 2 + accum_dy ** 2))
                    deviation = abs(45 - ((angle - 45) % 90))
                    direction = (angle + deviation) % 360 // 90
                    human_direction = ['up', 'right', 'down', 'left'][direction]

                    log.debug('Swiped {direction:<5} - {angle:03}° ±{deviation:02}° Δ{distance:04}'.format(
                        distance=distance,
                        angle=angle,
                        deviation=deviation,
                        direction=human_direction))

                    if dispatcher:
                        log.debug('Calling dispatcher.')
                        exit_code = subprocess.call(
                            [str(x) for x in [dispatcher, human_direction, distance, angle, deviation]],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if exit_code:
                            log.error('Dispatcher finished with a non-zero exit code: %s', exit_code)
                        else:
                            log.debug('Dispatcher executed.')
    except KeyboardInterrupt:
        pass
    finally:
        if p:
            p.kill()


if __name__ == '__main__':
    listen()
