#!/usr/bin/env python3
"""Make every BreadcrumbList say what the visible breadcrumb says.

Ten pages carried a JSON-LD trail that disagreed with the trail printed above
the article. The visible crumb is a short label; the markup had been filled from
whatever longer string was to hand:

    visible  Advertising            markup  Advertising Campaigns
    visible  Photo and Video        markup  Photo & Video Editing
    visible  Website                markup  Website Creation
    visible  SEO                    markup  SEO in 2026: Climb the Rankings...
    visible  Transform Your Brand   markup  Transform Your Brand: Growth, Creativity...

Google's breadcrumb guidance is explicit that the markup describes the trail the
page actually shows. Where the two disagree the rich result is the thing at
risk, and the disagreement is invisible to everyone until a validator says so.

The visible trail wins, always. It is the one a reader can see and complain
about, and its labels are shorter, which is what a breadcrumb is for. So this
copies the rendered crumb text into the markup rather than the other way round.

Position and item URLs are untouched - only `name`.

    python .build/fix-breadcrumbs.py            # all four trees
    python .build/fix-breadcrumbs.py en         # one tree
"""
import glob
import html
import io
import json
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TREES = sys.argv[1:] or ['en', 'it', 'es', 'sq']
TAG = '<script type="application/ld+json">'

changed = 0
scanned = 0

for lang in TREES:
    for path in sorted(glob.glob('*.html' if lang == 'en' else f'{lang}/*.html')):
        s = io.open(path, encoding='utf-8', newline='').read()
        nav = re.search(r'<nav class="breadcrumb".*?</nav>', s, re.S)
        if not nav or TAG not in s:
            continue
        scanned += 1

        visible = [html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', li)).strip())
                   for li in re.findall(r'<li>(.*?)</li>', nav.group(0), re.S)]

        i = s.index(TAG) + len(TAG)
        j = s.index('</script>', i)
        graph = json.loads(s[i:j])

        hit = False
        for node in graph['@graph']:
            if node.get('@type') != 'BreadcrumbList':
                continue
            items = node['itemListElement']
            if len(items) != len(visible):
                print(f'  !! {path}: {len(visible)} visible crumbs, '
                      f'{len(items)} in markup - skipped, needs a human')
                continue
            for it, name in zip(items, visible):
                if it.get('name') != name:
                    it['name'] = name
                    hit = True

        if not hit:
            continue
        s = (s[:i] + '\n  ' + json.dumps(graph, ensure_ascii=False, indent=2).replace('\n', '\n  ')
             + '\n  ' + s[j:])
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
        changed += 1
        print(f'  {path}: trail -> {" / ".join(visible)}')

print(f'\n  {changed} of {scanned} pages realigned to their visible breadcrumb')
