# Voci originali

Trova le proiezioni in lingua originale vicino a Pescara, entro circa 30 minuti di auto dal centro. Include i film italiani in versione originale. I film doppiati non compaiono.

## Come si avvia

1. Fai doppio clic su `Avvia Cinema.cmd`.
2. Il browser si apre su `http://127.0.0.1:8765`.
3. Scegli una data, un cinema o scrivi il titolo. La scheda “Lingua confermata” mostra solo le proiezioni con una prova della lingua originale. La scheda “Da verificare” raccoglie le altre.

Il sito parte in italiano. Il selettore in alto (`🇮🇹 IT` / `🇬🇧 EN`) passa all’inglese e ricorda la scelta nel browser. Titoli dei film e nomi dei cinema restano nella lingua della fonte.

Serve Python 3.10 o successivo. Non servono pacchetti aggiuntivi, account o chiavi. Il programma resta su questo computer e ascolta solo su `127.0.0.1`.

Il pulsante “Aggiorna gli orari” rilegge i siti dei cinema. I dati restano in memoria per 10 minuti. Per forzare una lettura si può aprire `http://127.0.0.1:8765/api/screenings?refresh=1`.

Se la porta 8765 è già occupata, chiudi l'altra copia oppure avvia da terminale:

```powershell
python cinema.py --port 8766
```

`python cinema.py --no-browser` avvia il server senza aprire il browser.

## Copertura

Sei cinema. Quattro vengono letti in automatico, due restano da verificare a mano.

| Cinema | Città | Lettura | Prova della lingua |
|---|---|---|---|
| Multiplex L’Arca | Spoltore | automatica, 7 giorni | Note “versione originale” nella programmazione, limitate al blocco di orari che le riporta. |
| Multiplex Universo | Silvi | automatica, 7 giorni | Stessa fonte e stesse regole dell’Arca. |
| UCI Luxe Megalò | Chieti | automatica, 7 giorni | Lingua audio della singola proiezione. Un audio non italiano resta “Da verificare” senza una prova esplicita. |
| The Space Porto Allegro | Montesilvano | automatica, 7 giorni | Etichetta di ogni spettacolo: “LINGUA ORIGINALE” oppure “ITALIANO”. |
| Cineteatro Massimo | Pescara | manuale | Il sito Cityplex non indica la lingua per proiezione. |
| Cineteatro Sant’Andrea | Pescara | manuale | Stessa situazione del Massimo. |

Alla verifica del 5 novembre 2026 le quattro fonti automatiche rispondevano e leggevano 7 giorni su 7. L’API restituiva 13 proiezioni in lingua originale e nessuna doppiatura confermata; le altre righe erano originali italiani o da verificare. Sono numeri di quel giorno: cambiano con la programmazione.

La copertura non è completa. Asterope a Francavilla al Mare, per esempio, non è tra le fonti. Non leggere questa tabella come “tutti i cinema della zona”.

## Limiti

- I minuti in auto sono stime dal centro di Pescara, senza traffico. Il limite di 30 minuti è indicativo.
- La finestra è di sette giorni. Gli orari nuovi possono comparire dopo l’ultima lettura.
- Se un sito non risponde, l’app lo segnala come fonte non disponibile. Non inventa proiezioni.
- A UCI, uno spettacolo in italiano di un film straniero senza lingua originale verificata resta “Da verificare”, non viene promosso a originale.
- A Massimo e Sant’Andrea la lingua va controllata sul sito o in biglietteria.
- I film italiani originali sono riconosciuti con una lista verificata a mano: 4 titoli al 5 novembre 2026.
- Controlla sempre orario, lingua e disponibilità sul sito del cinema prima di partire.

## Regole sui dati

- La lingua si conferma sulla singola proiezione, non sul film.
- La nazionalità italiana del film, da sola, non prova che l’audio sia originale.
- “Lingua confermata” contiene solo proiezioni originali o italiane originali. Le doppiate sono escluse. Le lingue incerte stanno in “Da verificare”.
- Le date seguono il fuso Europe/Rome.

## Dati tecnici

`GET /health` risponde `{"status": "ok", "version": "0.1-draft"}`.

`GET /api/screenings` (oppure `?refresh=1`) restituisce:

```json
{
  "updatedAt": "2026-11-05T15:00:36+01:00",
  "screenings": [{"id": "…", "title": "…", "cinemaId": "…", "cinema": "…", "city": "…", "date": "2026-11-05", "time": "19:00", "language": "…", "languageCode": "language.original", "classification": "original", "evidence": "…", "evidenceCode": "evidence.original.label", "evidenceParams": {"label": "…"}, "sourceUrl": "https://…", "bookingUrl": "https://…", "driveMinutes": 25}],
  "sources": [{"id": "…", "name": "…", "url": "https://…", "status": "ok", "message": "…", "messageCode": "source.ok", "messageParams": {"days": 7, "total": 7}, "checkedAt": "…", "driveMinutes": 25}],
  "notes": ["…"],
  "noteCodes": ["notes.dev", "notes.drive", "notes.sevenDays"]
}
```

`classification` vale `original`, `italian`, `unknown` o `dubbed`; solo i primi due entrano in “Lingua confermata”. `languageCode`, `evidenceCode`, `messageCode` e `noteCodes` sono codici stabili usati dal frontend per la traduzione; i campi `language`, `evidence`, `message` e `notes` restano in italiano. `evidenceParams` e `messageParams` contengono i valori da inserire nei testi. Il server espone anche i file statici da `web/`.
