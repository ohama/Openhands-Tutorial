# Phase 14: 부록 D Chapter + Publish — Research

**Researched:** 2026-06-04
**Domain:** mdBook Korean appendix authoring + GitHub Pages deploy (well-precedented pattern)
**Confidence:** HIGH

---

## Summary

Phase 14 is a well-precedented chapter-write + publish operation that mirrors the completed
Phases 5, 7, 9, and 11. The phase has no novel infrastructure: the chapter reads committed
Phase-13 artifacts verbatim, the SUMMARY.md edit is one line, the build + deploy pipeline is
unchanged, and the live-verification procedure is identical to Phase 11.

The research below focuses on the concrete data-source map (every number the chapter must show
and its authoritative file + field), the exact SUMMARY.md surgery, the build/deploy command
sequence, and the audit checklist for honesty. Prior-art plans (11-02/11-03) are used as
the execution templates.

**Primary recommendation:** Structure Phase 14 as three plans — (1) write appendix-d-planning-
comparison.md from committed artifacts, (2) wire SUMMARY.md + run clean mdbook build, (3) git
push + watch Actions + verify live. Optionally add a v1.4 milestone audit as plan 4. All data
sourcing must happen in plan 1; plans 2 and 3 touch no chapter content.

---

## Data-Source Map

### Authoritative artifact locations

All under `/Users/ohama/projs/OpenHandsTests/.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/`.

| Artifact | Path (relative to captured-planning/) | What it provides |
|----------|--------------------------------------|-----------------|
| CAPTURE-MANIFEST.md | `CAPTURE-MANIFEST.md` | Six-cell outcome table; per-rep canonical pass/fail detail; honesty-gate results; event numbers (1-based); timing caveats; planning artifact pointers; framing rule; `~14–32s/call` disclaimer |
| F# comparison.json | `fsharp/comparison.json` | All P1/P2 median/min/max/n for F# Arm A and Arm B; canonical_test_pass_counts; caveats |
| Scala comparison.json | `scala/comparison.json` | Same for Scala |
| Rust comparison.json | `rust/comparison.json` | Same for Rust |
| F# Arm A claude-plan.md | `fsharp/arm-a/planning-artifact/claude-plan.md` | 5-step Claude plan (verbatim) |
| F# Arm B oh-self-plan.md | `fsharp/arm-b/planning-artifact/oh-self-plan.md` | 5-task self-plan from TaskTrackerAction event #4 (verbatim) |
| Scala Arm A claude-plan.md | `scala/arm-a/planning-artifact/claude-plan.md` | 3-step Claude plan (verbatim) |
| Scala Arm B oh-self-plan.md | `scala/arm-b/planning-artifact/oh-self-plan.md` | 4-task self-plan from TaskTrackerAction event #6 (verbatim) |
| Rust Arm A claude-plan.md | `rust/arm-a/planning-artifact/claude-plan.md` | 3-step Claude plan (verbatim, from Phase-12) |
| Rust Arm B oh-self-plan.md | `rust/arm-b/planning-artifact/oh-self-plan.md` | 4-task self-plan from TaskTrackerAction event #4 (verbatim, from Phase-12 run-1) |
| PLAN-COMPARISON-QUALITATIVE.md | `PLAN-COMPARISON-QUALITATIVE.md` | ANAL-02 qualitative comparison; cross-example summary table |

### Cross-example comparison table — exact values by field

Source: the three comparison.json files. All values are median (min–max), n=3.

#### F# (fsharp/comparison.json)

| Field | Arm A | Arm B |
|-------|-------|-------|
| terminal_actions_count | 80 (77–210) | 74 (52–97) |
| total_events | 207 (204–456) | 174 (139–227) |
| wall_clock_seconds | 1475.25 (470.16–1852.78) | 486.78 (352.28–695.26) |
| avg_llm_call_gap_seconds | 5.01 (3.6–10.78) | 3.95 (3.11–4.0) |
| min_llm_call_gap_seconds | 1.3 (1.23–2.19) | 0.88 (0.8–1.49) |
| max_llm_call_gap_seconds | 37.91 (21.62–70.92) | 25.92 (25.54–40.31) |
| error_fix_cycle_count | 21 (17–28) | 11 (7–14) |
| task_tracker_observation_count | 0 (0–0) | 7 (4–8) |
| task_tracker_action_count | 0 (0–0) | 7 (5–8) |

