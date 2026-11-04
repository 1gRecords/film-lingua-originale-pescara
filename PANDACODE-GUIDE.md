# PandaCode guide for Cinema (notes for the human: agents ignore this file)

Written by Claude on 2026-11-04 from HANDOVER.md. Paste the prompts below into
PandaCode one at a time. Each prompt is meant to be run in its **own new task**,
except where it says otherwise. PROGRESS.md (created by Prompt 2) carries the memory
from one task to the next, so DeepSeek never needs the old chat.

## Setup (once)

1. PandaCode: add/open the project folder `C:\DEV\Cinema`.
2. **New task**. Harness **DeepSeek**, model **V4.1 Flash**, effort **Max**.
3. Permission mode **Plan** for Prompt 1 only. Use **Full access** for all the others.

## The plan

DeepSeek's approved plan (6 steps) lives in PROGRESS.md after Prompt 2.

| Task | What | Done when |
|---|---|---|
| Prompt 1 | Plan (Plan mode) | revised 6-step plan |
| Prompt 2 | Save plan + git | PROGRESS.md exists, first commit |
| Step 1 | Backend fixes + tests | all unit tests pass |
| Step 2 | Live audit of sources | source table + counts match the plan's "Expected" |
| Step 3 | Cityplex stays manual | clear manual messages, test passes |
| Step 4 | The Space official adapter | `space` source ok, VO sessions appear |
| Step 5 | Frontend | `node --check` passes, you clicked through it |
| Step 6 | README + launcher | README.md, launcher works, PROGRESS.md all ticked |
| End | Claude final check | see the end of this file |

---

## Prompt 1: plan (new task, **Plan** mode)

```text
Use the ds-mode and ds-plan-loop skills.
Goal: finish the "Voci originali" app in this folder (C:\DEV\Cinema): a local Python + HTML app that lists original-language and Italian-original cinema screenings within 30 minutes' drive of central Pescara, and never shows dubbed screenings.
Read first: @HANDOVER.md @PLAN.md @SOURCES.md @cinema.py @language-overrides.json and the three files in web/. The "Data rules" and "API contract" in HANDOVER.md are fixed requirements. Ignore PANDACODE-GUIDE.md (it is for me, not for you).
PLAN MODE: do not edit anything. Write a numbered plan of at most 6 steps following these phases:
1. Backend: fix the 5 "Known backend issues" in HANDOVER.md and write test_cinema.py.
2. Live run: start the server, check /health, /api/screenings, and every source status against the real websites.
3. Live parser for Pescara Cityplex (Massimo, Sant'Andrea), only if the site marks language per screening.
4. Frontend: web/app.js must match the API fields exactly; safe rendering; all filters and states work.
5. README.md, launcher check, final report.
For each step list: files touched, the exact command that proves it works, and what could go wrong. Then critique the plan once and give the revised plan.
Rules: Python standard library only, no installs, no deletes, stay inside C:\DEV\Cinema.
```

**Watch for:** it must not edit files. Copy its final revised plan; you need it for Prompt 2.

## Prompt 2: save plan (after Prompt 1 has finished, **Full access**)

Wait for Prompt 1's answer and copy the plan. Then either switch the same chat to
Full access and send this as the next message, or start a new task in Full access
and send it there. Both work the same: switching mode makes DeepSeek forget the
chat anyway, which is why you paste the plan back in.

```text
Use the ds-mode and ds-context-reset skills.
Create PROGRESS.md with the plan below copied in full (keep every command, link and "Expected" line), one checkbox per step and an "Evidence:" line under each. From now on, every task updates PROGRESS.md after finishing its step. Do not start any step.
Then run: git init, git add -A, git commit -m "Handover snapshot". If git asks for a user name or email, stop and tell me the exact command to run.
PLAN:
<paste the revised plan here>
```

## Steps 1-6: one prompt per plan step (new task each, Full access)

Use this prompt for every step. Change only `<N>` and `<SKILLS>` from the table below.

```text
Use the ds-mode, <SKILLS> skills.
Read @PROGRESS.md (it holds the full plan) and @HANDOVER.md. Do step <N> only, exactly as the plan describes, then stop.
Run the "Proof" commands of step <N> and paste their full real output. If a result differs from "Expected", fix it and run it again (at most 3 tries, then stop and explain).
Never invent data: a site that fails or blocks is reported as a gap, never as zero screenings. No installs, no deletes, stay inside C:\DEV\Cinema.
When it passes: git add -A, git commit -m "Step <N>", tick step <N> in PROGRESS.md with the evidence. Report: what changed, proof output, what is left.
```

| Step | `<N>` | `<SKILLS>` |
|---|---|---|
| Backend + tests | 1 | ds-tdd and ds-verify-loop |
| Live audit | 2 | ds-verify-loop |
| Cityplex manual | 3 | ds-tdd |
| The Space adapter | 4 | ds-tdd and ds-verify-loop |
| Frontend | 5 | ds-verify-loop and ds-design-audit |
| README + launcher | 6 | ds-unslop and ds-verify-loop |

For step 5, add this line at the end of the prompt: `Then tell me exactly what to click to test it myself in the browser, including at phone width.`

**You test it after step 5:** double-click `Avvia Cinema.cmd`, try each filter, then
make the browser window narrow (or F12, then the phone icon). If something looks
wrong, send a screenshot in the same task: "This is wrong: <what>. Fix it, re-run
node --check, commit."

---

## If something goes wrong (same task)

DeepSeek says "done" with no proof:

```text
Show me the evidence: paste the exact command you ran and its full output. If you did not run it, run it now.
```

The same error comes back twice:

```text
Use the ds-unstick skill. Stop retrying small variations. Name the assumption behind the failed fixes, test it directly, list three other approaches, pick one.
```

Terminal errors: `npm`/`npx` blocked means use `npm.cmd`/`npx.cmd`; a path starting
with `\\?\` means run `cd C:\DEV\Cinema` first.

## Step 8: final check by Claude

When PROGRESS.md is all ticked, open Claude Code in `C:\DEV\Cinema` and write:

```text
Final check of Cinema: read PROGRESS.md, run the tests and the server, spot-check a few screenings against the sources, and tell me what is wrong. Keep it short.
```
