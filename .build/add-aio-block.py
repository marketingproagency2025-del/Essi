#!/usr/bin/env python3
"""Add the AI search block to the four shipped services-seo.html pages.

WHY BY HAND AND NOT BY REGENERATING. gen-service-pages.py carries the same block, in
its own docstring's terms, so a future repaired regeneration keeps it. But running that
script today regresses all eight English service pages: it rewrites hreflang from the
blog-seo shell and never repoints it, and service-content.py is behind the shipped title
and description. That was measured on 2026-09-03 by running it and reading the diff. So
the shipped HTML is the source of truth and this edits it.

WHERE THE BLOCK GOES, and it is not a matter of taste. Gate check 23 reads the service
pages' <h2> elements BY INDEX: [0] is the covers heading and the last three are
who-suits, pricing and FAQ, compared across all eight pages in each tree. A heading that
exists on one page of eight is not boilerplate, so it may only be inserted between the
first heading and who-suits. Anchored on each tree's "How we work" heading, which sits
in that window in all four.

Idempotent.

    python .build/add-aio-block.py
"""
import io
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)

MARK = "AIO"          # already present means already done
IND = " " * 10        # the body indentation these pages use

BLOCKS = {
    "": dict(
        anchor="How we work",
        h2="AI search, also sold as AIO or AEO",
        paras=[
            "Buyers increasingly open an assistant before a search engine, and what comes back is a handful of names, already chosen. Nothing tells you when yours is not among them.",
            "This is not a separate product and it is not sold here as one. It is the same work "
            "the rest of this page describes: an answer in plain words directly beneath the "
            "question, a site whose meaning is not locked inside its pictures, and business "
            "details a machine can cross-check without finding two versions of them. What changes "
            "is that we check the page against what a machine can actually parse, and read what "
            "the assistants say about your trade before and after.",
            "Three acronyms are in circulation for it. AIO, AEO and GEO all describe the "
            "same job, so the acronym on a quote says more about a supplier's calendar than "
            "about the work. And nobody can sell you a "
            "position inside an answer, because there is none to buy.",
        ],
        link_lead="The longer version is here:",
        href="/blog-ai-search",
        label="what an assistant says about your business",
    ),
    "it": dict(
        anchor="Come lavoriamo",
        h2="Ricerca AI, venduta anche come AIO o AEO",
        paras=[
            "Sempre più clienti aprono un assistente prima di un motore di ricerca, e quello che "
            "torna è una manciata di nomi, già scelti. Niente ti dice quando il tuo non c'è.",
            "Non è un prodotto a parte e qui non viene venduto come tale. È lo stesso lavoro che "
            "descrive il resto di questa pagina: una risposta in parole chiare subito sotto la "
            "domanda, un sito che non chiude il proprio significato dentro le fotografie, e dati "
            "dell'attività che una macchina può riscontrare senza trovarne due versioni. Quello "
            "che si aggiunge è che verifichiamo la pagina rispetto a quello che una macchina "
            "riesce davvero a interpretare, e leggiamo cosa dicono gli assistenti sul tuo "
            "mestiere, prima e dopo.",
            "In giro ci sono tre sigle. AIO, AEO e GEO descrivono lo stesso lavoro, quindi "
            "la sigla su un preventivo dice più sul calendario di un fornitore che sul "
            "lavoro. E nessuno può venderti una posizione "
            "dentro una risposta, perché non ce n'è una da comprare.",
        ],
        link_lead="La versione lunga sta qui:",
        href="/it/blog-ai-search",
        label="cosa dice di te un assistente",
    ),
    "es": dict(
        anchor="Cómo trabajamos",
        h2="Búsqueda con IA, también vendida como AIO o AEO",
        paras=[
            "Cada vez más compradores abren un asistente antes que un buscador, y lo que vuelve "
            "es un puñado de nombres, ya elegidos. Nada te dice cuando el tuyo no está.",
            "No es un producto aparte y aquí no se vende como tal. Es el mismo trabajo que "
            "describe el resto de esta página: una respuesta en palabras claras justo debajo de "
            "la pregunta, una web que no encierra su significado dentro de las fotos, y datos del "
            "negocio que una máquina puede contrastar sin encontrar dos versiones. Lo que se "
            "añade es que comprobamos la página frente a lo que una máquina sí puede interpretar, "
            "y leemos qué dicen los asistentes sobre tu oficio, antes y después.",
            "Circulan tres siglas. AIO, AEO y GEO describen el mismo trabajo, así que la "
            "sigla de un presupuesto dice más sobre el calendario de un proveedor que sobre "
            "el trabajo. Y nadie puede venderte una posición dentro de "
            "una respuesta, porque no hay ninguna que comprar.",
        ],
        link_lead="La versión larga está aquí:",
        href="/es/blog-ai-search",
        label="qué dice de ti un asistente",
    ),
    "sq": dict(
        anchor="Si punojmë",
        h2="Kërkimi me AI, i shitur edhe si AIO ose AEO",
        paras=[
            "Gjithnjë e më shumë blerës hapin një asistent para një motori kërkimi, dhe ajo që "
            "kthehet është një dorë emrash, tashmë të zgjedhur. Asgjë nuk ju thotë kur i juaji nuk është aty.",
            "Nuk është produkt i veçantë dhe këtu nuk shitet si i tillë. Është e njëjta punë që "
            "përshkruan pjesa tjetër e kësaj faqeje: një përgjigje me fjalë të qarta menjëherë "
            "poshtë pyetjes, një faqe që nuk e mbyll kuptimin e vet brenda fotografive, dhe të "
            "dhëna biznesi që një makinë mund t'i kryqëzojë pa gjetur dy versione. Ajo që shtohet "
            "është se e kontrollojmë faqen kundrejt asaj që një makinë arrin ta interpretojë, dhe "
            "lexojmë çfarë thonë asistentët për zanatin tuaj, para dhe pas.",
            "Qarkullojnë tre shkurtesa. AIO, AEO dhe GEO përshkruajnë të njëjtën punë, "
            "kështu që shkurtesa në një ofertë thotë më shumë për kalendarin e një furnitori "
            "sesa për punën. Dhe askush nuk mund t'ju shesë një "
            "pozicion brenda një përgjigjeje, sepse nuk ka ndonjë për të blerë.",
        ],
        link_lead="Versioni i gjatë ndodhet këtu:",
        href="/sq/blog-ai-search",
        label="çfarë thotë një asistent për ju",
    ),
}


