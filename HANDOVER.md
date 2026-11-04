# Cinema Pescara: handover

Date: 4 November 2026, Europe/Rome.

## User request

Create very lightweight software that finds original-language cinema screenings near Pescara. The user clarified a maximum of **30 minutes by car from central Pescara**. Include Italian-original films; exclude dubbed screenings. Work in **C:\DEV\Cinema**. Agents were explicitly authorized. The user then requested stopping and a handover file, so work is paused and must not continue without a new instruction.

## Current state

**This is an unfinished application, not a tested or delivered product.** Research and initial implementation were in progress when the user requested the stop. Do not assume the launcher works until `cinema.py` exists and the checks below pass. Nothing has been published, no server was started, and this folder was not a Git repository at handover.

Files created by the coordinator:

- `PLAN.md`: goal, acceptance checks, plan critique, design direction.
- `Avvia Cinema.cmd`: Windows launcher. Uses `py -3 cinema.py`, falling back to `python cinema.py`. Intended to open the local app through the Python server. Requires the backend to be finished.
- `.gitignore`: ignores Python bytecode and cache files.
- `HANDOVER.md`: this document.

Agent output saved and confirmed on disk: `cinema.py`, `web/index.html`, `web/style.css`, `web/app.js`, `SOURCES.md`, and `language-overrides.json`. No `test_cinema.py` or backend notes file was created. Read `SOURCES.md` and inspect the actual code before resuming. An existing file is not evidence that integration passed.

## Chosen implementation

Local app: Python 3 standard library only, serving a buildless HTML/CSS/JavaScript UI at `http://127.0.0.1:8765`. No npm dependencies, accounts, API keys, external fonts, poster downloads, or hosted proxy. Bind to loopback only. Python 3.12, Node and Git are installed on this computer.

Frontend language: Italian. Name: **Voci originali.** Warm cream paper, ink text, serif display headline, burnt-orange actions, compact timetable layout. Responsive desktop/mobile, accessible labels and focus states.

Proposed controls: date, cinema, title search, include Italian originals (on by default), refresh, and a separate uncertain-language view. Show source coverage/errors, evidence for original language, booking/source links, and Google Maps directions. Driving minutes are estimates, not live traffic or a verified 30-minute isochrone.

## Data rules

- Confirm VO/VOS/OV or equivalent at the **screening** level. A film-level label must not accidentally mark every session as original audio.
- Italian nationality alone does **not** prove Italian original audio. Require original-language metadata and disclose how it is matched to the screening.
- Default results contain only confirmed original-language or Italian-original screenings. Unknown language is separate. Dubbed screenings must never appear in confirmed results.
- Never invent films, dates, times, language or availability. A blocked/failed feed must be shown as a coverage gap, not as zero screenings.
- Use Europe/Rome dates; handle year rollover, date-specific sessions, midnight times and expired shows.
- Fetch known fixed upstream sources with timeouts and bounded concurrency. Proposed in-memory cache TTL: 10 minutes. Do not create an arbitrary-URL proxy.

## API contract agreed between agents

`GET /api/screenings` and optional `?refresh=1`:

```json
{
  "updatedAt": "ISO timestamp",
  "screenings": [{
    "id": "stable identifier",
    "title": "Film title",
    "cinemaId": "venue-id",
    "cinema": "Venue name",
    "city": "Town",
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "language": "Screening language",
    "classification": "original | italian | unknown | dubbed",
    "evidence": "Why this screening qualifies",
    "sourceUrl": "https://...",
    "bookingUrl": "https://...",
    "driveMinutes": 20
  }],
  "sources": [{
    "id": "source-id",
    "name": "Source name",
    "url": "https://...",
    "status": "ok | error | manual",
    "message": "Coverage description or failure",
    "checkedAt": "ISO timestamp",
    "driveMinutes": 20
  }],
  "notes": []
}
```

Backend should also provide `GET /health`, static files from `web/`, CLI `--port` and `--no-browser`. Default launcher should open the browser. Use safe DOM rendering for upstream text and validate external link schemes.

## Verified research and remaining coverage

