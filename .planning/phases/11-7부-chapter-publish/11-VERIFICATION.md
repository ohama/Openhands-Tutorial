---
phase: 11-7부-chapter-publish
verified: 2026-06-01T07:00:00Z
status: passed
score: 4/4 success criteria verified
gaps: []
---

# Phase 11: 7부 Chapter Publish Verification Report

**Phase Goal:** A new 7부 "다른 워킹 예제: Scala 계산기" chapter group, written verbatim from Phase 10 captured evidence, wired into src/SUMMARY.md, mdbook build clean (no new warnings), live on GitHub Pages — strict honesty; deploy.yml unchanged.

**Verified:** 2026-06-01T07:00:00Z  
**Status:** passed  
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | src/ch07-scala-calc/ has exactly 5 .md files, SUMMARY.md has correct 7부 placement with 5 entries | VERIFIED | 5 files confirmed; SUMMARY.md lines 45–51: 7부 block after `[완성된 Rust 서버](ch06-rust-server/final.md)` (line 43), before `---` (line 53) |
| 2 | Every code quote, event number, error message traces verbatim to captured-scala/ | VERIFIED | See spot-checks below — all 6 sub-criteria pass |
| 3 | mdbook build completes with zero errors and zero NEW warnings | VERIFIED | `mdbook build` output: one WARN (appendix-c `<char>`) only — the pre-existing warning; no errors |
| 4 | Live site returns 200 for all ch07 pages; root 200; 7부 in sidebar; deploy.yml unchanged | VERIFIED | All 5 ch07 pages: HTTP/2 200; root: HTTP/2 200; 7부 in toc-5eb11a0d.js sidebar; `git diff origin/main -- .github/workflows/deploy.yml` is empty |

**Score:** 4/4 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/ch07-scala-calc/intro.md` | Intro chapter file | VERIFIED | Exists, 78 lines, substantive |
| `src/ch07-scala-calc/planning.md` | Planning chapter file | VERIFIED | Exists, 75 lines, substantive |
| `src/ch07-scala-calc/writing.md` | Writing chapter file | VERIFIED | Exists, 168 lines, substantive |
| `src/ch07-scala-calc/build-test.md` | Build-test chapter file | VERIFIED | Exists, 164 lines, substantive |
| `src/ch07-scala-calc/final.md` | Final chapter file | VERIFIED | Exists, 184 lines, substantive |
| `src/SUMMARY.md` 7부 block | 5 entries after 6부/before --- | VERIFIED | Lines 45–51, correct placement |

---

## Criterion 1: Structure and Callout Style

**5 files present:** intro.md, planning.md, writing.md, build-test.md, final.md — confirmed via `ls`.

**SUMMARY.md placement:** Line 43: `[완성된 Rust 서버](ch06-rust-server/final.md)`. Line 45: `# 7부: 다른 워킹 예제 - Scala 계산기`. Lines 47–51: 5 entries. Line 53: `---`. Line 55+: 부록 block. Placement is correct (after 6부, before `---`/부록).

**Parallel structure:** 7부 uses identical 5-file layout as 4부 (ch04-calculator) and 6부 (ch06-rust-server).

**Callout labels — no pictograph emoji:** Python emoji regex scan across all 5 ch07 files found zero matches. Callout headers use plain `**사용자 프롬프트**`, `**내부 프로세스**`, `**결과**` — no pictograph prefix.

**Concept-action callouts:** 4 confirmed:
- `intro.md` line 64: `**개념 ↔ 행동: 에이전트 루프와 자가 수정**`
- `planning.md` line 64: `**개념 ↔ 행동: 탐색(Explore) → 구현(Implement) → 검증(Verify)**`
- `writing.md` line 165: `**개념 ↔ 행동: 도구 사용(tool calling)과 액션-관찰 사이클**`
- `build-test.md` line 161: `**개념 ↔ 행동: 액션-관찰 사이클(action-observation cycle)과 자가 수정**`

**ADT-vs-FsLex contrast note:** Present in `writing.md` (lines 137–139) and `final.md` (lines 135–155). The contrast is framed correctly as "손 작성 재귀 하강(비보조) vs 파서 생성기 DSL(스캐폴드)" — not "ADT vs FsLex".

**No false sealed-trait ADT claim:** Both `writing.md` and `final.md` explicitly state `adt-style: None` — the agent did NOT use a `sealed trait Expr` ADT. The chapter correctly notes the absence.

**Criterion 1: PASS**

---

## Criterion 2: Verbatim Fidelity to captured-scala/

### (a) Calc.scala byte-identity

Code blocks in `writing.md` and `final.md` compared byte-for-byte with `final-source/Calc.scala`:

- `writing.md` scala block: **BYTE-IDENTICAL** to `final-source/Calc.scala` (2106 chars)
- `final.md` scala block: **BYTE-IDENTICAL** to `final-source/Calc.scala` (2106 chars)
- Calc.scala total lines: **70** (confirmed)
- Line 10 of Calc.scala: `  var pos = 0` — NOT `private`
- Chapter explicitly notes: "line 10: `var pos = 0`" in both writing.md and final.md

### (b) Compile error text

