# Albanian proofread punch list

Everything here was raised by the review pass and deliberately **not** resolved, because
it needs a native ear rather than a rule. This is the list to work through before the
Albanian tree goes live. It is not a list of known errors: most of these are defensible
as written, and the question is whether a native speaker would have written them.

Grouped so one decision can be applied everywhere, rather than page by page.

## Decide once, applies to all 16 pages

**1. Plural and inflection of English loanwords.** The guide keeps `lead`, `funnel`,
`render`, `brand`, `newsletter` in English with Albanian endings, following the corpus
convention (`cookie-t`). The translators settled on `lead-e` / `lead-et` with feminine
plural agreement (`lead-e të kualifikuara`), by analogy with `vend`/`vende`. Also in
use: `funnel-eve`, `funnel-e`, `render-et`, `brand-e`, `copywriting-u`, `storytelling-ut`.
Confirm the stems and the agreement they trigger. Whatever is chosen must be uniform.

**2. Heading case.** All H2s currently use English-style Title Case
(`SEO është Mirëmbajtje, jo Magji`). Standard Albanian uses sentence case for headings.
This was left consistent with the rest of the tree rather than changed on one page.
If it should be sentence case, it is a tree-wide sweep.

**3. The Cyclades.** Rendered `ishujt Kiklade`. Albanian usage varies between *Kikladet*,
*Qikladet* and *Kikladhet*. Whatever is picked, the adjective in two `alt` texts
(`growth.jpg`, `who-we-are.jpg`) must agree with it.

**4. "vanity metric".** Currently `matje kotësie e maskuar`. No settled Albanian term;
`metrikë kotësie` is the alternative. Recurs across several posts.

**5. SEO "relevance".** Rendered `përshtatshmëria` twice. `relevanca` (loanword) or
`përputhshmëria` are alternatives.

**6. `social media`.** Kept as the English loanword per the guide, giving
`Menaxhim i social media` uninflected. `Menaxhim i rrjeteve sociale` is the natural
Albanian. The guide's loanword rule currently wins; confirm that is right for a
marketing agency selling the service.

**7. Place names.** `Chicago` is transliterated `Cikago`, pairing with `Milano`.
Confirm place names should be localised rather than left in their original spelling.

**8. `font`.** Introduced as a loanword, replacing a genuine mistranslation
(`shkronjë`). Not on the guide's approved list, which is explicitly non-exhaustive.

**9. `articleSection` and `keywords` (RESOLVED, listed for the record).** These were
left English while the Italian tree localised them. Now localised in Albanian too,
keeping the approved loanwords (`SEO`, `social media`, `lead`, `funnel`, `render`,
`brand`, `web design`, `landing page`) in English. Worth a glance to confirm the phrases
read naturally as topic labels.

## Individual phrasings to read aloud

