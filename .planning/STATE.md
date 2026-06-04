# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-04 — v1.4 shipped; between milestones)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run real programs. The book teaches via REAL captured runs: v1 F# calculator (35B), v1.1 122B comparison (부록 C), v1.2 Rust HTTP server (6부), v1.3 Scala calculator (7부), v1.4 planning comparison A/B (부록 D).
**Current focus:** BETWEEN MILESTONES. v1.4 Planning Comparison SHIPPED + archived 2026-06-04 (tag `milestone-v1.4`). Next: run `/gsd:new-milestone` to scope the next version (open candidates in "Candidate next milestones" below + MILESTONES.md "What's next").

## Current Position

Milestone: v1.4 (Planning Comparison) — ✅ SHIPPED + ARCHIVED 2026-06-04. Between milestones; ready to plan the next one.
Phase: none active (Phases 12–14 archived to `milestones/v1.4-phases/`). `/gsd:new-milestone` starts the next cycle (questioning → research → requirements → roadmap).
Status: v1.4 live (부록 D, HTTP 200). Milestone audit PASSED (12/12 requirements, integration 6/6) → archived `milestones/v1.4-MILESTONE-AUDIT.md`. ROADMAP collapsed; REQUIREMENTS archived + reset; phases archived.
v1.4 RESULT (one-liner; full detail in milestones/v1.4-ROADMAP.md + MILESTONES.md): an expert-authored plan helps the 35B mainly on the OOD task (F# Arm A 1/3 vs Arm B 0/3); in-distribution it self-plans just as well (Scala 3/3 vs 2/3+PARTIAL; Rust 3/3 tie). Distribution, not size — now on the planning axis.
Last activity: 2026-06-04 — v1.4 milestone completed and archived (MILESTONES/ROADMAP/REQUIREMENTS/PROJECT/STATE updated; tag milestone-v1.4).

Progress: ✅ v1 + v1.1 + v1.2 + v1.3 + v1.4 shipped (14 phases, 38 plans complete). Between milestones.
Live: https://ohama.github.io/Openhands-Tutorial/ (worked examples: 4부 F# calc · 6부 Rust server · 7부 Scala calc · 부록 C model comparison · 부록 D planning comparison)

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial + 35B captured run of F# FsLex/FsYacc calculator. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C 35B-vs-122B comparison + UX callouts. See `milestones/v1.1-ROADMAP.md`.
- **v1.2 Rust Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Rust HTTP server (6부) — unaided. See `milestones/v1.2-ROADMAP.md`.
- **v1.3 Scala Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Scala 3 calculator (7부) — unaided, one self-corrected compile error. Completes the calculator trilogy; confirms capability is domain-distribution, not model size. See `milestones/v1.3-ROADMAP.md`.
- **v1.4 Planning Comparison** (shipped 2026-06-04): 3 phases (12/13/14), 10 plans. Arm A (Claude-authored plan → 35B executes) vs. Arm B (35B self-plans + executes) across F#/Rust/Scala; published as 부록 D. Key findings: F# OOD both arms fail mostly; Rust/Scala in-distribution both arms succeed. See `milestones/v1.4-ROADMAP.md`.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`. Verified host toolchains: .NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0 (Scala 3.8.3) + JDK 17.
- [run-config]: `OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy OPENHANDS_WORK_DIR=<wd> openhands --headless --json --yolo --override-with-envs -t "<task>"`. Capture pattern: background the run, `tee` to per-task JSONL, poll for settle (FinishAction/idle). The CLI exits 0 regardless of task success — judge from the JSONL, not the exit code.
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; `source=agent` on every ActionEvent (mechanical python3 gate before any commit); scaffolding disclosed; **pre-run predictions never presented as measurements**.
- [real measured per-call timing]: 35B ≈ 5.3s/call (v1 F# derived) / 3.8s/call (v1.2 Rust) / ~5.0s/call (v1.3 Scala); 122B ≈ 6.3s/call. The legacy `~14–32s/call` figure is a v1 pre-run PREDICTION, NOT a measurement.
- [capture event-numbering]: chapters cite the CAPTURE-MANIFEST's 1-based event numbers, NOT RUN-NOTES 0-based scratchpad positions (recurring tech debt — v1.2 TD-7/TD-8; held correct in v1.3).
- [35B capability]: domain-distribution, not size — fails OOD DSLs (FsLex) but writes in-distribution languages (Rust std, Scala 3) unaided; errors it makes are teachable in-distribution mistakes (borrow-checker, access modifiers).
- [publish]: book deploys to GitHub Pages via `.github/workflows/deploy.yml` on push to `main` (do NOT modify); mdbook sidebar nav is JS-rendered from `toc-{hash}.js` — verify live sidebar there. One accepted build warning: the `<char>` tag in 부록 C (TD-4).

### v1.4 decisions (archived — full detail in milestones/v1.4-phases/ + milestones/v1.4-ROADMAP.md)

v1.4 (Planning Comparison) shipped; its phase-specific decisions are archived. The reusable distillation that carries forward:
- [v1.4 method, reusable]: A/B planning capture = identical control block + literal symmetry diff (`CONTROL-BLOCK SYMMETRY: PASS`) before any run; one headless CodeActAgent invocation per arm; arm-isolated gitignored workspaces; counterbalanced run order; n=3 (median + min–max), `(단일 실행)` only for single-run prose; judge from JSONL never the exit code. Framing: "does an expert plan help the 35B execute?" — not "Claude plans better."
- [v1.4 result, carry-forward]: distribution-not-size holds on the **planning axis** — an expert plan helps mainly on the OOD task (F#); in-distribution (Rust/Scala) the 35B self-plans just as well via its TaskTracker (Arm B emits tracker steps; Arm A 0). No token `usage` in the JSONL → no token metrics. Timing has a cache/run-order confound — never a planning-quality signal.
- [v1.4 tooling note]: the canonical-test detector in `metrics_extractor.py` needs genuine run-command matching ("any successful run" semantics), NOT first-substring-match — the first-match version produced false-FAILs/nulls and was fixed mid-milestone (`b7a74b9`). The patched copy + `aggregate_metrics.py` live in `milestones/v1.4-phases/13-full-study-fsharp-scala-analysis/`. (Superintends/replaces the earlier "do not fix the extractor" note, which was pre-fix.)

### Open tech debt (deferrable; carried forward — not yet addressed)

- **TD-2**: 부록 C event-71 → should be event-25 citation. ~5 min sed.
- **TD-3**: 부록 C "events 9–30 (21 events)" should be 22 (inclusive count). Trivial.
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside a code span (부록 C). The one accepted build warning.
- **TD-5**: 부록 C Sources bibliography paths not clickable.
- **TD-11** (v1.4): the 13-04 gate-closing assertion checks `canonical_tests` on the *aggregate* metrics.json, where canonical lives under `canonical_tests_aggregate` (so the null-check ran over `{}` and passed vacuously). Underlying data is sound — all 18 per-run files have canonical fully populated (0/56 null) and match RUN-NOTES — but the aggregate-level assertion is a no-op. If the gate is re-used, point it at `canonical_tests_aggregate` (or the per-run files). Cosmetic; gate substantively correct.
- **TD-12** (v1.4): `__pycache__/` is not in `.gitignore`; running metrics_extractor.py creates `.planning/phases/*/__pycache__/`. Add `__pycache__/` to `.gitignore`. Trivial.
- **TD-13** (v1.4, cosmetic): in 3 Scala cells the chapter/CAPTURE-MANIFEST cite the final batch-test event (#39 / #31 / #129) while the extractor's `metrics-run-N.json` `event_index` recorded the earlier individual-PASS event (#31 / #23,#25 / #57). Both are valid exit-0 PASS events; PASS/FAIL identical; chapter↔manifest self-consistent (chapter cites the manifest per convention). No data error. If reconciled, align the extractor to record the last/batch run. Found in v1.4 milestone audit.
- (v1.2 TD-6/7/8 and v1.3 TD-9/10 were fixed during their respective milestone audits.)

### Roadmap Evolution

- Phase 15 added (post-v1.4 follow-up): Arm C (GSD mechanical) — Rust capture. ✅ Complete 2026-06-04; published 부록 D §6.
- Phase 16 added (post-v1.4 follow-up): Arm C (GSD mechanical) — F# + Scala capture + comparison with Phase 13 Arm A/B. Not planned yet (`/gsd:plan-phase 16`).

### Candidate next milestones (no commitment)

- EXT-07: cross-language "calculator in 3 languages" comparison appendix (F# / Scala / + future) — now natural since the trilogy is complete.
- EXT-01: more-language worked examples (Go / Python), following the precedent.
- EXT-06: 35B-vs-122B comparison on the Rust or Scala example.
- EXT-08: extend the planning comparison to 122B, or add the SDK `PlanningAgent` as a third arm.
- EXT-02: English translation. EXT-03: "build your own minimal agent" appendix. EXT-04: local-vs-cloud comparison. EXT-05: Rust/Scala with a framework.

### Blockers/Concerns

None. Host toolchains verified (.NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0 + JDK 17). LLM proxy serving qwen-35b/122b/local. Phase 12 is unblocked.

## Session Continuity

Last session: 2026-06-04
Stopped at: v1.4 milestone COMPLETED + ARCHIVED. ROADMAP collapsed (v1.4 → `<details>` + archive link); REQUIREMENTS archived to milestones/v1.4-REQUIREMENTS.md and reset; audit moved to milestones/v1.4-MILESTONE-AUDIT.md; phases 12–14 moved to milestones/v1.4-phases/; MILESTONES.md + PROJECT.md updated; tag `milestone-v1.4`.
Resume file: None — between milestones. Next: `/gsd:new-milestone` (questioning → research → requirements → roadmap). Open candidates in "Candidate next milestones" + MILESTONES.md "What's next".
Note: local branch is ahead of origin/main by the planning-doc commits since `7d5783a` (the live deploy); push when convenient — the live site does not depend on them.
