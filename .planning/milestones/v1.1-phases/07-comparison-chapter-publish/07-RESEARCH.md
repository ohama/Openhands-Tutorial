# Phase 7: 35B-vs-122B Comparison Chapter — Research

**Researched:** 2026-05-28
**Domain:** mdBook Korean chapter authoring from captured JSONL evidence; GitHub Pages re-deploy
**Confidence:** HIGH — all source material read directly from captured manifests, run notes, JSONL log summaries, and final-source files

---

## Summary

This phase writes a new Korean chapter contrasting the Qwen2.5-35B run (v1) with the Qwen2.5-122B run (v1.1) on the same F# calculator task. All comparison claims must trace to verbatim evidence in the two captured log sets. The chapter is then wired into SUMMARY.md and re-deployed to GitHub Pages via the existing CI workflow.

The primary finding from the captures: the two models differ most fundamentally on the lexer task. The 35B failed the FsLex format entirely in attempt 1 (three agents, 137+ TerminalActions, all produced `%%` separators — yacc-style confusion). The lexer was then provided verbatim for attempt 2. The 122B wrote a structurally valid FsLex file on its first unaided attempt (correct `rule tokenize = parse` format, no `%%`). This capability distinction is the heart of the chapter.

The timing finding is a surprise: the 122B run averaged **6.3s/call** (from the 122B CAPTURE-MANIFEST timing table). The 35B attempt 2 ran in 356s total with 67 TerminalActions, implying ~**5.3s/call average** computed from the RUN-NOTES task duration table. This means both models are in the same per-call speed range on this machine — not the "bigger = slower" expectation. The chapter must report this honestly.

**Primary recommendation:** Place the chapter as new **부록 C: 모델 비교** (Appendix C), file `src/appendix-c-comparison.md`. Create the file before wiring SUMMARY.md (required because `create-missing = false` in book.toml). Push to main triggers auto-deploy; verify live URL after push.

---

## 1. Chapter Placement Decision

### Options Weighed

| Option | Rationale | Verdict |
|--------|-----------|---------|
| New **6부: 35B vs 122B 비교** (between 5부 and 부록) | Most visible; signals this is a major v1.1 addition | Good but overweights the comparison relative to the primary tutorial |
| **부록 C: 모델 비교** (appended after 부록 B) | Consistent with reference-material framing; appendixes already established as "dig deeper" section; keeps the 4부 narrative clean; least disruption to book flow | **Recommended** |
| Inserted into 4부 as a final chapter | Keeps worked-example arc together but makes 4부 feel asymmetric (35B chapters + 1 comparison) | Not recommended |

**Recommendation: 부록 C** — the comparison is reference material that supplements the main worked-example narrative, consistent with how 부록 A (재현 가이드) and 부록 B (트러블슈팅) are framed. Readers who want the comparison find it in the appendix; it doesn't interrupt the tutorial flow. The planner can override to 6부 if visibility is a priority.

---

## 2. Concrete Comparison Content (Distilled from Both Captures)

### 2.1 Capability: Lexer-Unaided

**35B:** In attempt 1, three separate OpenHands agents (94+27+16 TerminalActions, totaling 137+) all produced FsLex files with `%%` separators — the FsYacc/yacc-style delimiter that is NOT valid FsLex syntax. After exhausting the retry budget, Lexer.fsl was provided verbatim in the task2 prompt for attempt 2. The 35B agent in attempt 2 wrote Lexer.fsl by copying the verbatim content (6 events, 2 TerminalActions in task2-lexer.jsonl).

**Citation (35B):** `03-02-RUN-NOTES-attempt1.md` § "Root Cause Analysis: FsLex Issues" and § "Final Fix (Manual - Deviation Rule 3)"; v1 CAPTURE-MANIFEST § "On the lexer and .fsproj (scaffolded, not agent-authored)".

