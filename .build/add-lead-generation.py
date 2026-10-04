#!/usr/bin/env python3
"""Build services-lead-generation, the ninth service page, in all four trees.

    python .build/add-lead-generation.py

WHY A NEW PAGE. Lead generation is the service the agency actually sells and the
one with the strongest proof behind it, and it had no page. Eight service pages
existed and the nearest was the sales funnel one. Live search shows the Italian
market searching the English loanword openly, with a field of named competitors
making the same promise we do, several of them publishing prices.

WHY A DONOR AND NOT gen-service-pages.py. That script is quarantined: its own
docstring records that it rewrites all eight service pages and REGRESSES all
eight, and that the shipped pages are the source of truth. So this builds the way
the city guides do, by copying a shipped page in the same tree and replacing only
what is page-specific. The donor is services-sales-funnel, the closest sibling.

WHAT THAT BUYS. Gate check 23 compares, across the service pages of one language,
the breadcrumb stem, the first h2, the last three h2s, the CTA, the back link and
the shared pricing paragraph. Taking a shipped page as donor means every one of
those is inherited rather than retyped, so the new page cannot drift from the
other eight.

PRICES. The owner's decision: say the cost per lead is low, publish no figure, no
market rates and no competitor names. Real numbers are coming. The FAQ answer
about cost is written so a figure drops into it without rewriting the paragraph
around it.

THE FAQ IS BUILT ONCE. Gate check 10 compares the visible <details> FAQ with the
FAQPage JSON-LD and fails on any difference. Both are generated from the same
list below, so they cannot disagree.

AFTER THIS, register the slug. Five hardcoded lists, named in register-ai-search.py,
and three of them fail the gate if missed.
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

DONOR = "services-sales-funnel"
SLUG = "services-lead-generation"
TREES = {"en": "", "it": "it", "es": "es", "sq": "sq"}

# The hero. clients-2 already ships on the home page of every tree, so its alt is
# already written and reviewed in all four languages, and check 15 already knows
# its real dimensions.
HERO = "clients-2"
HERO_W, HERO_H = 1200, 681
HERO_ALT = {
    "en": "A marketing team reviewing printed campaign photos in a meeting",
    "it": "Un team di marketing che esamina le foto stampate di una campagna in riunione",
    "es": "Un equipo de marketing revisando fotos impresas de una campaña en una reunión",
    "sq": "Një ekip marketingu që shqyrton foto të printuara të një fushate në mbledhje",
}

C = {}

C["en"] = dict(
    title="Lead Generation Agency for Qualified Leads | MarketingPro",
    desc="Lead generation agency for Italy, Germany, Europe and the US. We run the campaigns and call every lead, so your team gets qualified contacts.",
    h1="A Lead Is Only Worth Something If Somebody Calls It.",
    crumb="Lead Generation",
    svc_name="Lead Generation",
    svc_type="Lead generation",
    guide_label="lead quality guide",
    guide_slug="blog-lead-quality",
    intro=[
        "MarketingPro is a digital marketing agency that runs lead generation for businesses across Italy, Germany, Europe, the United States and Albania. We build the campaigns that bring enquiries in, then call and qualify every one before it reaches whoever sells.",
        "A lead is not a name on a list. It is a person who asked a question and is waiting for an answer, and the distance between those two things is where most budgets quietly disappear.",
    ],
    covers=[
        "Campaigns built to ask for a contact, not for applause.",
        "Landing pages and forms that collect what a salesperson actually needs to qualify.",
        "Every lead called by us, in your language, while it is still warm.",
        "Qualification before handover, so what reaches your team is a buyer and not a browser.",
        "A cost per lead kept low, and reported campaign by campaign rather than averaged.",
    ],
    explainer_h2="What does a lead generation agency actually do?",
    explainer=[
        "It finds people who are in the market now and gets them to raise a hand. That part is advertising, and a lot of agencies stop there, which is how a business ends up paying for a spreadsheet nobody rings.",
        "The part that decides whether any of it was worth the money comes next: calling each contact, asking the few questions that separate a buyer from a browser, and passing on only the ones worth an afternoon of selling.",
    ],
    how=[
        ("Decide what a lead is.", "Before any budget moves we agree what you actually want: a booked call, a quote request, a site visit. Everything downstream is chosen to serve that one number."),
        ("Put the offer where the buyers are.", "Meta finds people who were not looking yet. Google catches people already searching. Most businesses need one far more than the other, and the figures say which within weeks."),
        ("Call every lead.", "Not an email sequence. A person, on the phone, quickly. Interest has a short half-life and most of it is gone the same day."),
        ("Hand over only what is qualified.", "Your team gets contacts who answer, who want what you sell, and who know roughly what it costs."),
    ],
    who_h2="Who we generate leads for",
    who=[
        'We run this service today for <a href="/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia and Rika</a>. Fly System sells windows and outdoor products in Italy, OF Outdoorkitchen builds outdoor kitchens, OFYR Italia sells wood-fired barbecues, and Rika sells wood and pellet stoves through its Premium Store in Verona.',
        "Across that work the cost per lead stays low and every lead is called and qualified before anyone on your side sees it. We report the figure campaign by campaign, from the export, rather than quoting an average that flatters the good month.",
        "Our clients are spread across Italy, Germany, Europe, the US and Albania, and we work from our base in Durrës, Albania.",
    ],
    suits="Businesses with something to sell now and somebody who can answer the phone. If nobody can call back within the day, more leads will not help, and we would rather say so before taking the budget.",
    timeline="A lead generation campaign is usually live within a week of the goal being agreed, and the first qualified contacts follow in days rather than months.",
    faq=[
        ("What counts as a qualified lead?", "Someone we have spoken to who wants what you sell, is in the area you serve, and knows roughly what it costs. A contact that fails any of those does not reach your team."),
        ("Do you sell lists of contacts?", "No. Every contact comes from a campaign run for you, and every one of them asked to hear from you. Bought lists go cold, annoy people, and in Europe they are a legal problem as well as a commercial one."),
        ("How much does a lead cost?", "It depends on the sector, the offer, and how many others are bidding for the same attention. We keep it low, and we report what it actually was for your campaigns rather than an industry average."),
    ],
)

C["it"] = dict(
    title="Agenzia Lead Generation: Contatti Qualificati | MarketingPro",
    desc="Agenzia di lead generation per Italia, Germania, Europa e Stati Uniti. Creiamo le campagne e chiamiamo ogni contatto: ti arrivano solo lead qualificati.",
    h1="Un Contatto Vale Qualcosa Solo Se Qualcuno lo Chiama.",
    crumb="Lead Generation",
    svc_name="Lead Generation",
    svc_type="Lead generation",
    guide_label="guida alla qualità dei lead",
    guide_slug="blog-lead-quality",
    intro=[
        "MarketingPro è un'agenzia di marketing digitale che si occupa di lead generation per aziende in Italia, in Germania, nel resto d'Europa, negli Stati Uniti e in Albania. Creiamo le campagne che portano le richieste, poi chiamiamo e qualifichiamo ognuna prima che arrivi a chi vende.",
        "Un lead non è un nome in una lista. È una persona che ha fatto una domanda e sta aspettando una risposta, e nella distanza fra queste due cose sparisce silenziosamente gran parte dei budget.",
    ],
    covers=[
        "Campagne costruite per chiedere un contatto, non per raccogliere applausi.",
        "Landing page e moduli che raccolgono quello che serve davvero a un commerciale per qualificare.",
        "Ogni lead chiamato da noi, nella tua lingua, finché è ancora caldo.",
        "Qualifica prima del passaggio: a chi vende arriva un compratore, non un curioso.",
        "Un costo per contatto tenuto basso, e riportato campagna per campagna invece che come media.",
    ],
    explainer_h2="Cosa fa davvero un'agenzia di lead generation",
    explainer=[
        "Trova le persone che in questo momento sono sul mercato e le porta ad alzare la mano. Quella parte è pubblicità, e molte agenzie si fermano lì: è così che un'azienda finisce per pagare un foglio di calcolo che nessuno chiama.",
        "La parte che decide se ne è valsa la pena viene dopo: chiamare ogni contatto, fare le poche domande che distinguono un compratore da un curioso, e passare solo quelli che meritano un pomeriggio di lavoro commerciale.",
    ],
    how=[
        ("Decidere cos'è un lead.", "Prima che si muova un euro definiamo cosa vuoi davvero: una chiamata fissata, una richiesta di preventivo, un sopralluogo. Tutto il resto si sceglie per servire quel numero."),
        ("Mettere l'offerta dove sono i compratori.", "Meta intercetta chi non stava ancora cercando. Google prende chi sta già cercando. Quasi sempre serve molto più uno dei due, e i numeri lo dicono in poche settimane."),
        ("Chiamare ogni lead.", "Non una sequenza di email. Una persona, al telefono, in fretta. L'interesse dura poco e gran parte svanisce nella stessa giornata."),
        ("Passare solo quello che è qualificato.", "Al tuo commerciale arrivano contatti che rispondono, che vogliono quello che vendi e che sanno all'incirca quanto costa."),
    ],
    who_h2="Per chi facciamo lead generation",
    who=[
        'Questo servizio lo gestiamo oggi per <a href="/it/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia e Rika</a>. Fly System vende serramenti e prodotti da esterno in Italia, OF Outdoorkitchen realizza cucine da esterno, OFYR Italia vende barbecue a legna, e Rika vende stufe a legna e a pellet attraverso il suo Premium Store di Verona.',
        "In questo lavoro il costo per contatto resta basso e ogni lead viene chiamato e qualificato prima che lo veda qualcuno dalla tua parte. Il dato lo riportiamo campagna per campagna, dall'esportazione reale, invece di citare una media che fa bella figura grazie al mese buono.",
        "I nostri clienti sono in Italia, in Germania, nel resto d'Europa, negli Stati Uniti e in Albania, e lavoriamo dalla nostra sede di Durazzo, in Albania.",
    ],
    suits="Aziende che hanno qualcosa da vendere adesso e qualcuno che possa rispondere al telefono. Se non c'è nessuno che richiami in giornata, avere più contatti non aiuta, e preferiamo dirlo prima di prendere il budget.",
    timeline="Una campagna di lead generation è di solito attiva entro una settimana da quando l'obiettivo è definito, e i primi contatti qualificati arrivano in giorni, non in mesi.",
    faq=[
        ("Cosa conta come lead qualificato?", "Una persona con cui abbiamo parlato, che vuole quello che vendi, che si trova nella zona che servi e che sa all'incirca quanto costa. Un contatto che non supera uno di questi punti non arriva al tuo commerciale."),
        ("Vendete liste di contatti?", "No. Ogni contatto nasce da una campagna fatta per te, e ognuno di loro ha chiesto di essere ricontattato. Le liste comprate si raffreddano, infastidiscono le persone e in Europa sono un problema legale oltre che commerciale."),
        ("Quanto costa un lead?", "Dipende dal settore, dall'offerta e da quanti altri stanno comprando la stessa attenzione. Lo teniamo basso, e riportiamo quanto è stato davvero sulle tue campagne invece di una media di settore."),
    ],
)

C["es"] = dict(
    title="Agencia Lead Generation: Leads Cualificados | MarketingPro",
    desc="Agencia de lead generation para Italia, Alemania, Europa y Estados Unidos. Creamos las campañas y llamamos a cada lead: recibes contactos cualificados.",
    h1="Un Lead Solo Vale Algo Si Alguien lo Llama.",
    crumb="Lead Generation",
    svc_name="Lead Generation",
    svc_type="Lead generation",
    guide_label="guía sobre la calidad de los leads",
    guide_slug="blog-lead-quality",
    intro=[
        "MarketingPro es una agencia de marketing digital que hace lead generation para empresas de Italia, de Alemania, del resto de Europa, de Estados Unidos y de Albania. Creamos las campañas que traen las consultas y después llamamos y calificamos cada una antes de que llegue a quien vende.",
        "Un lead no es un nombre en una lista. Es una persona que ha hecho una pregunta y está esperando una respuesta, y en esa distancia es donde desaparece en silencio buena parte de los presupuestos.",
    ],
    covers=[
        "Campañas pensadas para pedir un contacto, no para recibir aplausos.",
        "Landing pages y formularios que recogen lo que un comercial necesita de verdad para calificar.",
        "Cada lead llamado por nosotros, en tu idioma, mientras sigue caliente.",
        "Calificación antes de la entrega: a quien vende le llega un comprador, no un curioso.",
        "Un coste por lead que mantenemos bajo, y que reportamos campaña a campaña, no como media.",
    ],
    explainer_h2="Qué hace realmente una agencia de lead generation",
    explainer=[
        "Encuentra a las personas que están ahora en el mercado y consigue que levanten la mano. Esa parte es publicidad, y muchas agencias se detienen ahí: así es como una empresa acaba pagando por una hoja de cálculo que nadie llama.",
        "La parte que decide si ha merecido la pena viene después: llamar a cada contacto, hacer las pocas preguntas que separan a un comprador de un curioso, y pasar solo los que merecen una tarde de trabajo comercial.",
    ],
    how=[
        ("Definir qué es un lead.", "Antes de mover un euro acordamos qué quieres de verdad: una llamada agendada, una solicitud de presupuesto, una visita. Todo lo demás se elige para servir a ese número."),
        ("Poner la oferta donde están los compradores.", "Meta encuentra a quien todavía no buscaba. Google capta a quien ya está buscando. Casi siempre hace falta mucho más uno de los dos, y los números lo dicen en pocas semanas."),
        ("Llamar a cada lead.", "No una secuencia de correos. Una persona, por teléfono, rápido. El interés dura poco y gran parte se pierde el mismo día."),
        ("Entregar solo lo que está cualificado.", "A tu equipo le llegan contactos que responden, que quieren lo que vendes y que saben más o menos lo que cuesta."),
    ],
    who_h2="Para quién hacemos lead generation",
    who=[
        'Hoy prestamos este servicio a <a href="/es/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia y Rika</a>. Fly System vende ventanas y productos de exterior en Italia, OF Outdoorkitchen construye cocinas de exterior, OFYR Italia vende barbacoas de leña, y Rika vende estufas de leña y de pellets a través de su Premium Store de Verona.',
        "En ese trabajo el coste por lead se mantiene bajo y cada lead se llama y se califica antes de que lo vea nadie de tu lado. El dato lo reportamos campaña a campaña, desde la exportación real, en vez de citar una media que queda bien gracias al mes bueno.",
        "Nuestros clientes están en Italia, Alemania, el resto de Europa, Estados Unidos y Albania, y trabajamos desde nuestra base en Durrës, Albania.",
    ],
    suits="Empresas con algo que vender ahora y con alguien que pueda contestar el teléfono. Si no hay nadie que devuelva la llamada en el día, más leads no van a ayudar, y preferimos decirlo antes de aceptar el presupuesto.",
    timeline="Una campaña de lead generation suele estar activa en una semana desde que se define el objetivo, y los primeros contactos cualificados llegan en días, no en meses.",
    faq=[
        ("Qué cuenta como lead cualificado?", "Una persona con la que hemos hablado, que quiere lo que vendes, que está en la zona que atiendes y que sabe más o menos lo que cuesta. Un contacto que falla en alguno de esos puntos no llega a tu equipo."),
        ("Vendéis listas de contactos?", "No. Cada contacto nace de una campaña hecha para ti, y todos ellos han pedido que se les contacte. Las listas compradas se enfrían, molestan a la gente y en Europa son un problema legal además de comercial."),
        ("Cuánto cuesta un lead?", "Depende del sector, de la oferta y de cuántos más estén pujando por la misma atención. Lo mantenemos bajo, y reportamos lo que ha sido de verdad en tus campañas en lugar de una media del sector."),
    ],
)

C["sq"] = dict(
    title="Agjenci Lead Generation: Lead të Kualifikuar | MarketingPro",
    desc="Agjenci lead generation për Itali, Gjermani, Evropë dhe SHBA. Ndertojmë fushatat dhe telefonojmë çdo lead: ju merrni vetëm kontakte të kualifikuara.",
    h1="Një Lead Vlen Dicka Vetëm Nëse Dikush e Telefonon.",
    crumb="Lead Generation",
    svc_name="Lead Generation",
    svc_type="Lead generation",
    guide_label="udhëzuesi për cilësinë e lead-eve",
    guide_slug="blog-lead-quality",
    intro=[
        "MarketingPro është agjenci marketingu dixhital që merret me lead generation për biznese në Itali, në Gjermani, në pjesën tjetër të Evropës, në Shtetet e Bashkuara dhe në Shqipëri. Ndërtojmë fushatat që sjellin kërkesat, pastaj telefonojmë dhe kualifikojmë secilën para se t'i vijë atij që shet.",
        "Një lead nuk është një emër në listë. Është një person që bëri një pyetje dhe po pret një përgjigje, dhe pikerisht në atë distancë zhduket pa zë pjesa më e madhe e buxheteve.",
    ],
    covers=[
        "Fushata të ndërtuara për të kërkuar një kontakt, jo duartrokitje.",
        "Landing page dhe formularë që mbledhin atë që i duhet vertët një shitësi për të kualifikuar.",
        "Çdo lead i telefonuar nga ne, në gjuhën tuaj, sa kohë është ende i ngrohtë.",
        "Kualifikim para dorëzimit: te shitësi mbërrin një blerës, jo një kureshtar.",
        "Një kosto për lead që e mbajmë të ulët, dhe që e raportojmë fushatë pas fushate, jo si mesatare.",
    ],
    explainer_h2="Çfarë bën vertët një agjenci lead generation",
    explainer=[
        "Gjen njerëzit që janë në treg tani dhe i bind të ngrejën dorën. Ajo pjesë është reklamë, dhe shumë agjenci ndalen aty: keshtu një biznes përfundon duke paguar për një fjetërllogari që nuk e telefonon askush.",
        "Pjesa që vendos nëse ia vlejti vjen pas: të telefonosh çdo kontakt, të bësh ato pak pyetje që dallojnë një blerës nga një kureshtar, dhe të kalosh vetëm ata që meritojnë një pasdite punë shitjeje.",
    ],
    how=[
        ("Të vendosim çfarë është një lead.", "Para se të lëvizë një euro, biem dakord çfarë doni vertët: një telefonatë të caktuar, një kërkesë oferte, një vizitë në vend. Gjithçka tjetër zgjidhet për t'i shërbyer asaj shifre."),
        ("Ta vendosim ofertën aty ku janë blerësit.", "Meta gjen ata që ende nuk po kërkonin. Google kap ata që po kërkojnë tashmë. Zakonisht njeri prej të dyve duhet shumë më shumë, dhe shifrat e thonë brenda pak javesh."),
        ("Të telefonojmë çdo lead.", "Jo një varg email-esh. Një person, në telefon, shpejt. Interesi zgjat pak dhe pjesa më e madhe humbet brenda ditës."),
        ("Të dorëzojmë vetëm atë që është e kualifikuar.", "Ekipit tuaj i vijnë kontakte që përgjigjen, që duan atë që shisni dhe që e dinë pak a shumë sa kushton."),
    ],
    who_h2="Për kë bëjmë lead generation",
    who=[
        'Këtë shërbim e ofrojmë sot për <a href="/sq/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia dhe Rika</a>. Fly System shet dritare dhe produkte të jashtme në Itali, OF Outdoorkitchen ndërton kuzhina të jashtme, OFYR Italia shet barbekju me dru, dhe Rika shet stufa me dru dhe me pelet përmes Premium Store-it të saj në Verona.',
        "Në këtë punë kostoja për lead mbetet e ulët dhe çdo lead telefonohet e kualifikohet para se ta shohë dikush nga ana juaj. Shifrën e raportojmë fushatë pas fushate, nga eksportimi real, në vend që të citojmë një mesatare që duket mirë falas muajit të mirë.",
        "Klientët tanë janë në Itali, në Gjermani, në pjesën tjetër të Evropës, në Shtetet e Bashkuara dhe në Shqipëri, dhe punojmë nga selia jonë në Durrës, në Shqipëri.",
    ],
    suits="Biznese që kanë diçka për të shitur tani dhe dikë që mund t'i përgjigjet telefonit. Nëse askush nuk mund të rikthejë telefonatën brenda ditës, më shumë lead-e nuk ndihmojnë, dhe preferojmë ta themi para se të marrim buxhetin.",
    timeline="Një fushatë lead generation zakonisht është aktive brenda një jave nga momenti kur caktohet objektivi, dhe kontaktet e para të kualifikuara vijnë brenda ditesh, jo muajsh.",
    faq=[
        ("Çfarë quhet lead i kualifikuar?", "Një person me të cilin kemi folur, që do atë që shisni, që ndodhet në zonën që mbuloni dhe që e di pak a shumë sa kushton. Një kontakt që nuk e kalon njërin prej këtyre pikave nuk mbërrin te ekipi juaj."),
        ("A shisni lista kontaktesh?", "Jo. Çdo kontakt lind nga një fushatë e bërë për ju, dhe secili prej tyre ka kërkuar të kontaktohet. Listat e blera ftohen, i bëzdisin njerëzit dhe në Evropë janë problem ligjor përveç se tregtar."),
        ("Sa kushton një lead?", "Varet nga sektori, nga oferta dhe nga sa të tjerë po blejnë të njëjtin vemëndje. E mbajmë të ulët, dhe raportojmë sa ka qenë vertët në fushatat tuaja në vend të një mesatareje sektori."),
    ],
)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def body_html(c, tree):
    """Everything between the hero and the post-service links."""
    L = []
    for p in c["intro"]:
        L.append("          <p>%s</p>" % p)
    L.append("          <h2>%s</h2>" % COVERS_H2[tree])
    L.append("          <ul>")
    for it in c["covers"]:
        L.append("            <li>%s</li>" % it)
    L.append("          </ul>")
    L.append("          <h2>%s</h2>" % c["explainer_h2"])
    for p in c["explainer"]:
        L.append("          <p>%s</p>" % p)
    L.append("          <h2>%s</h2>" % HOW_H2[tree])
    for lead, rest in c["how"]:
        L.append("          <p><strong>%s</strong> %s</p>" % (lead, rest))
    L.append("          <h2>%s</h2>" % c["who_h2"])
    for p in c["who"]:
        L.append("          <p>%s</p>" % p)
    L.append("          <h2>%s</h2>" % SUITS_H2[tree])
    L.append("          <p>%s</p>" % c["suits"])
    L.append("          <h2>%s</h2>" % PRICING_H2[tree])
    L.append("          <p>%s</p>" % PRICING_P[tree])
    L.append("          <p>%s</p>" % c["timeline"])
    L.append("          <h2>%s</h2>" % FAQ_H2[tree])
    L.append('          <div class="faq__list">')
    for q, a in c["faq"]:
        L.append('            <details class="faq__item">')
        L.append("              <summary>%s</summary>" % q)
        L.append("              <p>%s</p>" % a)
        L.append("            </details>")
    L.append("          </div>")
    return "\n".join(L)


# The boilerplate headings and the shared pricing paragraph are read out of the
# donor at run time, per tree, so this file never retypes a string that gate
# check 23 compares across the nine service pages.
COVERS_H2, HOW_H2, SUITS_H2, PRICING_H2, FAQ_H2, PRICING_P = {}, {}, {}, {}, {}, {}


def donor_path(tree):
    return os.path.join(SITE, tree, DONOR + ".html") if tree \
        else os.path.join(SITE, DONOR + ".html")


def read_boilerplate():
    for lang, tree in TREES.items():
        s = io.open(donor_path(tree), encoding="utf-8", newline="").read()
        main = s[s.index("<main"):s.index("</main>")]
        h2 = re.findall(r"<h2>(.*?)</h2>", main, re.S)
        if len(h2) < 4:
            raise SystemExit("  ! %s: only %d h2 in the donor" % (lang, len(h2)))
        COVERS_H2[tree] = h2[0]
        SUITS_H2[tree], PRICING_H2[tree], FAQ_H2[tree] = h2[-3], h2[-2], h2[-1]
        # "How we work" is the heading immediately before the who-we-serve one,
        # which is third from the end counting back past suits/pricing/faq.
        HOW_H2[tree] = h2[-5]
        m = re.search(r"<h2>" + re.escape(h2[-2]) + r"</h2>\s*<p>(.*?)</p>", main, re.S)
        if not m:
            raise SystemExit("  ! %s: cannot find the shared pricing paragraph" % lang)
        PRICING_P[tree] = m.group(1).strip()


def build(lang, tree):
    c = C[lang]
    s = io.open(donor_path(tree), encoding="utf-8", newline="").read()

    # 1. the slug, everywhere it appears: canonical, 5 hreflang, og:url, JSON-LD ids
    n_slug = s.count(DONOR)
    s = s.replace(DONOR, SLUG)

    # 2. head strings
    donor_title = re.search(r"<title>(.*?)</title>", s, re.S).group(1)
    donor_desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    s = s.replace(donor_title, esc(c["title"]))
    s = s.replace(donor_desc, esc(c["desc"]))

    # 3. the Service node
    s = re.sub(r'("@id": "[^"]*#service",\s*\n\s*"name": ")[^"]*(")',
               lambda m: m.group(1) + c["svc_name"] + m.group(2), s, count=1)
    s = re.sub(r'("serviceType": ")[^"]*(")',
               lambda m: m.group(1) + c["svc_type"] + m.group(2), s, count=1)

    # 4. breadcrumb, visible and in the graph
    donor_crumb = re.search(r'<li><span aria-current="page">(.*?)</span></li>', s).group(1)
    s = s.replace(donor_crumb, c["crumb"])

    # 5. h1
    s = re.sub(r'(<h1 class="article-hero__title">).*?(</h1>)',
               lambda m: m.group(1) + c["h1"] + m.group(2), s, count=1, flags=re.S)

    # 6. hero image.
    #
    #    A donor hero is named in FIVE places, not one: og:image, twitter:image, the
    #    rel=preload, primaryImageOfPage in the graph, and both halves of the <picture>.
    #    A first version replaced the <img> and a single srcset, and the result passed the
    #    whole gate while being wrong: check 22 only asks that the preload and the <source>
    #    agree with EACH OTHER, and they did, both still on the donor's image; check 15 only
    #    asks that the <img> dimensions match the file the <img> names, and they did. The
    #    browser would have fetched one photograph and read another one's alt text. So the
    #    donor's hero name is replaced everywhere it occurs, and the count is reported.
    donor_hero = re.search(r'<img src="[^"]*?([a-z0-9-]+)\.jpg"', s).group(1)
    n_hero = s.count(donor_hero)
    s = s.replace(donor_hero, HERO)
    s = re.sub(r'(<img src="[^"]*?' + re.escape(HERO) + r'\.jpg" alt=")[^"]*(" width=")\d+(" height=")\d+',
               lambda m: "%s%s%s%d%s%d" % (m.group(1), esc(HERO_ALT[lang]), m.group(2),
                                           HERO_W, m.group(3), HERO_H), s, count=1)

    # 7. the body
    start = s.index("          <p>", s.index('<div class="article article__body">'))
    end = s.index('          <p class="post-service">')
    s = s[:start] + body_html(c, tree) + "\n\n" + s[end:]

    # 8. the guide link, which is the reciprocal half of the wire-services pattern
    s = re.sub(r'(<p class="post-service"><strong>[^<]*</strong> <a href=")[^"]*(">)[^<]*(</a></p>)',
               lambda m: '%s/%s%s%s%s%s' % (m.group(1), (tree + "/") if tree else "",
                                            c["guide_slug"], m.group(2),
                                            c["guide_label"], m.group(3)), s, count=1)

    # 9. the FAQ graph, built from the same list as the visible FAQ
    entries = [{"@type": "Question", "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]
    blob = json.dumps(entries, ensure_ascii=False, indent=2)
    blob = "\n".join("        " + ln for ln in blob.splitlines()).strip()
    s = re.sub(r'("@type": "FAQPage",\s*\n\s*"@id": "[^"]*",\s*\n\s*"mainEntity": )\[.*?\n(\s*)\]',
               lambda m: m.group(1) + blob, s, count=1, flags=re.S)

    return s, n_slug


def main():
    read_boilerplate()
    out, bad = [], []

    for lang, tree in TREES.items():
        c = C[lang]
        if not (20 <= len(c["title"]) <= 60):
            bad.append("%s: title %d chars (want 20-60): %s" % (lang, len(c["title"]), c["title"]))
        if not (120 <= len(c["desc"]) <= 155):
            bad.append("%s: description %d chars (want 120-155)" % (lang, len(c["desc"])))
        for ch in ("—", "–"):
            if ch in json.dumps(c, ensure_ascii=False):
                bad.append("%s: contains an em or en dash" % lang)
    if bad:
        print("ABORTED, nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    for lang, tree in TREES.items():
        s, n_slug = build(lang, tree)
        rel = ("%s/%s.html" % (tree, SLUG)) if tree else "%s.html" % SLUG
        fp = os.path.join(SITE, tree, SLUG + ".html") if tree \
            else os.path.join(SITE, SLUG + ".html")
        out.append((fp, rel, s, n_slug))

    for fp, rel, s, n_slug in out:
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  wrote %-42s (%d slug references rewritten)" % (rel, n_slug))
    print("done. now register the slug, then run the gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
