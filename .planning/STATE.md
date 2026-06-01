# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-01 — v1.3 Scala Example shipped)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run real programs. v1: F# FsLex/FsYacc calculator (35B). v1.1: same calculator with 122B, comparison. v1.2: same 35B, different language — a minimal Rust HTTP server (6부). v1.3: same 35B, Scala 3 arithmetic calculator (7부) — completes the calculator trilogy.
**Current focus:** v1.3 functionally COMPLETE — both phases verified (Phase 10 capture 5/5; Phase 11 chapter+publish 4/4). 7부 live. Ready for /gsd:audit-milestone then /gsd:complete-milestone v1.3.

## Current Position

Milestone: v1.3 (Scala Example) — ALL PHASES COMPLETE + verified 2026-06-01. Ready for audit/close-out.
Phase: Phase 11 (7부 Chapter + Publish) — ✓ COMPLETE + verified 4/4 PASS (11-VERIFICATION.md).
Plan: All Phase 10 + 11 plans complete. Next: /gsd:audit-milestone (then /gsd:complete-milestone v1.3).
Status: SHIPPED. 7부 written verbatim from captured-scala/ (byte-identical code, ONE self-corrected compile error, no false sealed-trait claim, manifest 1-based event numbers, ~14–32s only as labeled prediction). mdbook clean; Actions run 26739869947 success; live root + ch07-scala-calc/intro.html HTTP 200; 7부 in live toc-5eb11a0d.js; deploy.yml unchanged. CHAP-01/02 + PUB-01/02 Complete.
Last activity: 2026-06-01 — Phase 11 executed (3 waves) + verified 4/4; ROADMAP/STATE/REQUIREMENTS updated.

Progress: ✅ v1 + v1.1 + v1.2 shipped. 🚧 v1.3 functionally complete (Phases 10–11 verified) — pending audit + close-out. Total: 11 phases, 32 plans.
Live: https://ohama.github.io/Openhands-Tutorial/ (7부 Scala calculator live at /ch07-scala-calc/intro.html)

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial + 35B captured run of F# calculator. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C comparison + UX callouts. See `milestones/v1.1-ROADMAP.md`.
- **v1.2 Rust Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Rust HTTP server capture + 6부 chapter (다른 워킹 예제) live. Confirmed Rust is more in-distribution for 35B than FsLex was (wrote the server unaided where it failed FsLex). Audit caught + fixed TD-6 (timing prediction mislabeled as measurement). See `milestones/v1.2-ROADMAP.md`.
- **v1.3 Scala Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Scala 3 recursive-descent calculator unaided + 7부 chapter (다른 워킹 예제 — Scala 계산기) live. Completes the calculator trilogy (F#/Scala/+future). Agent used direct Int-returning methods rather than sealed trait ADT. All canonical tests pass (14/20/5). Actions run 26739869947 success.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`; .NET 10 on host (verified) + rustc/cargo 1.95.0 on host (verified 2026-05-28).
- [run-config]: `LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy openhands --headless --json --yolo --override-with-envs -t "<task>"`.
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; setup-asymmetry (scaffolding) disclosed; **pre-run predictions never presented as measurements** (enforced again in v1.2 audit — TD-6).
- [real measured per-call timing on this hardware]: 35B ≈ 5.3s/call (v1 F# derived; v1.2 Rust run ≈ 3.8s/call), 122B ≈ 6.3s/call. The legacy "~14–32s/call" figure is a v1 pre-run prediction, NOT a measurement — do not cite it as measured.
- [publish]: book deploys to GitHub Pages via `.github/workflows/deploy.yml` on push to `main` (do NOT modify the workflow); mdbook sidebar nav is JS-rendered from `toc-{hash}.js` — verify live sidebar there, not in root HTML. One accepted build warning: the `<char>` tag in 부록 C (TD-4).
- [v1.3 scope]: minimal Scala 3 arithmetic calculator (integer `+ - * /` with precedence and parentheses); `scala-cli`; `sealed trait Expr` ADT + hand-rolled recursive-descent parser + pattern-matching evaluator; std-only (no parser-combinator library, no parser generator). Canonical test: `2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5`. Placed as 7부 (structurally parallel to 4부/6부).

### Open tech debt (deferrable; carried forward — not yet addressed)

- **TD-2**: 부록 C event-71 → should be event-25 citation (CAPTURE-MANIFEST + 부록 C §2). ~5 min sed.
- **TD-3**: 부록 C "events 9–30 (21 events)" should be 22 (inclusive count). Trivial.
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside a code span (부록 C). The one accepted build warning.
- **TD-5**: 부록 C Sources bibliography paths not clickable.
- (v1.2 TD-6/TD-7/TD-8 were fixed during the v1.2 audit close-out — see `milestones/v1.2-MILESTONE-AUDIT.md`.)

### Candidate next milestones (no commitment)

- EXT-01: more-language worked examples (Go / Python), following the Rust/Scala precedent.
- EXT-06: 35B-vs-122B comparison on the Rust example (parallel to v1.1 for F#).
- EXT-07: cross-language "calculator in 3 languages" comparison appendix (F# / Scala / + future) — language-axis parallel to 부록 C's model comparison.
- EXT-02: English translation. EXT-03: "build your own minimal agent in F#" appendix. EXT-04: local-vs-cloud comparison. EXT-05: Rust/Scala with a framework.

### Key decisions from Phase 10 (new, 2026-06-01)

- [v1.3 capture result]: did-write-calc-unaided=YES (attempt 1). scaffold-invoked=NO. 35B wrote idiomatic Scala 3 recursive-descent calculator unaided; one genuine compile error self-corrected (private member access → sed); all three canonical tests pass (14/20/5). This completes the calculator trilogy thesis.
- [v1.3 scala idiom]: `@main def calc(args: String*)`, `class ExprParser(input: String):` with significant-indentation `:`, `if/then`, `while/do`, `match` — Scala 3 throughout, no Scala 2 slip.
- [v1.3 timing real]: task1 30.5s (avg 2.1s/call), task2 174.8s (avg 6.5s/call), task3 29.5s (avg 2.3s/call). Total active ~234.8s. The legacy `~14-32s/call` is still NOT a measurement.
- [v1.3 no ADT]: agent did not use `sealed trait Expr` (mentioned in scope note) — used direct Int-returning methods instead. Simpler but valid; chapter can note this difference from spec.

### Key decisions from Phase 11 plan 11-03 (new, 2026-06-01)

- [PUB-02 audit guard]: git diff on deploy.yml must be empty (both working-tree and vs origin) before every publish. Confirmed this plan.
- [headless push artifact]: keychain -25308 stderr lines on headless macOS are benign; confirm push success from `main -> main` ref update line only.
- [v1.3 shipped]: 7부 live at https://ohama.github.io/Openhands-Tutorial/ch07-scala-calc/intro.html. Actions run 26739869947 concluded success. toc-5eb11a0d.js confirms all 5 ch07 pages in live sidebar.

### Blockers/Concerns

None. v1.3 milestone shipped. Open tech debt (TD-2, TD-3, TD-4, TD-5) carried forward — none blocking. Candidate next milestones: EXT-01, EXT-06, EXT-07.

## Session Continuity

Last session: 2026-06-01T07:01:00Z
Stopped at: Completed 11-03-PLAN.md (PUB-02: pushed to origin/main, Actions deploy success, 7부 live verified). Phase 11 CLOSED. v1.3 SHIPPED.
Resume file: None — milestone complete. See STATE.md "Candidate next milestones" for options.
