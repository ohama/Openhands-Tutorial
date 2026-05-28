---
phase: 01-scaffold-and-concept-chapters
plan: 01
subsystem: infra
tags: [mdbook, korean, github-pages, scaffold, toml]

requires: []
provides:
  - mdBook scaffold with book.toml (ko language, /OpenHandsTests/ site-url, create-missing=false)
  - src/SUMMARY.md with all 5-part TOC (Phase-1 real paths, Phase 2-5 draft entries)
  - src/about.md Korean prefix chapter (purpose, audience, prerequisites, ~240s/request warning)
  - Seven Phase-1 chapter H1-only stubs for ch01-agentic-ai/ and ch02-openhands/
  - .gitignore ignoring generated book/ directory
  - Verified mdbook build exits 0 with lang="ko" and /OpenHandsTests/ site-url
affects:
  - 01-02-PLAN.md (overwrites ch01-agentic-ai stubs with full prose)
  - 01-03-PLAN.md (overwrites ch02-openhands stubs with full prose)
  - All future phases (URL structure is now stable; Phase 2-5 draft entries ready for content)

tech-stack:
  added: [mdbook@0.5.3 (brew install)]
  patterns:
    - "ASCII kebab-case paths only; Korean text only inside file content and SUMMARY titles"
    - "Phase 2-5 chapters as mdBook draft entries with empty () hrefs to avoid missing-file errors"
    - "Minimal Korean H1 stubs for Phase-1 files that will be overwritten this same phase"

key-files:
  created:
    - book.toml
    - .gitignore
    - src/SUMMARY.md
    - src/about.md
    - src/ch01-agentic-ai/overview.md
    - src/ch01-agentic-ai/concepts.md
    - src/ch02-openhands/overview.md
    - src/ch02-openhands/agent-loop.md
    - src/ch02-openhands/actions-observations.md
    - src/ch02-openhands/runtime.md
    - src/ch02-openhands/llm-integration.md
  modified: []

key-decisions:
  - "mdbook not pre-installed; installed via brew install mdbook (0.5.3)"
  - "Plan verification criterion for grep -c '/OpenHandsTests/' book/index.html > 0 does not hold for mdBook 0.5.x - site-url is embedded in 404.html base href, not index.html asset paths. Build is correct."
  - "SUMMARY.md draft entry count is 12, not 13 as stated in plan verify comment - counting the actual template content, there are 12 empty () entries"

patterns-established:
  - "Pattern 1: All file paths under src/ use ASCII kebab-case only; Korean appears only in file content"
  - "Pattern 2: Draft chapters use empty () hrefs - never create empty files for unwritten chapters"
  - "Pattern 3: Phase-1 stubs contain a single Korean H1 matching their SUMMARY entry title"

duration: 15min
completed: 2026-05-27
---

# Phase 01 Plan 01: Scaffold and mdBook Foundation Summary

**mdBook 0.5.3 scaffold with Korean book.toml, 5-part SUMMARY.md with draft entries, Korean about.md prefix chapter, and seven Phase-1 H1 stubs; mdbook build exits 0**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-27T06:20:22Z
- **Completed:** 2026-05-27T06:35:00Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Installed mdbook 0.5.3 via Homebrew (was not pre-installed)
- Created book.toml with correct Korean locale, /OpenHandsTests/ GitHub Pages site-url, and create-missing=false
- Created full 5-part SUMMARY.md: Phase-1 chapters with real file paths, Phase 2-5 with draft () entries
- Created Korean about.md prefix chapter (35 lines, covering purpose/audience/prerequisites/structure/performance)
- Created seven Phase-1 stub files (H1-only) to satisfy create-missing=false while plans 01-02/01-03 fill them in
- mdbook build exits 0; book/index.html generated with lang="ko"

## Task Commits

Each task was committed atomically:

1. **Task 1: Create book.toml and .gitignore** - `eb64b4e` (chore)
2. **Task 2: Create SUMMARY.md and Phase-1 chapter stubs** - `ab21d70` (chore)
3. **Task 3: Write about.md and run mdbook build** - `94a6a79` (docs)

## Files Created/Modified

- `book.toml` - mdBook build config: ko language, /OpenHandsTests/ site-url, create-missing=false
- `.gitignore` - ignores generated book/ output directory
- `src/SUMMARY.md` - full 5-part TOC with Phase-1 real paths and Phase 2-5 draft entries
- `src/about.md` - Korean prefix chapter (purpose, audience, prerequisites, structure, performance warning)
- `src/ch01-agentic-ai/overview.md` - H1 stub: # 에이전틱 AI 개요
- `src/ch01-agentic-ai/concepts.md` - H1 stub: # 핵심 개념과 용어
- `src/ch02-openhands/overview.md` - H1 stub: # OpenHands 개요
- `src/ch02-openhands/agent-loop.md` - H1 stub: # 에이전트 루프 상세
- `src/ch02-openhands/actions-observations.md` - H1 stub: # 액션과 관찰 타입
- `src/ch02-openhands/runtime.md` - H1 stub: # 런타임과 샌드박스
- `src/ch02-openhands/llm-integration.md` - H1 stub: # LLM 연동: LiteLLM

## Decisions Made

- **mdbook installed via brew:** mdbook was not pre-installed; Homebrew was used (brew install mdbook → 0.5.3).
- **site-url embedding in mdBook 0.5.x:** The plan's verify criterion `grep -c '/OpenHandsTests/' book/index.html > 0` does not match mdBook 0.5.x behavior. The site-url is embedded in the 404.html `<base href="/OpenHandsTests/">` tag (used for GitHub Pages navigation), not in index.html asset paths. The build is correct; the criterion was written for an older mdBook version. Noted as informational.
- **Draft entry count is 12 not 13:** The plan's verify comment says "returns 13" but the SUMMARY.md template has exactly 12 empty () entries (3 + 5 + 2 + 2). The content was created exactly as specified in the template.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing mdbook dependency**
- **Found during:** Task 3 (mdbook build)
- **Issue:** mdbook was not installed; `command -v mdbook` and filesystem search returned nothing
- **Fix:** Ran `brew install mdbook` - installed version 0.5.3
- **Files modified:** None (system-level install)
- **Verification:** `/opt/homebrew/bin/mdbook build` exits 0
- **Committed in:** 94a6a79 (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking dependency install)
**Impact on plan:** Required to unblock the mdbook build verification. No scope creep.

## Issues Encountered

- Plan verify criterion `grep -c '/OpenHandsTests/' book/index.html > 0` does not match mdBook 0.5.x behavior (site-url goes into 404.html base href, not index.html asset paths). Build is functionally correct for GitHub Pages deployment.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 01-02 can immediately overwrite ch01-agentic-ai/ stubs with full Korean prose
- Plan 01-03 can immediately overwrite ch02-openhands/ stubs with full Korean prose
- URL structure is now stable; no reordering needed
- mdbook installed at /opt/homebrew/bin/mdbook for all subsequent builds

---
*Phase: 01-scaffold-and-concept-chapters*
*Completed: 2026-05-27*
