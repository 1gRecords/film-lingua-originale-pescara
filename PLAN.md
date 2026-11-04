# Cinema vicino a Pescara

Goal: a small local application that finds original-language cinema screenings within approximately 30 minutes of central Pescara, including Italian originals and excluding dubbed screenings.

1. Verify live cinema sources and language evidence. Check: actual HTTP responses and screening-level language markers.
2. Build a standard-library Python server and a buildless HTML/CSS/JS interface. Check: parser/classifier unit tests and JavaScript syntax.
3. Add a Windows launcher, run live API checks, and inspect desktop/mobile UI. Check: local HTTP 200, source statuses, no invented screenings, accessible filter and error states.
4. Have an independent agent review the result, fix real findings, and document launch instructions and coverage limits. Check: reviewer verdict and passing checks.

Plan critique: the main risk is inferring audio language from a film's nationality, or treating a film-level VO label as applying to every showing. Both require explicit evidence. Sources can fail or omit language, so the UI must show gaps. A local Python server avoids installation, API keys, bundling, accounts, and a hosted scraping proxy.

Design: an Italian cinema programme for someone choosing tonight's screening. Warm paper, dark ink, burnt orange actions, a serif headline, compact timetables and visible language evidence. No poster downloads or external fonts. Dates use Europe/Rome. Driving minutes are estimates, with directions linked for checking.

Status: source research, backend and frontend delegated to separate files. No prior project files were present.

Paused at user request on 4 November 2026. See HANDOVER.md for exact state, saved files and known bugs. Research and drafts are saved; frontend JavaScript syntax passed. Backend and end-to-end checks, browser verification and independent review are unfinished. Do not mark the application complete.