**122B:** Agent wrote Lexer.fsl in task2-lexer-unaided.jsonl event 9 (TerminalAction):
```
cat > Lexer.fsl << 'EOF'
{
open Parser
exception LexingError of string
}
rule tokenize = parse
  | [' ' '\t'] { tokenize }
  | ['0'-'9']+ as s { INT (int s) }
  ...
  | eof { EOF }
  | _ { raise (LexingError ...) }
EOF
```
The file uses the correct `rule tokenize = parse` format (no `%%` separator). Confirmed by event 12 (cat Lexer.fsl, exit_code=0).

**Citation (122B):** 122B CAPTURE-MANIFEST § "Lexer Outcome (RUN122-01/02)"; task2-lexer-unaided.jsonl events 9, 12.

**Honesty note for chapter:** Disclose explicitly that the comparison is between different setups — the 35B was given the lexer verbatim (attempt 2), while the 122B wrote it unaided. This is by design (to test what the 122B could do), but it means the comparison is not on equal footing.

---

### 2.2 Error-and-Fix Character

**35B (task3-parser.jsonl, events 10–30):** 4 build failures on Parser.fsy + Program.fs, all self-corrected:

| Attempt | Error | Fix |
|---------|-------|-----|
| Event 10 | `FSY000: at least one %start declaration required` — omitted `%start` | Added `%start <int> start` (wrong combined form) |
| Event 16 | `Parser.fsy(16,7): error parse error` — wrong FsYacc syntax | Another rewrite attempt |
| Event 20 | Same parse error | Another rewrite attempt |
| Event 26 | `FS0039: 'LexBuffer<_>' does not define 'FromText'` — non-existent API | Fixed to `LexBuffer<char>.FromString` |
| Event 30 | Build SUCCESS (exit_code=0) | `calc net10.0 성공 (0.7초)` |

**Nature:** Standard FsYacc declaration syntax errors + one non-existent API name. 4 iterations, concentrated in grammar/API discovery. The domain is in-distribution for the 35B.

**Citation (35B):** v1 CAPTURE-MANIFEST § "RUN-03 — A genuine error-and-fix cycle (not scripted)"; `03-02-RUN-NOTES.md` § "Error-and-Fix Cycle (Branch A)"; task3-parser.jsonl events 10–30.

**122B (task5-buildtest.jsonl, events 12–74):** 8 build failures (plus 1 runtime crash) on Lexer.fsl INT API, self-corrected:

| Attempt | Agent's INT line | Error |
|---------|-----------------|-------|
| 0 (event 12) | `as s { INT (int s) }` | FS0001, FS0039 |
| 1 (event 18) | `rule tokenize lexbuf = parse` + `Lexing.matched` | FS0038, FS0001 |
| 2 (event 30) | `Lexing.matched lexbuf` | FS0001, FS0039 |
| 3 (event 40) | `tokenize lexbuf` + `Lexing.matched lexbuf` | FS0039 |
| 4 (event 50) | `FSharp.Text.Lexing.matched` | FS0039 (non-existent) |
| 5 (event 56) | `Lexing.matchedText` | FS0039 (non-existent) |
| 6 (event 60) | full namespace + `matchedText` | FS0039 |
| 7 (event 66) | `lexbuf.ToString()` | exit_code=134 runtime crash (returns type name) |
| 8 (event 70) | `lexbuf.Lexeme` | FS0193 (char array → int) |
| **9 (event 74)** | **`new string(lexbuf.Lexeme)`** | **Build SUCCESS** |

Agent's reasoning at event 71: "`lexbuf.Lexeme` returns a char array. Let me convert it to a string:"

**Nature:** Extended API-search through genuinely obscure FSharp.Text.Lexing territory. 9 iterations across multiple guesses, including a runtime crash. The final fix (`new string(lexbuf.Lexeme)`) is correct but non-obvious — the 122B found it through systematic elimination, not recall.

Note: The 35B's scaffolded Lexer.fsl used `LexBuffer<_>.LexemeString lexbuf` (the manual-written correct form). The 122B independently converged on `new string(lexbuf.Lexeme)` — a different but equivalent approach.