Canonical pass: Arm A 1/3 reps PASS (run-1 only); Arm B 0/3 PASS.

#### Scala (scala/comparison.json)

| Field | Arm A | Arm B |
|-------|-------|-------|
| terminal_actions_count | 37 (21–62) | 13 (8–27) |
| total_events | 76 (44–132) | 50 (37–83) |
| wall_clock_seconds | 345.67 (304.24–543.95) | 936.16 (868.45–1442.28) |
| avg_llm_call_gap_seconds | 5.43 (4.06–9.86) | 19.76 (12.15–37.5) |
| min_llm_call_gap_seconds | 1.43 (1.33–2.08) | 1.7 (1.39–2.18) |
| max_llm_call_gap_seconds | 28.13 (20.47–57.5) | 64.03 (60.7–118.0) |
| error_fix_cycle_count | 6 (3–10) | 2 (2–5) |
| task_tracker_observation_count | 0 (0–0) | 5 (5–9) |
| task_tracker_action_count | 0 (0–0) | 8 (7–10) |

Canonical pass: Arm A 3/3; Arm B 2/3 PASS + 1 PARTIAL-PASS.

#### Rust (rust/comparison.json)

| Field | Arm A | Arm B |
|-------|-------|-------|
| terminal_actions_count | 12 (12–14) | 13 (12–16) |
| total_events | 26 (26–30) | 44 (40–50) |
| wall_clock_seconds | 48.3 (42.32–49.32) | 66.79 (59.04–71.48) |
| avg_llm_call_gap_seconds | 2.13 (2.11–2.56) | 2.21 (2.15–2.29) |
| min_llm_call_gap_seconds | 1.27 (1.12–1.54) | 0.87 (0.77–1.05) |
| max_llm_call_gap_seconds | 4.87 (4.85–5.28) | 5.07 (5.04–5.14) |
| error_fix_cycle_count | 0 (0–0) | 0 (0–0) |
| task_tracker_observation_count | 0 (0–0) | 7 (7–7) |
| task_tracker_action_count | 0 (0–0) | 7 (7–8) |

Canonical pass: Arm A 3/3; Arm B 3/3.

### n=1 status

