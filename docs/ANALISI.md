# Analisi iniziale — 26 ottobre 2026

> Documento storico della prima implementazione. Per la copertura attuale
> dell’anteprima 0.2 consultare README.md e coverage-0.2.json.

## Base ufficiale

La pagina https://github.com/colobot/colobot/releases/latest reindirizza a
`colobot-gold-0.2.2-alpha`. Il commit è del 23 dicembre 2024; nessun tag numerico
più recente è presente nel clone ufficiale. È la base consigliata per il primo
rilascio compatibile. `dev` è sviluppo successivo, non una release ufficiale.

Pin sorgenti: `e3addd66f6613174c1a61c373808046e7d49b320`.
Pin dati: `910b0dd8cf722b0bafbdfe9a506a1ca21f0b8f06`.

I percorsi `colobot-base/src/...` citati nella richiesta appartengono a `dev`:
nella release selezionata i sorgenti sono sotto `src/`. La patch fornita è
specifica per la release e non va applicata alla cieca a `dev`.

## Ricerca di lavori italiani

Nessun `it.po` è presente nei due repository ufficiali, né al tag selezionato
né negli alberi `origin/dev` clonati. La ricerca pubblica GitHub di repository
`colobot italian` restituisce zero risultati. L'API `api.github.com` risponde
con rifiuto del proxy (403); altre ricerche web non forniscono risultati
strutturati affidabili. Non è quindi dimostrata l'assenza di fork, mod,
progetti abbandonati o issue/PR. Nessun materiale italiano riutilizzabile è
stato identificato, ma la ricerca esterna resta **parziale**.
La wiki ufficiale Working-with-translations e README.i18n.md sono stati consultati.

## Quantità

Conteggi dei template del tag, prima della normalizzazione dei duplicati.
Le parole sono stimate separando sugli spazi e includono marcatori e codice:
non equivalgono a parole di prosa da tradurre.

| Categoria | Cataloghi | Voci | Parole sorgente |
|---|---:|---:|---:|
| Desktop e manuale | 1 | 58 | 238 |
| Interfaccia | 1 | 659 | 2439 |
| help/bots | 1 | 176 | 2255 |
| help/cbot | 1 | 1143 | 18109 |
| help/generic | 1 | 141 | 2458 |
| help/object | 1 | 323 | 3643 |
| help/programs | 1 | 46 | 1704 |
| levels/battles | 7 | 56 | 521 |
| levels/challenges | 14 | 173 | 1643 |
| levels/exercises | 39 | 926 | 13854 |
| levels/free | 10 | 36 | 181 |
| levels/missions | 37 | 878 | 10693 |
| levels/plus | 32 | 560 | 6026 |
| Totale | 146 | 5175 | 63764 |

I template dati contengono tre duplicati (uno in help/cbot, due in help/programs).
I cataloghi italiani li normalizzano senza cambiare i template ufficiali:
**5.172 voci**, **230 tradotte (4,45%)**, **4.942 vuote**. Le 230 comprendono
ripetizioni della stessa etichetta in cataloghi diversi. Le voci uniche per
msgid sono 717 nel repository motore e 3.101 nei dati, prima della deduplicazione
tra repository. Il conteggio non include eventuale prosa non estraibile dai POT.
`catalog-inventory.json` conserva il censimento grezzo per template.

## File da creare o modificare

Motore, patch in `patches/colobot-0.2.2-alpha-italian.patch`:

- `src/common/language.h`: aggiunta in coda `LANGUAGE_ITALIAN = 7`, preservando i valori esistenti.
- `src/common/language.cpp`: associazione `it` per parsing e serializzazione.
- `src/ui/screen/screen_setup_game.cpp`: voce `Italiano`.
- `src/app/app.cpp`: rilevamento locale `it`, locale `it_IT.utf8` e codice dati `I`.
- Nuovi `po/it.po` e `desktop/po/it.po`.