- **L'Arca, Spoltore**: `https://multicinema.it/Programmazione?cinema=arca` returns server-rendered HTML. Backend agent found `span.prog_nota1` containing `VERSIONE ORIGINALE SOTTOTITOLATA IN ITALIANO` next to specific sessions. Date-specific schedules are available. Film detail pages have nationality/original title but do not generally expose original-language metadata.
- **Massimo and Sant'Andrea, Pescara**: `https://pescaracityplex.it/` returns server-rendered weekly programmes. Parse date scopes carefully. Film metadata alone may omit language.
- **The Space, Montesilvano**: official site returned HTTP 403 to automation. Secondary original-language listings are available at `https://www.oraricinema.com/cinema/montesilvano/lingua-originale/`. Explicitly identify secondary data and failed official access.
- **UCI Megalò, Chieti**: research agent found a working official live API with session-level language fields and sent its details to the backend agent. See `SOURCES.md` or backend notes for the exact endpoint. Secondary VO/VOS listing: `https://www.oraricinema.com/cinema/chieti/lingua-originale/`.
- **Universo, Silvi**: backend agent considered adding the Multicinema schedule. Check whether driving time is actually within the chosen limit before including it.
- **Asterope, Francavilla al Mare**: initial search found a listing but no current programme. Do not infer that it is closed. Verify coverage if pursuing completeness.
- The researcher was preparing verified original-language references for current Italian titles, with a proposed `language-overrides.json` keyed by normalized title, each value containing `language`, `evidence`, and `sourceUrl`. Check actual saved references. Avoid matching a remake or a different release with the same title; year-aware matching is preferable.

The app must not claim all nearby cinemas are covered until that is substantiated. Current sources, access restrictions and estimated driving times limit completeness.

## Agent work at stop

- `/root/cinema_sources`: source research and Italian language evidence; asked to save `SOURCES.md` and any ready metadata overrides, then stop.
- `/root/backend`: owned only `cinema.py` and `test_cinema.py`; asked to stop feature work and save coherent drafts or `BACKEND-NOTES.md`, rather than finish an estimated eight more minutes of work.
- `/root/frontend`: owned only `web/` files; asked to save its current work and stop, with syntax-check status if ready.

## Resume steps

1. Read this file, `PLAN.md`, `SOURCES.md`, backend notes, and actual source. Check for unfinished drafts and mismatched API fields.
2. Finish the Python source adapters and classification without weakening the language-evidence rules. Integrate Italian metadata and document stale/missing metadata behavior.
3. Run `python -m unittest -v` and `node --check web/app.js`. Add focused tests for mixed dubbed/VO sessions, Italian nationality versus original language, date rollover, parser failures and feed errors.
4. Run `python cinema.py --no-browser`, then request `/health`, `/api/screenings` and `/`. Inspect real output and every source status; compare representative sessions against their sources.
5. Test the actual browser at desktop and approximately 390px widths. Verify filters, Italian toggle, unknown view, refresh, empty/error states, links and no horizontal overflow.
6. Get one independent review, fix real findings, write a concise `README.md`, and verify the Windows launcher. Report measured coverage and limits. Do not claim completion based only on syntax checks.

## Verification performed before stopping

- Confirmed project directory was initially empty and no parent `C:\DEV\AGENTS.md` was present.
- Confirmed Python, Node and Git are installed.
- Read official/secondary cinema source pages and agent-reported HTTP/parser evidence above.
- At the time this handover was first written, no end-to-end runtime, backend unit tests, or browser UI checks had completed. Agent completion notes below may add narrower checks; they do not substitute for integration tests.

## Final agent reports at stop

All three agents stopped. The backend is an **untested draft** (approximately 10 KB), with local server endpoints and seven-day adapters for Arca, Universo and UCI Megalò. Massimo, Sant'Andrea and The Space are manual coverage entries, not implemented live parsers.

Known backend issues reported by its author, to fix before use:

1. Override lookup normalizes titles by stripping punctuation/spaces, while saved metadata keys retain spaces. Normalize both consistently and match the film year.
2. UCI currently promotes any non-ITA session to original without verifying the film's actual original language. This can admit another dubbed language. Tighten before trusting confirmed results.
3. Date calculations use host-local `date.today()`, not explicit Europe/Rome.
4. Loopback server has no DNS-rebinding Host-header validation. Review network boundary before launching.
5. No backend syntax, unit, live API, or integration checks have run; no tests were written.

The frontend files are saved (approximately 23 KB combined). Its agent ran **`node --check web/app.js`: passed, exit 0**. It has the planned filters, separate confirmed/unknown views, source coverage, loading/error states and responsive styling. It has **not** been browser-tested or integrated against the backend.

Research is saved in `SOURCES.md`. Four Italian-original film metadata overrides are saved in `language-overrides.json`, with explicit references and verification dates. These are curated facts for current films, not an automatic metadata discovery system.

Important correction to source accessibility: Oraricinema pages were readable through indexed web results, but local automated HTTP requests returned **403**. They are not verified working live adapters. Do not turn snippets into purported live results. The Space API endpoint in `SOURCES.md` is a lead, not a tested endpoint. UCI's API, Arca/Universo HTML and Cityplex HTML were actually accessible during research.

No app server was launched. No hosted Site was created or published. Work is paused at the user's request.