Also note: The 122B's lexer error appeared first in task3-parser.jsonl (events 24, 42, 46) when the agent ran `dotnet build` to test the parser, and saw `FSLEX: error FSL000: The macro s is not defined`. The agent deferred the lexer fix to task5. The error-and-fix spans tasks 3–5 in the 122B run.

**Citation (122B):** 122B CAPTURE-MANIFEST § "Error-and-Fix Record (RUN122-03)"; task5-buildtest.jsonl events 12–74.

**Qualitative difference for the chapter:** The 35B's errors were compact grammar/API bugs (4 iterations, 20 events). The 122B's errors were a prolonged search across wrong API names and type-mismatch variants (9 iterations, 62 events). Both show genuine autonomous recovery; the 122B's domain (FsLex API) was genuinely harder to converge on.

---

### 2.3 Measured Speed (CMP-01) — Key Honesty Flag

**122B (directly measured, from CAPTURE-MANIFEST § "Timing Summary"):**

| Task | Total | TerminalActions | Avg LLM-call gap |
|------|-------|-----------------|-----------------|
| task1-scaffold | 167.5s | 20 | 6.6s |
| task2-lexer-unaided | 57.7s | 7 | 3.2s |
| task3-parser | 252.3s | 37 | 5.5s |
| task4-evaluator | 362.7s | 47 | 6.6s |
| task5-buildtest | 389.0s | 39 | 7.0s |
| **Total** | **1229.2s (20.5 min)** | **150** | **6.3s avg** |

Per-call range: 1.8s min, 46.6s max.

**35B attempt 2 (derived from 03-02-RUN-NOTES.md task duration table):**

| Task | Duration | TerminalActions | Implied avg |
|------|----------|-----------------|-------------|
| task1-scaffold | 186s (3m 6s) | 27 | 6.9s |
| task2-lexer | 16s | 2 | 8.0s |
| task3-parser | 77s (1m 17s) | 15 | 5.1s |
| task4-evaluator | 45s | 14 | 3.2s |
| task5-buildtest | 32s | 9 | 3.6s |
| **Total** | **356s (5.9 min)** | **67** | **~5.3s avg** |

**The Surprise Finding:** The 122B averaged **6.3s/call** vs the 35B's implied **~5.3s/call** — they are in the same range on this hardware, not dramatically different. The original hypothesis (bigger = slower) did NOT materialize as a large gap. The 122B used more total calls (150 vs 67), so total elapsed time is ~1229s vs ~356s — but the difference is driven by the 8-iteration error-fix cycle, not by per-call latency.

**CRITICAL GAP:** The 35B per-call timing (~5.3s/call) is DERIVED from task duration totals divided by TerminalAction counts — the 03-02-RUN-NOTES.md does not record per-LLM-call timestamps the way the 122B CAPTURE-MANIFEST does. The 122B manifest explicitly computed LLM-call gaps from JSONL timestamps. The 35B figure is an approximation (wall time ÷ TerminalActions), which includes bash execution time. The chapter should note this measurement asymmetry honestly.

**Also note:** The 122B CAPTURE-MANIFEST cites "35B's ~14–32s/call (from v1 RUN-NOTES)" — this figure originated from a **pre-run probe prediction** in 06-RESEARCH.md §1.3, not from the actual v1 run's measured timing. The actual v1 attempt-2 run data implies ~5.3s/call average. The chapter should use the measured attempt-2 data, not the pre-run prediction.

---

### 2.4 Final Source Differences

**Lexer.fsl INT token line:**

| Model | Line | How derived |
|-------|------|-------------|
| 35B (scaffolded) | `let s = LexBuffer<_>.LexemeString lexbuf` / `INT (System.Int32.Parse s)` | Manually provided verbatim |
| 122B (agent-written, after 9 iterations) | `INT (int (new string(lexbuf.Lexeme)))` | Agent's final convergence |