**All six cells are n=3.** There are no n=1 cells requiring `(단일 실행)` hedge in the cross-example table. The n=1 hedge is still needed for any prose reference to a specific rep (e.g., "Arm A run-1 passed" for F#), but the median/range figures themselves are all n=3.

### Canonical pass detail (from CAPTURE-MANIFEST.md, lines 101–159)

These are the per-rep event numbers to cite in 부록 D.

**F# Arm A run-1 PASS:** events #200 (2+3*4=14), #202 ((2+3)*4=20), #204 (10-3-2=5).
**F# Arm A run-2, run-3:** FAIL.
**F# Arm B all reps:** FAIL (build errors; tests NOT REACHED).

**Scala Arm A run-1 PASS:** events #39 (→14), #41 (→20), #43 (→5).
**Scala Arm A run-2 PASS:** events #55 (→14), #57 (→20), #59 (→5).
**Scala Arm A run-3 PASS:** all 3 at event #129.
**Scala Arm B run-1 PASS:** events #69 (→14), #73 (→20), #77 (→5).
**Scala Arm B run-2 PASS:** all 3 at event #31.
**Scala Arm B run-3 PARTIAL-PASS:** tests 2+3 at event #45; test 1 not re-run.

**Rust Arm A run-1 PASS:** event #25. Run-2 PASS: event #21. Run-3 PASS: event #21.
**Rust Arm B run-1 PASS:** event #31. Run-2 PASS: event #37. Run-3 PASS: event #45.

### Timing caveat (mandatory in chapter)

Source: CAPTURE-MANIFEST.md §"Timing caveat (mandatory)":
- Timing values are **derived from JSONL timestamps**.
- They carry a **cache-warmth / run-order confound** — the arm that ran second within
  each example benefited from a warmer proxy cache.
- F#/Scala: Arm B ran first (colder); Arm A second (warmer).
- Rust top-ups: Arm A ran first; Arm B second.
- Timing deltas MUST NOT be used as planning-quality signals in isolation.
- The legacy `~14–32s/call` figure is a v1 pre-run PREDICTION, NOT a measurement.
  It must not appear as a measurement anywhere in 부록 D.

### Task tracker confirmation

Source: CAPTURE-MANIFEST.md §"Task tracker confirmation":
- Arm B emitted task_tracker events in every example (F#: median 7; Scala: median 5;
  Rust: median 7, consistent all 3 reps).
- Arm A emitted 0 task_tracker events in all examples.
- This confirms the arms differ on the planning axis.

### P3 token metrics

NOT available. JSONL has no `usage` field. Confirmed in Phase 12 pilot. Do not cite token
counts; do not include a token-metrics row in any table.

### Planning artifact excerpts

The chapter must include per-arm plan excerpts per example (DCHAP-01). Use the verbatim
task list from the planning-artifact/ files (already summarised in PLAN-COMPARISON-QUALITATIVE.md).

Key excerpt facts from CAPTURE-MANIFEST.md §"Planning Artifact Pointers":
- F# Arm A: 5-step plan (fsharp/arm-a/planning-artifact/claude-plan.md) — covers fslex/fsyacc wiring; no source embedded.
- F# Arm B: event #4 TaskTrackerAction, 5 tasks (fsharp/arm-b/planning-artifact/oh-self-plan.md).
- Scala Arm A: 3-step plan (scala/arm-a/planning-artifact/claude-plan.md) — scaffold/write/test.
- Scala Arm B: event #6 TaskTrackerAction, 4 tasks (scala/arm-b/planning-artifact/oh-self-plan.md).
- Rust Arm A: 3-step plan (rust/arm-a/planning-artifact/claude-plan.md) — from Phase-12.
- Rust Arm B: event #4 TaskTrackerAction, 4 tasks (rust/arm-b/planning-artifact/oh-self-plan.md) — from Phase-12 run-1.

PLAN-COMPARISON-QUALITATIVE.md has the full per-example analysis (144 lines):
- §1 F# comparison table + notes (lines 33–53)
- §2 Rust comparison table + notes (lines 74–92)
- §3 Scala comparison table + notes (lines 113–133)
- Summary table (lines 136–144)

---

## Exact SUMMARY.md Edit

**Current SUMMARY.md (src/SUMMARY.md) last lines:**

```
[부록 A: 재현 가이드](appendix-a-repro.md)
[부록 B: 트러블슈팅](appendix-b-troubleshooting.md)
[부록 C: 모델 비교 — 35B vs 122B](appendix-c-comparison.md)
```

(Line 57 is the 부록 C entry; there is no trailing newline section separator before these appendix lines.)

**Required edit — add exactly one line after line 57:**

```
[부록 D: 계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획](appendix-d-planning-comparison.md)
```

**Result after edit (lines 55–58):**
```
[부록 A: 재현 가이드](appendix-a-repro.md)
[부록 B: 트러블슈팅](appendix-b-troubleshooting.md)
[부록 C: 모델 비교 — 35B vs 122B](appendix-c-comparison.md)
[부록 D: 계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획](appendix-d-planning-comparison.md)
```

The new file is: `src/appendix-d-planning-comparison.md`

**Note on format:** The appendix entries in SUMMARY.md use the unnested format (no leading `-`),
matching the existing 부록 A/B/C entries. They are NOT part of a sub-chapter hierarchy.

---

## mdBook Build + GitHub Pages Deploy Procedure

This is identical to Phase 11 (11-02-PLAN.md and 11-03-PLAN.md). Use these as the execution templates.

### Build command

```bash
mdbook build
```

Run from `/Users/ohama/projs/OpenHandsTests/`. mdbook v0.5.3 is at `/opt/homebrew/bin/mdbook`
(confirmed on PATH). Expected output on success:

```
 INFO Book building has started
 INFO Running the html backend
 WARN unclosed HTML tag `<char>` found in `appendix-c-comparison.md` while exiting TableCell
HTML tags must be closed before exiting a markdown element.
 INFO HTML book written to `/Users/ohama/projs/OpenHandsTests/book`
EXIT CODE: 0
```

**Acceptable warnings:** Only the pre-existing TD-4 `<char>` warning from `appendix-c-comparison.md`.
Any new warning (especially broken-link or missing-file for `appendix-d-planning-comparison.md`)
means the SUMMARY wiring or filename is wrong.

**Build output to check after build:**
```
book/appendix-d-planning-comparison.html   ← must exist
```

**Sidebar TOC verification (local):**
```bash
grep -l "appendix-d" book/toc-*.js
```
The TOC JS file (`toc-{hash}.js`) will have a new hash after SUMMARY.md changes.
Confirm `appendix-d-planning-comparison.html` appears as an entry.

### Regression check

Confirm these still exist after build:
```
book/ch01-agentic-ai/   book/ch02-openhands/   book/ch03-setup/
book/ch04-calculator/   book/ch05-wrap-up/     book/ch06-rust-server/
book/ch07-scala-calc/   book/appendix-a-repro.html
book/appendix-b-troubleshooting.html           book/appendix-c-comparison.html
```

### Commit + push procedure

```bash
# PUB-02 audit guard (MUST be first):
git diff -- .github/workflows/deploy.yml          # must be empty
git diff origin/main..HEAD -- .github/workflows/deploy.yml  # must also be empty

# Stage only the new files:
git add src/appendix-d-planning-comparison.md src/SUMMARY.md

# Commit:
git commit -m "feat(14): add 부록 D planning comparison chapter from captured evidence

..."

# Push:
git push origin main
```

**Headless macOS keychain artifact:** `fatal: failed to get: -25308` / `fatal: failed to store: -25308`
lines in push stderr are benign (SSH/headless Mac keychain — confirmed in Phase 11 11-03-SUMMARY.md).
Confirm success from the `main -> main` ref-update line only.

### GitHub Actions deploy verification

```bash
gh run list                     # find the run triggered by the push
gh run watch <run_id>           # watch until conclusion
```

Actions deploy: two jobs (build 9s + deploy 9s in Phase 11 precedent). Node.js 20 deprecation
annotations in Actions output are informational only, not failures.

### Live site verification

```bash
curl -sI https://ohama.github.io/Openhands-Tutorial/
curl -sI https://ohama.github.io/Openhands-Tutorial/appendix-d-planning-comparison.html

# Sidebar: check the live toc-{hash}.js for 부록 D entry
curl -s https://ohama.github.io/Openhands-Tutorial/toc-XXXX.js | grep "appendix-d"
```

Root must return HTTP 200. 부록 D page must return HTTP 200. The sidebar TOC JS file will have
a new hash after SUMMARY.md changes — find it by checking the HTML of any live page for the
`<script src="toc-XXXX.js">` tag, then fetch that file to confirm `appendix-d` appears.

CDN propagation: allow a brief retry window (GitHub Pages typically propagates within 1–2 minutes).

---

## Honesty Audit Checklist

These are the audit items the plan must build in as a verification step:

1. **`~14–32s/call` grep:** `grep -r "14.32\|14–32\|14-32" src/appendix-d-planning-comparison.md`
   Must return no matches. This figure is a v1 pre-run prediction and must never appear
   as a measurement in 부록 D (CAPTURE-MANIFEST.md §"Timing caveat").

2. **1-based event number confirmation:** Any event number cited in 부록 D must match the
   CAPTURE-MANIFEST.md's 1-based positions. The manifest §"EVENT-NUMBERING CONVENTION" states:
   "JSONL line N = event #N; first line is event #1." Key cited events (from CAPTURE-MANIFEST):
   - F# Arm A run-1 passes: events #200, #202, #204
   - Scala Arm A run-1 passes: events #39, #41, #43
   - Rust Arm A run-1 pass: event #25
   - F# Arm B plan: event #4 (TaskTrackerAction)
   - Scala Arm B plan: event #6 (TaskTrackerAction)
   - Rust Arm B plan: event #4 (TaskTrackerAction)

3. **Framing sentence check:** The chapter opening paragraph must state: "이 연구의 핵심 질문은 '전문가가 작성한 계획이 35B의 실행에 도움이 되는가?'이다" (or equivalent Korean phrasing from CAPTURE-MANIFEST framing rule). It must NOT state "Claude plans better than the 35B."

4. **Existing chapters unchanged:** `git diff HEAD -- src/appendix-c-comparison.md` must show
   no changes. The only src/ files touched in Phase 14 are `appendix-d-planning-comparison.md`
   (new) and `SUMMARY.md` (one-line append).

5. **deploy.yml unchanged:** `git diff -- .github/workflows/deploy.yml` must be empty
   (PUB-02 audit guard — run before push).

6. **n=3 labels:** All six cells are n=3; comparisons must use `median (min–max)` format, not
   single-value assertions. No cell requires `(단일 실행)` in the cross-example table; but any
   prose reference to a specific run (e.g., "Arm A run-1의 단 한 번의 PASS") must hedge accordingly.

7. **Mixed/inconclusive framing:** F# result is mixed/inconclusive (Arm A 1/3 vs Arm B 0/3 on
   OOD task); must not be written as "Arm A is better." Scala is broadly positive for both arms
   (both mostly passed). Rust is a tie (both 3/3, zero error-fix cycles). The chapter must
   report all three patterns honestly, not cherry-pick the Scala result.

