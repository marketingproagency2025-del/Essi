#!/usr/bin/env python3
"""The Italian source text for the Rome, Lugano and Ticino guides.

Italian is the source tree: it is the native language of the audience for all three cities,
and the Swiss two are written for readers who use Italian inside a Swiss context, which is
not the same register as Italy.

WHAT KEEPS THESE FROM BEING THE MILAN POST WITH THE NAME SWAPPED. Each argues from a
structural fact about its own market, and the arguments contradict each other on purpose:

  Roma   two audiences with different discovery paths (residents vs people passing through),
         neighbourhood as the unit of competition, reviews as the only signal a stranger has.
  Lugano the INVERSE of Milan's density argument: volume is the wrong target, the site
         verifies rather than discovers, and discretion rules out testimonial proof.
  Ticino canton scale, not city: four sub-economies, a border that moves the catchment, and
         Italian that has to read as Swiss.

HONESTY RULES APPLIED HERE, tighter than Milan's:
  - No superlatives, no comparison this business has not measured. Milan's "more companies
    than any other city in Italy" form is deliberately not reused.
  - NOTHING about Swiss search results. .build/guide-it.md's query table is Italy-scoped and
    verified against Italian SERPs only. The Swiss posts argue market structure, never
    ranking behaviour.
  - No prices, no invented figures, no claimed Swiss office. The remote-from-Durazzo position
    is stated plainly on all three, and now names Switzerland.
  - No "quasi tutti" as a claim about people: proofread-notes-it.md rejected that form.

    python write_it_content.py
"""
import io
import json
import os

CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "city-content")

COMMON = {
    "lang": "it",
    "breadcrumb_home": "Home",
    "breadcrumb_blog": "Blog",
    "date_display": "23 agosto 2026",
    "by": "Di",
    "summary_h2": "In Breve",
    "faq_h2": "Domande Frequenti",
    "related_h2": "Continua a Leggere",
    "service_label": "Servizio correlato:",
    "back_label": "Torna al Blog",
    "articleSection": "Marketing locale",
}

