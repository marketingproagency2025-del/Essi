#!/usr/bin/env python3
"""Stop the LCP element being discovered late, on the pages where it is.

Two distinct problems, and only these pages have them:

  contact  - its LCP is .contact-hero's CSS background-image, so the browser
             cannot see it until style.css has downloaded, parsed and matched.
             Longest discovery chain on the site. Fixed with a preload.

  services, portfolio, blog, about
           - these four have NO hero element, so content starts near the top of
             the viewport and their first content image is very likely inside
             it. All four marked that image loading="lazy", which is the
             textbook way to delay your own LCP. Fixed by making the first
             content image eager and high priority.

index is deliberately untouched: .hero is min-height:100svh, so its first
content image really is below the fold and correctly lazy, and its true LCP
(hero-poster.jpg) is already preloaded with fetchpriority="high".

    python .build/fix-lcp.py
"""
import io
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TREES = {'en': '', 'it': 'it/', 'es': 'es/', 'sq': 'sq/'}
EAGER = ('services', 'portfolio', 'blog', 'about')

changed = 0

for lang, pre in TREES.items():
    asset = '' if lang == 'en' else '../'

    # 1. contact: preload the CSS background that is the LCP element
    path = f'{pre}contact.html'
    s = io.open(path, encoding='utf-8', newline='').read()
    if 'contact-hero.jpg" fetchpriority' not in s:
        anchor = '  <link rel="manifest" href='
        i = s.find(anchor)
        if i == -1:
            sys.exit(f'  !! manifest link not found in {path}')
        end = s.index('\n', i) + 1
        block = ('\n  <!-- LCP: the hero is a CSS background, so it is invisible to the\n'
                 '       preload scanner until style.css has parsed. -->\n'
                 f'  <link rel="preload" as="image" href="{asset}assets/img/contact-hero.jpg" fetchpriority="high" />\n')
        s = s[:end] + block + s[end:]
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
        print(f'  {path:20} preloaded contact-hero.jpg')
        changed += 1

    # 2. the four heroless pages: first content image eager + high priority
    for slug in EAGER:
        path = f'{pre}{slug}.html'
        s = io.open(path, encoding='utf-8', newline='').read()
        if 'fetchpriority' in s:
            continue
        head, sep, body = s.partition('<main')
        if not sep:
            sys.exit(f'  !! no <main> in {path}')
        m = re.search(r'<img[^>]*>', body)
        if not m:
            continue
        tag = m.group(0)
        new = tag.replace(' loading="lazy"', '')
        if 'fetchpriority' not in new:
            new = new.replace('<img ', '<img fetchpriority="high" ', 1)
        body = body[:m.start()] + new + body[m.end():]
        io.open(path, 'w', encoding='utf-8', newline='').write(head + sep + body)
        src = re.search(r'src="([^"]*)"', new)
        print(f'  {path:20} eager LCP: {src.group(1).split("/")[-1]}')
        changed += 1

print(f'\n  {changed} pages updated')
