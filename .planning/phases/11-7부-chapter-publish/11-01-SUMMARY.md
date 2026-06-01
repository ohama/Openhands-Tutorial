---
phase: 11-7부-chapter-publish
plan: 11-01
subsystem: docs
tags: [scala3, calculator, recursive-descent, chapter-writing, mdbook, korean]

# Dependency graph
requires:
  - phase: 10-capture-the-35b-scala-calculator-run
    provides: captured-scala/ (CAPTURE-MANIFEST.md, task1/2/3 JSONL, final-source/Calc.scala, test-output.txt)
provides:
  - 7부 chapter (5 files) under src/ch07-scala-calc/
  - src/SUMMARY.md wired with 7부 section (5 entries, after 6부, before ---)
affects:
  - any phase that deploys the mdBook (GitHub Pages publish)
  - future EXT-07 cross-language comparison appendix

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "5-file 워킹예제 chapter shape: intro/planning/writing/build-test/final (mirrors 4부/6부)"
    - "honesty-first callouts: 사용자 프롬프트/내부 프로세스/결과 + 개념↔행동, no emoji, 출처: lines"
    - "manifest 1-based event-number citations (authoritative; JSONL 0-based +1)"

key-files:
  created:
    - src/ch07-scala-calc/intro.md
    - src/ch07-scala-calc/planning.md
    - src/ch07-scala-calc/writing.md
    - src/ch07-scala-calc/build-test.md
    - src/ch07-scala-calc/final.md
  modified:
    - src/SUMMARY.md

key-decisions:
  - "Code quoted byte-identical from final-source/Calc.scala (70 lines, var pos = 0 on line 10; private appears only in error narrative)"
  - "Honesty framing: no sealed-trait ADT claim (manifest adt-style=None); contrast = hand-rolled recursive descent (unaided) vs FsLex/FsYacc DSL (scaffolded)"
  - "~14-32s/call cited ONLY as an explicitly-labeled v1 pre-run prediction being corrected (솔직한 표기 주의 callout in final.md), never as a measurement"
  - "Event numbers from CAPTURE-MANIFEST.md 1-based (task1 #6/#12/#16/#17; task2 #6/#30/#32/#34/#36/#38/#40/#41; task3 #6-#15)"

patterns-established:
  - "Calculator trilogy thesis: v1 F# (FsLex scaffolded) → v1.2 Rust (unaided) → v1.3 Scala (unaided)"
  - "Host re-run date = agent run date = 2026-06-01 (no invented second date)"

# Metrics
duration: ~5min
completed: 2026-06-01
---

# Phase 11 Plan 01: 7부 Scala Calculator Chapter Summary

**35B Scala 3 재귀 하강 계산기 실행을 5개 챕터로 기록 + SUMMARY.md 7부 섹션 배선 — 70줄 Calc.scala 바이트 동일 인용, 컴파일 오류 1회 verbatim + agent sed 자가 수정 (#6–#9), 정규 테스트 14/20/5 (#10–#15), ADT-vs-FsLex 대조 솔직 기술**

## Performance

- **Duration:** ~5분 26초 (2026-06-01T06:32:25Z – 2026-06-01T06:37:51Z)
- **Started:** 2026-06-01T06:32:25Z
- **Completed:** 2026-06-01T06:37:51Z
- **Tasks:** 4 (Task 1: evidence absorption + cross-check; Task 2: intro/planning/writing; Task 3: build-test/final/SUMMARY; Task 4: honesty audit)
- **Files created:** 5 (ch07-scala-calc/*.md) + 1 modified (SUMMARY.md)

## Accomplishments

- 5개 7부 챕터 파일 작성 — `src/ch07-scala-calc/intro.md`, `planning.md`, `writing.md`, `build-test.md`, `final.md` (4부/6부 구조 미러)
- `src/SUMMARY.md`에 7부 섹션 배선 — 6부 블록 다음, `---`/부록 앞, 5개 항목
- 모든 인용이 `captured-scala/` 증거에서 직접 추출: 70줄 Calc.scala 바이트 동일, 컴파일 오류 verbatim, 매니페스트 1-based 이벤트 번호, 실측 타이밍 표
- 정직성 가드레일 전부 통과: sealed-trait ADT 주장 없음, ~14–32s/call 측정값으로 인용 안 함, 이모지 없음

## Task Commits

1. **Task 2: intro, planning, writing 작성** — `4a4569e` (feat)
2. **Task 3: build-test, final, SUMMARY 배선** — `cde9170` (feat)

**Plan metadata:** (다음 커밋 — docs)

## Files Created/Modified

- `src/ch07-scala-calc/intro.md` — 계산기 삼부작 소개, 실행 메타데이터, 스캐폴딩 공개, 에이전트 루프 개념↔행동
- `src/ch07-scala-calc/planning.md` — 3태스크 분해 표, task1 스캐폴드 사이클 callout, Explore→Implement→Verify 매핑
- `src/ch07-scala-calc/writing.md` — 70줄 Calc.scala 바이트 동일, Scala 3 관용어 해설(no sealed-trait ADT), tool calling callout
- `src/ch07-scala-calc/build-test.md` — 컴파일 오류 verbatim (#6/#7), agent sed 수정 (#8/#9), 3개 정규 테스트 (#10–#15), 호스트 재실행, 액션-관찰 사이클 callout
- `src/ch07-scala-calc/final.md` — 70줄 Calc.scala verbatim, 매니페스트 타이밍 표, 솔직한 표기 주의, ADT-vs-FsLex 대조, 계산기 삼부작 표, Sources 절
- `src/SUMMARY.md` — 7부 섹션 추가 (6부 다음, `---` 앞, 5항목)

## Decisions Made

- code quoted byte-identical from `final-source/Calc.scala` (post-fix state, `var pos = 0` on line 10); `private var pos = 0` text appears only in the error narrative (build-test.md) and the prose note in writing.md
- No sealed-trait ADT claim anywhere — manifest `adt-style: None` honored; contrast framed as "hand-rolled recursive descent (unaided)" vs "FsLex/FsYacc DSL (scaffolded)"
- `~14–32s/call` appears only inside the `> **솔직한 표기 주의**` callout in final.md, explicitly labeled as a v1 pre-run prediction, mirroring the 6부 pattern
- All event-number citations use manifest 1-based positions (task1: #6/#7/#12/#16/#17; task2: #6/#30/#32/#34/#36/#38/#40/#41; task3: #6/#7/#8/#9/#10/#11/#12/#13/#14/#15)
- Run date 2026-06-01 used throughout for both agent run and host re-run (no invented second date)

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- 7부 챕터 5개 파일 완성, SUMMARY.md 배선 완료
- GitHub Pages 배포 (`main` push) 실행 가능 — `.github/workflows/deploy.yml` 미변경
- Phase 11 추가 계획(11-02 등)이 있다면 즉시 시작 가능
- 열린 tech debt (TD-2/TD-3/TD-4/TD-5)는 이 계획에서 건드리지 않음 — 그대로 유지

---
*Phase: 11-7부-chapter-publish*
*Completed: 2026-06-01*
