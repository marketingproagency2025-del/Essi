#!/usr/bin/env python3
"""Add Switzerland to areaServed, because the client said to.

fix-geo-schema.py records the shape of this decision: adding a market to areaServed is a
positioning change that belongs to the client, not to whoever is editing. On 2026-08-23 the
client asked for it, in the course of commissioning guides aimed at Lugano and Ticino. Both
are in Switzerland, and the site had never named the country: areaServed carried Italy,
Europe, United States and Albania, so a page titled for a Swiss city would have told a Swiss
reader they were a residual of "Europe".

So this does for Switzerland exactly what fix-geo-schema.py did for Albania:

  1. Switzerland joins the Organization's areaServed as a Country object.
  2. Switzerland joins contactPoint.areaServed as a string, matching its existing strings.
  3. Switzerland joins every Service node on the 32 service pages.

STILL DELIBERATELY ABSENT: any Swiss address, phone number or geo point. There is none, and
none is invented here. Without them no Swiss local-pack result is earned, and the Lugano and
Ticino guides must not imply otherwise.

Serialization matters: gate check 9 compares inLanguage and availableLanguage as exact
single-line strings, so those two arrays are collapsed back onto one line after
json.dumps(indent=2) expands them. Same parse -> mutate in place -> rebuild as
fix-geo-schema.py, which is proven to satisfy the gate.

    python .build/add-swiss-market.py
"""
import glob
import io
import json
import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAG = '<script type="application/ld+json">'
SWITZERLAND = {'@type': 'Country', 'name': 'Switzerland'}


def collapse_lang_arrays(s):
    """inLanguage and availableLanguage live on one line; every other array stays expanded."""
    def fix(m):
        items = re.findall(r'"([^"]*)"', m.group(2))
        return '"%s": [%s]' % (m.group(1), ', '.join('"%s"' % i for i in items))
    return re.sub(r'"(inLanguage|availableLanguage)":\s*\[([^\]]*)\]', fix, s)


pages = sorted(glob.glob('*.html') + glob.glob('it/*.html')
               + glob.glob('es/*.html') + glob.glob('sq/*.html'))

changed = orgs = services = 0
for path in pages:
    s = io.open(path, encoding='utf-8', newline='').read()
    if TAG not in s:
        continue
    i = s.index(TAG) + len(TAG)
    j = s.index('</script>', i)
    graph = json.loads(s[i:j])

    hit = False
    for node in graph['@graph']:
        types = node.get('@type')
        tlist = types if isinstance(types, list) else [types]

        if str(node.get('@id', '')).endswith('#organization'):
            area = node.get('areaServed', [])
            if SWITZERLAND not in area:
                area.append(SWITZERLAND)
                node['areaServed'] = area
                hit = True
            cp = node.get('contactPoint', {})
            cpa = cp.get('areaServed', [])
            if cpa and 'Switzerland' not in cpa:
                cpa.append('Switzerland')
                cp['areaServed'] = cpa
                hit = True
            if hit:
                orgs += 1

        if 'Service' in tlist and not str(node.get('@id', '')).endswith('#organization'):
            area = node.get('areaServed', [])
            if SWITZERLAND not in area:
                area.append(SWITZERLAND)
                node['areaServed'] = area
                services += 1
                hit = True

    if not hit:
        continue
    body = collapse_lang_arrays(json.dumps(graph, ensure_ascii=False, indent=2)).replace('\n', '\n  ')
    s = s[:i] + '\n  ' + body + '\n  ' + s[j:]
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    changed += 1

print(f'  {changed} pages rewritten: {orgs} Organization nodes gained Switzerland, '
      f'{services} Service nodes gained Switzerland')
