---
phase: 11-7부-chapter-publish
plan: 11-03
subsystem: infra
tags: [mdbook, github-pages, github-actions, deploy, publish]

# Dependency graph
requires:
  - phase: 11-7부-chapter-publish
    provides: "11-01 wrote ch07-scala-calc/*.md + wired SUMMARY.md; 11-02 verified mdbook build (PUB-01 gate)"
provides:
  - "7부 Scala 계산기 chapter live at https://ohama.github.io/Openhands-Tutorial/ch07-scala-calc/intro.html"
  - "GitHub Actions deploy run 26739869947 concluded success"
  - "v1.3 milestone fully published to GitHub Pages"
affects: [any future publish plans, EXT-01, EXT-06, EXT-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PUB-02 audit guard: git diff on deploy.yml must be empty before every publish"
    - "Headless push: keychain -25308 stderr lines are benign on SSH/headless Mac; confirm success from 'main -> main' ref update line only"

key-files:
  created:
    - .planning/phases/11-7부-chapter-publish/11-03-SUMMARY.md
  modified:
    - .planning/STATE.md

key-decisions:
  - "deploy.yml confirmed byte-identical (git diff empty both working-tree and vs origin/main) — PUB-02 audit guard satisfied"
  - "Push to origin/main approved by user; no branch created"
  - "Node.js 20 deprecation annotations in Actions output are warnings only, not failures"

patterns-established:
  - "Verify deploy.yml unchanged via two git diff commands (working-tree AND vs origin) before every publish"
  - "Confirm Actions run success via gh run watch + exit status before checking live URLs"

# Metrics
duration: 8min
completed: 2026-06-01
---

# Phase 11 Plan 03: Publish 7부 to GitHub Pages Summary

**7부 Scala 계산기 chapter published live via git push + Actions deploy (run 26739869947 success); root and ch07-scala-calc/intro.html both return HTTP 200 and all 5 ch07 pages confirmed in live toc-5eb11a0d.js sidebar.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-01T06:53:10Z
- **Completed:** 2026-06-01T07:01:00Z
- **Tasks:** 3
- **Files modified:** 1 (STATE.md); 0 src/ changes (already committed Wave 1)

## Accomplishments

- deploy.yml unchanged confirmed — two git diff commands both returned empty output (hard guard passed)
- Pushed 4 Phase 11 commits to origin/main; Actions deploy run 26739869947 concluded success (build 9s + deploy 9s)
- Live verification: root HTTP 200, ch07-scala-calc/intro.html HTTP 200, all 5 ch07 pages in live toc-5eb11a0d.js, Korean "계산기" content confirmed in intro page (27,086 bytes)

## Task Commits

Tasks 1-3 had no new src/ commits (content was already committed in Wave 1 — 11-01). This plan's work was operational (push + watch + verify).

**Plan metadata:** committed below as `docs(11-03): complete publish plan`

## Evidence Log

### Task 1: deploy.yml hard guard

```
git diff -- .github/workflows/deploy.yml          → (empty)
git diff origin/main..HEAD -- .github/workflows/deploy.yml → (empty)
```

Both empty. Byte-identical confirmed. PUB-02 audit guard satisfied.

### Push result

```
git push origin main
fatal: failed to get: -25308     ← known headless keychain artifact, not a failure
fatal: failed to store: -25308   ← same
To https://github.com/ohama/Openhands-Tutorial
   7a8f1a3..256f294  main -> main
```

4 Phase 11 commits (7a8f1a3 → 256f294) delivered to origin/main.

### Task 2: Actions deploy run

- **Run ID:** 26739869947
- **Trigger:** push to main (commit 256f294 docs(11-02))
- **Job: build** — ID 78801088739, concluded success in 9s
  - checkout, install mdBook, Build book, Setup Pages, Upload artifact — all green
- **Job: deploy** — ID 78801113357, concluded success in 9s
  - Deploy to GitHub Pages — green
- **Annotations:** Node.js 20 deprecation warnings only (not failures; will auto-migrate June 16 2026)
- **Overall conclusion:** success

### Task 3: Live verification

| Check | Result |
|---|---|
| `curl -I https://ohama.github.io/Openhands-Tutorial/` | HTTP 200 |
| `curl -I https://ohama.github.io/Openhands-Tutorial/ch07-scala-calc/intro.html` | HTTP 200 |
| Live toc file | toc-5eb11a0d.js |
| ch07-scala-calc pages in toc | intro.html, planning.html, writing.html, build-test.html, final.html (all 5) |
| `7부` label in live toc | FOUND |
| Korean content in intro.html | "계산기" found, 27,086 bytes |

## Files Created/Modified

- `.planning/phases/11-7부-chapter-publish/11-03-SUMMARY.md` — this file
- `.planning/STATE.md` — updated position, v1.3 milestone marked complete

## Decisions Made

- deploy.yml was NOT modified (PUB-02 requirement); Node.js 20 deprecation warnings in Actions output are informational only and do not affect the deploy outcome.
- Push to origin/main performed directly on main branch as approved; no feature branch created.

## Deviations from Plan

None — plan executed exactly as written. The context note about `-25308` keychain stderr was accurate; push succeeded on first attempt.

## Issues Encountered

None. The known headless macOS keychain stderr artifact (`-25308`) appeared as expected but did not affect push success.

## Next Phase Readiness

- v1.3 milestone complete: 7부 Scala 계산기 is live at https://ohama.github.io/Openhands-Tutorial/ch07-scala-calc/intro.html
- All 5 ch07-scala-calc pages reachable from sidebar nav
- Open tech debt (TD-2, TD-3, TD-4, TD-5) carried forward — none blocking
- Candidate next milestones: EXT-01 (more languages), EXT-06 (35B vs 122B on Rust), EXT-07 (cross-language calculator comparison appendix)

---
*Phase: 11-7부-chapter-publish*
*Completed: 2026-06-01*
