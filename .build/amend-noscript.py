#!/usr/bin/env python3
"""Update the <noscript> fallback in every page that already has one.

fix-noscript.py INJECTS the block and is deliberately `if '<noscript>' in s: skip`, so it is
idempotent but cannot revise a block once written. The portfolio's new case-row motion hides
.split__media and the .split__text children by default, and anything hidden by default has to be
lifted here too or a visitor with JS off loses the case content entirely, which is the exact bug
fix-noscript.py exists to prevent.

Two fixes ride along:

  the accent-bar line was dead. `.reveal .section__title::after` scores (0,2,1) and loses to
  `.reveal:not(.in-view) .section__title::after` at style.css:752, which scores (0,3,1).
  Specificity beats source order, so with JS off the bar stayed collapsed. Matching the
  selector exactly makes source order the tie-break, and this block is emitted after the
  stylesheet link, so it now wins.

  the gallery reveal moved off the two rows and onto the six items, so the fallback covers
  .gallery__item through the .reveal rule it already carries.

Idempotent: pages already carrying the new block are left alone.

    python .build/amend-noscript.py
"""
import io
import os

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREES = ("", "it", "es", "sq")

OLD = """  <noscript>
    <style>
      /* main.js adds .in-view to lift .reveal. Without it the page would be blank. */
      .reveal { opacity: 1; transform: none; }
      .reveal .section__title::after { transform: scaleX(1); }
    </style>
  </noscript>"""

NEW = """  <noscript>
    <style>
      /* main.js adds .in-view to lift .reveal. Without it the page would be blank. */
      .reveal { opacity: 1; transform: none; }
      .reveal:not(.in-view) .section__title::after { transform: scaleX(1); }
      .feature-row.reveal:not(.in-view) .split__media,
      .feature-row.reveal:not(.in-view) .split__text > * { opacity: 1; transform: none; }
      .feature-row .case-frame--grid { transform: none; }
    </style>
  </noscript>"""

changed = skipped = 0
for tree in TREES:
    d = os.path.join(SITE, tree) if tree else SITE
    for name in sorted(os.listdir(d)):
        if not name.endswith(".html"):
            continue
        p = os.path.join(d, name)
        s = io.open(p, encoding="utf-8", newline="").read()
        if NEW in s:
            skipped += 1
            continue
        if OLD not in s:
            raise SystemExit("  ! %s: noscript block is not the shape this script expects"
                             % os.path.relpath(p, SITE))
        io.open(p, "w", encoding="utf-8", newline="").write(s.replace(OLD, NEW, 1))
        changed += 1

print("  %d pages amended, %d already current" % (changed, skipped))
