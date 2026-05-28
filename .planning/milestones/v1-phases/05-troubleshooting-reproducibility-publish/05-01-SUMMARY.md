---
phase: 05-troubleshooting-reproducibility-publish
plan: 01
subsystem: content-writing
tags: [troubleshooting, korean-prose, appendix, wrap-up, FsLex, FsYacc, agent-behavior]

dependency-graph:
  requires:
    - "03-capture-the-openhands-run/03-02-RUN-NOTES-attempt1.md (verbatim error strings)"
    - "03-capture-the-openhands-run/captured/CAPTURE-MANIFEST.md (artifact evidence)"
    - "05-RESEARCH.md §1 real failure modes + §1.2 reconciliation"
    - "STATE.md accumulated decisions (REAL-01 through REAL-06)"
  provides:
    - "src/appendix-b-troubleshooting.md — 부록 B: 6 real failure modes + honest reconciliation"
    - "src/ch05-wrap-up/review.md — 개념 되짚기 (4 agentic concepts in the real run)"
    - "src/ch05-wrap-up/next-steps.md — 다음 단계 (where to go from here)"
  affects:
    - "05-03-PLAN.md — must wire src/appendix-b-troubleshooting.md and src/ch05-wrap-up/*.md into SUMMARY.md"

tech-stack:
  added: []
  patterns:
    - "Verbatim error string documentation from captured JSONL evidence"
    - "Honest reconciliation section (anticipated-but-didn't-occur)"

file-tracking:
  created:
    - src/appendix-b-troubleshooting.md
    - src/ch05-wrap-up/review.md
    - src/ch05-wrap-up/next-steps.md
  modified: []

decisions:
  - "부록 B uses 4-section structure: 환경 문제 / 에이전트 동작 문제 / 빌드 오류 / 예상했지만 발생하지 않은 문제"
  - "§4 reconciliation explicitly names host.docker.internal, 240s estimate, .NET sandbox, %left as anticipated-but-did-not-apply"
  - "240s framed ONLY as 'unmeasured estimate that did not hold' — never as a real measured value"
  - "review.md cites task3-parser.jsonl event numbers (10, 16, 20, 26, 30) to ground concepts in evidence"
  - "next-steps.md points to 부록 A in prose only (no Markdown link — appendix-a wired only in 05-03)"
  - "No Markdown links to unwired draft entries; all forward references are prose"

metrics:
  duration: "~10 min"
  completed: "2026-05-28"
---

# Phase 5 Plan 01: Troubleshooting Appendix + Wrap-up Chapters Summary

**One-liner:** 6 실제 장애 모드(DOCKER_HOST, --override-with-envs, FsLex OOD, file_editor security_risk, FS0010 line-directive, FsYacc %start/%type) 진단+수정 + 4가지가 발생하지 않은 정직한 화해 절 + 5부 wrap-up 2개 챕터.

## What Was Built

Three new content files in Korean prose, grounded in verbatim evidence from the captured JSONL logs:

**src/appendix-b-troubleshooting.md** (274 lines):
- §1 환경 문제: REAL-01 (Colima/DOCKER_HOST), REAL-02 (--override-with-envs + openai/ prefix), REAL-05 (.NET 10 + FixLineDirectives XML target verbatim)
- §2 에이전트 동작 문제: REAL-03 (FsLex OOD — `Lexer.fsl(8): error : Unexpected character '%'`), REAL-04 (file_editor security_risk — verbatim error + IMPORTANT instruction block)
- §3 빌드 오류: REAL-06 (FSY000, Parser.fsy parse error x2, FS0039 LexBuffer.FromText — 4-row table + fix)
- §4 예상했지만 발생하지 않은 문제: host.docker.internal, timeout/240s (framed as unmeasured estimate), .NET sandbox, %left precedence

**src/ch05-wrap-up/review.md** (67 lines):
- 4 agentic concepts (tool calling, agent loop, plan→write→test→run, memory/context) revisited through the real run evidence
- ASCII event sequence diagram for the task3 error-and-fix cycle
- Grounded in specific JSONL event numbers (events 10, 16, 20, 26, 30)

**src/ch05-wrap-up/next-steps.md** (55 lines):
- Larger/cloud models comparison suggestion
- Other language experiments (Python, TypeScript, Go)
- OpenHands experiment extension ideas
- Prose-only forward reference to 부록 A 재현 가이드 (no Markdown link)

## Honesty Constraints Met

- "240" appears only once in appendix-b, framed as "측정되지 않은 최악의 경우 추정치" (unmeasured worst-case estimate)
- §4 explicitly labels all 4 anticipated-but-didn't-occur items with "DID NOT APPLY" / "발생하지 않음"
- All verbatim error strings sourced from 05-RESEARCH.md §1.1 and 03-02-RUN-NOTES-attempt1.md
- No fabricated failure presented as if it happened
- No Markdown links to unwired SUMMARY.md entries

## Verification Results

- appendix-b-troubleshooting.md: 274 lines (requirement: ≥90) ✓
- review.md: 67 lines (requirement: ≥20) ✓
- next-steps.md: 55 lines (requirement: ≥20) ✓
- `grep -c "security_risk"` → 5 (requirement: ≥1) ✓
- `grep -c "DID NOT\|발생하지 않은\|적용되지"` → 6 (requirement: ≥1) ✓
- `mdbook build` → exits 0, "HTML book written" ✓

## Deviations from Plan

None — plan executed exactly as written. Files are unwired (wiring happens in 05-03); mdbook build remains green.

## Next Phase Readiness

05-02 (appendix-a-repro.md) runs in parallel and is already committed (2a0506c).
05-03 must wire all four 5부/appendix entries into SUMMARY.md:
- `src/ch05-wrap-up/review.md`
- `src/ch05-wrap-up/next-steps.md`
- `src/appendix-a-repro.md` (from 05-02)
- `src/appendix-b-troubleshooting.md` (this plan)
