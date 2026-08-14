#!/usr/bin/env python3
"""Make the Organization a local business in Albania, because the client said to.

fix-org-address.py records the earlier position: no LocalBusiness subtype and no
Albania in areaServed, because both were positioning changes that belonged to the
client. On 2026-08-15 the client made them, twice-confirmed: rank in Albania and
Italy first, full Durrës local presence. So this script does exactly the two
things that one declined to do, and nothing it warned against doing without data
we still do not have:

  1. #organization becomes ["Organization", "ProfessionalService"] on all 96
     pages. ProfessionalService is a LocalBusiness subtype, so this states "a
     professional service business located somewhere" - which Durrës,
     city-precision, already in the node, supports. One entity, one @id; the
     type changes everywhere or the merged graph contradicts itself.

  2. Albania joins areaServed - the Organization node (as a Country object),
     contactPoint.areaServed (as a string, matching its existing strings), and
     every Service node on the 32 service pages.

STILL DELIBERATELY ABSENT: street address, opening hours beyond the published
9-5 line, and a geo point - none supplied. Without them no local-pack rich
result will be earned, and nothing here pretends otherwise. When the client
sends a street address, extend ADDRESS here and re-run.

Serialization matters: gate check 8 compares availableLanguage as an exact
single-line string, so this uses the same parse -> mutate in place ->
json.dumps(indent=2) rebuild as fix-org-address.py, which is proven to satisfy
it.

    python .build/fix-geo-schema.py
"""
import glob
import io
import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAG = '<script type="application/ld+json">'
ALBANIA = {'@type': 'Country', 'name': 'Albania'}

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

        if node.get('@id', '').endswith('#organization'):
            if types != ['Organization', 'ProfessionalService']:
                node['@type'] = ['Organization', 'ProfessionalService']
                hit = True
            area = node.get('areaServed', [])
            if ALBANIA not in area:
                area.append(ALBANIA)
                node['areaServed'] = area
                hit = True
            cp = node.get('contactPoint', {})
            cpa = cp.get('areaServed', [])
            if 'Albania' not in cpa:
                cpa.append('Albania')
                cp['areaServed'] = cpa
                hit = True
            if hit:
                orgs += 1

        if 'Service' in tlist and not node.get('@id', '').endswith('#organization'):
            area = node.get('areaServed', [])
            if ALBANIA not in area:
                area.append(ALBANIA)
                node['areaServed'] = area
                services += 1
                hit = True

    if not hit:
        continue
    s = (s[:i] + '\n  ' + json.dumps(graph, ensure_ascii=False, indent=2).replace('\n', '\n  ')
         + '\n  ' + s[j:])
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    changed += 1

print(f'  {changed} pages rewritten: {orgs} Organization nodes dual-typed + Albania, '
      f'{services} Service nodes gained Albania')