8. **PARTIAL-PASS disclosure:** Scala Arm B run-3 is PARTIAL-PASS (2 of 3 canonical tests ran
   after compile fix; test 1 not re-run). Must be disclosed; cannot be reported as full PASS.

9. **Wall-clock caveat label:** All timing values must carry the label "JSONL 타임스탬프에서
   도출됨" or equivalent, with the run-order/cache confound disclosed.

---

## Common Pitfalls from Prior Publish Phases

### Pitfall 1: Event numbering (recurring TD)

The worst recurring technical debt across all prior chapters. ARCHITECTURE.md uses 0-based
`events.index()`; metrics_extractor.py and CAPTURE-MANIFEST.md use 1-based positions.
The chapter MUST cite CAPTURE-MANIFEST.md numbers exclusively.

**How to avoid:** All event number citations trace directly to CAPTURE-MANIFEST.md.
Never cite from RUN-NOTES or extractor debug output. The manifest §"EVENT-NUMBERING CONVENTION"
is explicit; every cited event number is there.

### Pitfall 2: Sidebar toc hash changes after SUMMARY.md edit

After adding 부록 D to SUMMARY.md and rebuilding, the sidebar TOC JS file (`toc-{hash}.js`)
gets a new hash. The prior live site uses `toc-5eb11a0d.js` (from Phase 11). After Phase 14's
rebuild + deploy, there will be a new hash. To verify 부록 D in the live sidebar:
1. Fetch the root HTML page and grep for `<script src="toc-` to find the new hash.
2. Fetch `https://ohama.github.io/Openhands-Tutorial/toc-{newhash}.js` and confirm `appendix-d-planning-comparison.html` is in it.

