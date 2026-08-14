#!/usr/bin/env python3
"""Turn the Rika camera master into web assets, and pull its stills.

The master is a 4K vertical phone export: 2160x3840, 50 fps, 32 Mbps, 122.6 MiB
for 31.7 seconds. Three separate reasons it cannot ship as it stands:

  Cloudflare Workers Assets rejects any single file over 25 MiB, so the deploy
  would fail outright rather than merely be slow.

  The whole deployed site is 13.6 MiB today. The master alone is nine times that.

  It is nine times the pixels and twelve times the bitrate of anything the page
  can display. The video renders inside a phone-shaped frame roughly 340 px wide.

ENCODER SETTINGS ARE BORROWED, NOT INVENTED. flysystem.io/tools/make_video.py in
the workspace next door documents each of these as a fix for a real iOS or
Safari failure, found by reading MP4 boxes. Rediscovering them would be a waste:

  -profile:v main -level 3.1 -refs 4
      A slow preset otherwise picks ref=16 and has to declare High@5.0 to hold
      that DPB. iOS hardware decoders refuse that level, so the video plays on
      desktop Safari and silently never starts on an iPhone.

  -movflags +faststart+negative_cts_offsets, and deliberately NOT
  -avoid_negative_ts make_zero
      The latter writes a 66 ms empty edit at the head. Safari honours edit
      lists where Chrome ignores them, so that edit is the black flash on first
      frame. Leaving the CTS offsets negative avoids needing an edit at all.

  -g 50 -keyint_min 50 -sc_threshold 0
      Fixed 2 s GOP at 25 fps. The default 250-frame GOP gives three keyframes
      in the whole clip and a visible jump every time the loop restarts.

TWO PLACES THIS DEPARTS FROM THAT SCRIPT, both deliberate:

  720x1280, not 1080x1920. Level 3.1 allows 3600 macroblocks. 1080x1920 is 8100
  and would force level 4.0, giving up the exact compatibility guarantee above.
  720x1280 is 3600 on the nose, and is still 2x the frame's display width.

  No scale=in_range=full:out_range=limited. That script's sources are full-range
  phone captures. This one reports plain yuv420p with no range flag, i.e. already
  limited, and converting a limited source again crushes the blacks it is meant
  to protect.

50 -> 25 fps is an exact 2:1 decimation, so no frame is blended or unevenly
dropped. 50 -> 30 would judder, which drone footage shows badly.

ONE file, not two. The plan called for a silent copy for the autoplay loop and a
second track-bearing copy swapped in on unmute, to save the audio bytes for
everyone who never presses it. Encoding both showed why that is the wrong trade:
the audio is 0.5 MB of a 3.7 MB file, while swapping `src` mid-playback forces a
re-buffer and drops the current position, so unmute would stall and jump. A
single file makes unmute one property assignment, `video.muted = false`, with no
network round trip at all. The loop is desktop-only to begin with, so nobody on a
phone pays the 0.5 MB either way.

CRF 28, not the 24 tried first. At 720x1280 in a 340 px frame, 24 and 28 are
indistinguishable on the hardest frame in the clip - flames behind glass against
stone - and 28 lands at 3.7 MB, level with the existing hero.mp4, where 24 came
in at 5.5 MB.

    python .build/make-video.py            # encode + stills
    python .build/make-video.py --stills   # stills only
"""
import io
import os
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = 'originals/rika-master.mp4' if os.path.isfile('originals/rika-master.mp4') else '005.mp4'
VID = 'assets/video'
IMG = 'assets/img'

IOS_SAFE = [
    '-c:v', 'libx264',
    '-profile:v', 'main',
    '-level', '3.1',
    '-refs', '4',
    '-bf', '2',
    '-preset', 'slow',
    '-pix_fmt', 'yuv420p',
    '-g', '50',
    '-keyint_min', '50',
    '-sc_threshold', '0',
    '-movflags', '+faststart+negative_cts_offsets',
]
SCALE = ['-vf', 'fps=25,scale=720:1280:flags=lanczos']

# Chosen off a 1 fps contact sheet of the whole clip, for variety rather than
# for prettiness: exterior identity, product, range, and the store sign that
# says what this place actually is.
STILLS = [
    ('rika-fire',     '10.4', 'A wood fire burning behind the glass door of a stone-clad Rika stove'),
    ('rika-facade',    '4.4', 'The Rika store building, dark cladding with the illuminated Rika sign'),
    ('rika-range',    '21.8', 'A row of Rika pellet stoves lined up along the showroom wall'),
    ('rika-store',    '17.2', 'The Rika Premium Store sign on the showroom wall'),
    ('rika-stove',     '8.8', 'A black cylindrical Rika stove on display against a curtained wall'),
    ('rika-showroom', '19.2', 'The showroom seating area beneath the wall quote from Karl Riener'),
]
POSTER_AT = '10.4'


def run(args):
    subprocess.run([FF, '-y', '-loglevel', 'error', *args], check=True)


def mb(p):
    return os.path.getsize(p) / 1024 / 1024


def encode():
    print(f'  source: {SRC}  {mb(SRC):.1f} MB')
    out = f'{VID}/rika.mp4'
    run(['-i', SRC, *SCALE, *IOS_SAFE, '-crf', '28',
         '-c:a', 'aac', '-b:a', '128k', '-ac', '2', out])
    print(f'  {out:34} {mb(out):5.2f} MB   (starts muted; unmute needs no refetch)')
    if mb(out) > 8:
        print(f'  !! {out} is {mb(out):.1f} MB, over the 8 MB sanity bound - check the settings')
    if mb(out) > 25:
        sys.exit(f'  ABORT: {out} exceeds the 25 MiB Cloudflare per-file limit')


def stills():
    # Poster keeps the full 9:16 frame, because it stands in for the video.
    poster = f'{IMG}/rika-poster.jpg'
    run(['-ss', POSTER_AT, '-i', SRC, '-frames:v', '1', '-q:v', '2',
         '-vf', 'scale=720:1280:flags=lanczos', poster])
    print(f'  {poster:34} {Image.open(poster).size}  {os.path.getsize(poster)//1024} KB')

    # Gallery tiles are locked to 3/4 by .gallery__item img, so crop to 3:4 here
    # rather than letting the browser centre-crop something it did not choose.
    for name, t, _alt in STILLS:
        out = f'{IMG}/{name}.jpg'
        run(['-ss', t, '-i', SRC, '-frames:v', '1', '-q:v', '3',
             '-vf', 'crop=2160:2880,scale=750:1000:flags=lanczos', out])
        print(f'  {out:34} {Image.open(out).size}  {os.path.getsize(out)//1024} KB')


if __name__ == '__main__':
    if not os.path.isfile(SRC):
        sys.exit(f'source not found: {SRC}')
    if '--stills' not in sys.argv:
        encode()
    stills()
    total = sum(mb(f'{VID}/{f}') for f in os.listdir(VID))
    print(f'\n  assets/video now {total:.1f} MB total')
