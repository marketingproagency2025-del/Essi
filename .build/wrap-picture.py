#!/usr/bin/env python3
"""Wrap every local raster <img> in a <picture> that offers WebP first.

    <picture>
      <source srcset="assets/img/foo.webp" type="image/webp" />
      <img src="assets/img/foo.jpg" ... unchanged ... />
    </picture>

The <img> is left byte-identical, so alt, width, height, loading,
fetchpriority, decoding and every class survive, and a client that cannot take
WebP still gets exactly what it got before. No existing URL changes.

Safe against the stylesheet: a grep of style.css found no direct-child "> img"
selectors, only descendant ones, which reach through the wrapper. CSS also gets
`picture { display: contents }` so the wrapper never becomes a flex or grid item
in place of the image.

Idempotent: an <img> already inside a <picture> is skipped.

    python .build/wrap-picture.py --dry-run
    python .build/wrap-picture.py
"""
import glob
import io
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRY = '--dry-run' in sys.argv

IMG_RX = re.compile(r'<img\b[^>]*>')
SRC_RX = re.compile(r'src="([^"]+)"')

pages = (glob.glob('*.html') + glob.glob('it/*.html')
         + glob.glob('es/*.html') + glob.glob('sq/*.html'))

wrapped = skipped = 0
files_touched = 0

for path in sorted(pages):
    s = io.open(path, encoding='utf-8', newline='').read()
    base = os.path.dirname(os.path.abspath(path))
    out = []
    last = 0
    local_wrapped = 0

    for m in IMG_RX.finditer(s):
        tag = m.group(0)
        sm = SRC_RX.search(tag)
        if not sm:
            continue                      # lightbox placeholder, no src
        src = sm.group(1)
        if re.match(r'^(https?:|//|data:)', src):
            continue

        stem, ext = os.path.splitext(src)
        if ext.lower() not in ('.jpg', '.jpeg', '.png'):
            continue

        webp_disk = os.path.normpath(os.path.join(base, stem + '.webp'))
        if not os.path.isfile(webp_disk):
            continue                      # no WebP was generated for this one

        # already wrapped?
        before = s[max(0, m.start() - 220):m.start()]
        if '<picture' in before and '</picture>' not in before:
            skipped += 1
            continue

        indent = ''
        line_start = s.rfind('\n', 0, m.start()) + 1
        indent = s[line_start:m.start()]
        indent = indent if indent.strip() == '' else ''

        block = (f'<picture>\n{indent}  <source srcset="{stem}.webp" type="image/webp" />\n'
                 f'{indent}  {tag}\n{indent}</picture>')

        out.append(s[last:m.start()])
        out.append(block)
        last = m.end()
        local_wrapped += 1

    if local_wrapped:
        out.append(s[last:])
        if not DRY:
            io.open(path, 'w', encoding='utf-8', newline='').write(''.join(out))
        files_touched += 1
        wrapped += local_wrapped
        print(f'  {path:28} {local_wrapped} images')

print(f'\n  {wrapped} <img> wrapped across {files_touched} files'
      + (f', {skipped} already wrapped' if skipped else ''))
if DRY:
    print('  (dry run - nothing written)')