### Pitfall 3: Timing figures presented without the run-order caveat

In Phase 11, final.md included an explicit "솔직한 표기 주의" callout for timing. 부록 D
must do the same. The Scala Arm B wall_clock (936s vs 345s) looks striking but is almost
entirely explained by run-order cache warmth (Arm B ran first = colder proxy cache).
The F# wall_clock delta is confounded by OOD task difficulty, not planning quality.
These confounds must be stated in the chapter, not buried in footnotes.

### Pitfall 4: Cherry-picking Scala result

Scala is the clearest positive signal (Arm A 3/3 vs Arm B ~3/3, but Arm A had lower
error-fix cycles). The chapter must also report F# (mixed/OOD-dominated) and Rust
(tie at n=3). The cross-example summary must present all three columns.

### Pitfall 5: `~14–32s/call` appearing in the chapter

This appeared in 부록 C (the 122B comparison chapter, §3, line 224, correctly labeled as a
legacy prediction). It must NOT appear in 부록 D as a measurement. The grep audit (Checklist
item 1) catches this.

### Pitfall 6: Comparing median values directly without caveat

Each comparison.json has a `deltas_a_minus_b` field. These are raw median differences and
must be treated as descriptive observations, not causal evidence, given the cache/run-order
confound on timing and the OOD confound on F#.

