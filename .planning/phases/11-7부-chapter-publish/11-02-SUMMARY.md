---
phase: 11-7부-chapter-publish
plan: 11-02
subsystem: infra
tags: [mdbook, build-verification, publish-gate, PUB-01]

# Dependency graph
requires:
  - phase: 11-7부-chapter-publish
    plan: 11-01
    provides: "5 src/ch07-scala-calc/*.md files + 7부 section wired into src/SUMMARY.md"
provides:
  - "PUB-01 gate: confirmed mdbook build exits 0, zero errors, zero new warnings"
  - "7부 HTML rendered under book/ch07-scala-calc/ (5 pages)"
  - "7부 sidebar nav entries #23–#27 verified in toc-5eb11a0d.js"
  - "1부–6부 + 부록 A/B/C regression-free"
affects:
  - "11-03-PLAN (GitHub Pages deploy — safe to push now that build is clean)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verify-only plan: no source edits; report failures rather than fix them here"
    - "Warning-set subset assertion: only TD-4 <char> warning accepted; any new warning = structured blocker"

key-files:
  created:
    - .planning/phases/11-7부-chapter-publish/11-02-SUMMARY.md
  modified: []

key-decisions:
  - "PUB-01 PASS: build is clean; no blockers for GitHub Pages deploy"
  - "Warning set confirmed: only the pre-existing TD-4 <char> warning from appendix-c-comparison.md; zero new warnings for 7부"

patterns-established:
  - "Post-chapter build gate: run before every publish; assert warning-set subset, not just exit-0"

# Metrics
duration: 3min
completed: 2026-06-01
---

# Phase 11 Plan 02: PUB-01 Build Gate Summary

**mdbook build exits 0 with zero errors; the only warning is the pre-existing TD-4 `<char>` tag in appendix-c-comparison.md; all five 7부 HTML pages rendered and wired into sidebar nav items 23–27; no regression to 1부–6부 or 부록 A/B/C.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-06-01T06:40:00Z
- **Completed:** 2026-06-01T06:40:53Z
- **Tasks:** 3
- **Files modified:** 0 (verify-only plan)

## Accomplishments

- mdbook build confirmed exit 0, zero errors.
- Warning set confirmed: exactly one warning, the pre-existing TD-4 `<char>` warning — zero new warnings for the 7부 entries.
- All five 7부 HTML pages generated (intro, planning, writing, build-test, final) and linked as sidebar items 23–27 in `toc-5eb11a0d.js`.
- No regression: 1부 through 6부 all present (ch01–ch06 dirs with HTML); 부록 A/B/C HTMLs exist; all TOC entries intact.

## Task Commits

This plan is verify-only; no task commits to source files. The only commit is the plan-metadata commit.

**Plan metadata:** see below (docs: complete PUB-01 build gate plan)

## Build Evidence

### Full `mdbook build` stdout+stderr (verbatim)

```
 INFO Book building has started
 INFO Running the html backend
 WARN unclosed HTML tag `<char>` found in `appendix-c-comparison.md` while exiting TableCell
HTML tags must be closed before exiting a markdown element.
 INFO HTML book written to `/Users/ohama/projs/OpenHandsTests/book`
EXIT CODE: 0
```

### Warning-set assertion

| Warning observed | Source file | Accepted? |
|---|---|---|
| `unclosed HTML tag <char>` (TableCell) | `appendix-c-comparison.md` | YES — pre-existing TD-4 |

**New warnings introduced by 7부:** ZERO. No broken-link, no missing-file, no any other warning.

Assertion passes: `observed_warnings ⊆ {TD-4 <char>}` — TRUE.

### 7부 HTML files generated

```
book/ch07-scala-calc/
  build-test.html
  final.html
  intro.html
  planning.html
  writing.html
```

All 5 expected files present.

### 7부 sidebar TOC (from toc-5eb11a0d.js)

Sidebar entries 23–27 (verbatim from generated JS):

```
23. ch07-scala-calc/intro.html      "예제 프로젝트 소개"
24. ch07-scala-calc/planning.html   "태스크 계획 단계"
25. ch07-scala-calc/writing.html    "코드 작성 단계"
26. ch07-scala-calc/build-test.html "빌드와 테스트 단계"
27. ch07-scala-calc/final.html      "완성된 Scala 계산기"
```

Part title in TOC: `7부: 다른 워킹 예제 - Scala 계산기` — confirmed present.

### No-regression check

| Part | Directory | HTML count |
|---|---|---|
| 1부 (에이전틱 AI) | book/ch01-agentic-ai/ | 2 |
| 2부 (OpenHands) | book/ch02-openhands/ | 5 |
| 3부 (환경 설정) | book/ch03-setup/ | 3 |
| 4부 (F# 계산기) | book/ch04-calculator/ | 5 |
| 5부 (정리) | book/ch05-wrap-up/ | 2 |
| 6부 (Rust 서버) | book/ch06-rust-server/ | 5 |
| 7부 (Scala 계산기) | book/ch07-scala-calc/ | 5 |
| 부록 A | book/appendix-a-repro.html | exists |
| 부록 B | book/appendix-b-troubleshooting.html | exists |
| 부록 C | book/appendix-c-comparison.html | exists |

All parts present. Zero regression.

## Decisions Made

- PUB-01 PASS. The build is clean and it is safe to push to `main` for GitHub Pages deploy.
- No source edits were made in this plan (honesty discipline: verify-only; any failure would be reported as a structured blocker back to plan 11-01).

## Deviations from Plan

None — plan executed exactly as written. Build was clean on the first attempt.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- PUB-01 gate satisfied.
- Safe to push `main` to GitHub Pages (`git push origin main` triggers the deploy workflow).
- TD-4 (`<char>` warning in 부록 C) remains open but accepted — cosmetic, no action needed before deploy.

---
*Phase: 11-7부-chapter-publish*
*Completed: 2026-06-01*