Both produce the same result. The 122B's form uses `lexbuf.Lexeme` (char array) + `new string(...)` + `int` conversion; the scaffolded form uses `LexBuffer<_>.LexemeString` (the higher-level API).

**Parser.fsy differences:**

| Aspect | 35B | 122B |
|--------|-----|------|
| Grammar structure | Flat `expr` rules (no `term`/`factor` nonterminals) | Explicit `expr → term → factor` hierarchy |
| Unary minus | Not present | `factor: \| MINUS factor { -$2 }` |
| Token declaration syntax | `%token <int> INT` (with space) | `%token<int> INT` (no space) |
| `%start`/`%type` | Separate lines: `%start start` / `%type <int> start` | Same (correct FsYacc two-line form) |

The 122B's grammar is more structured (expr/term/factor hierarchy vs flat expr) and adds a `%right NEG`-equivalent unary-minus rule. Both pass all three test cases (14/20/5).

**Source citations:** `captured/final-source/Parser.fsy` (35B); `captured-122b/final-source/Parser.fsy` (122B); `captured/final-source/Lexer.fsl` (35B scaffolded); `captured-122b/final-source/Lexer.fsl` (122B agent-written).

---

## 3. Honesty Constraints for Chapter Tasks

These must be baked into planner task prompts as hard requirements:

1. **Disclose the setup difference:** The 35B was given the lexer verbatim (attempt 2 design choice after attempt 1 failure). The 122B wrote it unaided. The comparison is on different setups — that is the experiment, not a flaw, but it must be stated clearly in the chapter.

2. **No invented numbers:** Every speed figure must come from the manifests. Use the 122B's 6.3s/call (directly measured from JSONL timestamps). Use the 35B's ~5.3s/call with explicit note that it is derived from wall-time ÷ TerminalAction count (approximation), not from per-call JSONL timestamps.

3. **Don't use the pre-run prediction:** The "~14–32s/call" figure for 35B in the 122B CAPTURE-MANIFEST is from a pre-run probe prediction (06-RESEARCH.md §1.3), not from measured attempt-2 timing. Use the attempt-2 measured data instead.

4. **Report the timing finding honestly:** The 122B is NOT dramatically slower per call on this machine. Both models are ~5–7s/call average. The 122B's total run was longer because of 150 vs 67 TerminalActions (driven by error-fix depth), not because of slower per-call latency.

5. **Report error-fix iteration counts verbatim:** 35B = 4 iterations (events 10–30 of task3-parser.jsonl). 122B = 9 iterations (events 12–74 of task5-buildtest.jsonl) plus cross-task context (task3 events 24/42/46 + task4 multiple events).

6. **No fabrication:** Where the JSONL record is ambiguous, say so. Where evidence is in the manifest summary vs. actual JSONL, cite the manifest (it was verified against the JSONL by the capture phase).

---

## 4. Practical Mechanics

### 4.1 Recommended File Path

```
src/appendix-c-comparison.md
```

(If planner overrides to 6부: `src/ch06-comparison.md` — chapter files go in `src/`, matching existing convention of flat files for appendixes and `chNN-*/` subdirectories for multi-file parts.)

### 4.2 SUMMARY.md Wiring

**Current SUMMARY.md tail (lines 37–41):**
```markdown
---

[부록 A: 재현 가이드](appendix-a-repro.md)
[부록 B: 트러블슈팅](appendix-b-troubleshooting.md)
```

**New SUMMARY.md tail (add one line after 부록 B):**
```markdown
---

[부록 A: 재현 가이드](appendix-a-repro.md)
[부록 B: 트러블슈팅](appendix-b-troubleshooting.md)
[부록 C: 모델 비교 — 35B vs 122B](appendix-c-comparison.md)
```

Note: mdBook appendix-style entries use `[Title](path.md)` with no leading `-` (flat list under `---`), matching the existing 부록 A and B pattern. Confirm this matches the actual SUMMARY.md format before wiring.

