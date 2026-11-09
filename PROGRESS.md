# PROGRESS — Cinema VO handover

**Goal:** Hand over the six-step "Voci originali" completion plan without starting it: keep the plan verbatim, add one checkbox and one Evidence line per step, then create the initial git snapshot.

**Acceptance for this handover:** every command, link and "Expected" line from the supplied plan is present; all six revised steps are unchecked; no plan step has been run; `git log` contains a commit named "Handover snapshot" (or the missing git identity is reported).

**State:** Steps 1–6 of 6 complete. Step 1 (2026-11-04): backend correctness and tests. Step 2 (2026-11-05): live run and source audit; server stopped afterwards; no installs or deletes. Step 3 (2026-11-05): Cityplex has no per-screening language token; both venues stay `manual` with date-free messages and no parser. Step 4 (2026-11-05): The Space official adapter live, `7/7 giorni letti`, 46 offline tests passing, server stopped afterwards. Step 5 (2026-11-05): frontend null/notes/driveMinutes guards, display-only title normalization, explicit loading state, all states and both widths verified; no backend data changed; server stopped afterwards. Step 6 (2026-11-05): README, launcher, run script and final acceptance; 46 tests, 4 live sources, 2 manual, launcher opened Firefox, server stopped afterwards. Tracking applies to the six revised steps; the earlier five-step table is kept as history and is not tracked. Step 7 (2026-11-05): Italian/English switch with a persisted choice, backend translation codes, and bilingual dates, states and messages; 58 tests; server stopped afterwards. Follow-up (2026-11-05): Windows flag-emoji fallback replaced with inline SVG flags; 58 tests; server stopped afterwards. Step 8 (2026-11-05): TMDB ratings and Italian/English plots, optional local token, 30-day cache and manual overrides; 73 tests; 25 of 30 distinct titles matched live; first refresh 3.99s, cached refresh 1.41s; server stopped afterwards. Step 8 fixes (2026-11-05): yearless matches older than two years rejected, `C.A.` suffix cleaned, zero-vote ratings hidden; 77 tests; live run 711 rows, 0 matches with TMDB year < 2024; server stopped afterwards.

**Rule:** Whenever a plan step finishes, tick its single checkbox and replace that step's Evidence line with the command and observed result. Unverified work does not get evidence.

## Done

- Step 1 of 6: backend correctness and tests. See its Evidence line below.
- Step 2 of 6: live run and source audit. See its Evidence line below.
- Step 3 of 6: Cityplex condition check. See its Evidence line below.
- Step 4 of 6: The Space official adapter. See its Evidence line below.
- Step 5 of 6: frontend fields, safe rendering and all states. See its Evidence line below.
- Step 6 of 6: README, launcher, run script, final report. See its Evidence line below.
- Step 7 of 7: English version. See its Evidence line below.
- Step 8 of 8: TMDB rating and plot. See its Evidence line below.

## PLAN (copied in full)

## Read-only findings (2026-11-04, no edits, no server)