ROMA = dict(COMMON,
    title="Marketing Digitale a Roma: Farsi Scegliere in Città",
    h1="Marketing Digitale a Roma: Chi Passa e Chi Resta",
    description="A Roma la stessa attività vende a chi resta e a chi è di passaggio. Quartiere, stagionalità e recensioni: cosa cambia nel modo di farsi trovare.",
    og_description="Due pubblici, un quartiere che conta più della città e recensioni che valgono come reputazione: cosa funziona per farsi scegliere a Roma.",
    breadcrumb_last="Roma",
    hero_alt="Architettura cicladica bianca contro un cielo azzurro intenso",
    read_time="6 min di lettura",
    intro=[
        "Roma ha una caratteristica che cambia il modo di fare marketing: la stessa attività serve due pubblici che non si somigliano. Da una parte i residenti, che scelgono con calma e poi restano per anni. Dall'altra chi è in città per due giorni e decide in dieci minuti. Cercano con parole diverse, in momenti diversi, e si convincono con segnali diversi.",
        "Vediamo cosa cambia in pratica: perché il quartiere conta più della città, come si muove davvero la stagionalità romana, e che lavoro fanno le recensioni quando il cliente non ti conosce.",
    ],
    sections=[
        {"h2": "A Roma vendi a due pubblici nello stesso giorno", "p": [
            "Il residente sceglie una volta e poi resta. Cerca un dentista, un idraulico, una palestra, confronta, chiede in giro, e la decisione vale per anni. Chi è di passaggio fa l'opposto: decide sul momento, quasi sempre dal telefono, spesso a poche centinaia di metri da dove si trova, e non tornerà.",
            "Le due persone cercano con parole diverse. Il residente cerca il servizio. Chi passa cerca il servizio più la posizione, e guarda la mappa prima del sito. Se costruisci tutta la comunicazione intorno a uno dei due, l'altro semplicemente non ti vede.",
            "Non serve scegliere. Serve sapere quale dei due porta più margine nella tua attività, dare a quello la prima riga, e lasciare all'altro un percorso che funzioni comunque.",
        ]},
        {"h2": "Il quartiere conta più della città", "p": [
            "Roma come parola chiave dice poco. Il comune è vasto e ha più centri: dal centro storico al Raccordo la distanza è tale che si tratta di mercati separati, non di zone della stessa piazza. Chi cerca davvero scrive il quartiere: Prati, Trastevere, Monteverde, San Giovanni, EUR. È lì che si gioca la concorrenza, e quella di Prati non è quella di Centocelle.",
            "Per chi ha una sede fisica è una buona notizia, perché il bacino reale è più piccolo di quanto sembri e si può presidiare. Una scheda Google Business curata, con il quartiere nel testo e nelle foto, fa più lavoro di una campagna generica su tutta la città.",
            "C'è anche un vincolo che a Roma pesa più della distanza: le limitazioni al traffico nel centro decidono chi può davvero arrivare da te in auto e a che ora. Vale la pena scriverlo dove si vede, insieme a come si arriva con i mezzi e dove si parcheggia.",
            "Se hai più sedi, vanno trattate come attività separate: una scheda ciascuna, foto diverse, recensioni proprie. Accorparle per comodità è il modo più rapido per non comparire bene in nessuna delle due zone.",
        ]},
        {"h2": "La stagionalità romana non segue il calendario di tutti", "p": [
            "In molte città italiane agosto è semplicemente un mese vuoto. A Roma no, perché chi arriva da fuori arriva tutto l'anno e non in una stagione sola. Il mese non si svuota, si sposta: i quartieri residenziali perdono gente mentre il centro si riempie. Chi vende ai residenti perde volume e chi vende a chi arriva lo guadagna, spesso nella stessa settimana.",
            "Lo stesso vale per i ponti, per le festività e per gli eventi che portano gente in città. Un calendario costruito sulla media nazionale sbaglia i mesi in cui vale la pena spingere e quelli in cui conviene tenere fermo il budget.",
            "La verifica è semplice: guardare i propri dati dell'anno prima, mese per mese, e far coincidere le campagne con i mesi che sono buoni per te, non con quelli che lo sono per il paese.",
        ]},
        {"h2": "Per chi non ti conosce, le recensioni sono la reputazione", "p": [
            "Un residente può chiedere a un vicino. Chi è arrivato ieri non ha nessuno a cui chiedere, e allora legge. Per quel pubblico le recensioni non sono un contorno: sono l'unica prova disponibile prima di entrare.",
            "Contano il numero, la data e la risposta. Venti recensioni recenti dicono più di ottanta ferme a tre anni fa, perché la domanda vera non è se eri bravo allora ma se sei affidabile adesso. E una risposta scritta bene a una recensione negativa convince più di molte positive, perché mostra come tratti un problema.",
            "Chiederle non è mendicare. Vanno chieste subito dopo il momento in cui il cliente è più contento, di persona o con un messaggio, e va reso facile rispondere: un link diretto, non istruzioni.",
        ]},
        {"h2": "I social parlano ai due pubblici in modi diversi", "p": [
            "Per il residente i social sono memoria: ti vede, ti riconosce, e quando gli serve si ricorda di te. Per chi passa sono scoperta: un video girato dentro il tuo locale o davanti alla vetrina è spesso il primo contatto, e arriva a chi in quel momento è geograficamente vicino.",
            "Il contenuto che funziona per entrambi è anche il meno costoso da produrre: mostrare il posto e le persone. Non un annuncio, il posto. Le foto vere fanno il lavoro che di solito fa il passaparola.",
            "Una cosa va tenuta ferma: il profilo deve dire dove sei, con che orari, e cosa succede se qualcuno scrive. Un profilo curato che non risponde ai messaggi diretti disperde esattamente le richieste che ha generato.",
        ]},
        {"h2": "Serve un'agenzia con sede a Roma?", "p": [
            "Non per forza. Lavoriamo da remoto, con sede operativa a Durazzo e un team che scrive e chiama in italiano. Quello che conta è chi conosce il tuo mercato e chi risponde quando arriva una richiesta, non la distanza in chilometri.",
            "Detto questo, la conoscenza del quartiere non si improvvisa e non si trova in nessuno strumento. È la parte che sa il cliente e che l'agenzia deve farsi raccontare all'inizio, prima di scrivere una riga.",
            "Lavoriamo con aziende in Italia, in Svizzera, nel resto d'Europa e negli Stati Uniti, e ogni richiesta viene chiamata e qualificata prima di arrivare al cliente.",
        ]},
    ],
    summary=[
        "A Roma servi due pubblici: chi resta sceglie con calma, chi passa decide in pochi minuti.",
        "La concorrenza si gioca sul quartiere: presidia la zona, non la città intera.",
        "La stagionalità locale non coincide con quella nazionale: guarda i tuoi dati, non il calendario.",
        "Per chi non ti conosce, le recensioni recenti sono l'unica prova disponibile.",
        "I social sono memoria per i residenti e scoperta per chi è di passaggio.",
    ],
    faq=[
        {"q": "Meglio puntare su tutta Roma o su un quartiere?",
         "a": "Se hai una sede fisica, sul quartiere e sulle zone confinanti. Il bacino di chi si sposta per un servizio locale è ristretto, e concentrare lì budget e contenuti costa meno e rende di più che coprire una città in cui la maggior parte delle persone non verrebbe comunque da te."},
        {"q": "Ha senso comunicare anche in inglese?",
         "a": "Dipende da quanto pesa il pubblico di passaggio sul tuo fatturato. Se è una parte importante, conviene almeno che le informazioni essenziali siano leggibili in inglese: cosa fai, dove sei, gli orari e come si prenota. Tradurre l'intero sito è un passo successivo, da decidere sui numeri."},
        {"q": "Come si gestisce il calo di agosto?",
         "a": "Prima verificando che ci sia davvero: a Roma dipende dalla zona e dal tipo di cliente, e per alcune attività agosto è un mese pieno. Se il calo c'è, è il momento di spendere meno in acquisizione e di usare il tempo per le cose che negli altri mesi non si fanno, dalle foto alla scheda Google alle recensioni."},
    ],
    related=[
        {"slug": "blog-social-media", "label": "Gestione social media: trasforma i follower in clienti fedeli"},
        {"slug": "blog-milano", "label": "Marketing digitale a Milano: come farti trovare dai clienti giusti"},
    ],
    service_slug="services-social-media",
    service_name="Gestione Social Media",
    cta_label="Parliamo del tuo quartiere",
    card_excerpt="A Roma la stessa attività vende a chi resta e a chi è di passaggio. Quartiere, stagionalità e recensioni: cosa cambia nel modo di farsi trovare.",
    keywords=["marketing digitale Roma", "agenzia marketing Roma", "farsi trovare a Roma"],
)

