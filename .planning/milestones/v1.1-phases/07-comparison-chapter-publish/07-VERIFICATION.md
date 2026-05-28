---
phase: 07-comparison-chapter-publish
verified: 2026-05-28T00:00:00Z
status: passed
score: 4/4 must-haves verified
re_verification: false
---

# Phase 7: Comparison Chapter + Publish — Verification Report

**Phase Goal:** A 35B-vs-122B comparison chapter, backed by verbatim evidence from both captured runs, is added to the book; `mdbook build` is clean; the updated book is live on GitHub Pages.

**Verified:** 2026-05-28
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Comparison chapter exists as new `src/` file, wired into `SUMMARY.md`, `mdbook build` exits 0 | VERIFIED | `src/appendix-c-comparison.md` exists (316 lines); `SUMMARY.md` line 41 links it; `mdbook build` exits 0 with one WARN (not error) |
| 2 | Chapter addresses lexer-writing ability, error-fix cycles, and speed | VERIFIED | §1 covers FsLex writing; §2 covers error-and-fix comparison; §3 covers speed with explicit methodological disclaimer |
| 3 | Every claim traces to verbatim lines in captured JSONL logs or RUN-NOTES | VERIFIED | All numeric claims carry inline `(출처: …)` citations; cross-checked against 5 source files; no fabricated figures found |
| 4 | Live GitHub Pages returns HTTP 200 for root and comparison chapter | VERIFIED | `curl -I https://ohama.github.io/Openhands-Tutorial/` → 200; `…/appendix-c-comparison.html` → 200 |

**Score:** 4/4 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/appendix-c-comparison.md` | New comparison chapter | VERIFIED | 316 lines; substantive content in 5 sections |
| `src/SUMMARY.md` line 41 | Chapter wired into book nav | VERIFIED | `[부록 C: 모델 비교 — 35B vs 122B](appendix-c-comparison.md)` present |
| `book/appendix-c-comparison.html` | Built HTML output | VERIFIED | File exists after `mdbook build` |
| GitHub Pages root | HTTP 200 | VERIFIED | curl returned 200 |
| GitHub Pages comparison URL | HTTP 200 | VERIFIED | curl returned 200 |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/appendix-c-comparison.md` | `src/SUMMARY.md` | link entry on line 41 | WIRED | Exact entry present |
| Chapter claims | 122B final-source/Lexer.fsl | verbatim code block | WIRED | Chapter's Lexer.fsl block matches file exactly: `new string(lexbuf.Lexeme)` on line 10 |
| Chapter claims | 35B final-source/Lexer.fsl | verbatim code block | WIRED | Chapter's INT block matches file exactly: `LexBuffer<_>.LexemeString lexbuf` |
| Chapter claims | 122B final-source/Parser.fsy | verbatim code block | WIRED | Chapter's Parser.fsy block matches file exactly: `factor: \| MINUS factor { -$2 }` present |
| Chapter claims | 35B final-source/Parser.fsy | verbatim code block | WIRED | Chapter's 35B Parser.fsy block matches: `%{ %}` header, `expr PLUS expr` flat grammar |
| 122B timing table | captured-122b/CAPTURE-MANIFEST.md §Timing (CMP-01) | numeric match | WIRED | All 5 task rows (timestamps, seconds, TA counts, avg) match CAPTURE-MANIFEST lines 132–137 exactly |
| 35B timing table | 03-02-RUN-NOTES.md §Per-Task Outcome Table | numeric match | WIRED | task1 186s/27TA, task2 16s/2TA, task3 77s/15TA, task4 45s/14TA, task5 32s/9TA — all match RUN-NOTES lines 27–31 |
| Attempt 1 TA counts | 03-02-RUN-NOTES-attempt1.md table | numeric match | WIRED | task4-adjusted 94TA, task5 27TA, task6-lexer-fix 16TA — confirmed lines 152–154 |
| Build success string | 03-02-RUN-NOTES.md line 74 | verbatim quote | WIRED | `calc net10.0 성공 (0.7초)` present in both RUN-NOTES and chapter |

---

## Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| CMP-01 (speed comparison with measured data) | SATISFIED | 122B timing from JSONL timestamps (direct); 35B from wall-time/TA (derived, disclosed as such); methodological difference explicitly stated |
| CMP-02 (capability claims backed by verbatim evidence) | SATISFIED | Lexer.fsl and Parser.fsy verbatim blocks present; event numbers cited; CAPTURE-MANIFEST sections cited |
| PUB-01 (mdbook build clean) | SATISFIED | Exit code 0; one WARN about `<char>` tag in table cell (not an error, does not affect output) |
| PUB-02 (GitHub Pages live, chapter reachable) | SATISFIED | Both URLs return HTTP 200 |

---

## Anti-Patterns Found

| File | Pattern | Severity | Assessment |
|------|---------|----------|------------|
| `src/appendix-c-comparison.md` line 75 | `LexBuffer<char>` inside backtick code span inside table cell triggers mdbook WARN "unclosed HTML tag `<char>`" | Info | Not a functional defect; mdbook builds successfully (exit 0) and HTML renders correctly. The `<char>` is inside a backtick code span which is a valid, honest verbatim quote from the source material. Suppressing it would require escaping the verbatim quote, which would harm accuracy. |

No stub patterns. No TODO/FIXME. No placeholder text. No fabricated numbers detected.

---

## Honesty / Core Value Checks

### Asymmetry Disclosure

The chapter's opening section "실험 설계와 공정성 전제" (§ Experimental Design and Fairness Premise) explicitly states:

> "따라서 이 비교는 동일 조건의 head-to-head 비교가 아니다. 35B는 렉서가 스캐폴딩된 환경에서, 122B는 렉서를 무지원으로 작성하는 환경에서 평가되었다."

Translation: "This comparison is not a head-to-head comparison under identical conditions. 35B was evaluated with the lexer scaffolded; 122B was evaluated writing the lexer unaided."

VERIFIED: Asymmetry is prominently disclosed at the start.

### `~14–32s` Disclaimer

Chapter line 161:

> "122B CAPTURE-MANIFEST.md의 vs-35B-speed 코멘트는 35B에 대해 '~14–32s/call' 수치를 인용하지만, 이 수치는 06-RESEARCH.md §1.3의 사전 예측(pre-run prediction)이지 attempt 2의 실제 측정값이 아니다."

VERIFIED: The `~14–32s` figure is correctly identified as a pre-run prediction, not a measured value. The chapter uses actual attempt 2 data (derived ~5.3s/call) instead.

### No Bare `%right NEG` Claim

Searched `appendix-c-comparison.md` for `%right NEG` and `NEG` — zero results. The chapter correctly describes 122B's unary minus as `| MINUS factor { -$2 }` (recursive rule, no separate `NEG` token), which matches the actual `Parser.fsy`.

### No Fabricated Figures

All numeric claims cross-checked:
- 122B TA counts (150 total, per-task breakdown): match CAPTURE-MANIFEST
- 122B timing (1229.2s total, per-task): match CAPTURE-MANIFEST
- 35B TA counts (67 total): match RUN-NOTES
- 35B task timings: match RUN-NOTES Per-Task Outcome Table
- Attempt 1 TA counts (94+27+16=137): match RUN-NOTES-attempt1 table
- Build success timing "0.7초": present verbatim in RUN-NOTES line 74
- Error-fix iteration counts (35B: 4 iterations/events 9–30; 122B: 9 iterations/events 12–74): match cited JSONL event ranges in CAPTURE-MANIFESTs

---

## mdbook Build Output

```
INFO Book building has started
INFO Running the html backend
WARN unclosed HTML tag `<char>` found in `appendix-c-comparison.md` while exiting TableCell
HTML tags must be closed before exiting a markdown element.
INFO HTML book written to `/Users/ohama/projs/OpenHandsTests/book`
EXIT:0
```

Build exits 0. The WARN is cosmetic: `<char>` appears inside a backtick code span (`LexBuffer<char>.FromString`) within a table cell — a legitimate verbatim code quote. The HTML output is correct.

---

## Live GitHub Pages

| URL | HTTP Status |
|-----|-------------|
| `https://ohama.github.io/Openhands-Tutorial/` | 200 |
| `https://ohama.github.io/Openhands-Tutorial/appendix-c-comparison.html` | 200 |

---

_Verified: 2026-05-28_
_Verifier: Claude (gsd-verifier / claude-sonnet-4-6)_
