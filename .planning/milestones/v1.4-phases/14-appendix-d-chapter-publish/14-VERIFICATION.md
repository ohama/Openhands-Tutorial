---
phase: 14-appendix-d-chapter-publish
verified: 2026-06-04T00:00:00Z
status: passed
score: 4/4 success criteria verified
---

# Phase 14: 부록 D Chapter + Publish — Verification Report

**Phase Goal:** A new 부록 D "계획 방식 비교: Claude 계획 vs OpenHands 자체 계획" chapter is written verbatim from the committed captured-planning/ data, wired into the book after 부록 C, and deployed live to GitHub Pages — with all existing 1부–7부 and 부록 A/B/C chapters not regressed.

**Verified:** 2026-06-04
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Criterion 1: Chapter Content + Traceability

**Requirement:** `src/appendix-d-planning-comparison.md` exists with cross-example P1/P2 comparison table (F#/Rust/Scala × Arm A/B), per-arm planning-artifact excerpts, qualitative observations, honest interpretation. Numbers traceable to committed comparison.json artifacts.

### Artifact existence

`/Users/ohama/projs/OpenHandsTests/src/appendix-d-planning-comparison.md` — EXISTS (287 lines, substantive).

Sections present:
- Section 1: Experimental design table — PRESENT
- Section 2: Per-example planning artifact excerpts (F#, Rust, Scala) — PRESENT (per-arm summaries with source citations)
- Section 2.4: Qualitative plan structure summary table — PRESENT
- Section 3: P1/P2 metrics comparison tables (F#, Rust, Scala) — PRESENT
- Section 4: Canonical test results with PARTIAL-PASS definition — PRESENT
- Section 5: Qualitative interpretation with per-example analysis — PRESENT
- Section 6: Full sources list — PRESENT

### Number spot-check (4 values, chapter vs. committed comparison.json)

| Value | Chapter text | comparison.json | Match |
|-------|-------------|-----------------|-------|
| F# Arm A TerminalActions | `80 (77–210)` | `"median": 80, "min": 77, "max": 210` | MATCH |
| Scala Arm B wall_clock_seconds | `936.16 (868.45–1442.28)` | `"median": 936.16, "min": 868.45, "max": 1442.28` | MATCH |
| Rust Arm A total_events | `26 (26–30)` | `"median": 26, "min": 26, "max": 30` | MATCH |
| Scala Arm A error_fix_cycle_count | `6 (3–10)` | `"median": 6, "min": 3, "max": 10` | MATCH |

All 4 spot-checked values trace exactly to committed comparison.json files. No discrepancy found.

### Event number traceability (chapter vs. CAPTURE-MANIFEST)

| Chapter citation | CAPTURE-MANIFEST | Match |
|-----------------|-----------------|-------|
| F# Arm A run-1: events #200, #202, #204 (14/20/5) | "PASS (14/20/5 at events #200, #202, #204)" | MATCH |
| Scala Arm A rep-1: events #39, #41, #43 | "PASS (14/20/5 at events #39, #41, #43)" | MATCH |
| Rust rep-1 Arm A event #25, Arm B event #31 | "PASS (event #25, exit=0)" / "PASS (event #31, exit=0)" | MATCH |
| Scala Arm B rep-3 event #45 (PARTIAL-PASS) | "PARTIAL-PASS (tests 2+3 at event #45; test 1 not re-run)" | MATCH |

Event numbers are 1-based throughout, consistent with CAPTURE-MANIFEST §"EVENT-NUMBERING CONVENTION".

**Criterion 1: VERIFIED**

---

## Criterion 2: Opening Paragraph + Honesty Controls

### Research question framing

Chapter line 3: "이 연구의 핵심 질문은 **"전문가가 작성한 계획이 35B의 실행에 도움이 되는가?"** 이다 — Claude가 35B보다 계획을 더 잘 짠다는 주장이 아니다."

Research question correctly stated. Explicit disclaimer that this is NOT "Claude plans better" — PRESENT.

### No "Claude plans better" claim

`grep -nE "Claude가 35B보다|Claude plans better|더 잘 짠|우수" src/appendix-d-planning-comparison.md` — 0 matches. CLEAN.

### 14–32 forbidden measurement claim

`grep -nE "14[–-]32" src/appendix-d-planning-comparison.md` — 0 matches. CLEAN. The pre-run prediction is not cited as a measurement in the chapter.

### (단일 실행) hedge usage

`(단일 실행)` appears at:
- Line 225 (prose): "Arm A run-1 PASS (단일 실행): 이벤트 #200..." — single-run F# PASS correctly hedged
- Line 251 (interpretation): "Arm A run-1(단일 실행)의 PASS는..." — correctly hedged in narrative

The hedge is applied ONLY to the single-rep F# Arm A PASS observation, NOT to n=3 table cells. Table cells use `중앙값 (최솟값–최댓값)` format without `(단일 실행)`. Correct.

### Mixed/inconclusive results reported

| Result | Present in chapter |
|--------|-------------------|
| F# Arm A 1/3 / Arm B 0/3 | Section 4, line 213 |
| Scala Arm A 3/3 / Arm B 2/3 + PARTIAL-PASS | Section 4, line 214 |
| Rust 3/3 both arms | Section 4, line 215 |
| PARTIAL-PASS defined inline | Section 4, lines 209–210 |
| Overall conclusion: mixed/inconclusive | Section 5.4, lines 263–269 |

### Event numbers are 1-based

All event citations in the chapter use 1-based numbers matching the CAPTURE-MANIFEST convention (verified above).

**Criterion 2: VERIFIED**

---

## Criterion 3: SUMMARY.md Wiring + mdbook Build + No Regression

### SUMMARY.md wiring

`src/SUMMARY.md` line 58: `[부록 D: 계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획](appendix-d-planning-comparison.md)`

Position: immediately after 부록 C (line 57). CORRECT.

### mdbook build

Command: `/opt/homebrew/bin/mdbook build`

Output:
```
INFO Book building has started
INFO Running the html backend
WARN unclosed HTML tag `<char>` found in `appendix-c-comparison.md` while exiting TableCell.
HTML tags must be closed before exiting a markdown element.
INFO HTML book written to `/Users/ohama/projs/OpenHandsTests/book`
```

Zero errors. One warning: pre-existing `<char>` in appendix-c-comparison.md (known TD-4 issue). No new warnings introduced. BUILD CLEAN.

### No regression in existing chapters

`git diff b30f292 HEAD -- src/ --name-only` output:
```
src/SUMMARY.md
src/appendix-d-planning-comparison.md
```

Only these two files changed in src/. No edits to ch01–ch07 or appendix-a/b/c. CLEAN.

### deploy.yml unchanged

`git diff b30f292 HEAD -- .github/workflows/deploy.yml` — empty diff (no output). Both pre- and post-phase versions are 53 lines. UNCHANGED.

**Criterion 3: VERIFIED**

---

## Criterion 4: Live Site HTTP 200 + Sidebar TOC

### HTTP status

| URL | Status |
|-----|--------|
| `https://ohama.github.io/Openhands-Tutorial/` | 200 |
| `https://ohama.github.io/Openhands-Tutorial/appendix-d-planning-comparison.html` | 200 |

Both return 200. LIVE.

### Live TOC references appendix-d

Live `toc-7239dd3a.js` contains: `<a href="appendix-d-planning-comparison.html">부록 D: 계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획</a>`

Appendix D is present in the sidebar nav. WIRED.

### origin/main up to date

`git log origin/main --oneline -3` shows:
```
7d5783a docs(14-03): complete push + deploy + live verify plan — v1.4 milestone shipped
616bb45 docs(14-02): complete SUMMARY.md wiring + mdbook build plan
bb2de66 feat(14): add 부록 D planning comparison chapter from captured evidence
```

`git status` shows no uncommitted changes to tracked files (only untracked `.claude/`). Local HEAD matches origin/main. PUSHED.

**Criterion 4: VERIFIED**

---

## Overall Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| 1. Chapter content + number traceability | VERIFIED | 4/4 spot-checked values match comparison.json exactly; all event citations match CAPTURE-MANIFEST 1-based positions |
| 2. Opening paragraph + honesty controls | VERIFIED | Research question correct; no "Claude plans better" claim; 14–32 absent; (단일 실행) applied only to n=1 observations; mixed results reported |
| 3. SUMMARY.md wiring + mdbook build + no regression | VERIFIED | Zero build errors; only pre-existing <char> warning; only SUMMARY.md and appendix-d changed; deploy.yml byte-unchanged |
| 4. Live HTTP 200 + sidebar TOC | VERIFIED | Both URLs return 200; live toc-7239dd3a.js references appendix-d-planning-comparison.html |

**Score: 4/4 criteria VERIFIED**

**Phase goal achieved.** The chapter is written from committed artifacts, wired into the book after 부록 C, deployed live, and all existing chapters are unmodified.

---

_Verified: 2026-06-04_
_Verifier: Claude (gsd-verifier)_
