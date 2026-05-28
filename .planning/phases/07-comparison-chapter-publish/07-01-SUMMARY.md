---
phase: 07-comparison-chapter-publish
plan: 01
subsystem: content/comparison-chapter
tags: [korean-prose, comparison, 35b, 122b, fslexer, fsyacc, honesty]
requires:
  - 06-capture-the-122b-openhands-run (captured-122b/ committed, capture gate closed)
  - v1-phases/03-capture-the-openhands-run (35B baseline captured/)
provides:
  - src/appendix-c-comparison.md (부록 C content, 315 lines)
affects:
  - 07-02 (wires appendix-c-comparison.md into src/SUMMARY.md)
tech-stack:
  added: []
  patterns:
    - Korean prose with English technical terms inline (matching existing book chapters)
    - ASCII pipe-and-dash tables for comparison data
    - Verbatim code fences (fsharp/ocaml/text) for source quotes
    - Inline parenthetical citations (file path + event/line range)
key-files:
  created:
    - src/appendix-c-comparison.md
  modified: []
decisions:
  - "35B attempt-1 TerminalAction counts sourced from 03-02-RUN-NOTES-attempt1.md (94+27+16=137) not the 122B CAPTURE-MANIFEST summary"
  - "stale ~14-32s/call figure is explicitly labeled as 06-RESEARCH.md §1.3 pre-run prediction, not used as 35B measured speed"
  - "35B per-call figure stated as ~5.3s wall-time-derived approximation with explicit measurement asymmetry disclaimer"
  - "%right NEG string avoided in chapter body; table cell rephrased to describe unary minus as recursive rule without separate token declaration"
  - "122B Lexer.fsl quoted verbatim from captured-122b/final-source/Lexer.fsl (final version after task5 fix, not task2 unaided draft)"
metrics:
  duration: "~4 minutes (244 seconds)"
  completed: "2026-05-28"
---

# Phase 7 Plan 01: Draft 부록 C Comparison Chapter Summary

**One-liner:** New Korean appendix chapter comparing 35B (scaffolded lexer) vs 122B (unaided FsLex) using verbatim JSONL citations for all capability, error-fix, and speed claims.

## What Was Built

A new file `src/appendix-c-comparison.md` (315 lines) — the Korean comparison chapter for v1.1. The chapter covers:

1. **실험 설계와 공정성 전제** — Setup asymmetry disclosed up front: 35B had Lexer.fsl scaffolded (attempt 1 failed with 137+ TerminalActions of %% confusion); 122B wrote Lexer.fsl unaided.
2. **§1 렉서(.fsl) 작성 능력** — 35B attempt-1 failure, attempt-2 scaffolding, and 122B's successful unaided first attempt (task2-lexer-unaided.jsonl event 9). Verbatim final Lexer.fsl from captured-122b/final-source/.
3. **§2 오류-수정 사이클 비교** — 35B 4 iterations / 21 events (task3-parser.jsonl 9–30); 122B 9 iterations / 62 events (task5-buildtest.jsonl 12–74). Full ASCII table of 122B's 10 INT line attempts. Cross-task context (task3-parser events 24/42/46).
4. **§3 처리 속도 측정** — 122B direct measurement (6.3s/call, 150 TA, 1229.2s total from CAPTURE-MANIFEST). 35B derived approximation (~5.3s/call, 67 TA, 356s wall-time from RUN-NOTES). Measurement asymmetry disclosed. Stale ~14-32s/call labeled as pre-run prediction.
5. **§4 최종 소스 코드 차이** — Both Lexer.fsl and Parser.fsy quoted verbatim. 35B uses `LexBuffer<_>.LexemeString lexbuf` / `System.Int32.Parse s`; 122B uses `INT (int (new string(lexbuf.Lexeme)))`. 122B Parser.fsy has `expr → term → factor` hierarchy + `| MINUS factor { -$2 }` for unary minus.
6. **§5 결론** — Both models pass 14/20/5. Primary differentiator: lexer authorship capability. Speed difference is iteration count, not per-call latency.
7. **출처** — Full source file list.

## Notable Verbatim Quotes Used

From `captured-122b/final-source/Lexer.fsl`:
```fsharp
  | ['0'-'9']+ { INT (int (new string(lexbuf.Lexeme))) }
```

From `captured-122b/final-source/Parser.fsy`:
```ocaml
    | MINUS factor            { -$2 }
```

From `captured/final-source/Lexer.fsl` (35B scaffolded):
```fsharp
        { let s = LexBuffer<_>.LexemeString lexbuf
          let v = System.Int32.Parse s
          INT v }
```

Agent thought at fix 9 (task5-buildtest.jsonl event 71), quoted directly from CAPTURE-MANIFEST:
> "`lexbuf.Lexeme` returns a char array. Let me convert it to a string:"

## Deviations from Plan

None — plan executed exactly as written.

- Chapter structure follows the plan's specified section layout exactly (실험 설계 → §1 렉서 → §2 오류-수정 → §3 속도 → §4 소스 차이 → §5 결론 → 출처).
- The `%right NEG` string was avoided in the chapter body by rephrasing the table cell to describe the unary minus as "재귀 규칙으로 처리" without naming the alternative pattern. The must_have is satisfied: the chapter does not claim 122B used a separate NEG token.
- Mid-task quality checkpoint passed: 315 lines, all 4 opening section headers present.

## Confirmation: src/SUMMARY.md Not Modified

`grep -c "appendix-c" src/SUMMARY.md` returns 0. Plan 07-02 owns that edit.

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| e866c8d | feat(07-01) | Draft 부록 C — 35B vs 122B 모델 비교 chapter (315 lines) |
