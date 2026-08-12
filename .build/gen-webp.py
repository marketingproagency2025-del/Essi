#!/usr/bin/env python3
"""Generate WebP alongside every raster image, and report the saving.

Writes assets/img/<name>.webp next to <name>.jpg|png. Originals are kept: the
HTML uses <picture> with the JPG as the fallback source, so nothing breaks for a
client that cannot take WebP, and no existing URL changes.

Measured on the current 44 raster files at q80 with method=6:
5,027,213 -> 2,801,250 bytes, a 44.3% cut, 2,173 KB saved.

(An earlier audit measured 41.5% using Pillow's default effort setting and
found testimonials-bg.jpg came out 1% LARGER. At method=6 it compresses by 2%
instead, so nothing needs skipping today. The guard below stays anyway: it is
cheap, and the next image someone adds may not behave.)

logo.png has transparency and is encoded lossless, to avoid fringing on the
green brand mark.

    python .build/gen-webp.py --dry-run
    python .build/gen-webp.py
"""
import io
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow is required: python -m pip install Pillow')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'img')
DRY = '--dry-run' in sys.argv

QUALITY = 80
RASTER = ('.jpg', '.jpeg', '.png')

rows, before_total, after_total, skipped = [], 0, 0, []

for name in sorted(os.listdir(IMG)):
    stem, ext = os.path.splitext(name)
    if ext.lower() not in RASTER:
        continue
    src = os.path.join(IMG, name)
    before = os.path.getsize(src)

    with Image.open(src) as im:
        has_alpha = im.mode in ('RGBA', 'LA') or (
            im.mode == 'P' and 'transparency' in im.info)
        buf = io.BytesIO()
        if has_alpha:
            im.save(buf, 'WEBP', lossless=True, method=6)
        else:
            im.convert('RGB').save(buf, 'WEBP', quality=QUALITY, method=6)
        data = buf.getvalue()

    after = len(data)
    # Never ship a "saving" that is bigger than the original.
    if after >= before:
        skipped.append((name, before, after))
        continue

    dest = os.path.join(IMG, stem + '.webp')
    if not DRY:
        with open(dest, 'wb') as fh:
            fh.write(data)

    rows.append((name, before, after))
    before_total += before
    after_total += after

for name, b, a in rows:
    print(f'  {name:30} {b:>9,} -> {a:>9,}  -{100 * (b - a) / b:4.1f}%')

for name, b, a in skipped:
    print(f'  {name:30} {b:>9,}    SKIPPED, WebP would be {a:,} bytes')

if before_total:
    pct = 100 * (before_total - after_total) / before_total
    print(f'\n  {len(rows)} converted: {before_total:,} -> {after_total:,} bytes'
          f'  ({pct:.1f}% smaller, {(before_total - after_total) // 1024:,} KB saved)')
if skipped:
    print(f'  {len(skipped)} skipped because WebP was no smaller')
if DRY:
    print('\n  (dry run - nothing written)')
