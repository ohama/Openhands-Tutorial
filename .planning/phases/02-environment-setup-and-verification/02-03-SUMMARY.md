---
phase: 02-environment-setup-and-verification
plan: "03"
subsystem: tutorial/mdbook
tags: [openhands, korean, headless, uv, qwen-local, litellm, dotnet, mdbook, ch03-setup]

# Dependency graph
requires:
  - phase: 02-environment-setup-and-verification/02-02
    provides: "Verified headless invocation: PING PASS + DOTNET PASS; verbatim JSONL evidence in 02-VERIFICATION-EVIDENCE.md"
  - phase: 01-scaffold-and-concept-chapters
    provides: "mdBook scaffold, Korean prose conventions, ASCII-art diagrams, no preprocessors"
provides:
  - "src/ch03-setup/installation.md — OpenHands install via uv, PATH, --version → 1.16.0, Docker-as-GUI-only aside"
  - "src/ch03-setup/qwen-connection.md — Mode A env-var LLM config, openai/qwen-local@4000, --override-with-envs REQUIRED, litellm preflight"
  - "src/ch03-setup/first-run.md — full headless invocation, JSONL reading guide, echo ping + dotnet checklist, real timing"
  - "src/SUMMARY.md — 3부 () drafts replaced with real ch03-setup paths; 4부/5부 remain drafts"
  - "mdbook build green after wiring 3부 chapters"
affects:
  - phase 3 (run capture): reader-facing setup already documented; invocation shape established
  - phase 4 (worked-example chapter): first-run.md forward references 4부 in prose

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Mode A env-var config: LLM_MODEL/LLM_BASE_URL/LLM_API_KEY + --override-with-envs, no config.toml"
    - "JSONL reading: ActionEvent kind=TerminalAction + ObservationEvent kind=TerminalObservation"
    - "Performance reporting: cite measured evidence, not plan estimates"

key-files:
  created:
    - src/ch03-setup/installation.md
    - src/ch03-setup/qwen-connection.md
    - src/ch03-setup/first-run.md
    - .planning/phases/02-environment-setup-and-verification/02-03-SUMMARY.md
  modified:
    - src/SUMMARY.md

key-decisions:
  - "Real measured timing documented (~14-15s/call from evidence), not the plan's fictional 240s estimate"
  - "dotnet PATH: bare dotnet works (no fallback needed); documented as verified in evidence"
  - "4부/5부 forward references prose-only; no markdown links to draft () entries (per 01-02 decision)"
  - "Docker framed only as GUI/DockerWorkspace alternative, not on reader's critical path"

patterns-established:
  - "ch03-setup/ chapters match the exact invocation shape from 02-VERIFICATION-EVIDENCE.md verbatim"
  - "Pre-run checklist 4-item structure: command + success signal for each item"

# Metrics
duration: 3min
completed: 2026-05-27
---

# Phase 2 Plan 03: 3부 환경 설정 Chapter Summary

**Three Korean mdBook chapters (install/qwen-connection/first-run) written from verified headless evidence, documenting the exact uv+openhands+openai/qwen-local@4000+--override-with-envs path and ~14-15s measured timing; mdbook build green.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-05-27T08:05:52Z
- **Completed:** 2026-05-27T08:08:44Z
- **Tasks:** 3
- **Files modified:** 4 (3 new, 1 updated)

## Accomplishments

- Wrote installation.md: headless SSH Mac premise, `uv tool install openhands --python 3.12`, PATH `~/.local/bin`, `openhands --version` → 1.16.0, GUI aside (Docker for `openhands serve` only)
- Wrote qwen-connection.md: Mode A env-var config, `LLM_MODEL=openai/qwen-local`, `LLM_BASE_URL=http://127.0.0.1:4000/v1`, `LLM_API_KEY=dummy`, `--override-with-envs` REQUIRED, litellm preflight `curl` with real `MODELS: ['qwen-local'] PASS` output, real measured timing ~14-15s cited
- Wrote first-run.md: full copy-pasteable headless invocation, 4-item pre-run checklist (command + success signal), verbatim ActionEvent/ObservationEvent from JSONL for echo ping and dotnet, real timing table from evidence, prose-only forward reference to 4부
- Wired SUMMARY.md 3부 entries: three `()` drafts replaced with `ch03-setup/installation.md`, `ch03-setup/qwen-connection.md`, `ch03-setup/first-run.md`; 9 `()` draft entries remain (4부/5부/appendix)
- `mdbook build` exits 0 with `create-missing=false`; no broken links

## Task Commits

Each task was committed atomically:

1. **Task 1: installation.md + qwen-connection.md** - `b06d6af` (feat)
2. **Task 2: first-run.md** - `ab5c882` (feat)
3. **Task 3: SUMMARY.md wired + build verified** - `d3789ef` (docs)

## Files Created/Modified

- `src/ch03-setup/installation.md` — OpenHands 설치: uv install, PATH, version check, Docker-GUI aside
- `src/ch03-setup/qwen-connection.md` — 로컬 Qwen 서버 연결: env-var Mode A, --override-with-envs, litellm preflight, real timing
- `src/ch03-setup/first-run.md` — 첫 실행 테스트: headless invocation, JSONL reading guide, ping+dotnet checks, 4-item checklist
- `src/SUMMARY.md` — 3부 () drafts → real ch03-setup paths; 4부/5부 unchanged

## Decisions Made

- **Real timing documented**: Evidence shows ~14-15s/call for simple single-tool tasks. The plan text mentioned "~240s per tool-call cycle" as a worst-case estimate for the 35B model, but the measured reality was 14-15 seconds. The chapters document the actual measured times and note longer multi-step tasks will take more time. No fabrication.
- **dotnet PATH**: No fallback needed per evidence. Bare `dotnet --version` succeeded — LocalWorkspace PTY inherits host PATH including `/opt/homebrew/bin`. Documented as verified; no conditional PATH export added.
- **Docker framing**: Docker mentioned only once in installation.md as a clearly-marked aside for the GUI alternative path; not on the reader's critical path.

## Deviations from Plan

None — plan executed exactly as written. The "~240s" figure in the plan's qwen-connection.md must_haves was correctly overridden by the objective's CRITICAL ACCURACY NOTE instructing to use real measured timing from the evidence.

## Issues Encountered

None. mdbook build passed on first attempt after creating the three files before editing SUMMARY.md (per `create-missing=false` constraint).

## User Setup Required

None — no external service configuration required beyond what the chapters themselves document.

## Next Phase Readiness

- 3부 documentation complete; reader can now install and verify the headless path end-to-end
- 02-03 completes SETUP-01/02/03/04 documentation criterion for Phase 2
- Next in Phase 2: plans 02-04 and 02-05 (if required); otherwise Phase 3 (run capture) can proceed
- Phase 3 invocation shape is already documented in first-run.md — no conflict

---
*Phase: 02-environment-setup-and-verification*
*Completed: 2026-05-27*