### Pitfall 7: Modifying deploy.yml

The deploy.yml workflow at `.github/workflows/deploy.yml` must stay byte-identical.
The existing pipeline handles mdbook build + Pages deploy with zero configuration changes.
Two `git diff` checks before push (working tree + vs origin) are the guard.

### Pitfall 8: Emitting comparison.json canonical_test_pass_counts without cross-check

STATE.md note `[13-03 canonical_tests authoritative source]` states: "For 부록 D, cite
13-02-RUN-NOTES.md pass/fail matrix, NOT comparison.json canonical_test_pass_counts."
However, STATE.md also notes `[13-04 canonical authoritative source]`: "After canonical-
detector fix (b7a74b9), metrics.json/comparison.json canonical_tests now agree with
13-02-RUN-NOTES.md for all reps. Either source may be cited in 부록 D."

**Resolution:** comparison.json is now confirmed authoritative for canonical pass counts
(after the b7a74b9 fix). The chapter can cite comparison.json pass_fraction_labels directly.
The CAPTURE-MANIFEST.md six-cell table provides the same authoritative data in a single file.

---

## Chapter Structure Recommendation

The chapter should parallel the style of `appendix-c-comparison.md` (부록 C: 378 lines, Korean
prose, honesty-first callouts without emoji). Suggested sections for
`src/appendix-d-planning-comparison.md`:

1. **Opening / 연구 질문**: Framing paragraph (1–2 paragraphs) — "does an expert-authored
   plan help the 35B execute?" Arm A / Arm B definition. CAPTURE-MANIFEST framing rule cited.

2. **실험 설계**: Study design table (n=3 per cell, counterbalanced run order, single-session
   per arm, CodeActAgent, version block from CAPTURE-MANIFEST §"Version Block").

3. **계획 아티팩트 비교**: Per-example subsections with plan excerpt tables (from
   PLAN-COMPARISON-QUALITATIVE.md). Claude plan step count vs self-plan task count.
   Scaffold→Write→Build→Test match column. Key difference (F#: OOD specificity; Scala:
   test-driven self-plan; Rust: nearly identical).

4. **지표 비교 테이블 (P1/P2)**: Cross-example table with all six cells × all metrics
   (TerminalActions, TotalEvents, WallClock, ErrorFixCycles, AvgLLMCallGap, TaskTracker
   counts). Mandatory timing caveat footnote. Mandatory n=3 / median(min–max) format.

5. **정규 테스트 결과**: Pass/fail table (F#: 1/3 vs 0/3; Scala: 3/3 vs 2/3+PARTIAL;
   Rust: 3/3 vs 3/3). PARTIAL-PASS definition inline.