Dati: 144 nuovi `it.po`, nelle directory po dei livelli missions, exercises,
challenges, battles, free e plus e nei cinque gruppi help. L'elenco completo
è ricostruibile dall'inventario sostituendo il nome del POT con `it.po`.
La pipeline ufficiale associa già `it` a `I`: nessuna modifica necessaria agli
script Python o ai CMakeLists. I PO producono `Title.I`, `Resume.I`,
`ScriptName.I`, help `*.I.txt` e documentazione sotto `I/`.

Restano da controllare stringhe eventualmente codificate direttamente nei
livelli, contenuti delle mod e istruzioni CBOT incluse come esempi: i soli POT
non dimostrano copertura assoluta di tutti i contenuti del gioco.

## Caratteri e formati

UTF-8, plurale italiano `nplurals=2; plural=(n != 1);`. I cinque font DejaVu
inclusi contengono àèéìòù, le corrispondenti maiuscole e l'apostrofo tipografico:
verificato interrogando le cmap con fontTools. Larghezza delle etichette,
a capo e rendering reale richiedono ancora verifica nel gioco.
Preservati marcatori pseudo-HTML, comandi, link e nomi CBOT. `msgfmt` controlla
i formati gettext; il validatore aggiunge confronto dei marcatori e dei blocchi
`<code>`. Il simbolo percentuale nella prosa non viene interpretato come printf.

## Risultati verificati

- Applicazione della patch a una copia isolata dei sorgenti ufficiali: riuscita.
- Test C++17 compilato ed eseguito: parsing/serializzazione `it`, sette lingue
  preesistenti e rifiuto di un codice sconosciuto.
- 146 PO: `msgfmt --check --check-format`, confronto con template, marcatori,
  compilazione MO e lettura GNUTranslations riusciti; log in gettext-validation.log.
- CMake e build completa colobot-data con TRANSLATIONS=ON, parallelismo 2:
  completata fino al 100%. Usati Python e gli script ufficiali.
- Test funzionale sugli output: titolo italiano, briefing NASA, soluzione,
  marcatori di tasti/pulsanti/link e presenza documentazione CBOT italiana.
- Font: copertura degli accenti italiani verificata nei cinque TTF.
- Checkout ufficiali originali lasciati senza modifiche.

La configurazione CMake del motore si ferma a OpenGL mancante. Non sono stati
compilati il gioco completo né la suite CTest; nessun avvio grafico effettuato.
Mancano le dipendenze native di sviluppo (OpenGL, SDL2/image/ttf, PNG, PhysFS,
Boost system/filesystem/regex, GLEW, libsndfile, gettext; OpenAL se abilitato),
la predisposizione della locale e un display per la verifica interattiva.
Il build parziale non prova la selezione a schermo o la giocabilità.

## Piano per la prima versione giocabile

1. Completare le 659 voci dell'interfaccia, iniziando da menu, impostazioni,
   comandi e messaggi indispensabili alla prima missione.
2. Tradurre la documentazione richiamata dalla prima missione (comandi,
   astronauta, kit e centro di controllo), mantenendo fallback inglese altrove.
3. Compilare motore e dati, eseguire CTest, generare `it_IT.UTF-8` e avviare
   una sessione: selezione Italiano, riavvio, prima missione, SatCom e soluzione.
4. Controllare visivamente testi lunghi, accenti e risoluzioni, correggere solo
   i problemi di integrazione italiana, quindi confezionare un'anteprima parziale.
5. Estendere missioni ed esercizi, poi aiuto generale, oggetti/robot e riferimento
   CBOT. Desktop/manuale e contenuti aggiuntivi restano nel censimento completo.
6. Preparare due PR distinte, motore e dati, rispettando le licenze e spiegando
   la copertura reale. Nessun invio o pubblicazione senza autorizzazione.

Le traduzioni seguono le licenze dei rispettivi progetti upstream; prima della
distribuzione includere le loro informative. Non inventare autori o attribuzioni.
