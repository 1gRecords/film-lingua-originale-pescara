# PROGRESS — Cinema VO handover

**Goal:** Hand over the six-step "Voci originali" completion plan without starting it: keep the plan verbatim, add one checkbox and one Evidence line per step, then create the initial git snapshot.

**Acceptance for this handover:** every command, link and "Expected" line from the supplied plan is present; all six revised steps are unchecked; no plan step has been run; `git log` contains a commit named "Handover snapshot" (or the missing git identity is reported).

**State:** Steps 1–3 of 6 complete. Step 1 (2026-11-04): backend correctness and tests, 32 offline tests passing. Step 2 (2026-11-05): live run and source audit; server stopped afterwards; no installs or deletes. Step 3 (2026-11-05): Cityplex has no per-screening language token; both venues stay `manual` with date-free messages and no parser; 34 offline tests passing; server stopped afterwards. Steps 4–6 not started. Tracking applies to the six revised steps; the earlier five-step table is kept as history and is not tracked.

**Rule:** Whenever a plan step finishes, tick its single checkbox and replace that step's Evidence line with the command and observed result. Unverified work does not get evidence.

## Done

- Step 1 of 6: backend correctness and tests. See its Evidence line below.
- Step 2 of 6: live run and source audit. See its Evidence line below.
- Step 3 of 6: Cityplex condition check. See its Evidence line below.

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

- [ ] **Step 4 of 6 — The Space official adapter (critique-driven addition)**
  **Evidence:** _Not started; no command from this step has been run._

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

- [ ] **Step 5 of 6 — Frontend: exact fields, safe rendering, all states**
  **Evidence:** _Not started; no command from this step has been run._

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

- [ ] **Step 6 of 6 — README, launcher, run script, final report**
  **Evidence:** _Not started; no command from this step has been run._

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

## Scope note

The revised plan is six steps, within the limit. Step 4 is the critique-driven addition; if you want the original five-phase scope, drop step 4 and renumber 5–6 — the other steps stand on their own. No files were edited, no server was started, and no installs or deletions were made. If approved, I would execute step 1 only and stop after `python -B -m unittest -v test_cinema` passes.

## Next

1. Steps 1–3 are complete and evidenced. Do not start step 4 without a new instruction.

## Open questions

- Git author identity is not configured in this repo or globally. The snapshot commit cannot be created until these commands are run in `C:\DEV\Cinema`:
  ```powershell
  git config user.name "YOUR NAME"
  git config user.email "YOUR EMAIL"
  git commit -m "Handover snapshot"
  ```
- Should step 4 (The Space) stay in scope? The plan's scope note allows dropping it and renumbering steps 5–6.

## Key facts

- Repo root: `C:\DEV\Cinema`. Git 2.55.0.windows.4. No `.git` existed before this handover.
- `PROGRESS.md` did not exist before this file. `.gitignore` excludes `__pycache__/`, `*.pyc`, `.cache/`.
- The plan's findings and "Expected" lines are claims from the 2026-11-04 handover; this session re-measured none of them.
- Only the handover operations were run: file creation, `git init`, `git add -A`, `git commit -m "Handover snapshot"`. No plan command was executed.