LUGANO = dict(COMMON,
    title="Marketing Digitale a Lugano: Qualità Prima del Volume",
    h1="Marketing Digitale a Lugano: Pochi Clienti, Quelli Giusti",
    description="A Lugano il mercato è ristretto e il volume è la metrica sbagliata. Come farsi verificare invece che scoprire, e che lavoro deve fare il sito.",
    og_description="Mercato ristretto, passaparola forte e clienti che non vogliono comparire: cosa funziona davvero nel marketing digitale a Lugano.",
    breadcrumb_last="Lugano",
    hero_alt="Barche da pesca in un porto al tramonto",
    read_time="6 min di lettura",
    intro=[
        "Buona parte di ciò che si legge sul marketing digitale è scritta per mercati grandi, dove il problema è emergere dal rumore. A Lugano il problema è quasi opposto: il mercato è ristretto, le persone che contano si conoscono, e il numero di clienti realistici per un servizio professionale in un anno si conta senza calcolatrice.",
        "Questo cambia gli obiettivi. Raccogliere tanti contatti non è un successo: è un modo di riempire l'agenda di conversazioni che non porteranno da nessuna parte. Di seguito, cosa funziona quando il bacino è piccolo e il passaparola pesa più della pubblicità.",
    ],
    sections=[
        {"h2": "In un mercato ristretto il volume è la metrica sbagliata", "p": [
            "In una città grande il ragionamento è statistico: aumenti il numero di richieste, tieni una percentuale di conversione, ottieni più clienti. In un bacino piccolo quel ragionamento smette di funzionare, perché il limite non è quanti contatti raccogli ma quante aziende esistono che hanno davvero bisogno di quello che vendi. Nei settori che pesano di più qui, dalla gestione patrimoniale alle fiduciarie agli studi professionali, quel numero è basso e si può quasi elencare.",
            "La conseguenza pratica è che la qualifica conta più della generazione. Dieci conversazioni con persone che possono comprare valgono più di duecento moduli compilati, e costano molto meno da gestire.",
            "Cambia anche il modo di misurare. Un costo per contatto basso non dice niente se quei contatti non erano nel mercato. La domanda utile è quante di quelle conversazioni sono arrivate a un preventivo.",
        ]},
        {"h2": "Il sito non ti fa scoprire: ti fa verificare", "p": [
            "Quando il passaparola funziona, il primo incontro con il tuo nome raramente avviene online. Qualcuno lo sente a cena, in una riunione, da un collega. In una città dove gli stessi nomi ricorrono agli stessi tavoli, capita più spesso che altrove. Poi va a cercarlo. Il sito non è il canale che ti fa conoscere: è quello che conferma o smonta ciò che hanno appena sentito dire di te.",
            "Questo cambia cosa deve esserci sopra. Non devi convincere uno sconosciuto partendo da zero: devi rispondere in fretta a chi sta verificando. Chi siete, cosa fate esattamente, per chi lo avete già fatto, e come vi si contatta. Se una di queste quattro cose richiede più di qualche secondo per essere trovata, la verifica va storta.",
            "Un sito lento o costruito male fa danno proprio qui, perché questo è l'unico momento in cui viene guardato con attenzione.",
        ]},
        {"h2": "La discrezione fa parte del servizio", "p": [
            "In diversi settori qui il cliente non vuole comparire. Non firmerà una testimonianza, non vuole il proprio nome in un caso studio, e in certi casi non potrebbe nemmeno. Un marketing costruito sulle referenze pubbliche resta senza materiale.",
            "La prova allora deve essere strutturale invece che aneddotica: come lavorate, con che metodo, con quali competenze, quali domande fate prima di accettare un incarico. È meno appariscente di una citazione entusiasta e regge meglio lo sguardo di chi sta valutando sul serio.",
            "Vale anche per il modo di farsi contattare. Un modulo che chiede fatturato e numero di dipendenti prima ancora di una conversazione allontana esattamente le persone che volevi.",
        ]},
        {"h2": "Non tutti i tuoi clienti leggono in italiano", "p": [
            "Lugano lavora in italiano, ma non soltanto. Si trova in un cantone italofono in un paese in cui la maggior parte del mercato parla tedesco o francese, e capita spesso che la sede principale del cliente, il partner o chi decide davvero si trovino a Zurigo. A questo si aggiunge chi arriva da oltre confine. Un sito in una lingua sola non è sbagliato per definizione, ma è una scelta, e vale la pena farla guardando da dove arrivano le richieste invece che per abitudine.",
            "Se aggiungere una lingua intera è troppo, si comincia dalle pagine che contano: cosa fate, chi siete, come contattarvi. Tradurre tutto il blog è raramente il primo passo utile.",
        ]},
        {"h2": "Il prezzo dice qualcosa prima che tu parli", "p": [
            "Competere sul prezzo qui è una posizione difficile da difendere, e non solo perché il cliente non sta cercando il risparmio. Milano è a circa un'ora, e un fornitore italiano che costa meno il tuo cliente lo trova senza sforzo. Su quel terreno la partita è persa in partenza. Chi sceglie un professionista a Lugano sta comprando affidabilità e vicinanza, e un prezzo molto al di sotto degli altri viene letto come un segnale, non come un'occasione.",
            "Non significa esporre cifre alte. Significa che la comunicazione dovrebbe spiegare cosa è compreso e perché, invece di puntare sul confronto. La chiarezza convince più dello sconto.",
        ]},
        {"h2": "Serve un'agenzia con sede a Lugano?", "p": [
            "Non per forza. Lavoriamo da remoto, con sede operativa a Durazzo e un team che scrive e chiama in italiano. Seguiamo aziende in Italia, in Svizzera, nel resto d'Europa e negli Stati Uniti, e ogni richiesta viene chiamata e qualificata prima di arrivare al cliente.",
            "Quello che non abbiamo è una presenza fisica in Svizzera, e non serve far finta del contrario. Conta chi conosce il tuo mercato e chi risponde quando arriva una richiesta.",
            "Se il tuo lavoro non si ferma alla città, vale la pena leggere anche la guida dedicata al cantone: fuori Lugano il quadro cambia parecchio.",
        ]},
    ],
    summary=[
        "In un bacino ristretto il numero di contatti dice poco: conta quanti erano davvero nel mercato.",
        "Il sito serve a farti verificare da chi ha già sentito il tuo nome, non a farti scoprire.",
        "Dove il cliente non vuole comparire, la prova è il metodo, non la testimonianza.",
        "Una parte del mercato legge in tedesco o in inglese: guarda da dove arrivano le richieste.",
        "Con Milano a un'ora, competere sul prezzo è terreno perso: il posizionamento è vicinanza e affidabilità.",
    ],
    faq=[
        {"q": "Ha senso fare pubblicità online in un mercato così piccolo?",
         "a": "Sì, ma con obiettivi diversi da quelli abituali. Con un bacino ristretto le campagne servono a farsi trovare da chi sta già cercando e a restare presenti per poche persone rilevanti, più che a generare volume. Il budget va tenuto contenuto e giudicato sulle conversazioni utili, non sul numero di contatti."},
        {"q": "Serve un sito in più lingue a Lugano?",
         "a": "Dipende da chi sono i tuoi clienti. Se una parte lavora in tedesco o in inglese, conviene almeno che le pagine principali siano leggibili in quelle lingue. Prima di decidere, guarda da dove arrivano le richieste che ricevi già: è un dato che hai in casa e risponde meglio di qualsiasi regola generale."},
        {"q": "Lavorate con aziende svizzere pur non avendo una sede in Svizzera?",
         "a": "Sì. Lavoriamo da remoto da Durazzo, in italiano, inglese, spagnolo e albanese, e seguiamo aziende in Italia, in Svizzera, nel resto d'Europa e negli Stati Uniti. Non abbiamo uffici in Svizzera e non ci presentiamo come agenzia locale: quello che offriamo è la gestione dei canali e la qualifica di ogni richiesta prima che arrivi a te."},
    ],
    related=[
        {"slug": "blog-website", "label": "Il tuo sito web è il tuo venditore più instancabile"},
        {"slug": "blog-ticino", "label": "Marketing digitale in Ticino: quattro mercati, non uno"},
    ],
    service_slug="services-website",
    service_name="Creazione Sito Web",
    cta_label="Parliamo della tua situazione",
    card_excerpt="A Lugano il mercato è ristretto e il volume è la metrica sbagliata. Farsi verificare invece che scoprire, e che lavoro deve fare davvero il sito.",
    keywords=["marketing digitale Lugano", "agenzia marketing Lugano", "sito web Lugano"],
)