`build-test.md` verbatim block (events #7) compared to CAPTURE-MANIFEST.md Error-and-Fix Record:

**Result: byte-identical.** The full 11-line error block including `[error] variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level definitions in package <empty>.` and the `^^^^^^^^^^` underlines is reproduced exactly.

### (c) Three results 14/20/5 present

Confirmed in multiple files:
- `intro.md`: output table showing `14`, `20`, `5`
- `build-test.md`: event #11 verbatim `14`, event #13 `20`, event #15 `5`
- `final.md`: results table with `14 (exit 0)`, `20 (exit 0)`, `5 (exit 0, 왼쪽 결합)`

### (d) No Cargo/Rust facts bleeding in

`grep -ni "cargo\|rustc\|rust\b\|Actix\|tokio"` across all 5 ch07 files — zero hits that are not correctly contextualized cross-references (e.g., "v1.2 (6부) Rust HTTP 서버" in comparison tables). No Rust-specific technical claims (Cargo, rustc, Actix) appear in ch07 content.

### (e) No false sealed-trait ADT claim

`writing.md` line 137: `**\`sealed trait Expr\` ADT 없음**` — explicitly states the agent did NOT use one. `final.md` line 108 (results table): `sealed trait Expr ADT | 없음 (직접 Int 반환 재귀 하강)`. No false claim of an ADT existing.

### (f) `~14–32s/call` framing

`final.md` line 131: `v1 35B에 대해 한때 인용되던 "~14–32초/call" 수치는 2026-05-28 pre-run 예측값(v1 ROADMAP의 사전 예측)이며 실측이 아닙니다.` — The figure is cited only to correct/contextualize it. It is labeled explicitly as a v1 prediction, not a measurement.

**Criterion 2: PASS (all 6 sub-criteria)**

---

## Criterion 3: mdbook Build

**Command run:** `mdbook build` in `/Users/ohama/projs/OpenHandsTests/`

**Output:**
```
INFO Book building has started
INFO Running the html backend
WARN unclosed HTML tag `<char>` found in `appendix-c-comparison.md` while exiting TableCell
HTML tags must be closed before exiting a markdown element.
INFO HTML book written to `/Users/ohama/projs/OpenHandsTests/book`
```

**Zero errors.** One warning: the pre-existing `<char>` warning in `appendix-c-comparison.md`. No new warnings. All 5 ch07 HTML files confirmed generated in `book/ch07-scala-calc/`.

**1부–6부 + 부록 A/B/C regression:** Live site check confirmed HTTP/2 200 for ch01, ch04, ch06-rust-server/final.html, appendix-a, appendix-b, appendix-c.

**Criterion 3: PASS**

---

## Criterion 4: Live Site

**All 5 ch07 pages (curl -sI):**

| Page | HTTP Status |
|------|-------------|
| ch07-scala-calc/intro.html | HTTP/2 200 |
| ch07-scala-calc/planning.html | HTTP/2 200 |
| ch07-scala-calc/writing.html | HTTP/2 200 |
| ch07-scala-calc/build-test.html | HTTP/2 200 |
| ch07-scala-calc/final.html | HTTP/2 200 |

**Root:** `https://ohama.github.io/Openhands-Tutorial/` → HTTP/2 200

**7부 in live sidebar:** Confirmed in `toc-5eb11a0d.js` (the built TOC JS file, deployed to live site). Entry: `<li class="part-title">7부: 다른 워킹 예제 - Scala 계산기</li>` followed by all 5 ch07 entries (entries numbered 23–27 in the sidebar).

**deploy.yml:** `git diff origin/main -- .github/workflows/deploy.yml` → empty output. Unchanged.

**Criterion 4: PASS**

---

## Event-Numbering Consistency

**Risk:** The 10-02-RUN-NOTES.md uses 0-based enumerate() indexing (a scratchpad convention). CAPTURE-MANIFEST.md uses 1-based JSONL positions. Phase 11 chapter must cite MANIFEST numbers.

**10-02-RUN-NOTES.md line 7** explicitly documents this: `"the per-task event indices in the sections below use 0-based enumerate() positions (a scratchpad convention). The committed CAPTURE-MANIFEST.md — authoritative for all Phase 11 citations — uses 1-based JSONL positions (i.e. +1 vs the lists below)."`

**Chapter citations verified** (task3, build-test.md):
- Error at `#7` (MANIFEST 1-based) = RUN-NOTES `#6` (0-based) — chapter cites `#7` ✓
- Sed fix at `#8` (MANIFEST) — chapter cites `#8` ✓
- `2+3*4→14` at ObservationEvent `#11` (MANIFEST) — chapter cites `#11` ✓
- `(2+3)*4→20` at `#13` (MANIFEST) — chapter cites `#13` ✓
- `10-3-2→5` at `#15` (MANIFEST) — chapter cites `#15` ✓

**Conclusion:** Chapter consistently uses MANIFEST 1-based numbering throughout. No mixed convention, no RUN-NOTES 0-based scratchpad numbers cited. Event numbering is internally consistent and traces to the committed CAPTURE-MANIFEST.md.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | — |

No TODOs, FIXMEs, placeholder text, empty handlers, or stub patterns found in any ch07 file.

---

## Human Verification Required

None required. All automated checks passed. The honest outcome (unaided Scala 3 + one self-corrected compile error + 14/20/5) is accurately and completely documented in the chapter.

---

## Summary

Phase 11 goal is **achieved**. The 7부 chapter group exists with 5 substantive files byte-faithful to the captured evidence, is correctly wired into SUMMARY.md at the right position, builds cleanly with only the pre-existing appendix-c warning, and is live on GitHub Pages with all 5 pages returning 200. The honest narrative (unaided calc, one private-access compile error, self-corrected via sed, three canonical tests all pass, no ADT, no Cargo bleed, ~14–32s/call labeled as prediction not measurement) is what the chapter actually says.

---

_Verified: 2026-06-01T07:00:00Z_  
_Verifier: Claude (gsd-verifier)_
