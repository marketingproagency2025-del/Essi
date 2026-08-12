#!/usr/bin/env python3
"""Preload the image the browser is actually going to fetch.

Eighteen page types carry an article-hero, and every one of them preloaded the
wrong file. Two separate causes, found by a translator reading the Italian
copies and noticing the head did not match the body.

  WRONG IMAGE (8 service pages x 4 trees). The service pages were generated
  from blog-seo.html as a structural shell. Head metadata, JSON-LD and <main>
  were all replaced; the preload was not. So all eight shipped

      <link rel="preload" as="image" href="assets/img/svc-seo-1.jpg" ...>

  while showing svc-social-1, clients-1, svc-web-1 and so on. That is a wasted
  high-priority download competing with the real hero, plus the real hero left
  undiscovered until the parser reaches <main>. Strictly worse than no preload.

  WRONG FORMAT (all 18 x 4 trees). Every hero is a <picture> with a WebP source
  and a JPEG fallback, so any browser made in the last several years fetches the
  .webp. The preloads all pointed at the .jpg. A browser that honoured them
  downloaded the JPEG nobody would display, then downloaded the WebP as well.
  This one predates the service pages: it arrived when <picture> was wrapped
  around heroes that already had preloads, and nothing checked the pair.

The fix is one rule: the preload names the same file the <picture> will resolve
to, and carries type="image/webp" so a browser without WebP support skips the
preload instead of fetching a file it cannot decode, falling back to the <img>.

Two pages are deliberately left alone, and neither is a miss:

  contact  - its LCP is a CSS background, not an <img>, and it already preloads
             the right WebP with the right type.
  index    - preloads hero-poster.jpg, the poster of the hero video, which is
             its real LCP. The first <img> in its <main> sits below a
             min-height:100svh hero and is correctly lazy.

    python .build/fix-preload.py            # all four trees
    python .build/fix-preload.py en         # one tree
"""
import glob
import io
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TREES = sys.argv[1:] or ['en', 'it', 'es', 'sq']
SKIP = ('index.html', 'contact.html')

PRELOAD_RX = re.compile(r'[ \t]*<link rel="preload"[^>]*as="image"[^>]*>\n')

changed = 0
checked = 0

for lang in TREES:
    prefix = '' if lang == 'en' else '../'
    for path in sorted(glob.glob('*.html' if lang == 'en' else f'{lang}/*.html')):
        if os.path.basename(path) in SKIP:
            continue
        s = io.open(path, encoding='utf-8', newline='').read()
        m = PRELOAD_RX.search(s)
        if not m:
            continue

        main = s[s.index('<main'):s.index('</main>')]
        pic = re.search(r'<picture>.*?</picture>', main, re.S)
        if not pic:
            print(f'  !! {path}: preloads an image but has no <picture> hero - skipped')
            continue
        src = re.search(r'srcset="([^"]*)"', pic.group(0))
        img = re.search(r'<img[^>]*\bsrc="([^"]*)"', pic.group(0))
        if not src or not img:
            print(f'  !! {path}: <picture> hero has no srcset or no img - skipped')
            continue
        checked += 1

        webp = src.group(1).split('/')[-1]
        indent = m.group(0)[:len(m.group(0)) - len(m.group(0).lstrip())]
        want = (f'{indent}<link rel="preload" as="image" '
                f'href="{prefix}assets/img/{webp}" type="image/webp" '
                f'fetchpriority="high" />\n')
        if m.group(0) == want:
            continue

        had = re.search(r'href="([^"]*)"', m.group(0))
        s = s[:m.start()] + want + s[m.end():]
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
        changed += 1
        print(f'  {path}: {(had.group(1).split("/")[-1] if had else "?")} -> {webp}')

print(f'\n  {changed} of {checked} hero preloads now name the file the browser will fetch')
