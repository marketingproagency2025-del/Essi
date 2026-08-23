#!/usr/bin/env python3
"""Make every page readable when JavaScript does not run.

THE BUG. .reveal sets opacity:0 and the class .in-view that undoes it is added only by
assets/js/main.js. If that script does not run, the opacity:0 is never lifted and the content
stays invisible for good. It is not a degraded experience, it is a blank page: with JS off the
blog index shows 0 of 14 cards, 0 of 3 group headings and no <h1>, and /services hides 29
elements. Only pages with no .reveal at all (the article pages) are unaffected.

That is a real mobile failure mode, not a hypothetical: content blockers, privacy browsers and
locked-down corporate proxies all stop scripts, and a visitor sees an empty page rather than a
slow one.

THE FIX. A <noscript> block in the head restoring the end state of the animation. It costs
nothing when scripts run, because the browser ignores it entirely, and it needs no inline
script, no extra request and no change to main.js.

Deliberately NOT using a .js class toggled from a blocking head script, which is the other
standard answer. It would also cover "JS is on but main.js failed to download", but it needs a
new render-blocking request on all 112 pages and inline script the site does not otherwise use.
The noscript block covers the common cases at a fraction of the cost; if the harder case ever
matters, that is the upgrade path.

Idempotent.

    python .build/fix-noscript.py
"""
import glob
import io
import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BLOCK = ('  <noscript>\n'
         '    <style>\n'
         '      /* main.js adds .in-view to lift .reveal. Without it the page would be blank. */\n'
         '      .reveal { opacity: 1; transform: none; }\n'
         '      .reveal .section__title::after { transform: scaleX(1); }\n'
         '    </style>\n'
         '  </noscript>\n')

pages = sorted(glob.glob('*.html') + glob.glob('it/*.html')
               + glob.glob('es/*.html') + glob.glob('sq/*.html'))

done = skipped = 0
for p in pages:
    s = io.open(p, encoding='utf-8', newline='').read()
    if '<noscript>' in s:
        skipped += 1
        continue
    m = re.search(r'^  <link rel="stylesheet" href="[^"]*" />\n', s, re.M)
    if not m:
        raise SystemExit(f'  ! {p}: no stylesheet link to anchor to')
    s = s[:m.end()] + BLOCK + s[m.end():]
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    done += 1

print(f'  {done} pages given a noscript fallback, {skipped} already had one '
      f'({len(pages)} total)')
