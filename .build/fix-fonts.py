#!/usr/bin/env python3
"""Drop the Google Fonts requests and preload the self-hosted font instead.

Before, in every one of the 64 heads:

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:..." rel="stylesheet" />
    <link rel="stylesheet" href="assets/css/style.css?v=12" />

Two problems. The render-blocking third-party stylesheet sat BEFORE the
same-origin one, so the browser had to resolve, connect to and fetch
googleapis before it could even begin the CSS it definitely needed. And the
font itself lived behind a second hop to gstatic, discovered only once that
stylesheet arrived.

After:

    <link rel="preload" href="assets/fonts/dm-sans-latin.woff2" as="font"
          type="font/woff2" crossorigin />
    <link rel="stylesheet" href="assets/css/style.css?v=13" />

The upright font is preloaded because every page paints upright text
immediately; the italic file is left to load on demand, since italics are rare
and never in the hero. crossorigin is required on font preloads even
same-origin, or the preload is discarded and fetched twice.

    python .build/fix-fonts.py
"""
import glob
import io
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The "<!-- Fonts: DM Sans -->" comment is present on some pages and not others,
# so it is optional here rather than required.
BLOCK_RX = re.compile(
    r'(?:[ \t]*<!-- Fonts: DM Sans -->\n)?'
    r'(?:[ \t]*<link[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>\n)+'
)

pages = (glob.glob('*.html') + glob.glob('it/*.html')
         + glob.glob('es/*.html') + glob.glob('sq/*.html'))

changed = 0
for path in sorted(pages):
    s = io.open(path, encoding='utf-8', newline='').read()
    if 'fonts.googleapis.com' not in s:
        continue
    prefix = '' if os.path.dirname(path) == '' else '../'
    replacement = (
        '  <!-- Fonts: DM Sans, self-hosted. crossorigin is required on font\n'
        '       preloads even same-origin, or the file is fetched twice. -->\n'
        f'  <link rel="preload" href="{prefix}assets/fonts/dm-sans-latin.woff2"'
        ' as="font" type="font/woff2" crossorigin />\n'
    )
    new, n = BLOCK_RX.subn(replacement, s)
    if n != 1:
        print(f'  !! font block matched {n} times in {path}')
        sys.exit(1)
    io.open(path, 'w', encoding='utf-8', newline='').write(new)
    changed += 1

print(f'  {changed} pages: Google Fonts removed, self-hosted font preloaded')
