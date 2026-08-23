#!/usr/bin/env python3
"""Measure whether the four city guides are four articles or one article with four names.

This is the check the plan demands before publishing, and it is the one thing the 24-check gate
cannot do: verify-langs.ps1 will happily pass a textbook doorway cluster. Four posts built from
one skeleton, differing only in the place name, is the failure mode search engines penalise and
readers notice, and it is the natural outcome of generating them from a shared donor.

TWO NUMBERS, and they are not the same kind of number.

  1. PAIRWISE OVERLAP is objective and reproducible: Jaccard similarity over 5-word shingles of
     the body prose, for each of the six pairs. It measures whether sentences were reused. Near
     zero is what independent articles look like; a high number is proof of templating. This is
     the number that can actually falsify the work.

  2. PLACE-ANCHORED SENTENCE RATE is a proxy, and a weak one: the share of body sentences naming
     the city, a district of it, or a neighbouring place. A sentence can name a city and say
     nothing city-specific ("marketing in Milan needs a good website"), so a high rate does not
     prove depth. It is reported because the Milan post was measured this way and the comparison
     is the point, not because it settles anything.

  What NEITHER number measures is whether the ARGUMENT is city-contingent: whether the reasoning
  would survive swapping the name. That was judged by hand when these were written, and the
  judgement is recorded in write_it_content.py: Rome argues two audiences with different
  discovery paths, Lugano argues the INVERSE of Milan's density case, Ticino argues canton scale
  and a border. Those three claims contradict each other, which is the real evidence. Do not
  read a good Jaccard score as proof of that.

Run against the Italian tree, which is the source the other three are ported from. If the source
is templated, every tree is.

    python originality.py
"""
import io
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)          # the repo root, one level above .build
CONTENT = os.path.join(_HERE, "city-content")

POSTS = ["blog-milano", "blog-roma", "blog-lugano", "blog-ticino"]

# Place tokens that make a sentence anchored to its own post's market. Districts and
# neighbouring towns count: "Prati" is as Rome-specific as "Roma", and "Mendrisiotto" is more
# Ticino-specific than "Ticino". For the two Swiss posts the country counts too, because
# being in Switzerland rather than Italy IS the specific fact those posts turn on.
PLACES = {
    "blog-milano": ["milano", "milan", "lombard"],
    "blog-roma":   ["roma", "roman", "prati", "trastevere", "monteverde",
                    "san giovanni", "eur", "centocelle"],
    "blog-lugano": ["lugano", "svizzer", "ticino", "confine", "tedesc"],
    "blog-ticino": ["ticino", "ticines", "svizzer", "bellinzona", "locarn", "mendrisiotto",
                    "chiasso", "ascona", "stabio", "como", "varese", "confine", "franch",
                    "fiduciario", "dogana"],
}


# where the prose stops in each tree: the summary heading, in that tree's own words
SUMMARY_H2 = {
    "": "The Short Version",
    "it": "In Breve",
    "es": "En resumen",
    "sq": "Shkurtimisht",
}


def body_text(slug, tree="it"):
    """The article prose only: intro and section paragraphs. Summary bullets, FAQ answers and
    navigation are excluded, so shared furniture cannot flatter the overlap score.

    Runs per tree because a translator can reintroduce templating the source does not have:
    three posts written distinctly in Italian can still come out formulaic in Albanian if the
    same stock phrase is reached for each time. Measuring only the source would miss that."""
    p = os.path.join(SITE_DIR, tree, slug + ".html") if tree else os.path.join(SITE_DIR, slug + ".html")
    s = io.open(p, encoding="utf-8").read()
    m = s[s.index('<div class="article article__body">'):
          s.index("<h2>%s</h2>" % SUMMARY_H2[tree])]
    paras = re.findall(r"<p>(.*?)</p>", m, re.S)
    txt = " ".join(re.sub(r"<[^>]+>", "", p) for p in paras)
    return re.sub(r"\s+", " ", txt).strip()


def words(t):
    return re.findall(r"[a-zà-ÿ']+", t.lower())


def shingles(t, n=5):
    w = words(t)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?]) +", t) if len(s.strip()) > 20]


def main(tree="it"):
    texts = {}
    for slug in POSTS:
        p = os.path.join(SITE_DIR, tree, slug + ".html") if tree else os.path.join(SITE_DIR, slug + ".html")
        if not os.path.exists(p):
            sys.exit(f"  ! {p} does not exist yet")
        texts[slug] = body_text(slug, tree)

    print(f"  [{tree or 'en'}] post       words   place-anchored sentences")
    for slug in POSTS:
        sents = sentences(texts[slug])
        toks = PLACES[slug]
        hit = [s for s in sents if any(t in s.lower() for t in toks)]
        pct = 100.0 * len(hit) / len(sents) if sents else 0
        print(f"  {slug:14} {len(words(texts[slug])):5}   {len(hit):2}/{len(sents):2} "
              f"= {pct:4.1f}%")

    print()
    print("  pairwise 5-gram overlap (Jaccard, body prose only)")
    worst = 0.0
    for i, a in enumerate(POSTS):
        for b in POSTS[i + 1:]:
            sa, sb = shingles(texts[a]), shingles(texts[b])
            j = 100.0 * len(sa & sb) / len(sa | sb) if (sa | sb) else 0
            worst = max(worst, j)
            flag = "" if j < 3 else ("  <- TEMPLATED" if j >= 8 else "  <- check")
            print(f"    {a[5:]:8} vs {b[5:]:8}  {j:5.2f}%{flag}")

    print()
    print(f"  worst pair: {worst:.2f}%")
    if worst >= 8:
        print("  VERDICT: templated. These are not four articles. Do not publish.")
        return 1
    if worst >= 3:
        print("  VERDICT: some shared phrasing. Read the flagged pair before publishing.")
        return 0
    print("  VERDICT: no meaningful sentence reuse between any pair.")
    print("  (Argument-level distinctness is a human judgement, not this number. See the")
    print("   docstring in write_it_content.py for what each post actually argues.)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "it"))
