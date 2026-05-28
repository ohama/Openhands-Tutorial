---
phase: 01-scaffold-and-concept-chapters
plan: 02
subsystem: docs
tags: [mdbook, korean, agentic-ai, concepts, vocabulary]

# Dependency graph
requires:
  - phase: 01-scaffold-and-concept-chapters
    plan: 01
    provides: mdBook scaffold with SUMMARY.md and ch01-agentic-ai stub files
provides:
  - Full Korean prose overview.md (CONCEPT-01): agentic AI vs reactive chatbot contrast
  - Full Korean prose concepts.md (CONCEPT-02): four vocabulary terms with prose forward pointers to 4부
affects:
  - 01-03 (ch02-openhands architecture chapter references these definitions)
  - 04 (ch04-calculator chapters assume readers know these four terms)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Korean prose with English technical terms inline (agent loop, tool calling, EventLog, ActionEvent)"
    - "Prose-only forward pointers to unwritten chapters to avoid dead Markdown links in deployed book"
    - "Concept↔component↔chapter mapping table for cross-reference"

key-files:
  created: []
  modified:
    - src/ch01-agentic-ai/overview.md
    - src/ch01-agentic-ai/concepts.md

key-decisions:
  - "Forward pointers to 4부 are prose-only ('4부 ... 볼 수 있습니다'), not Markdown links — avoids 404s in deployed Phase 1 book"
  - "Only allowed cross-chapter Markdown link is overview.md → concepts.md (same directory, file already exists)"
  - "Closing concept↔component↔4부 mapping table in concepts.md reinforces forward pointers without introducing links"

patterns-established:
  - "Each vocabulary term section ends with one prose forward-pointer sentence containing '4부'"
  - "Technical terms stay in English inline within Korean prose (agent loop, tool calling, EventLog, CondensationSummaryEvent)"

# Metrics
duration: 5min
completed: 2026-05-27
---

# Phase 1 Plan 02: Concept + Vocabulary Chapter Summary

**Full Korean prose for 1부: overview.md contrasts agentic AI vs reactive chatbot; concepts.md defines tool calling, agent loop, plan→write→test→run, and memory/context — each anchored to 4부 via prose forward pointers**

## Performance

- **Duration:** 5 min
- **Started:** 2026-05-27T06:26:29Z
- **Completed:** 2026-05-27T06:32:15Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Wrote overview.md: explicit 4-point contrast table (응답 방식, 환경 행동, 단계 결정, 상태 관리), Korean prose, English technical terms, prose foreshadowing of F# calculator, link to concepts.md
- Wrote concepts.md: four `##` sections (tool calling, agent loop, plan→write→test→run, memory/context), each with a prose forward-pointer sentence containing "4부" (10 occurrences total), closing concept↔component↔4부 mapping table
- `mdbook build` exits 0 after both files written

## Task Commits

Each task was committed atomically:

1. **Task 1: Write overview.md (agentic AI vs reactive chatbot)** - `d39ccb2` (docs)
2. **Task 2: Write concepts.md (four vocabulary terms with prose forward pointers)** - `b5ecb73` (docs)

**Plan metadata:** (this commit) (docs: complete concept+vocabulary chapter)

## Files Created/Modified

- `src/ch01-agentic-ai/overview.md` - Full Korean prose: agentic AI definition, 4-point chatbot contrast table, prose foreshadowing of OpenHands F# calculator, link to concepts.md (68 lines, 41 non-blank)
- `src/ch01-agentic-ai/concepts.md` - Full Korean prose: four vocabulary terms with prose forward pointers to 4부, closing mapping table, summary section (104 lines, 60 non-blank)

## Decisions Made

- **Prose-only forward pointers** — Forward references to 4부 chapters use prose ("4부 '코드 작성 단계'에서 ... 볼 수 있습니다") rather than Markdown links. Phase 4 chapter files do not exist yet; Markdown links would produce 404s in the deployed Phase 1 book.
- **Only allowed cross-chapter link is overview.md → concepts.md** — Both files are in the same directory and both exist; this link is safe and correct per plan specification.
- **Closing mapping table in concepts.md** — Added concept↔OpenHands V1 component↔4부 mapping table consistent with 01-RESEARCH.md. Reinforces forward pointers without introducing links to unwritten files.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The non-blank line count for concepts.md required careful attention — the initial draft had 49 non-blank lines, which was below the required minimum of 60. Content was expanded across each section with additional substantive prose (deeper explanations, cross-concept relationships, summary section) to reach exactly 60 non-blank lines.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CONCEPT-01 and CONCEPT-02 are complete; 1부 concept chapters are ready
- Plan 01-03 (ch02-openhands architecture) can reference these definitions freely
- Phase 4 chapters (ch04-calculator) can assume readers have read these two chapters
- No blockers from this plan

---
*Phase: 01-scaffold-and-concept-chapters*
*Completed: 2026-05-27*
