# Cinema source research — 2026-11-04, updated 2026-11-05

Scope: maximum 30 minutes driving from central Pescara, confirmed by user. Travel estimates must be labelled estimates and users should check route/traffic. Nearby venues: Massimo and Sant’Andrea (Pescara), Arca (Spoltore), The Space (Montesilvano), UCI Luxe Megalò (Chieti Scalo), Universo (Silvi; boundary case).

## Working official sources

### Arca and Universo — Multicinema
- `https://multicinema.it/Programmazione?cinema=arca&giornoSettimana=0`
- `https://multicinema.it/Programmazione?cinema=universo&giornoSettimana=0`
- `giornoSettimana=0` is today; 1 through6 are subsequent dates. Date labels on page should be checked, not assumed.
- Server-rendered HTML. Each `<div class="item_small" ...>` contains a film. Within `item-details-prog` h3/a holds title and detail href. `tagcloud_orari` holds time anchor text such as17.20.
- Detail example: `https://multicinema.it/Film/Scheda/6809?titolo=Dio-ride`. Fields include Titolo originale, Nazione, Anno, genre, duration, director; generally NO actual original language. Nationality alone MUST NOT qualify Italian-language screening as confirmed original.
- Explicit VO/VOS annotations, when present, may qualify only the annotated screening/block, never every screening of a movie globally.

### Pescara Cityplex (Massimo and Sant’Andrea)
- `https://pescaracityplex.it/` is accessible plain HTML. Date ranges and per-film schedules are embedded in Elementor heading/text widgets. It has links to Comingsoon film details and Ciaotickets purchase.
- Current heading: Massimo program29Oct–4Nov2026, Monday closed. Multiple films have exceptions/different times by day. Parse date restrictions carefully. Sant’Andrea now lists 6–8 Nov (2026-11-05 check); the earlier 31Oct/1Nov note was stale.
- 2026-11-05 live check: the page contains zero occurrences of `lingua originale`, `versione originale`, `v.o.`, `vos`, `doppiat` and `sottotitol` (casefolded). There is no per-screening language marker, so both venues stay `manual` and no Cityplex parser exists. The app message makes no date claim, so it stays true as the programme changes.

### UCI Luxe Megalò — WORKING OFFICIAL JSON BACKEND
Base: `https://myuci---uci-backend-production-nfluwp7wga-oc.a.run.app/api`
- GET `/theatres` -> `{data:[theatres]}`. Megalò has id61, slug`uci-cinemas-megalo`, lat42.3565 lon14.1279.
- GET `/theatres/uci-cinemas-megalo/programming/2026-11-04` -> `{data:[movies]}`. Verified works via Python urllib without keys.
- Movie fields: title, slug, poster, genres, description, screens, search.
- `screens` is a list of objects keyed by screen type, e.g. `[{"2D":[version,...]}]`.
- Each version: language `{name:"ITA",slug:"ITA"}`, subtitles (nullable), duration, performances.
- Performance: day`2026-11-04`, starts_at`2026-11-04 17:30:00`, actual_start_at`17:30`, room, cart_link`/movies/...`, price_starting_from. cart_link is relative to`https://ucicinemas.it`.
- ITA alone does NOT mean dubbed: combine with independently verified original film language; foreign original language or explicit OV tokens qualify as appropriate.
- UCI website direct returned403; backend is separately publicly accessible and worked.
- Official mall confirms weekly OV screenings: `https://www.megaloweb.it/cinema/uci-luxe/`.

