# Spanish proofread punch list

Raised by the review pass and deliberately **not** resolved, because each needs a native
ear or a client call rather than a rule. Work through this before the Spanish tree goes
live. Most items are defensible as written; the question is whether a native speaker
would have written them.

Covers the six core pages. The ten blog pages are appended as they complete.

## Decide once, applies to the whole tree

**1. `vídeo` or `video`.** This is the biggest neutrality call in the tree.
`.build/guide-es.md` fixes `vídeo` with the accent, which is the Spain spelling; Latin
America and US Hispanic readers write `video`. Both are correct per the RAE. The site
targets Europe *and* the United States, so whichever is chosen leaves one audience
slightly off. It appears in the services page headings, the photo/video service, and
several alt texts, so it is a one-line guide change plus a sweep, not a per-page fix.

**2. Heading case.** Headings use English-style Title Case (`Gestión de Redes Sociales`,
`Crecimiento Creativo`, `Éxito de los Clientes`), mirroring the English and Italian trees.
Spanish convention capitalises only the first word. Changing it is a tree-wide sweep and
would make Spanish differ from the other three trees, so it is a deliberate choice either
way. **The same question is open on Albanian**, so decide both together.

**3. `og:locale` is `es_ES` while `hreflang` is plain `es`.** The locale carries a Spain
territory tag on copy that is deliberately region-neutral. It parallels `it_IT` on the
Italian page so it is probably fine, and Open Graph has no neutral Spanish value, but it
is worth one look. Changing it means editing `$LANGS.es.locale` in `.build/lib-chrome.ps1`
and regenerating; do not hand-edit pages.

**4. `storytelling`** survives in an article card excerpt. It is standard Spanish
marketing jargon but is not on the guide's keep-in-English list. Either add it to the list
or replace it.

## Region-marked words that survived

Each was kept as the most widely understood option, but a native reader may disagree.

| Page | Word | Note |
|---|---|---|
| services | `gafas de sol` | Spain-marked. Mexico says `lentes de sol`. In an `alt`, so low stakes. |
| portfolio | `Buganvilla` | Spain-preferred spelling. Mexico writes `bugambilia`, and `buganvilia` is the neutral middle. |
| services | `tazón` | Replaced Spain's `bol`. Understood in both Spain and Mexico; confirm it is the natural word for the bowl in that photograph. |
| contact | `día hábil` | Chosen over Spain's `día laborable` for neutrality. Confirm it reads naturally to a Spain reader. |
| contact | `Con gusto lo hablamos` | Leans Latin American. Spain might prefer `Encantados de hablarlo`. |

## Individual phrasings to read aloud

| Page | Phrase | Why it is flagged |
|---|---|---|
| index | `Prospección` for "Outreach" | Standard sales vocabulary and neutral, but it is jargon. Confirm the register suits a card title aimed at business owners. |
| index | `zona de descanso al sol` (alt) | Generalises "sun loungers" because `tumbonas`, `reposeras` and `camastros` are each region-locked. A native may want something more concrete. |
| index | `Hablemos` for the contact CTA | Changed from `Conectemos` during review. Both work; a tone call. |
| portfolio | `Un salto de danza recortado contra un cielo intenso de atardecer` (alt) | Deliberately avoids gendering the dancer, where English says "a dancer leaping". Confirm it still reads as a description of the photo rather than of an abstract movement. |
| about | `azul infinito` for "open blue" | Replaced the calque `azul abierto`. Poetic; confirm the register suits the brand. |
| contact | FAQ 4, `¿Qué pasa después de escribirles?` | The reader addresses the agency as `ustedes` while the answer replies in `nosotros`/`tú`. Grammatical and consistent with the languages FAQ, but a native may prefer `escribirnos`. **If changed it must change in BOTH the JSON-LD and the `<details>` block**, or the gate fails. |

## Resolved, listed so nobody re-opens them

- **`calificar` is the brand term.** The first pass split the qualify-family three ways:
  `filtrados` on the homepage, `calificados` on services, `cualificado` on about. English
  uses qualify/qualified/qualification 28 times and the word "filter" exactly once, in the
  hero "We Call, Filter, and Deliver". Spanish now mirrors that split exactly, and it is
  pinned in the guide.
- **The founder's title carries no grammatical gender.** Client decision. Use verbs, never
  `Fundador`/`Fundadora`, and no adjective or participle that would have to agree.
- **`"inLanguage": ["en", "it"]` on Spanish pages is correct**, not a defect. It states
  which languages the *site* is published in, and Spanish is not published yet.
  `availableLanguage` already lists all four because it describes the team.
- **`noindex, follow` and no `hreflang="es"` self-reference** are deliberate staging.
- **The ad-results table headers on `services`** stay English on purpose: they mimic a
  Meta Ads Manager screenshot, and the Italian page does the same.
