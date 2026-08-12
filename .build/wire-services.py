#!/usr/bin/env python3
"""Wire the eight service pages into the site so they are not born orphaned.

Three edits, all four trees:

1. Each guide's "Related service" line (added in 3811c22) currently points at
   /services#anchor. It now points at the dedicated page. The guide and its
   service page link to each other, which is what stops the commercial and
   informational pages competing for the same query.

2. services.html gains a link to each service page from its own section, so the
   hub actually leads somewhere. The existing #anchor targets are untouched, so
   nothing that already links to them breaks and no redirect is needed.

3. The Service JSON-LD nodes are removed from services.html, because each now
   lives on the page it describes. The ItemList stays on the hub and its items
   point at the new URLs.

    python .build/wire-services.py
"""
import io
import json
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# anchor id -> new slug
PAIR = {
    'social-media': 'services-social-media', 'advertising': 'services-advertising',
    'website': 'services-website',           'seo': 'services-seo',
    'sales-funnel': 'services-sales-funnel', 'photo-video': 'services-photo-video',
    'renders': 'services-renders',           'catalogues': 'services-catalogues',
}
GUIDE = {'blog-' + k if k != 'website' else 'blog-website': v for k, v in PAIR.items()}
GUIDE = {f'blog-{k}': v for k, v in PAIR.items()}

TREES = {'en': '', 'it': 'it/', 'es': 'es/', 'sq': 'sq/'}
# "See the service" line label per language, matching the Related service label
# already in use on those pages.
SEE = {'en': 'See the service', 'it': 'Scopri il servizio',
       'es': 'Ver el servicio', 'sq': 'Shihni sherbimin'}

changed = 0

for lang, pre in TREES.items():
    prefix = '' if lang == 'en' else f'/{lang}'

    # --- 1. guides point at the dedicated page ---------------------------
    for anchor, slug in PAIR.items():
        path = f'{pre}blog-{anchor}.html'
        if not os.path.isfile(path):
            continue
        s = io.open(path, encoding='utf-8', newline='').read()
        old = f'href="{prefix}/services#{anchor}"'
        new = f'href="{prefix}/{slug}"'
        if old not in s:
            continue
        s = s.replace(old, new)
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
        changed += 1

    # --- 2. hub links out to each service page ---------------------------
    path = f'{pre}services.html'
    s = io.open(path, encoding='utf-8', newline='').read()
    for anchor, slug in PAIR.items():
        if f'href="{prefix}/{slug}"' in s:
            continue
        m = re.search(r'(id="' + anchor + r'"[^>]*>.*?<p class="service__desc">)(.*?)(</p>)', s, re.S)
        if not m:
            print(f'  !! no service__desc for #{anchor} in {path}')
            sys.exit(1)
        add = f' <a href="{prefix}/{slug}">{SEE[lang]}</a>.'
        s = s[:m.end(2)] + add + s[m.end(2):]
        changed += 1
    io.open(path, 'w', encoding='utf-8', newline='').write(s)

    # --- 3. Service nodes move off the hub; ItemList points at the pages --
    s = io.open(path, encoding='utf-8', newline='').read()
    i = s.index('<script type="application/ld+json">')
    j = s.index('</script>', i)
    head = s[:i + len('<script type="application/ld+json">')]
    graph = json.loads(s[i + len('<script type="application/ld+json">'):j])

    graph['@graph'] = [n for n in graph['@graph'] if n.get('@type') != 'Service']
    for node in graph['@graph']:
        if node.get('@type') == 'ItemList':
            for it in node.get('itemListElement', []):
                u = it.get('url', '')
                mm = re.search(r'#([a-z-]+)$', u)
                if mm and mm.group(1) in PAIR:
                    it['url'] = f"https://www.marketingpro-agency.com{prefix}/{PAIR[mm.group(1)]}"
    s = head + '\n  ' + json.dumps(graph, ensure_ascii=False, indent=2).replace('\n', '\n  ') + '\n  ' + s[j:]
    io.open(path, 'w', encoding='utf-8', newline='').write(s)

print(f'  {changed} links rewired; Service nodes moved off the four hubs')