## The Space, Montesilvano — WORKING OFFICIAL JSON API
- `https://www.thespacecinema.it/cinema/montesilvano/al-cinema` returns 200 with an ordinary cookie jar (checked 2026-11-05; the earlier 403 is stale).
- `GET https://www.thespacecinema.it/api/microservice/showings/cinemas` lists cinemas. Montesilvano is cinema `1026`.
- `GET /api/microservice/showings/cinemas/1026/films?showingDate=YYYY-MM-DDT00:00:00&minEmbargoLevel=3&includesSession=true&includeSessionAttributes=true` returns `{result:[film], responseCode:0, errorMessage:null}`.
- Film fields used: `filmTitle`, `filmUrl`, `releaseDate`, `showingGroups[].date`, `showingGroups[].sessions[]`. There is no film-level language field.
- Session fields used: `sessionId`, `startTime`, `showTimeWithTimeZone`, `bookingUrl` (relative), `attributes[]` with `attributeType:"Language"` and `name:"LINGUA ORIGINALE"` or `"ITALIANO"`.
- Rules: `LINGUA ORIGINALE` → `original`, or `italian` when a verified Italian override matches title and year. `ITALIANO` → `italian` only with a verified Italian override; otherwise `unknown`, never `dubbed` and never `original`. Other/missing language → `unknown`. The `releaseDate` year is passed to the override matcher; a known mismatch rejects the override.
- Adapter: primes cookies once, then seven day requests one at a time under a lock with a 20 s timeout; 401 re-primes and retries once; a failed prime is reused for 60 s. No secondary site.
- Live 2026-11-05 check: `space` `ok`, `7/7 giorni letti`; Space rows `italian` 49, `unknown` 173, `original` 11, `dubbed` 0. All-source counts `italian` 185, `unknown` 529, `original` 13, `dubbed` 0, exactly the step-2 counts plus the Space rows. The 11 originals are Wild Horse Nine (eight sessions, 5–11 Nov, 19:00 plus 8 Nov 11:10), Rammstein Live in Mexico City (7 Nov 15:00) and Stray Kids (7 Nov 13:00 and 17:15).
- Live spot checks: Wild Horse Nine 5 Nov 16:55 is `ITALIANO` and stays `unknown`; 19:00 is `LINGUA ORIGINALE` and is `original`; Fast & Furious 5 Nov 22:35 is `ITALIANO` and stays `unknown`; Dio ride, Je so’ pazzo and Un tranquillo funerale di famiglia match the Italian overrides and are `italian`.
- The plan’s 2026-11-04 snapshot (Fast and Furious 18:50 VO, three ITALIANO sessions, two Rammstein VO sessions) is date-specific and is not in the 2026-11-05 seven-day window. The same mixed-session rule is proven by the offline fixture and by Wild Horse Nine.

## Aggregators and caveats
- `https://www.oraricinema.com/cinema/montesilvano/lingua-originale/` and`https://www.oraricinema.com/cinema/chieti/lingua-originale/` explicitly mark VO/VOS per time and date, but plain urllib returned403. Web search can read indexed content. Do not fabricate live coverage from indexed snippets. Some aggregator FAQs falsely call Italian originals dubbed because they classify ITA vsVO mechanically.

## Italian originals verified
See`language-overrides.json`: four current2026 films have explicit original-language Italian infobox fields checked via web tool. These are film-language facts, not actual future screenings. Match title AND year when possible to avoid collisions with2018 documentary Je so’ pazzo. Unrecognized or uncertain language should remain unknown rather than be silently admitted.
- Dio ride — https://it.wikipedia.org/wiki/Dio_ride
- Je so’ pazzo2026 — https://it.wikipedia.org/wiki/Je_so%27_pazzo_(film_2026)
- Un tranquillo funerale di famiglia — https://it.wikipedia.org/wiki/Un_tranquillo_funerale_di_famiglia
- L’estranea2026 — https://it.wikipedia.org/wiki/L%27estranea_(film_2026)
Wikipedia/Wikidata APIs returned403 in local urllib, so automated reusable enrichment not established. Curated metadata is explicit-source verified but requires maintenance for future titles.

## Saved raw research outside app folder
`%USERPROFILE%\cinema-arca.html`, `cinema-arca-film.html`, `cinema-cityplex.html`, `cinema-uci-theatres.json`, `cinema-uci-program.json` contain verified working response samples.