def build(b):
    """The guide link goes INSIDE the last paragraph, not in a <p class="post-service">.

    Gate check 23 reads the long-version label with the FIRST match of
    'post-service"><strong>(.*?)</strong>' inside <main>, then compares it across all
    eight service pages in a tree. A second post-service paragraph placed above the
    existing one takes that match, and the check reports the other seven disagreeing
    with this one, in all four trees at once. Measured: that is exactly what the first
    attempt did."""
    out = [f"{IND}<h2>{b['h2']}</h2>"]
    out += [f"{IND}<p>{p}</p>" for p in b["paras"][:-1]]
    out.append(f'{IND}<p>{b["paras"][-1]} {b["link_lead"]} '
               f'<a href="{b["href"]}">{b["label"]}</a>.</p>')
    return "\n".join(out) + "\n"


for tree, b in BLOCKS.items():
    path = os.path.join(SITE_DIR, tree, "services-seo.html") if tree \
        else os.path.join(SITE_DIR, "services-seo.html")
    s = io.open(path, encoding="utf-8", newline="").read()
    rel = os.path.relpath(path, SITE_DIR)
    if MARK in s:
        print(f"  {rel:26} already carries the block")
        continue
    anchor = f"<h2>{b['anchor']}</h2>"
    if s.count(anchor) != 1:
        raise SystemExit(f"  ! {rel}: {s.count(anchor)} copies of {anchor!r}, expected 1")
    i = s.index(anchor)
    start = s.rfind("\n", 0, i) + 1      # keep the anchor line's own indentation intact
    s = s[:start] + build(b) + s[start:]
    io.open(path, "w", encoding="utf-8", newline="").write(s)
    print(f"  {rel:26} + AI search block before {b['anchor']!r}")

print("done")