**If planner chooses 6부 instead:**
```markdown
# 6부: 35B vs 122B 비교

- [같은 작업, 더 큰 모델로](ch06-comparison/overview.md)
```
(Would require creating `src/ch06-comparison/` directory.)

### 4.3 mdBook Conventions to Honor

- `create-missing = false` in `book.toml` — **create the .md file BEFORE editing SUMMARY.md**. If SUMMARY.md references a file that doesn't exist, `mdbook build` fails.
- Korean prose, English technical terms inline (matching existing chapter style: "에이전트 루프", "OpenHands", "F#", "FsLex", "TerminalAction", etc.).
- Headers in Korean: `## 레서 비교`, `## 오류-수정 사이클`, `## 속도 측정`, `## 소스 코드 차이`, etc.
- Verbatim code blocks: use triple-backtick fenced blocks with language identifier (`fsharp`, `text`, etc.) — matches existing book style.
- Keep existing cross-reference tone: chapter may link to `ch04-calculator/` sections if referencing the 35B run's details.

### 4.4 Build Verification Step

Before committing, run locally:
```bash
mdbook build
```
Confirm: `book/appendix-c-comparison.html` exists in the build output and `mdbook build` exits with code 0. Then commit + push; CI handles the rest.

---

## 5. Deploy Mechanics Confirmation

**Existing workflow:** `.github/workflows/deploy.yml` triggers on `push` to `main` branch, installs latest mdBook, runs `mdbook build`, uploads `book/` artifact, deploys to GitHub Pages.

**No workflow changes needed.** PUB-02 (live on Pages) is achieved by:
1. `git push` to `main`
2. Wait for GitHub Actions to complete (typically 2–3 minutes)
3. Verify: `curl -s https://ohama.github.io/Openhands-Tutorial/appendix-c-comparison.html | grep -c "35B"` (or equivalent) returns > 0.

The site-url is `/Openhands-Tutorial/` (from book.toml). The live URL for the new chapter would be:
`https://ohama.github.io/Openhands-Tutorial/appendix-c-comparison.html`