6. **해석**: Honest per-example interpretation. F# (OOD-dominated, mixed). Scala (both
   arms broadly succeed; Arm A had more error-fix cycles; wall-clock confounded). Rust
   (both arms tie; zero error-fix cycles; no meaningful arm difference). Overall: the
   expert plan helped navigate OOD in 1 run (F# Arm A run-1), had no observable effect on
   in-distribution tasks.

7. **출처 (Sources)**: List all committed captured-planning/ artifacts cited.

---

## Architecture Patterns

No new architecture is introduced. The appendix follows the existing single-file appendix
pattern (`appendix-{a,b,c}-*.md`). No sub-chapter directory is created.

**Callout style:** Match `appendix-c-comparison.md` exactly:
- Blockquote `> **사용자 프롬프트**` / `> **내부 프로세스**` / `> **결과**` for event narration
- No pictograph emoji in any callout
- 출처: lines inside callouts cite specific artifact paths

---

## Standard Stack

| Tool | Version | Purpose |
|------|---------|---------|
| mdbook | v0.5.3 | Local build (`/opt/homebrew/bin/mdbook`) |
| gh CLI | available | Watch Actions run, verify deploy |
| curl | system | Live HTTP 200 verification |
| git | system | PUB-02 audit guard, commit, push |

No new dependencies. All tools verified in prior publish phases.

---

## Recommended Plan/Wave Breakdown

**Plan 14-01 (Wave 1): Write appendix-d-planning-comparison.md**
- Read all 10 committed artifacts (CAPTURE-MANIFEST, 3x comparison.json, 6x planning-artifact,
  PLAN-COMPARISON-QUALITATIVE.md)
- Write `src/appendix-d-planning-comparison.md` verbatim from artifacts
- Run honesty audit inline (grep ~14–32s/call; confirm 1-based event numbers; confirm framing)
- Do NOT touch SUMMARY.md or run mdbook build yet

**Plan 14-02 (Wave 2): Wire SUMMARY.md + mdbook build (DPUB-01)**
- One-line edit to `src/SUMMARY.md`: add 부록 D after 부록 C
- Run `mdbook build`; assert exit 0 and only TD-4 `<char>` warning
- Confirm `book/appendix-d-planning-comparison.html` exists
- Spot-check no regression (existing HTML dirs still present)
- Commit `src/appendix-d-planning-comparison.md` + `src/SUMMARY.md`

**Plan 14-03 (Wave 3): Deploy + live verify (DPUB-02)**
- PUB-02 audit: `git diff -- .github/workflows/deploy.yml` must be empty
- `git push origin main`
- `gh run watch` until Actions run concludes success
- `curl -sI` root + `appendix-d-planning-comparison.html` → HTTP 200
- Confirm `appendix-d` in live sidebar toc-{hash}.js

**Optional Plan 14-04: v1.4 Milestone Audit**
- Cross-check all DCHAP-01/02 + DPUB-01/02 requirements satisfied
- Update `.planning/STATE.md` + `.planning/ROADMAP.md` to mark v1.4 complete
- Create v1.4 milestone archive documents

---

## Sources

### Primary (HIGH confidence)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/CAPTURE-MANIFEST.md` — event numbers, framing rule, six-cell table, timing caveat, all honesty gates
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/{fsharp,scala,rust}/comparison.json` — all P1/P2 numeric values
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/PLAN-COMPARISON-QUALITATIVE.md` — ANAL-02 qualitative analysis
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/{fsharp,scala,rust}/arm-{a,b}/planning-artifact/*.md` — verbatim plan excerpts
- `.planning/milestones/v1.3-phases/11-7부-chapter-publish/11-02-PLAN.md`, `11-02-SUMMARY.md`, `11-03-PLAN.md`, `11-03-SUMMARY.md` — exact prior-art build+deploy procedure
- `.planning/milestones/v1.3-phases/11-7부-chapter-publish/11-VERIFICATION.md` — live verification evidence including toc hash, sidebar entry format, HTTP 200 checks
- `src/SUMMARY.md` — current SUMMARY.md (line 57 = 부록 C; 부록 D appended after it)
- `.github/workflows/deploy.yml` — deploy pipeline (do not modify)
- `src/appendix-c-comparison.md` — chapter style precedent (378 lines, Korean, no emoji)

### Confidence assessment

| Area | Level | Reason |
|------|-------|--------|
| Data-source map | HIGH | All numeric values directly read from committed JSON files |
| SUMMARY.md edit | HIGH | Current file read; single-line append confirmed |
| Build/deploy procedure | HIGH | Exact commands and expected output from Phase 11 11-02/11-03 SUMMARYs |
| Honesty audit checklist | HIGH | Derived from CAPTURE-MANIFEST + STATE.md decisions |
| Chapter structure | HIGH | Mirrors prior appendix + requirements DCHAP-01/02 |
| Sidebar toc hash | MEDIUM | Hash will change after SUMMARY.md edit; procedure to find new hash is reliable but must be followed at execution time |

---

## Metadata

**Research date:** 2026-06-04
**Valid until:** 2026-07-04 (stable data; all numeric values are committed + frozen)
**Phase gate:** CAPTURE-MANIFEST.md §"PHASE 13 CAPTURE GATE: CLOSED" — Phase 14 is unblocked.