- **Toolchain:** Python 3.12.10, Node 24.19, Chrome and Edge are installed. `zoneinfo.ZoneInfo("Europe/Rome")` raises `ZoneInfoNotFoundError`, and `time.tzset` is absent. The backend cannot rely on `zoneinfo` or the host timezone; it needs a small standard-library EU DST helper.
- **Cityplex:** the live [Pescara Cityplex](https://pescaracityplex.it/) page is 140 KB and contains **zero** occurrences of `lingua originale`, `versione originale`, `v.o.`, `vos`, `doppiat` or `sottotitol`. It lists titles, date ranges and times only. Sant’Andrea is open only 31 Oct/1 Nov. The phase-3 condition is already false.
- **Arca:** [today’s programme](https://multicinema.it/Programmazione?cinema=arca&giornoSettimana=0) has 16 daily blocks and one VO block: Fast and Furious, 17:40 and 21:20. The `prog_nota1` note sits inside the daily film block, not next to one time. [Universo](https://multicinema.it/Programmazione?cinema=universo&giornoSettimana=0) has no VO note today.
- **UCI:** the [official programming API](https://myuci---uci-backend-production-nfluwp7wga-oc.a.run.app/api/theatres/uci-cinemas-megalo/programming/2026-11-04) returned 30 movies / 25 shows, all `ITA`; later days add `EN` and `KOR`. Its `search.languages` and `/movies/{slug}.languages` fields are **audio versions**, not the film’s original language. Non-ITA promotion is unsafe.
- **The Space:** the official cinemas and films APIs return 200 with an ordinary cookie jar. Montesilvano is cinema `1026`; sessions carry `Language` attributes `LINGUA ORIGINALE` and `ITALIANO`. Fast and Furious today: 16:10/18:20/21:30 `ITALIANO`, 18:50 `LINGUA ORIGINALE`; Rammstein has two VO sessions. This is the strongest screening-level evidence available, and the current app leaves it manual.
- **Frontend:** field names already match the contract. The real edge cases are a `link()` result appended without a null guard, `notes` not validated as an array, and `driveMinutes: null` being treated as 0.
- No local server was started, no files were written, no installs or deletions were made.

## Plan v1 (5 steps)

| # | Step | Files | Proof | Main risks |
|---|---|---|---|---|
| 1 | Fix the five known backend issues; add tests | `cinema.py`, `test_cinema.py` | `python -B -m unittest -v test_cinema`; `python -B -c "import cinema; print(cinema.rome_now().isoformat())"` | `zoneinfo` is absent; UCI non-ITA rows must become unknown; no year in most sources; Arca note is block-level |
| 2 | Start the server and audit every source | none | `/health` 200; `/api/screenings` 200; `curl.exe` with `Host: evil.example` returns 403 | Sites change or block; cache hides staleness; slow fetch; manual sources |
| 3 | Cityplex parser only if language is per screening | `cinema.py`, `test_cinema.py`, `SOURCES.md` | Live language-token scan; statuses from `/api/screenings` | Condition is false, so no parser; date exceptions; overclaiming |
| 4 | Align the frontend and verify every state | `web/app.js`, `web/index.html`, `web/style.css` | `node --check web/app.js`; browser at 1280 px and 390 px | Null links, async timing, mobile overflow, error state |
| 5 | README, launcher check, final report | `README.md`, `Avvia Cinema.cmd` (check only), `pandacode-run.sh` | `cmd /c "Avvia Cinema.cmd"` then `/health`; full test rerun | Port/browser blocking; PATH differences; overclaiming coverage |

## Critique (fresh pass)

**Which step is missing?** The Space. The plan leaves a 25-minute venue manual even though its official API provides exactly the screening-level `LINGUA ORIGINALE` evidence the data rules require. The live audit step also lacks a concrete expected-status table, a `?refresh=1` check, and a final measurable acceptance for the report.

**Which assumptions are unchecked or wrong?**
- `zoneinfo` is not available. The step-1 “use Europe/Rome” fix needs a manual EU DST rule, not a library assumption.
- Cityplex does not mark language per screening. Step 3 as written has no work to do; a parser would either be dead code or infer language from nationality, which the fixed data rules forbid.
- UCI has no original-language field. `search.languages` is the set of audio versions, so “tighten before trusting” must mean: non-ITA audio is unknown unless an explicit VO label or verified metadata matches it.
- The Arca VO note is attached to the daily block with multiple times. The plan must say whether it applies to all times in that block and test that it does not leak to other films or days.
- Year matching has no year in the UCI or Space payloads. The plan needs a defined fallback: year when available; unique-title match otherwise, with disclosure; known year mismatch rejected.
- The frontend’s null-append bug is not mentioned; it can inject the text “null” into the actions area.

**Is there a simpler path?** Yes:
- Do not build a Cityplex parser. Keep it manual with a specific message; that is the honest result of the live check.
- Use The Space’s official JSON API with ordinary cookies. It is simpler and safer than parsing HTML or using a secondary aggregator.
- Keep the frontend and patch the edge cases; do not rewrite it.
- Test parsers with inline fixtures, not live sites.

## Revised plan (6 steps)

### 1. Backend correctness and tests

- [x] **Step 1 of 6 — Backend correctness and tests**
  **Evidence:** 2026-11-04. `python -B -m unittest -v test_cinema` → `Ran 32 tests in 0.010s` / `OK`, exit 0. `python -B -c "import cinema; print(cinema.rome_now().isoformat())"` → `2026-11-04T14:35:41.167592+01:00`.

**Files:** `cinema.py`, `test_cinema.py`.

**Changes**
- Add `rome_now()` / `rome_today()` using the EU DST rule (last Sunday of March and October at 01:00 UTC), with an optional fixed `utc` argument for tests. Replace `date.today()` and `datetime.now().astimezone()` everywhere, including `updatedAt` and `checkedAt`.
- Normalize override keys on load: case-fold, strip accents and punctuation, collapse spaces. Index by normalized title and keep the year. Add `match_override(title, year)`:
  - exact title and year when a year is supplied;
  - unique-title match when no year is available, with `anno non disponibile` in the evidence;
  - no match for ambiguous titles or a known year mismatch.
- Change `classify(label, title, known, audio_lang=None, year=None)` precedence:
  1. explicit `doppiato` / `dubbed` label → `dubbed`;
  2. verified metadata language differs from the session audio language → `dubbed`;
  3. verified Italian → `italian`;
  4. verified language equals the session audio language → `original`;
  5. explicit `VO` / `VOS` / `OV` / `versione originale` label → `original`;
  6. otherwise `unknown`.
- UCI: remove the “any non-ITA is original” branch. Pass the session audio language to `classify`; use `https://ucicinemas.it` for `cart_link`; guard missing `day`, `title`, `language`, `subtitles` and malformed times.
- Arca: keep the VO note scoped to its daily `item_small` block; evidence must say it applies to the times in that block. Tests must prove it does not leak to the sidebar/eventi blocks or another film.
- Add `http_url()` validation for `sourceUrl` and `bookingUrl`; fall back to the source URL for anything not `http(s)`.
- Add Host-header validation: allow `127.0.0.1:<port>` and `localhost:<port>`, reject others with 403, and add `X-Content-Type-Options: nosniff`.
- Replace `SOURCES[:3]` with a loader map and explicit manual messages, so The Space can be added later without another special case.
- Test file: inline HTML/JSON fixtures only, no network. Cover normalization, year match/ambiguity/title-only, the full classification truth table, Arca block leakage, UCI ITA/EN/KOR and missing fields, DST boundaries and year rollover, Host allow/deny, API shape, manual status, and URL validation.

**Proof**
```powershell
python -B -m unittest -v test_cinema
python -B -c "import cinema; print(cinema.rome_now().isoformat())"
```
Expected: every test passes; the timestamp shows `+01:00` in November.

**What could go wrong:** a wrong DST boundary; UCI confirmed rows drop sharply because non-ITA becomes unknown; the year fallback is too permissive or too strict; the Arca block-note interpretation is disputed; tests accidentally hit the network; a Host rule breaks `localhost`; global cache state leaks between tests.

---

### 2. Live run and source audit

- [x] **Step 2 of 6 — Live run and source audit**
  **Evidence:** 2026-11-05, proof script run verbatim. `/health` → `{"status":"ok","version":"0.1-draft"}` (HTTP 200); `arca`, `universo`, `uci` = `ok` with `7/7 giorni letti`; `massimo`, `santandrea`, `space` = `manual`; classifications `italian` 136, `unknown` 356, `original` 2, `dubbed` 0; evil `Host` → `403`; `?refresh=1` → `updatedAt` `2026-11-05T14:29:54.017460+01:00`. Live cross-checks: Arca 11 Nov Wild Horse Nine 18:15/20:50 carries `VERSIONE ORIGINALE SOTTOTITOLATA IN ITALIANO`; UCI 5 Nov Wild Horse Nine 18:40 is `EN` and stays `unknown`; Cityplex has 0 occurrences of all six language terms; The Space cinemas API returns 200 but has no adapter, so `manual` is accurate. Cityplex now lists Sant'Andrea open 6–8 Nov, so the earlier 31 Oct/1 Nov note is stale. Server stopped at the end (no listener on 8765, no `cinema.py` process).

**Files:** none (read-only; record evidence for the final report).

**Changes**
- Start the server, check `/health`, `/api/screenings`, and `?refresh=1`.
- Confirm the Host attack returns 403 and a normal request returns 200.
- Compare every source status and at least one representative row against its live page/API. Expected after step 1:
  - `arca` `ok`; `universo` `ok`; `uci` `ok`;
  - `massimo` `manual`; `santandrea` `manual`; `space` `manual`;
  - no confirmed `dubbed` rows; UCI non-ITA rows are `unknown`; Italian overrides are `italian`.
- Record the current coverage counts and times; do not treat this snapshot as permanent.

**Proof**
```powershell
$server = Start-Process -FilePath python -ArgumentList '-B','cinema.py','--no-browser' -PassThru -WindowStyle Hidden
try {
  for ($i=0; $i -lt 40; $i++) {
    try { $h = Invoke-RestMethod 'http://127.0.0.1:8765/health'; break } catch { Start-Sleep -Milliseconds 500 }
  }
  $h | ConvertTo-Json -Compress
  $d = Invoke-RestMethod 'http://127.0.0.1:8765/api/screenings'
  $d.sources | Format-Table id,status,driveMinutes,message -AutoSize
  $d.screenings | Group-Object classification | Format-Table Name,Count
  $d.screenings | Where-Object classification -eq 'original' | Select-Object title,cinema,date,time,language,evidence -First 8 | Format-List
  $fresh = Invoke-RestMethod 'http://127.0.0.1:8765/api/screenings?refresh=1'
  $fresh.updatedAt
  curl.exe -s -o NUL -w "%{http_code}`n" -H "Host: evil.example" http://127.0.0.1:8765/health
} finally {
  if ($server -and -not $server.HasExited) { Stop-Process -Id $server.Id -Force }
}
```
Expected: `200` from health; source table as above; `403` from the evil Host; `updatedAt` present after refresh.

Then open these pages/endpoints and compare the app’s rows:
- [Cityplex](https://pescaracityplex.it/)
- [Arca](https://multicinema.it/Programmazione?cinema=arca&giornoSettimana=0)
- [Universo](https://multicinema.it/Programmazione?cinema=universo&giornoSettimana=0)
- [UCI API](https://myuci---uci-backend-production-nfluwp7wga-oc.a.run.app/api/theatres/uci-cinemas-megalo/programming/2026-11-04)
- [The Space cinemas API](https://www.thespacecinema.it/api/microservice/showings/cinemas)

**What could go wrong:** a site changes or blocks automation; an official page works in a browser but not in the audit; the cache returns stale `updatedAt`; a full refresh takes longer than the frontend’s 60-second abort; a source is down and must be reported as `error`, not as zero screenings; editing backend code requires restarting the process, because Python does not hot-reload.

---

### 3. Cityplex: verify the condition and do not parse

- [x] **Step 3 of 6 — Cityplex: verify the condition and do not parse**
  **Evidence:** 2026-11-05, proof commands run as written. `pescaracityplex.it` token scan → `{'lingua originale': 0, 'versione originale': 0, 'v.o.': 0, 'vos': 0, 'doppiat': 0, 'sottotitol': 0}`. `/api/screenings` → `massimo` `manual`, `santandrea` `manual`; 0 rows with `cinemaId` `massimo` or `santandrea`; no source `ok`. Messages read back from the API: Massimo “Il sito elenca titoli, date e orari ma non la lingua per proiezione. Verificare la versione sul sito o in biglietteria.”; Sant’Andrea “Il sito Cityplex elenca titoli, date e orari ma non la lingua per proiezione. Verificare la versione sul sito o in biglietteria.” No Cityplex parser; the plan’s dated Sant’Andrea wording was not used because Cityplex now lists Sant’Andrea open 6–8 Nov, and neither message makes a date claim. `python -B -m unittest -v test_cinema` → `Ran 34 tests in 0.014s` / `OK`, exit 0; the two new tests failed first on the old `settimanale` wording. Server stopped: no listener on 8765, 0 python processes.

**Files:** `cinema.py` (manual messages only), `SOURCES.md`, `test_cinema.py`.

**Changes**
- Keep Massimo and Sant’Andrea as `manual`. There is no per-screening language token, so there is no parser.
- Replace the generic message:
  - Massimo: “Il sito elenca titoli, date e orari ma non la lingua per proiezione. Verificare la versione sul sito o in biglietteria.”
  - Sant’Andrea: “Programma aggiornato al 1° novembre; nessuna proiezione successiva indicata.”
- Do not emit rows from Cityplex. Do not infer language from Italian nationality or the Comingsoon film page.
- Add a test that a manual source produces no screenings and no `ok` status.
- Append the live finding to `SOURCES.md`.

**Proof**
```powershell
@'
import urllib.request
raw = urllib.request.urlopen(urllib.request.Request('https://pescaracityplex.it/', headers={'User-Agent':'CinemaVO/1.0'}), timeout=20).read().decode('utf-8','replace')
terms = ('lingua originale','versione originale','v.o.','vos','doppiat','sottotitol')
print({t: raw.casefold().count(t) for t in terms})
'@ | python -B -
(Invoke-RestMethod 'http://127.0.0.1:8765/api/screenings').sources |
  Where-Object id -in 'massimo','santandrea' | Format-Table id,status,message
```
Expected: all counts zero; both sources `manual`; no rows with `cinemaId` `massimo` or `santandrea`.

**What could go wrong:** the site later adds a per-screening language marker; the manual message becomes stale; the Sant’Andrea programme changes; a future parser overclaims by applying a film-level label to every time. If language markers appear later, re-run this check before writing a parser.

---

### 4. The Space official adapter (critique-driven addition)

- [x] **Step 4 of 6 — The Space official adapter (critique-driven addition)**
  **Evidence:** 2026-11-05, step 4 Proof commands run against the live server on the final code. `python -B -m unittest -v test_cinema` → `Ran 46 tests in 0.024s` / `OK`, exit 0 (12 new tests: 10 Space parser, 1 canonical URL, 1 source-error status). `/api/screenings?refresh=1` → `space` `ok`, `7/7 giorni letti`, `checkedAt` `2026-11-05T15:00:35.019047+01:00`, `updatedAt` `2026-11-05T15:00:36.640998+01:00`. Space rows: `italian` 49, `unknown` 173, `original` 11, `dubbed` 0. All sources: `italian` 185, `unknown` 529, `original` 13, `dubbed` 0 — exactly step 2’s 136/356/2 plus the Space rows. The 11 originals are Wild Horse Nine (8 sessions: 5–11 Nov at 19:00 plus 8 Nov 11:10), Stray Kids 7 Nov 13:00/17:15 and Rammstein 7 Nov 15:00; the raw official API output shows `Language` = `LINGUA ORIGINALE` for Wild Horse Nine 5 Nov 19:00, Rammstein 7 Nov 15:00 and Stray Kids 7 Nov 13:00. Live spot checks: Wild Horse Nine 5 Nov 16:55 `ITALIANO` → `unknown`; Fast & Furious 5 Nov 22:35 `ITALIANO` → `unknown`; Dio ride, Je so’ pazzo and Un tranquillo funerale di famiglia → `italian`. The plan’s 2026-11-04 expectations (Fast and Furious 18:50 VO plus three ITALIANO sessions, two Rammstein VO sessions) were not replayable on 2026-11-05: that date is outside the window, Fast now has one ITALIANO session at 22:35 and Rammstein one VO at 7 Nov 15:00. The same mixed rule is proven by the inline fixture (three ITALIANO + one VO) and by Wild Horse Nine live. Server stopped at the end (no listener on 8765, no python process).

**Files:** `cinema.py`, `test_cinema.py`, `SOURCES.md`.

**Why this step:** The Space is 25 minutes from Pescara, its official API works with an ordinary cookie session, and it labels each session `LINGUA ORIGINALE` or `ITALIANO`. That is exactly the screening-level evidence the data rules demand, and it includes mixed dubbed/VO sessions for the same film.

**Changes**
- Add a `SpaceClient` using `http.cookiejar`:
  - GET `https://www.thespacecinema.it/cinema/montesilvano/al-cinema` once to obtain the ordinary cookies;
  - GET `/api/microservice/showings/cinemas/1026/films?showingDate=YYYY-MM-DDT00:00:00&minEmbargoLevel=3&includesSession=true&includeSessionAttributes=true` for seven days;
  - on 401, refresh the page cookies once and retry;
  - protect the shared opener with a lock, or serialize the seven Space requests.
- Parse `result[].showingGroups[].sessions[]`:
  - `Language` attribute `LINGUA ORIGINALE` → `original` (or `italian` if the override verifies Italian);
  - `ITALIANO` + verified Italian override → `italian`;
  - `ITALIANO` without verified metadata → `unknown`, never `dubbed` and never `original`;
  - other/missing language → `unknown`;
  - use `startTime` / `showTimeWithTimeZone` for date and time;
  - join `bookingUrl` to `https://www.thespacecinema.it`; use `filmUrl` as the row’s source link;
  - canonical source URL `https://www.thespacecinema.it/cinema/montesilvano/al-cinema`; drive time 25.
- Tests with an inline fixture: Fast and Furious with three `ITALIANO` and one `LINGUA ORIGINALE`; Dio ride with an Italian override; a foreign film with only `ITALIANO`; missing attributes; malformed time; booking URL join.
- If the API is unavailable during execution, keep the source `manual`/`error` with the exact failure. Do not invent rows.

**Proof**
```powershell
python -B -m unittest -v test_cinema
$d = Invoke-RestMethod 'http://127.0.0.1:8765/api/screenings?refresh=1'
$d.sources | Where-Object id -eq 'space' | Format-List
$d.screenings | Where-Object { $_.cinemaId -eq 'space' } | Group-Object classification | Format-Table Name,Count
$d.screenings | Where-Object { $_.cinemaId -eq 'space' -and $_.classification -eq 'original' } |
  Select-Object title,date,time,language,evidence | Format-List
```
Compare against the live API:
```powershell
@'
import json, urllib.request, http.cookiejar
UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0 Safari/537.36'}
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.open(urllib.request.Request('https://www.thespacecinema.it/cinema/montesilvano/al-cinema', headers=UA), timeout=30)
u = 'https://www.thespacecinema.it/api/microservice/showings/cinemas/1026/films?showingDate=2026-11-04T00:00:00&minEmbargoLevel=3&includesSession=true&includeSessionAttributes=true'
data = json.loads(op.open(urllib.request.Request(u, headers=UA), timeout=30).read())
for film in data.get('result', []):
    for group in film.get('showingGroups', []):
        for session in group.get('sessions', []):
            langs = [a.get('name') for a in session.get('attributes', []) if a.get('attributeType') == 'Language']
            if 'LINGUA ORIGINALE' in langs:
                print(film.get('filmTitle'), session.get('startTime'), langs)
'@ | python -B -
```
Expected: `space` `ok`; Fast and Furious 18:50 and Rammstein sessions appear as `original`; the three `ITALIANO` Fast and Furious sessions are `unknown`; the Italian overrides are `italian`; no `dubbed` in the confirmed tab.

**What could go wrong:** the cookie/token flow changes or returns 401; rate limiting; the 7-day loop serializes and slows the refresh; the API labels a session VO but the film/year match is wrong; duplicate rows; booking links change; the source is unavailable at execution time. Fall back to `manual` with a precise message rather than faking coverage.

---

### 5. Frontend: exact fields, safe rendering, all states

- [x] **Step 5 of 6 — Frontend: exact fields, safe rendering, all states**
  **Evidence:** 2026-11-05. `node --check web/app.js` → exit 0; `Select-String` sink scan → no matches. Chrome `--dump-dom` → shell `<h1 id="title">Voci originali`, `Lingua confermata`, 196 `class="screening"`. Real `GET /api/screenings?refresh=1` → 1.49s (an earlier run 1.92s); browser refresh 1.47–1.51s; the 60s abort is unchanged because it is already ≈30× the measured time, and the wait now shows `Aggiorno gli orari dai cinema…` plus `aria-busy`. Display-only title normalization: The Space `WILD HORSE NINE` and Arca `Wild Horse Nine` both render `Wild Horse Nine` (10 filtered rows), no all-caps headings on either tab, and the API JSON still returns the raw titles. Verified with live and intercepted responses: initial loading, confirmed 196 / unknown 528, search (`wild horse` 10), date 5 Nov (23), cinema (69, one venue), Italian toggle 196→13→196, refresh, empty unknown, stale-data error keeping rows, first-load 500 + retry, sources ok/manual/error, `dubbed` and `driveMinutes: null`/31 excluded, non-array `notes` normalized, `javascript:` links dropped, no `null` text. Layout: 1280 → clientWidth 1265 = scrollWidth 1265 (15px scrollbar); 390 → 390/390 with 0 elements past the edge. `desktop.png` and `mobile.png` under `.pandacode/progress-shots` inspected; the plan’s raw `--window-size=390` capture is cropped by Chrome headless on Windows, so `mobile.png` was recaptured with CDP 390×900 emulation. Server stopped: no listener on 8765, no `cinema.py` process.

**Files:** `web/app.js`, `web/index.html`, `web/style.css`.

**Changes**
- Field audit against the fixed contract: `updatedAt`, `screenings[]` (`id,title,cinemaId,cinema,city,date,time,language,classification,evidence,sourceUrl,bookingUrl,driveMinutes`), `sources[]`, `notes[]`. The current names already match; verify rather than rewrite.
- Fix the null-append bug in `rowCard`: only append the Maps link when `link()` returns a node.
- In `load()`, normalize `data.notes` to an array and keep the existing `screenings`/`sources` validation.
- Tighten `driveMinutes`: accept only a finite number between 0 and 30; do not treat `null` as 0.
- Verify all states: initial loading, confirmed tab, unknown tab, empty results, stale-data error, first-load error with retry, date/cinema/title filters, Italian toggle, refresh, source statuses `ok`/`manual`/`error`, and the `dubbed` exclusion.
- Safe rendering: keep `textContent` for all upstream text; keep `safeUrl()` restricted to `http(s)`; add no `innerHTML`.
- Responsive checks at 1280 px and 390 px: tabs, filters, actions, source cards, footer, no horizontal overflow, visible focus.

**Proof**
```powershell
node --check web/app.js
Select-String -Path 'web/app.js' -Pattern 'innerHTML|outerHTML|insertAdjacentHTML|document.write'
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --virtual-time-budget=65000 --dump-dom http://127.0.0.1:8765/ |
  Select-String -Pattern 'Voci originali','Lingua confermata','class="screening"'
```
Expected: JS check exits 0; no unsafe HTML sinks; the rendered DOM contains the app shell and at least one row or a correctly worded empty/source state.

Take screenshots for visual inspection:
```powershell
New-Item -ItemType Directory -Force 'C:\DEV\Cinema\.pandacode\progress-shots' | Out-Null
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --window-size=1280,1600 --screenshot="C:\DEV\Cinema\.pandacode\progress-shots\desktop.png" http://127.0.0.1:8765/
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --hide-scrollbars --window-size=390,900 --screenshot="C:\DEV\Cinema\.pandacode\progress-shots\mobile.png" http://127.0.0.1:8765/
```
Then open `http://127.0.0.1:8765/` for the click-through checklist. If Chrome DevTools automation is unavailable, the checklist is the acceptance evidence.

**What could go wrong:** `--dump-dom` captures the loading state before the fetch completes; live data changes between checks; the error state is hard to force without stopping the server; a selected date/cinema disappears after refresh; mobile negative margins cause overflow; a null URL still produces a text “null”; the frontend’s 60-second abort is shorter than a slow full refresh.

---

### 6. README, launcher, run script, final report

- [x] **Step 6 of 6 — README, launcher, run script, final report**
  **Evidence:** 2026-11-05. `python -B -m unittest -v test_cinema` → `Ran 46 tests in 0.024s` / `OK`, exit 0. `node --check web/app.js` → exit 0. `cmd /c "Avvia Cinema.cmd"` → launcher printed `Cinema VO: http://127.0.0.1:8765`; `/health` returned HTTP 200 `{"status":"ok","version":"0.1-draft"}`; the Firefox window title became `Voci originali · Cinema a Pescara — Mozilla Firefox`; launcher log showed the browser's `GET /` 304 (cached shell), `/health` 200 and `/api/screenings` 200; server stopped afterwards (0 listeners, 0 `cinema.py` processes). `py -3 -B cinema.py --no-browser --port 8766` → `/health` 200; stopped. `bash pandacode-run.sh` (WSL, `python3` fallback) → `/health` 200 on 8765; stopped. `/api/screenings` 200 in 2.34s; `?refresh=1` 200 in 1.79s, `updatedAt` `2026-11-05T17:19:57.580426+01:00`; 722 rows: `italian` 182, `unknown` 527, `original` 13, `dubbed` 0. Live counts drifted from step 4's 185/529/13/0; the 13 originals and 0 dubbed held. Sources: `arca`, `universo`, `uci`, `space` `ok` `7/7 giorni letti`; `massimo`, `santandrea` `manual`; no Cityplex rows; Space 231 rows; evil Host 403, `localhost:8765` 200. Chrome 156 at 1280: clientWidth 1265 = scrollWidth 1265, 0 elements past the edge; at 390: 390 = 390, 0 past; confirmed 195, unknown 520, search `wild horse` 10, date 5 Nov 22, cinema Space 59, Italian toggle 195→13→195, empty state 0; forced `/api/screenings` failure showed `Non riesco a caricare gli orari` + `Riprova adesso`, and retry recovered 194 rows. `README.md` is Italian, 72 lines, 6 cinemas (4 live, 2 manual), states the coverage gap and omits volatile exact counts; `Avvia Cinema.cmd` unchanged (check passed); `pandacode-run.sh` is LF-only, `bash -n` OK, declares `http://127.0.0.1:8765`. Server stopped at the end (0 listeners on 8765/8766, 0 `cinema.py` processes).

**Files:** `README.md` (new), `Avvia Cinema.cmd` (check; edit only if the check fails), `pandacode-run.sh` (new), `SOURCES.md` if not already updated.

**Changes**
- `README.md`: what the app does; Python 3.10+ with no packages; double-click `Avvia Cinema.cmd` or run `python cinema.py`; `--port` and `--no-browser`; the 10-minute cache and `?refresh=1`; the API contract; the data rules; a coverage table for Arca, Universo, UCI, The Space, Massimo and Sant’Andrea; the limits (estimated driving times, no live traffic, no completeness claim, UCI non-ITA unknown, Cityplex no language, source failures).
- `Avvia Cinema.cmd`: verify the `py -3` path, the `python` fallback, the browser opening, and the error pause. Document the port-in-use case.
- `pandacode-run.sh`: keep the server in the foreground and declare the preview:
```bash
#!/usr/bin/env bash
# pandacode-preview: http://127.0.0.1:8765
set -eu
cd "$(dirname "$0")"
exec python -B cinema.py --no-browser
```
- Final report: measured test result, live source table, coverage counts, browser checks, launcher check, open issues. Do not claim completeness beyond the sources actually read.

**Proof**
```powershell
cmd /c "Avvia Cinema.cmd"
# second terminal
Invoke-RestMethod http://127.0.0.1:8765/health
# fallback port, no browser
py -3 -B cinema.py --no-browser --port 8766
Invoke-RestMethod http://127.0.0.1:8766/health
# managed preview script
bash pandacode-run.sh
```
Expected: the launcher starts the server and opens the app; `/health` returns 200 on both ports; the run script declares `http://127.0.0.1:8765`.

Final acceptance:
- `python -B -m unittest -v test_cinema` passes.
- `node --check web/app.js` exits 0.
- `/health`, `/api/screenings`, `?refresh=1` return 200; evil Host returns 403.
- Source statuses are accurate; Cityplex remains manual; The Space is `ok` if the API held during the run.
- Confirmed results contain no `dubbed`; unknown results are separate; Italian originals are toggleable.
- 1280 px and 390 px layouts show no horizontal overflow; filters and states work.
- README and launcher match the measured behavior.

**What could go wrong:** port 8765 already in use; the launcher opens a browser and blocks the terminal; `py`/`python` is missing from PATH; `pandacode-run.sh` gets CRLF line endings; the README claims broader coverage than the live sources support; a last-minute source failure changes the counts.

---

### 7. English version

- [x] **Step 7 of 7 — English version**
  **Evidence:** 2026-11-05. TDD: the new contract/code tests failed first on the old API (`13 errors, 2 failures`: missing `languageCode`/`evidenceCode`/`evidenceParams`, `messageCode`/`messageParams`, `noteCodes`), then passed after the backend change. `py -3 -m unittest -v` → `Ran 58 tests in 0.033s` / `OK`, exit 0. `node --check web/app.js` → exit 0. Dictionary parity check: 100 IT keys, 100 EN keys, 74 static/literal uses, no missing or extra keys. Live server on 8765 (716 API rows, 4 sources `ok`, 2 `manual`): fresh profile stored no language, `<html lang="it">`, `Voci originali · Cinema a Pescara`, `Lingua confermata 193` / `Da verificare 518`, `giovedì 5 novembre`, `193 proiezioni`, switch `🇮🇹 IT` pressed; screenshot `step7-it-desktop.png`. Focused the `EN` button and sent a real Enter through CDP: `<html lang="en">`, `localStorage["cinemavo.lang"]="en"`, `aria-pressed` flipped, `:focus-visible` true, active element `en`; `Original voices · Cinema in Pescara`, `Language confirmed 193` / `To verify 518`, `Thursday 5 November`, `Updated 5 Nov, 17:46`, `4 of 6 sources available`, source messages `The site lists titles…` / `The Cityplex site lists titles…`, notes `DEVELOPMENT VERSION…`, evidence `Curated metadata confirms Italian as the original language (year unavailable).`, actions `Times and tickets` / `Source` / `Directions`; screenshots `step7-en-desktop.png`, `step7-en-coverage.png`. Reload kept EN (`lang=en`, storage `en`, switch pressed). EN visible-text scan over whole text nodes (allowed raw film titles, cinema/source names and city names): 0 Italian-phrase hits, 0 Italian-token hits, 0 accented-character hits. The only Italian left is cinema-supplied titles, e.g. `Un tranquillo funerale di famiglia`, `Je so' pazzo`, `L'estranea`, `Stray Kids … Lingua Originale`, `Rammstein … Lingua Originale`, plus names such as `Multiplex L’Arca`, `UCI Luxe Megalò`, `Cineteatro Sant’Andrea`. At 390 px: clientWidth 390 = scrollWidth 390, 0 elements past the edge, switch box `left 285 / right 370 / height 36`; `step7-it-mobile.png`, `step7-en-mobile.png`. EN states: empty `No confirmed screenings` + `Try changing the date, cinema or title…`; loading `Checking showtimes…` + `Updating showtimes from the cinemas…`; stale error `Update failed · showing previous data` + `You are seeing data from the last check…`; first-load error `I can’t load the showtimes` + `Failed to fetch Check your connection…` + `Try again`, recovered to 193 rows after retry; 0 Italian-token hits in all four states. Focus ring captured in `step7-switch-en-focus.png`. Server stopped: no listener on 8765, no `cinema.py` process; CDP 9222 closed. DOM dumps at `.pandacode/step7-it.html` and `.pandacode/step7-en.html` (ignored).

  **Flag fix (2026-11-05):** Windows Chrome showed the regional-indicator fallback (`IT IT`, `GB EN`) for the flag emoji. Both flags are now inline SVG in `web/index.html` (Italy `viewBox="0 0 3 2"` with green/white/red stripes; UK `viewBox="0 0 60 36"` with a simple Union Jack), sized by `.lang-flag` in `web/style.css`. The `IT` / `EN` text stays beside each flag, and `aria-pressed`, the two buttons and the focus ring are unchanged. `node --check web/app.js` → exit 0. `py -3 -m unittest -v` → `Ran 58 tests in 0.034s` / `OK`, exit 0. Desktop 1280: switch `112×36` at `left 1120 / right 1232`, flags `17×11`, no overflow. 390 px: switch `96×36` at `left 274 / right 370`, flags `15×10`, `clientWidth 390 = scrollWidth 390`, 0 elements past the edge. A real Enter on `EN` via CDP set `lang=en`, `localStorage["cinemavo.lang"]="en"`, `aria-pressed` `it=false` / `en=true`, and the focused button matched `:focus-visible`. Screenshots `step7svg-desktop.png`, `step7svg-mobile.png`, `step7svg-mobile-en.png`. Server stopped afterwards (no listener on 8765, no `cinema.py` process; CDP 9222 closed).

**Files:** `cinema.py`, `test_cinema.py`, `web/app.js`, `web/index.html`, `web/style.css`, `README.md` (language note and API contract), `PROGRESS.md`.

**Goal:** The site switches between Italian (default) and English with a small flag-plus-text control at the top: an inline SVG Italian flag with `IT` and an inline SVG Union Jack with `EN`. The choice is remembered in `localStorage`, wrapped in `try/catch`. Every string written by the app switches, including headings, buttons, filters, tabs, empty/error/loading states, source messages, evidence wording produced by `cinema.py`, dates and weekday names. Film titles and cinema names supplied by the cinemas stay as they are.

**Changes**
- Backend: add stable codes and parameters while keeping every existing Italian field:
  - screening row: `languageCode`, `evidenceCode`, `evidenceParams`;
  - source status: `messageCode`, `messageParams`;
  - payload: `noteCodes`, parallel to `notes`.
- Frontend: one `MESSAGES` dictionary for `it` and `en` plus a `t()` helper in `web/app.js`; no libraries and no npm.
- Static HTML: `data-i18n`, `data-i18n-placeholder` and `data-i18n-aria-label` attributes; split icons and counts into their own spans so replacing `textContent` cannot delete them.
- Locale-aware `Intl` formatters for day headings and timestamps; localized select options, result counts and source summaries.
- Set `<html lang>` on every language change. Read and write the stored language in `try/catch`.
- Two-button segmented switch with inline SVG flags and `IT` / `EN` text, `aria-pressed`, reachable and operable by keyboard, wrapping without overflow at 390 px.

**Proof**
```powershell
py -3 -m unittest -v
node --check web/app.js
# start the server; headless Chrome DOM dumps and screenshots for IT and EN;
# switch via the real buttons, reload to prove localStorage, scan EN visible text
```
Expected: every test passes; the JS syntax check exits 0; IT and EN both render; EN shows no Italian app text apart from film titles and cinema names; the choice survives a reload; the switch is keyboard-operable and fits at 390 px; the server is stopped afterwards.

**What could go wrong:** a missing English key silently falling back to Italian; `textContent` wiping the tab counts or the refresh icon; dates still formatted with `it-IT`; localStorage blocked or unavailable; source errors exposing raw Italian diagnostics; curated override evidence leaking into EN; the extra control causing horizontal overflow at 390 px.

---

### 8. TMDB rating and plot

- [x] **Step 8 of 8 — TMDB rating and plot**
  **Evidence:** 2026-11-05. TDD: the new `TmdbTests` failed first with `Ran 72 tests` / `19 errors` (`NotImplementedError`) before `tmdb.py`, then `py -3 -m unittest -v` → `Ran 73 tests in 0.044s` / `OK`, exit 0. `node --check web/app.js` → exit 0; IT/EN dictionaries 104/104 keys with no difference. `git check-ignore -v tmdb-key.txt tmdb-cache.json` → `.gitignore:4:tmdb-key.txt` and `.gitignore:5:tmdb-cache.json`, exit 0; the key never appeared in the API JSON or the cache (`key_in_cache=False key_in_api=False`). Live server on 8765: `/health` 200; `/api/screenings?refresh=1` 200 in 3.99s, 715 rows; `arca`, `universo`, `uci`, `space` `ok`; `massimo`, `santandrea` `manual`. TMDB: 30 distinct cleaned titles, 25 matched, 5 unmatched; 40 film keys (year/no-year variants) and 8 miss keys. Five examples (cinema title || TMDB title || year || rating || first 80 chars of Italian plot): `Je so' pazzo` || `Je so’ pazzo` || 2026 || 6.4 (31 votes) || `Je so’ pazzo è un ritratto intenso di Pino Daniele, un’anima ribelle nata nei vi`; `L'estranea` || `L'estranea` || 2026 || 7.4 (172 votes) || `La trama ruota attorno a una donna che si presenta all’improvviso a casa di sua`; `Clayface` || `Clayface` || 2026 || 7.4 (387 votes) || `La terrificante discesa di un uomo, da astro nascente di Hollywood a mostro asse`; `IT ENDS` || `It Ends` || 2026 || 5.9 (106 votes) || `Quattro amici appena diplomati partono per un giro in auto a tarda notte, speran`; `Shaun vita da pecora - Operazione Z.U.C.C.A.` || `Shaun, vita da pecora - Operazione Z.U.C.C.A.` || 2026 || 7.4 (53 votes) || `Halloween è alle porte. Shaun e tutti gli animali della fattoria si preparano pe`. Unmatched: `Hope` (ambiguous: multiple exact titles), `Fast and Furious - 25° Anniversario` (no results), `FAST & FURIOUS - 25MO ANNIVERSARIO` (no results, same film), `Stray Kids World Tour RUN IT C.A.` (no results), `Il Gruffalò e la sua piccolina + Bastoncino` (no results). A yearless `Ragione e sentimento`/`Ice Cream Man` search was ambiguous while the year-qualified Space row matched; no match was forced. Cache: first refresh 3.99s, second `?refresh=1` 1.41s (2.8×), `tmdb-cache.json` 41,811 bytes and its mtime stayed unchanged after the second refresh. Headless Chrome DOM: 193 `tmdb-rating`, 193 `tmdb-plot`, 3 fallback notes `Trama non disponibile in italiano: mostro quella inglese.`, footer `Questo prodotto usa l’API di TMDB ma non è approvato o certificato da TMDB.` with `https://www.themoviedb.org/`; screenshot `.pandacode/progress-shots/step8.png`. Server stopped: no listener on 8765, 0 python processes. The official logo was not downloaded; the credit is a text link.

  **TMDB fixes (2026-11-05):** TDD: the new tests failed first (`Hunger Games C.A.` not cleaned, `enrich()` had no `today`, rating `0.0` with `vote_count` 0), then `py -3 -m unittest -v` → `Ran 77 tests in 0.047s` / `OK`, exit 0; `node --check web/app.js` → exit 0. Changes: `clean_title` drops a trailing `C.A.`; yearless rows reject search results released more than two years before `today`, and dropping old results cannot trigger the single-result fallback; `details()` returns `rating: null` when `vote_count` is 0; cache version 2 discards matches made under the old rules; `cinema.gather` passes the Rome date. Live run on 8765: `/health` 200; `/api/screenings?refresh=1` 200, 711 rows, 40 film keys, 8 misses; `arca`, `universo`, `uci`, `space` `ok`; `massimo`, `santandrea` `manual`. Matches with TMDB year < 2024: none. Six zero-vote film entries, 0 with a rating. `Hunger Games C.A.` (3 UCI rows, 9–11 Nov 21:30) has no `tmdbKey`; the miss key `hunger games` reads `no exact title match`. Server stopped at the end (0 listeners on 8765, 0 python processes).

**Files:** `.gitignore`, `tmdb.py` (new), `cinema.py`, `test_cinema.py`, `web/app.js`, `web/index.html`, `web/style.css`, `README.md`, `tmdb-overrides.json` (new), `PROGRESS.md`.

**Files (TMDB fixes):** `tmdb.py`, `cinema.py`, `test_cinema.py`, `README.md`, `PROGRESS.md`.

**Goal:** For each distinct film, show the TMDB rating (`TMDB 7.4/10`, with vote count) and a short plot in the current UI language. If the Italian plot is empty, show the English one and say so. A missing key file leaves the app exactly as before, just without ratings and plots.

**Changes**
- Read the API Read Access Token from `tmdb-key.txt` (v4 bearer). The file is gitignored before any code is written and is never logged, printed or committed. It is sent only to `api.themoviedb.org`.
- Clean the cinema title: drop suffixes such as `- Lingua originale`, `(VO)` / `(V.O.)`, `Lingua Originale`; fold capitals and accents for comparison.
- Search `GET /3/search/movie` with `language=it-IT` (add the year when a source supplies one); on zero results retry without the year, then with `en-US`.
- Accept only:
  - exactly one result whose normalised `title` or `original_title` equals the cleaned title, with the release year within 1 year when known; or
  - a single search result with at least the minimum vote count (50) when no exact title matches.
  Multiple exact matches, or several unrelated results, stay unmatched: show nothing.
- `tmdb-overrides.json` maps a cleaned title to a TMDB id, or to `null` to block a match. An override wins over search; changing it bypasses stale cache entries.
- Fetch `GET /3/movie/{id}?language=it-IT` and `?language=en-US` for `overview`, `vote_average`, `vote_count`, title and year. Empty Italian overview falls back to English with a visible note.
- `tmdb-cache.json` (gitignored) stores matched and unmatched results for at most 30 days, far below TMDB’s 6-month limit. Only uncached films are looked up. At most 4 requests run at once. A 429 waits and retries once. Any TMDB error is caught and never breaks `/api/screenings`.
- Frontend: compact rating line and plot under each screening, language-aware on the IT/EN switch; no TMDB block when no data. Footer text credit with a link to `https://www.themoviedb.org/`. The official logo is not downloaded, so the text link is used.
- Tests with inline TMDB JSON fixtures and an injected transport, no network: title cleaning, exact match, year mismatch, ambiguous result, override (id and null), missing key, empty Italian plot, 429 retry and cache reuse.

**Proof**
```powershell
py -3 -m unittest -v
node --check web/app.js
git check-ignore -v tmdb-key.txt tmdb-cache.json
# live server: one refresh, five real films with rating and IT plot, match counts, then a timed second refresh
```

Expected: every test passes; the JS check exits 0; the key and cache are ignored; five films show matching TMDB title/year/rating/Italian plot; unmatched films have a reason; the second refresh is faster because the disk cache is reused; server stopped afterwards.

**What could go wrong:** TMDB blocked or the token invalid; a remake matched to the wrong year; a localised title differs from both TMDB titles; the extra requests push a refresh past the frontend’s 60-second abort; a cache write races a concurrent request; the key leaks into a log or a commit.

---

## Scope note

The revised plan is six steps, within the limit. Step 4 is the critique-driven addition; if you want the original five-phase scope, drop step 4 and renumber 5–6 — the other steps stand on their own. No files were edited, no server was started, and no installs or deletions were made. If approved, I would execute step 1 only and stop after `python -B -m unittest -v test_cinema` passes. Step 7 extends the plan to seven steps; the “execute step 1 only” sentence is kept as handover history.

## Next

1. All eight steps are complete and evidenced. No further step is planned; the remaining work is listed under Open issues.

## Open issues

- Massimo and Sant’Andrea stay `manual`: the Cityplex site has no per-screening language marker, so no parser can confirm their language. Users must check the venue.
- Fixed 2026-11-09: UCI versions whose `slug` starts with `ov-` (EN audio, ITA subtitles; the movie endpoint marks them "O.V.") now get the label "versione originale" and are classified `original`. Live: 5 UCI rows moved from `unknown` to `original` (George Michael: The Faith Tour x3, Wild Horse Nine, Scrooge); no UCI row with non-Italian audio is left `unknown`. Test `test_ov_slug_version_is_original_and_italian_slug_is_not`; 79 tests OK. Cityplex re-checked the same day (site, Ciaotickets, Comingsoon, Mymovies): still no per-screening language marker, so Massimo and Sant'Andrea stay `manual`.
- Coverage is not complete. Asterope in Francavilla al Mare and other nearby venues are not sources; the app covers the six named cinemas only.
- Driving times are fixed estimates from central Pescara, with no live traffic or 30-minute isochrone. Universo is exactly at the 30-minute boundary.
- Italian-original recognition depends on four hand-verified overrides in `language-overrides.json`; new Italian originals stay `unknown` until added, and ambiguous titles are rejected.
- Fixed 2026-11-09: `cinema.py` module docstring rewritten to describe the current app.
- Browser, layout and API-failure checks were run ad hoc through Chrome CDP; no committed end-to-end browser test exists.
- Fixed 2026-11-09: a busy port now prints a clear Italian message and exits 1 without a traceback; on Windows `CinemaServer` disables SO_REUSEADDR so a second copy cannot bind the same port. Verified with a server already on 8765: `exit=1`.
- The English UI is a hand-written dictionary. New UI strings must be added to both the `it` and `en` entries in `web/app.js`; since 2026-11-09 `UiDictionaryParityTest` in `test_cinema.py` enforces equal key sets and no empty values (78 tests, OK).
- A failed source’s raw diagnostic is passed through in both languages; only the surrounding template is translated. The live step 7 run had no failed source, so no raw Italian diagnostic was visible in EN.
- TMDB is optional. Without `tmdb-key.txt` there are no ratings or plots, by design; the footer credit stays visible.
- TMDB matching is deliberately conservative. Eight miss keys stayed unmatched in the fix run; `tmdb-overrides.json` is the manual fix. A yearless row of a film can stay without TMDB even when a year-qualified row of the same title matched.
- The official TMDB logo was not downloaded (no network asset downloads). The footer uses the required text credit and a link to `themoviedb.org`.

## Open questions

- None for step 4. The plan’s 2026-11-04 Fast and Furious/Rammstein expectations could not be replayed on 2026-11-05 because the programme changed; the step 4 Evidence records what was measured.
- None for step 5. The 60-second fetch timeout was not changed because the measured refresh was 1.49–1.92s; the visible loading status was added anyway.
- None for step 6. The live counts moved slightly between steps 4 and 6, so the README does not pin exact daily counts.
- None for step 7. The IT and EN dictionaries have the same 104 keys after step 8 (100 at step 7 plus the four TMDB strings), and the live EN visible-text scan found no Italian app copy outside film titles and venue/city names.
- None for step 8. The live token was valid, 25 of 30 distinct cleaned titles matched, and the five misses are recorded with their reasons. The official logo was not downloaded, so the footer uses a text link.

## Key facts

- Repo root: `C:\DEV\Cinema`. Git 2.55.0.windows.4. No `.git` existed before this handover.
- `PROGRESS.md` did not exist before this file. `.gitignore` excludes `__pycache__/`, `*.pyc`, `.cache/`, `tmdb-key.txt`, `tmdb-cache.json` and `tmdb-cache.json.tmp`.
- The plan's findings and "Expected" lines are claims from the 2026-11-04 handover. Steps 1–6 re-measured the parts they exercised; the Step 2 and Step 6 Evidence lines record the live results.
- At handover, only the handover operations were run: file creation, `git init`, `git add -A`, `git commit -m "Handover snapshot"`. No plan command was executed then.
- Step 7 stores the language in `localStorage` under `cinemavo.lang`; Italian is used when the key is absent, invalid or storage is blocked.
- Step 8 reads the TMDB token only from `tmdb-key.txt` and sends it only to `api.themoviedb.org`. `tmdb-overrides.json` (tracked) maps a cleaned title to a TMDB id or `null`. The cache and the key are gitignored; the key is never in the API JSON or the cache.
- The TMDB fix run rejects yearless releases older than two years, strips a trailing `C.A.`, and emits `rating: null` when `vote_count` is 0. The cache version is 2 so matches made under the older rules are not reused.