(Adjust if the repo name differs from `Openhands-Tutorial` — confirm from `book.toml`'s `git-repository-url` field which reads `https://github.com/ohama/Openhands-Tutorial`.)

---

## 6. Gaps and Open Questions

### Gap 1: 35B Per-Call Timing Not Precisely Measured (HIGH IMPORTANCE)
**What we know:** 35B attempt-2 task durations from RUN-NOTES (186s/27TA, 16s/2TA, 77s/15TA, 45s/14TA, 32s/9TA) → implied avg ~5.3s/call.
**What's unclear:** This is wall-time ÷ TerminalAction count. It includes bash execution time within each call window. The 122B manifest computed LLM-call gaps differently (ObservationEvent timestamp → next ActionEvent timestamp = pure model think time, excluding bash). The 35B logs could yield the same precise measurement if analyzed at the JSONL timestamp level.
**Recommendation:** The chapter should use "approximately 5–7s/call" for both models, with a footnote that the 35B figure is derived (wall-time approximation) while the 122B figure is directly measured. If the planner wants precise 35B numbers, add a task to compute per-call gaps from task1-scaffold.jsonl and task3-parser.jsonl (the two largest logs).

### Gap 2: 35B Attempt-1 TerminalAction Count Nuance
**What we know:** 03-02-RUN-NOTES-attempt1.md says "3 separate agents (94+27+16 TerminalActions)" failed on the lexer.
**What's unclear:** The "94+27+16" figure comes from the attempt-1 JSONL files archived in `oh-workdir/_attempt1-attic/` (gitignored). The actual JSONL is not committed. The chapter should use these numbers as cited in the run notes without claiming to have verified them independently.
**Recommendation:** Cite 03-02-RUN-NOTES-attempt1.md directly; add "(archived, not committed)" notation.

### Gap 3: 122B Attempt-1 Confirmation for task2
**What we know:** CAPTURE-MANIFEST says "unaided-attempts: 1" and "RUN122-02 status: N/A — fallback not needed". The file task2-lexer-scaffold.jsonl does not exist.
**What's unclear:** Minor — confirms there was no fallback, this is complete. No gap.

### Gap 4: 122B Parser Unary-Minus Token Name
**What we know:** The 122B Parser.fsy has `| MINUS factor { -$2 }` (using the `MINUS` token for unary minus). The 122B CAPTURE-MANIFEST says "a correct `factor: | MINUS factor { -$2 }` for unary minus." The 35B has no unary-minus rule.
**What's unclear:** The context mentions `%right NEG` in the objective brief, but the actual 122B Parser.fsy uses `MINUS` (not a separate `NEG` token). There is no `%right NEG` in the committed Parser.fsy. The chapter should describe the actual code, not the brief's expectation.
**Recommendation:** Describe 122B's unary minus as `| MINUS factor { -$2 }` reusing the `MINUS` token — which is what the file actually contains.

### Gap 5: Live GitHub Pages URL Verification
**What we know:** `book.toml` specifies `git-repository-url = "https://github.com/ohama/Openhands-Tutorial"` and `site-url = "/Openhands-Tutorial/"`.
**What's unclear:** Whether GitHub Pages is currently serving (might need to verify the repo name and Pages config). Not a blocker for writing the chapter.
**Recommendation:** PUB-02 verification step should include `curl -sI https://ohama.github.io/Openhands-Tutorial/` to confirm 200 before checking the new chapter URL.

---

## Standard Stack / Tools

No new libraries needed. This phase uses:

| Tool | Purpose | Already in place |
|------|---------|-----------------|
| mdBook | Book builder | Yes — `mdbook build` runs locally |
| GitHub Actions | CI/CD deploy | Yes — `deploy.yml` already configured |
| Korean prose | Chapter language | Established convention in existing chapters |
| Verbatim JSONL evidence | All comparison claims | Captured in both log sets |

---

## Architecture Patterns

### Chapter Structure (Recommended)

```markdown
# 부록 C: 모델 비교 — Qwen2.5-35B vs 122B

## 실험 설계와 공정성 전제
[Disclose setup difference upfront: 35B lexer was scaffolded, 122B was unaided]

## 1. 렉서 작성 능력
[Core capability distinction: 35B failure → scaffold; 122B unaided success]

## 2. 오류-수정 사이클 비교
[35B: 4 iterations on parser grammar; 122B: 9 iterations on lexer API]

## 3. 처리 속도 측정
[Both ~5–7s/call; total elapsed: 35B ~356s vs 122B ~1229s; reason: iteration count not speed]

## 4. 최종 소스 코드 차이
[Lexer.fsl INT line; Parser.fsy grammar structure; unary minus]

## 5. 결론
[Summary finding; both pass 14/20/5; the lexer question is the key differentiator]
```

### Anti-Patterns to Avoid

- **Inventing timing narrative:** Do NOT say "122B is slower" — the per-call data doesn't support this. Do say "122B took more total calls due to the longer error-fix sequence."
- **Treating the setup difference as a flaw:** The scaffolded-vs-unaided design was intentional. Present it as the experiment design, not as a caveat.
- **Citing the pre-run prediction:** The "~14–32s/call" figure in the 122B CAPTURE-MANIFEST cross-references a pre-run probe, not measured attempt-2 data. Use the attempt-2 derived timing instead.
- **Over-reading the grammar difference:** The 122B's expr/term/factor hierarchy vs 35B's flat expr is a style difference, not a correctness difference — both pass all tests. Don't claim one is "better."

---

## Common Pitfalls

### Pitfall 1: SUMMARY.md wired before file created
**What goes wrong:** `mdbook build` fails with "file not found" because `create-missing = false`.
**How to avoid:** Write `src/appendix-c-comparison.md` first, verify it exists, then edit SUMMARY.md, then run `mdbook build`.

### Pitfall 2: Broken indentation in fenced code blocks
**What goes wrong:** mdBook renders code blocks incorrectly if there's inconsistent indentation or if backticks are inside list items.
**How to avoid:** Keep code blocks at top-level indentation within the chapter, not nested inside list items.

### Pitfall 3: Citing wrong 35B timing figure
**What goes wrong:** Using "~14–32s/call" (pre-run prediction) instead of the derived ~5.3s/call average from the actual attempt-2 run.
**How to avoid:** Task prompt must specify: use 03-02-RUN-NOTES.md duration table ÷ TerminalAction counts for 35B timing; do NOT use figures from 06-RESEARCH.md §1.3.

### Pitfall 4: Missing `open FSharp.Text.Lexing` in quoted 122B Lexer.fsl
**What goes wrong:** The final committed `captured-122b/final-source/Lexer.fsl` does not have `open FSharp.Text.Lexing` in the header — it uses `lexbuf.Lexeme` which does not require the namespace to be opened (it's accessed via the lexbuf object). If the chapter quotes the file, it should quote the actual content, not add the namespace.
**How to avoid:** Quote `src/final-source/Lexer.fsl` verbatim.

---

## Sources

### Primary (HIGH confidence — directly read)

- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/CAPTURE-MANIFEST.md` — 35B attempt-2 artifact map, task timing, error-fix events
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/03-02-RUN-NOTES.md` — 35B attempt-2 per-task durations and error-fix narrative
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/03-02-RUN-NOTES-attempt1.md` — 35B attempt-1 failure record (FsLex confusion, 137+ TerminalActions)
- `/Users/ohama/projs/OpenHandsTests/.planning/phases/06-capture-the-122b-openhands-run/captured-122b/CAPTURE-MANIFEST.md` — 122B timing table, lexer outcome, 9-iteration error-fix table, comparison hooks
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/final-source/Parser.fsy` — 35B final Parser.fsy (flat expr grammar, no unary minus)
- `/Users/ohama/projs/OpenHandsTests/.planning/phases/06-capture-the-122b-openhands-run/captured-122b/final-source/Parser.fsy` — 122B final Parser.fsy (expr/term/factor hierarchy, MINUS factor unary minus)
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/final-source/Lexer.fsl` — 35B scaffolded Lexer.fsl (LexBuffer<_>.LexemeString)
- `/Users/ohama/projs/OpenHandsTests/.planning/phases/06-capture-the-122b-openhands-run/captured-122b/final-source/Lexer.fsl` — 122B agent-written Lexer.fsl (new string(lexbuf.Lexeme))
- `/Users/ohama/projs/OpenHandsTests/src/SUMMARY.md` — current book structure
- `/Users/ohama/projs/OpenHandsTests/book.toml` — `create-missing = false` confirmed; site-url confirmed
- `/Users/ohama/projs/OpenHandsTests/.github/workflows/deploy.yml` — deploy-on-push-to-main confirmed

### Secondary (HIGH confidence — cross-referenced)

- `/Users/ohama/projs/OpenHandsTests/.planning/phases/06-capture-the-122b-openhands-run/06-RESEARCH.md` §1.3 — source of the "~14–32s/call" pre-run prediction (flagged as NOT the measured data)

---

## Metadata

**Confidence breakdown:**
- Chapter placement: MEDIUM — rationale clear, but planner may have narrative preferences that override
- Comparison content (capability, error-fix): HIGH — directly read from manifests and source files
- Measured speed: MEDIUM-HIGH — 122B timing is directly measured; 35B timing is derived approximation
- File mechanics (path, SUMMARY wiring): HIGH — read from actual SUMMARY.md and book.toml
- Deploy mechanics: HIGH — deploy.yml read; workflow is straightforward push-to-main

**Research date:** 2026-05-28
**Valid until:** Indefinite (source material is static captured artifacts)