| Page | Phrase | Why it is flagged |
|---|---|---|
| index | `Lindur nga qartësia, udhëhequr nga rezultatet.` | Bare participles with no preposed article. Stricter would be `E lindur…, e udhëhequr…`, but that presumes a feminine subject the sentence never names. Left as slogan register. |
| index | three commas before `dhe` | Joining independent clauses with different subjects. Albanian permits it; a native may prefer to drop them. |
| services | `Menaxhimi i Reklamave` for "Ad Campaigns" | Renders it as *management* rather than *campaigns*, mirroring what Italian did (`Gestione Campagne Sponsorizzate`). Confirm that is the intended offer name. |
| services | `Koktejë verorë freskues` (alt) | Plural of `koktej` and the resulting adjective agreement are internally consistent but not obviously standard. |
| services | `Sfond i bardhë ose me sfond` | Faithfully mirrors an odd English source line, "White background or with a background". **Fix the English first**, then retranslate. |
| portfolio | `Integrime të Përsosura` for "Seamless Integrations" | Reads as *perfect* rather than *without visible joins*. Matches Italian `Integrazioni Perfette`. |
| portfolio | `Një balerinë` (alt, port-success) | Makes the dancer female where English "dancer" is neutral. `kërcen` is closer to *dances* than *leaping*. |
| portfolio | `që shikon përtej një muri prej guri` (alt, port-6) | Loses the *peeking* nuance the English and Italian both carry. |
| portfolio | `5 yje nga 5` | Confirm this is the natural phrasing for "5 out of 5 stars". |
| portfolio | `Klient i Kënaqur` for "Happy Client" | A placeholder byline rather than a real name, so it was localised and the avatar initials updated `HC` to `KK`. Confirm localising it is wanted. |
| blog-social-media | `ngulitin në kujtesë` | Idiomatic to the reviewer; the original had a broken subject and could not stand. |
| blog-social-media | `e heshtin shpejt vetë ndjekësit` for "mute an account" | No settled Albanian rendering. `e shpërfillin` or `i heqin zërin` are alternatives. The original `heshtet shpejt` was wrong: intransitive *to fall silent*, not *to be muted*. |
| blog-social-media | `Ndjekësit janë gjë e mirë` | Slightly colloquial against the business-owner tone. |
| blog-social-media | `shpenzoni kohë që nuk ju tepron` | Confirm it beats a literal `kohë që nuk e keni`. |
| blog-social-media | FAQ 1, `Si i sjell realisht klientët social media?` | Subject last. Grammatical but momentarily ambiguous. Rewording means touching the JSON-LD and the `<details>` block in lockstep. |
| blog-website | `rrëshqitje fotosh` / `bazament` | For "slideshow" and "groundwork". Reviewer was not confident these are what a native would reach for. |
| blog-website | `Së pari telefoni:` for "Mobile first" | Alternatives: `Telefoni në radhë të parë:` or keeping the English term. |
| blog-seo | `Fjala kyçe këtu është *fitoj*` | 1sg citation form, the dictionary convention. In running prose `fitohet` or `ta fitosh` may read better. |
| blog-seo | `sepse aty ndodhin shumica e kërkimeve` | Plural agreement with `shumica`. Common usage; a prescriptivist wants singular `ndodh`. |
| blog-sales-funnel | `vë firmën në një kontratë` | Confirm the collocation. `firmos kontratën` and `nënshkruan kontratën` are alternatives, and the meta description on the same page already uses `nënshkruan kontratën`. |
| blog-photo-video | `foto me kokrra` for "grainy" | Appears three times: prose plus both FAQ copies. Possibly calque-y; `me kokrriza` or `me zhurmë` are alternatives. Changing it means editing the JSON-LD answer and the `<details>` answer together so they stay identical. |
| blog-photo-video | `Psikologët e quajnë efekt halo` | A native may prefer `efekti i halos`, or a short gloss. |
| blog-photo-video | `një zë i keq duket më i lirë se një pamje e keqe` | Uses `duket` (looks/seems) of sound. Acceptable, but worth an ear. |
| blog-photo-video | `një sy i qëndrueshëm` for "a consistent eye" | Serviceable, may read mechanical. |
| blog-renders | `mbi projekt` for "off-plan" | Albanian real-estate copy more often says `në projekt`. Appears in the bullet list and in FAQ 3, so it must change in both to keep the FAQ pair in sync. |
| blog-renders | `finiturat` for "finishes" | An Italian loan current in Albanian construction jargon. Fine for a builder-facing page, possibly too technical for general marketing prose. Alternatives: `veshjet`, `përfundimet`. |
| blog-renders | H2 `I Kapin Gabimet para se t'ju Kushtojnë` | Opens with an object clitic. Grammatical (standard clitic doubling) but unusual as a heading; confirm it does not read truncated. |
| blog-catalogues | `finiturë` for a print finish | Italianate trade term. Confirm it beats `përpunim` for an Albanian business audience. |
| blog-catalogues | `arnë shabllonesh`, `pushon së qeni dokument reference` | Two idioms carried over from the first pass; both want a native check. |
| article-1 | `një buxhet marketingu plot aktivitet` | For "a busy marketing budget". Sense is right; a native may have a better idiom. |
| article-1 | `dhe, gjithnjë, pjesa që…` | Renders an English aside. Correct, but the parenthetical rhythm may read flatter in Albanian. |
| article-1 | `Fija që lidh gjithçka që bëjmë` | Confirm the "thread" metaphor carries in Albanian business prose. |
| article-1 | H1 ends `rritje, kreativitet dhe strategji së bashku` | Changed from a participle for safety. Confirm it still lands as a headline, not a fragment. |
| article-2 | `punë të rezervuar` for "booked work" | Slightly literal. `punë konkrete` or `porosi` are alternatives. |
| article-2 | `shfaqjet` for advertising "impressions" | Confirm Albanian marketers use this rather than keeping `impressions` as a loanword. |

## Not defects, so do not "fix" them

- **`"inLanguage": ["en", "it"]` on Albanian pages.** Correct. It states which languages
  the *site* is published in, and Albanian is not published yet. It becomes
  `["en", "it", "sq"]` automatically when the tree is marked live in
  `.build/translation-status.json`. `availableLanguage` already lists all four because
  that describes the team, not the site.
- **`noindex, follow` and no `hreflang="sq"` self-reference.** Deliberate staging, so an
  unfinished translation cannot be indexed or offered in the language switcher.
- **English `areaServed`, `knowsAbout`, `contactType`.** Machine-readable schema fields.
  The Italian tree leaves these English too, correctly.
- **The ad-results table headers on `services`.** Left English on purpose: they mimic a
  Meta Ads Manager screenshot, and the Italian page does the same.
