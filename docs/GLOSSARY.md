# Italian terminology and translation rules

The tables record terminology used in the Italian catalogs. API identifiers,
CBOT keywords, function names and executable string literals remain unchanged.

## Interface and gameplay

| English | Italian |
|---|---|
| bot | robot |
| Mission Control | centro di controllo missione |
| spacesuit | tuta spaziale |
| survival kit | kit di sopravvivenza |
| programming exercises | esercizi di programmazione |
| walkthrough | soluzione |
| challenges | sfide |
| free game | gioco libero |
| settings / setup | impostazioni |
| controls | comandi |
| SatCom | SatCom |
| power cell | batteria |
| nuclear power cell | batteria nucleare |
| power station | centrale elettrica |
| power plant | fabbrica di batterie |
| grabber | robot trasportatore |
| shooter | robot tiratore |
| orga shooter | robot tiratore organico |
| sniffer | robot rilevatore |
| builder | robot costruttore |
| winged / tracked / wheeled / legged | volante / cingolato / su ruote / a zampe |
| shielder | robot scudo |
| thumper | robot percussore |
| subber | robot sommergibile |
| phazer shooter | robot tiratore a fasore |
| derrick | torre di estrazione |
| power captor | parafulmine |
| vault | deposito blindato |
| research center | centro di ricerca |
| black box | scatola nera |
| information exchange post | centro di scambio dati |
| radar station | stazione radar |
| autolab | laboratorio automatico |
| converter | convertitore |
| drawer bot | robot disegnatore |

## Programming documentation

| English | Italian |
|---|---|
| array | array |
| reference (prose, not an identifier) | riferimento |
| parent class / base class | classe base |
| child class / derived class | classe derivata |
| field / method | campo / metodo |
| source code | codice sorgente |

## Markup and code preservation

- Link targets, `<key help/>`, `<button 63/>`, `<format key>` and other control
  markers are preserved. Explicit corrections to upstream source typos are
  listed in [tools/review_rules.py](../tools/review_rules.py).
- Visible prose is translated, including captions displayed in a monospaced
  style. Captions such as “reference”, “functions”, “block”, “Type” and
  “Constants” are distinct from executable CBOT code.
- Program comments are translated; keywords such as `class`, `public` and
  `static`, function names, executable strings and numeric literals are preserved.
  API identifiers such as `PowerPlant`, `PowerStation` and `WingedGrabber` remain
  in English.
- Visible labels in angle brackets, such as `<build a ...>`, are translated;
  actual tags such as `<a object|factory>` are preserved. The validator
  distinguishes these cases.
- Numbers and punctuation in prose may follow Italian conventions.

The corresponding safeguards are implemented in
[tools/localization_checks.py](../tools/localization_checks.py),
[tools/code_comments.py](../tools/code_comments.py) and
[tools/test_code_preservation.py](../tools/test_code_preservation.py).
