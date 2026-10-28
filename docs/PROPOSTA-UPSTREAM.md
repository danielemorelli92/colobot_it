# Proposta di integrazione ufficiale

[Bozza inglese per una nuova issue italiana](upstream/ISSUE-ITALIAN.md).
Il titolo è la prima riga; il testo è pronto da rivedere prima dell’invio.
Nessuna issue o PR è stata pubblicata nei repository ufficiali.

Il precedente è [colobot/colobot#1124](https://github.com/colobot/colobot/issues/1124):
la traduzione brasiliana è stata integrata tramite due PR coordinate,
[motore #1167](https://github.com/colobot/colobot/pull/1167) e
[dati #36](https://github.com/colobot/colobot-data/pull/36).
Lo stesso percorso è stato indicato nella proposta spagnola
[#1883](https://github.com/colobot/colobot/issues/1883) nel 2026.
Le [linee guida](https://github.com/colobot/colobot/blob/dev/CONTRIBUTING.md#submitting-pull-requests)
richiedono PR verso `dev` e una discussione preventiva delle nuove funzionalità.

## Materiale pronto

| Repository ufficiale | Contributo |
|---|---|
| `colobot/colobot` | Cataloghi interfaccia e desktop; selettore Italiano; mapping `it` e `I`; locale `it_IT.utf8`; test della nuova lingua e dei codici esistenti. |
| `colobot/colobot-data` | 144 cataloghi italiani e due POT rigenerati dai testi inglesi attuali, necessari per coprire anche `searchall` e le etichette dei cicli. |

I commit di base sono in [upstream.json](../upstream.json).
`tools/export_upstream.py` esporta le due patch complete, applicabili ai
repository ufficiali su quei commit. La patch nativa usa i percorsi correnti
`colobot-base/src/` e aggiunge un identificatore senza rinumerare le altre lingue.
Il generatore dati produce `I`, coerente con il motore; la regola `pt` -> `B`
che risolveva la collisione portoghese/polacco rimane intatta.

Il repository è pubblico e i sorgenti sono accessibili ai manutentori.
La proposta non richiede lo ZIP, il launcher o lo slot French: questi restano
soltanto nel pacchetto comunitario per la vecchia release.

## Prima dell’invio

- Ricontrollare eventuali proposte italiane già aperte e l’avanzamento di `dev`.
- Concordare il contributo nella nuova issue e creare i due fork per le PR.
- Allegare i [risultati delle verifiche](VERIFICHE.md); completare il collaudo
  nativo Windows tramite CI o un ambiente Windows, se richiesto dai manutentori.
- Gestire eventuali richieste di revisione e aggiornamenti dei cataloghi.

Build, installazione e avvio nativi Linux sono verificati. La prova della 1.0
su Windows riguarda l’eseguibile 0.2.2-alpha; non viene presentata come prova
della nuova integrazione Windows. La decisione sull’inclusione in una release
spetta ai manutentori del progetto.
