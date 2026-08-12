# Italian proofread queue

The Italian tree is **live**, and 16 of its 24 pages are the client's own native Italian.
The other eight are not.

## Held pending your reading: the eight service pages

`it/services-social-media`, `it/services-advertising`, `it/services-website`,
`it/services-seo`, `it/services-sales-funnel`, `it/services-photo-video`,
`it/services-renders`, `it/services-catalogues`.

These are **model-produced Italian**. `.claude/rules/writing.md` is explicit that machine
translation is never shipped unproofread, so all eight are listed in `holdback.it` in
`.build/translation-status.json`. They are complete, gate-clean, and deliberately invisible:
noindex, absent from `sitemap.xml`, absent from every hreflang set, absent from `llms.txt`
and absent from the language switcher.

**Removing the eight slugs from `holdback.it` is the act of publishing them.** Do that
after reading, not before, then run the step-3 regeneration in `cutover.md`.

## What to check

- **Register.** The shipped Italian is informal `tu` throughout. These eight follow it.
- **Service names match the hub.** They were seeded from `it/services.html` on purpose:
  `Gestione Social Media`, `Gestione Sponsorizzate`, `Creazione Sito Web`, `SEO`,
  `Funnel di Vendita`, `Editing Foto e Video`, `Renders`, `Cataloghi`.
- **One known disagreement, worth settling.** `it/services.html` heads the funnel section
  `Funnel di Vendite`, while its own body prose, its FAQ, its blog link and
  `it/blog-sales-funnel.html` all say `funnel di vendita`. The eight new pages follow the
  majority form, `Funnel di Vendita`. The hub heading is the outlier. One word, one file.
- **The advertising numbers are real client figures** converted to Italian convention:
  `6.150`, `1.084.529`, `1,87`, `1,47`, `2,30`, `11.480,98`. Check the convention only.
- **Shared boilerplate.** `Cosa comprende il servizio`, `Come lavoriamo`, `A chi è adatto`,
  `Tempi e costi`, `Domande Frequenti`, `Per approfondire:`, `Raccontaci il tuo obiettivo`,
  `Tutti i servizi`. Identical across all eight by design.

## Cold review, applied

- **Sixteen `Come lavoriamo` lead-ins converted from infinitive to first person
  plural** on three pages. Four pages already used the plural, and the live
  `it/services.html` is first person plural throughout - `Gestiamo`,
  `Progettiamo`, `Creiamo`. `it/services-website.html` is correctly left nominal
  because its English heading is nominal.
- **`funnel di vendita` settled**, 49 occurrences to 3. Two edits in
  `it/services.html` and one in `it/blog-sales-funnel.html`, which had been
  labelling a link `Funnel di Vendite` that landed on a page calling itself
  `Funnel di Vendita`.
- **Seven `quasi tutti` reduced to `la maggior parte`.** English says "most";
  "almost all" is a claim this business cannot support.
- `chiamiamo ogni contatto di persona` - `di persona` means face to face, which
  contradicts a phone call.
- `it/services-catalogues.html` had dropped *with room for every product* from
  its description with 23 characters to spare. Restored.
