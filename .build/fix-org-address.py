#!/usr/bin/env python3
"""Give the Organization an address, because the site already states one.

Every contact page in all four languages says the operations hub is in Durres:

    "Our operations hub is in Durres, where a qualified team runs your
     campaigns, calls every lead and qualifies it before it reaches you."

That is a fact the business publishes about itself, in prose, in four languages,
and it appeared nowhere in the structured data. An Organization with a phone
number, an email and no location is harder for a search engine to resolve to a
real entity than one with a locality, and entity resolution is most of what
Organization markup is for.

WHAT THIS DELIBERATELY DOES NOT DO.

It does not add a LocalBusiness or ProfessionalService node. Those are schema.org
subtypes for a business customers travel to, and they carry the expectation of
opening hours, a street address and a geo point. MarketingPro is remote-first,
which the same contact page says just as plainly. Claiming a storefront to chase
a local rich result would be asserting something the business has not said, and
without a street address or opening hours it would not earn the rich result
anyway.

It does not add Albania to areaServed. The site's stated markets are Italy,
Europe and the United States, and Europe already contains Albania. Naming it
separately would be a positioning change, and positioning is the client's to
make, not mine. If they want it, it is one entry in the same list.

So: addressLocality and addressCountry, both of which are true and already
published, and nothing else.

The node is written into all four trees because #organization is ONE entity with
one @id. If the Italian tree said Durres and the Spanish tree said nothing, the
merged graph would contradict itself about a single subject.

    python .build/fix-org-address.py
"""
import glob
import io
import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAG = '<script type="application/ld+json">'
ADDRESS = {
    '@type': 'PostalAddress',
    # The Albanian spelling is the place's actual name; structured data is not
    # prose, so it does not follow the English page's unaccented "Durres".
    'addressLocality': 'Durrës',
    'addressCountry': 'AL',
}

pages = sorted(glob.glob('*.html') + glob.glob('it/*.html')
               + glob.glob('es/*.html') + glob.glob('sq/*.html'))

changed = 0
for path in pages:
    s = io.open(path, encoding='utf-8', newline='').read()
    if TAG not in s:
        continue
    i = s.index(TAG) + len(TAG)
    j = s.index('</script>', i)
    graph = json.loads(s[i:j])

    hit = False
    for node in graph['@graph']:
        if not node.get('@id', '').endswith('#organization'):
            continue
        if node.get('address') == ADDRESS:
            continue
        # Insert after email, so the contact block reads together.
        rebuilt = {}
        for k, v in node.items():
            rebuilt[k] = v
            if k == 'email':
                rebuilt['address'] = ADDRESS
        if 'address' not in rebuilt:
            rebuilt['address'] = ADDRESS
        node.clear()
        node.update(rebuilt)
        hit = True

    if not hit:
        continue
    s = (s[:i] + '\n  ' + json.dumps(graph, ensure_ascii=False, indent=2).replace('\n', '\n  ')
         + '\n  ' + s[j:])
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    changed += 1

print(f'  Organization address (Durrës, AL) written into {changed} of {len(pages)} pages')