TICINO = dict(COMMON,
    title="Marketing Digitale in Ticino: Guida per le Aziende",
    h1="Marketing Digitale in Ticino: Quattro Mercati, Non Uno",
    description="Bellinzona, Locarno, Lugano e il Mendrisiotto funzionano in modo diverso. Cosa cambia per le campagne, per il confine e per il modo di scrivere.",
    og_description="Il cantone contiene economie diverse e un confine che sposta il bacino: cosa cambia per le campagne di un'azienda ticinese.",
    breadcrumb_last="Ticino",
    hero_alt="Il sole che tramonta sul mare",
    read_time="6 min di lettura",
    intro=[
        "Impostare una campagna su tutto il Ticino sembra la scelta ovvia: è un cantone piccolo, si attraversa in poco più di un'ora. In pratica significa mettere lo stesso budget su economie che si somigliano poco, e chiedere allo stesso messaggio di funzionare per tutte.",
        "Questa guida parte da lì: cosa distingue le zone del cantone, cosa cambia per chi ha clienti o fornitori oltre confine, e perché con pochi contatti e decisioni lente conviene ragionare per percorso invece che per singola campagna.",
    ],
    sections=[
        {"h2": "Il Ticino non è un mercato solo", "p": [
            "Bellinzona è una città amministrativa, con un tessuto di servizi e di impiego pubblico. Il Locarnese vive in buona parte di turismo, con una stagionalità marcata. Lugano è il polo dei servizi e della finanza. Il Mendrisiotto, verso Chiasso, è la parte industriale e logistica, ed è la più intrecciata con l'Italia.",
            "Sono quattro clienti tipo diversi, con problemi diversi e mesi buoni diversi. Un annuncio scritto per l'albergatore di Ascona non parla al fiduciario di Bellinzona, e nessuno dei due riconosce il linguaggio pensato per un'azienda di logistica a Stabio.",
            "La cosa utile non è dividere il budget in quattro, ma scegliere: quale di queste economie contiene i tuoi clienti migliori, e partire da quella con un messaggio che le somiglia.",
        ]},
        {"h2": "Il confine cambia il calcolo", "p": [
            "Nel Mendrisiotto e lungo tutta la fascia di confine il bacino reale non finisce alla dogana. Una parte della clientela arriva da Como e da Varese, e una parte della forza lavoro attraversa il confine ogni mattina. Chi vende al pubblico lo sa già; chi vende ad altre aziende spesso lo sottovaluta.",
            "Le conseguenze concrete sono due. La prima è che l'area geografica delle campagne va decisa guardando da dove arrivano i clienti, non dove passa il confine amministrativo. La seconda è che il messaggio deve reggere due contesti: chi legge dall'Italia e chi legge dalla Svizzera non ha le stesse aspettative su prezzi, tempi e garanzie.",
            "Se quel flusso vale per te, conviene dirlo in modo esplicito sul sito. Scrivere che servite anche clienti che arrivano dall'Italia evita una parte delle domande e ne qualifica un'altra.",
        ]},
        {"h2": "Scrivere in italiano non basta: bisogna scrivere per la Svizzera", "p": [
            "L'italiano del Ticino è italiano, ma i riferimenti no. I prezzi sono in franchi. Le regole che contano sono svizzere. E una parte del vocabolario professionale è diversa: il fiduciario non è il commercialista, e chi legge se ne accorge alla prima riga.",
            "Un testo che dà per scontato il contesto italiano comunica una cosa sola, e cioè che non è stato scritto per chi lo sta leggendo. In un mercato dove la fiducia si costruisce lentamente, è un inizio che costa caro.",
            "La verifica richiede pochi minuti: rileggere il testo chiedendosi se un'azienda di Bellinzona lo riconoscerebbe come rivolto a sé. Valuta, riferimenti normativi, festività, nomi delle professioni.",
        ]},
        {"h2": "Pochi contatti e cicli lunghi: serve un percorso, non una campagna", "p": [
            "In un cantone di queste dimensioni il numero di richieste possibili in un mese è limitato, e in molti settori la decisione richiede settimane o mesi. Una campagna giudicata sul numero di contatti generati misura la cosa sbagliata, e spinge a spendere di più per riempire un imbuto che non ha quel problema.",
            "Quello che serve è un percorso: raccogliere le poche richieste che ci sono, capire subito quali sono reali, e restare presenti per quelle che decideranno più avanti. A questi volumi la differenza tra chi chiude e chi no è di solito il seguito, non il primo contatto.",
            "In concreto sono tre cose: qualificare ogni richiesta parlandoci, tenere traccia di chi ha detto non adesso, e avere qualcosa da mandare a quelle persone nei mesi successivi che non sia un sollecito.",
        ]},
        {"h2": "Le distanze corte allargano il bacino", "p": [
            "Un cliente di Bellinzona raggiunge Lugano in mezz'ora, e questo cambia il raggio realistico di un'attività. Il bacino non coincide con il comune, ed è quasi sempre più largo di quanto immagini chi lo imposta guardando la mappa della propria città.",
            "Vale in entrambe le direzioni: puoi servire più zone di quante ne stai considerando, e i tuoi concorrenti non sono soltanto quelli con l'insegna nella tua via. Prima di stringere il raggio di una campagna, guarda da dove arrivano i clienti che hai già.",
        ]},
        {"h2": "Da dove partire, in ordine", "p": [
            "Messe in fila: scegliere l'economia del cantone a cui parli, riscrivere i testi principali perché siano riconoscibili da chi legge dalla Svizzera, decidere l'area geografica sui dati dei clienti reali invece che sul confine, e solo dopo ragionare su quanto spendere in pubblicità.",
            "Chi lavora soprattutto in città trova nella guida dedicata a Lugano un quadro più preciso: il mercato cittadino ha regole sue, e non sono quelle del resto del cantone.",
            "Noi lavoriamo da remoto, con sede operativa a Durazzo, e seguiamo aziende in Italia, in Svizzera, nel resto d'Europa e negli Stati Uniti. Non abbiamo uffici in Svizzera. Ogni richiesta viene chiamata e qualificata prima di arrivare al cliente.",
        ]},
    ],
    summary=[
        "Il cantone contiene economie diverse: amministrativa, turistica, finanziaria e industriale.",
        "Lungo il confine il bacino reale supera la dogana, in entrata e in uscita.",
        "Italiano sì, ma con riferimenti svizzeri: franchi, regole e nomi delle professioni.",
        "Con pochi contatti e decisioni lente conta il seguito più del primo contatto.",
        "Le distanze corte allargano il bacino: guarda da dove arrivano i clienti che hai già.",
    ],
    faq=[
        {"q": "Conviene fare campagne su tutto il Ticino o su una zona sola?",
         "a": "In genere su una zona, almeno all'inizio. Le aree del cantone hanno economie diverse e un messaggio unico finisce per non parlare bene a nessuna. Scegli quella in cui hai già i clienti migliori, verifica che funzioni, e allarga solo dopo."},
        {"q": "Ha senso rivolgersi anche ai clienti oltre confine?",
         "a": "Dipende dalla tua zona e dal tuo settore. Lungo la fascia di confine una parte reale della clientela arriva da Como e da Varese, e ignorarla significa lasciare fuori richieste che arriverebbero comunque. Il modo di verificarlo è guardare da dove arrivano i clienti che hai già, non deciderlo in astratto."},
        {"q": "In che lingua vanno fatte le campagne in Ticino?",
         "a": "In italiano, ma scritto per un pubblico svizzero: prezzi in franchi, riferimenti normativi svizzeri e il vocabolario professionale locale. Se hai clienti anche oltre confine, valuta versioni separate invece di un testo unico che prova a parlare a tutti."},
    ],
    related=[
        {"slug": "blog-sales-funnel", "label": "Un funnel di vendita che chiude: da sconosciuto a contratto firmato"},
        {"slug": "blog-lugano", "label": "Marketing digitale a Lugano: pochi clienti, quelli giusti"},
    ],
    service_slug="services-sales-funnel",
    service_name="Funnel di Vendita",
    cta_label="Parliamo della tua zona",
    card_excerpt="Bellinzona, Locarno, Lugano e il Mendrisiotto funzionano in modo diverso. Cosa cambia per le campagne, per il confine e per il modo di scrivere.",
    keywords=["marketing digitale Ticino", "agenzia marketing Ticino", "campagne Ticino"],
)

if __name__ == "__main__":
    for name, c in [("roma", ROMA), ("lugano", LUGANO), ("ticino", TICINO)]:
        io.open(os.path.join(CONTENT, f"{name}-it.json"), "w", encoding="utf-8", newline="\n").write(
            json.dumps(c, ensure_ascii=False, indent=1) + "\n")
        words = sum(len(p.split()) for p in c["intro"]) + \
                sum(len(p.split()) for s in c["sections"] for p in s["p"])
        t, d = len(c["title"]), len(c["description"])
        print("  %-8s title %2d %-8s desc %3d %-12s h1 %2d  body %d words  "
              "%d sections, %d faq" % (
                  name, t, "ok" if t <= 60 else "TOO LONG",
                  d, "ok" if 120 <= d <= 155 else "OUT OF RANGE",
                  len(c["h1"]), words, len(c["sections"]), len(c["faq"])))
    print("done")
