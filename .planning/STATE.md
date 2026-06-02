# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-01 — v1.4 Planning Comparison started)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run real programs. The book teaches via REAL captured runs: v1 F# calculator (35B), v1.1 122B comparison (부록 C), v1.2 Rust HTTP server (6부), v1.3 Scala calculator (7부), v1.4 planning comparison A/B (부록 D).
**Current focus:** v1.4 Planning Comparison — Phase 13 (F#+Scala full study). 13-02 COMPLETE (all 18 live runs captured). Next: 13-03 (metrics_extractor + honesty gate + comparison) then 13-04 (부록 D).

## Current Position

Milestone: v1.4 (Planning Comparison) — IN PROGRESS. Phase 12 done; Phases 13–14 remain.
Phase: 13 — Full Study F#+Scala + Analysis — IN PROGRESS (2/4 plans complete).
Plan: 13-01 COMPLETE. 13-02 COMPLETE. 13-03 (metrics+comparison), 13-04 (부록 D) next.
Status: All 18 JSONL runs captured (F# 6 + Scala 6 + Rust 6). PCAP-01 satisfied. KEY RESULTS: F# arm-a 1/3 PASS (OOD); F# arm-b 0/3 PASS (OOD); Scala arm-a 3/3 PASS; Scala arm-b 2/3 PASS + 1 PARTIAL; Rust both arms 3/3 PASS. Ready for 13-03 metrics extraction.
KEY v1.4 FINDINGS (updated from 13-02): (1) F# is OOD for 35B: arm-b 0/3 PASS, arm-a 1/3 PASS (claude plan helped in one run but OOD dominated). (2) Scala in-distribution: arm-a 3/3, arm-b ~3/3 PASS. (3) Rust in-distribution: both arms 3/3 PASS. (4) Arm B consistently self-plans via task_tracker across all examples. (5) Idle-settle detection: runs can continue after 3-poll idle; final event count is authoritative.
Last activity: 2026-06-02 — Phase 13 plan 02 executed; 18 live 35B runs captured across F#/Scala/Rust.

Progress: ✅ v1 + v1.1 + v1.2 + v1.3 shipped (11 phases, 35 plans). 🚧 v1.4: Phase 12 ✓ (3/3); Phase 13: 2/4 plans ✓; Phase 14 next.
Live: https://ohama.github.io/Openhands-Tutorial/ (worked examples: 4부 F# calc · 6부 Rust server · 7부 Scala calc · 부록 C model comparison)

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial + 35B captured run of F# FsLex/FsYacc calculator. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C 35B-vs-122B comparison + UX callouts. See `milestones/v1.1-ROADMAP.md`.
- **v1.2 Rust Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Rust HTTP server (6부) — unaided. See `milestones/v1.2-ROADMAP.md`.
- **v1.3 Scala Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Scala 3 calculator (7부) — unaided, one self-corrected compile error. Completes the calculator trilogy; confirms capability is domain-distribution, not model size. See `milestones/v1.3-ROADMAP.md`.
- **v1.4 Planning Comparison** (in progress — started 2026-06-01): 3 phases planned (12/13/14), 0 plans complete. Arm A (Claude-authored plan → 35B executes) vs. Arm B (35B self-plans + executes) across F#/Rust/Scala; published as 부록 D.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`. Verified host toolchains: .NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0 (Scala 3.8.3) + JDK 17.
- [run-config]: `OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy OPENHANDS_WORK_DIR=<wd> openhands --headless --json --yolo --override-with-envs -t "<task>"`. Capture pattern: background the run, `tee` to per-task JSONL, poll for settle (FinishAction/idle). The CLI exits 0 regardless of task success — judge from the JSONL, not the exit code.
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; `source=agent` on every ActionEvent (mechanical python3 gate before any commit); scaffolding disclosed; **pre-run predictions never presented as measurements**.
- [real measured per-call timing]: 35B ≈ 5.3s/call (v1 F# derived) / 3.8s/call (v1.2 Rust) / ~5.0s/call (v1.3 Scala); 122B ≈ 6.3s/call. The legacy `~14–32s/call` figure is a v1 pre-run PREDICTION, NOT a measurement.
- [capture event-numbering]: chapters cite the CAPTURE-MANIFEST's 1-based event numbers, NOT RUN-NOTES 0-based scratchpad positions (recurring tech debt — v1.2 TD-7/TD-8; held correct in v1.3).
- [35B capability]: domain-distribution, not size — fails OOD DSLs (FsLex) but writes in-distribution languages (Rust std, Scala 3) unaided; errors it makes are teachable in-distribution mistakes (borrow-checker, access modifiers).
- [publish]: book deploys to GitHub Pages via `.github/workflows/deploy.yml` on push to `main` (do NOT modify); mdbook sidebar nav is JS-rendered from `toc-{hash}.js` — verify live sidebar there. One accepted build warning: the `<char>` tag in 부록 C (TD-4).

### v1.4 decisions (new this milestone)

- [v1.4 study design]: One OpenHands invocation per arm per example (single-session constraint); BOTH arms use the default CodeActAgent via established headless CLI (no SDK PlanningAgent); Arm A uses `-f plan.txt` or pre-written `.agents_tmp/PLAN.md`; Arm B prompt: control block + "Plan your own implementation steps using the task tracker, then execute each step."
- [v1.4 prompt symmetry]: Arm A and Arm B prompts share an identical control block (goal wording, constraints, canonical tests); the ONLY difference is whether a numbered task plan is supplied (Arm A) or withheld (Arm B). A literal diff is mandatory before any invocation.
- [v1.4 workspace isolation]: `oh-workdir-planning/` is gitignored; each arm gets its own empty directory; workspace empty verified before each run.
- [v1.4 run order counterbalancing]: litellm proxy restarted between arms OR run order counterbalanced (e.g., Arm B first for F#, Arm A first for Rust, Arm B first for Scala) to mitigate KV-cache prefix warmth.
- [v1.4 repetition policy]: n=3 preferred (median + min–max); n=1 acceptable floor with explicit `(단일 실행)` label on every metric. Never use "significantly," "consistently," or "reliably" at n=1.
- [v1.4 metrics]: P1 (auto from JSONL): TerminalAction count, total event count, wall-clock active time, error-fix cycle count, AgentErrorEvent count, canonical-test pass/fail. P2: avg/min/max LLM-call gap, time-to-first-correct, qualitative plan comparison. P3 (only if `usage` in JSONL): token counts — confirm in Phase 12 pilot before committing to P3.
- [v1.4 framing rule]: 부록 D frames the study as "does an expert-authored plan help the 35B execute?" — NOT "Claude plans better." Inconclusive/mixed results are valid findings, reported honestly.
- [v1.4 artifact layout]: `captured-planning/` under `.planning/milestones/v1.4-phases/12-planning-comparison-harness/`; structure per example: `arm-a/` and `arm-b/` each with `logs/run.jsonl`, `planning-artifact/`, `final-source/`, `test-output.txt`, `metrics.json`; plus `comparison.json` per example; plus top-level `CAPTURE-MANIFEST.md`.
- [v1.4 open unknowns — to resolve in Phase 12 pilot]: (1) Does the Qwen 35B emit `TaskTrackerObservation` events at the chosen Arm B prompt phrasing? (2) Is `usage` data (prompt/completion tokens) present in the JSONL ObservationEvents? — metrics_extractor.py now emits task_tracker_observation_count and usage_present to answer both automatically.
- [12-01 symmetry evidence]: PROMPT-DIFF-rust.txt records control-block diff with CONTROL-BLOCK SYMMETRY: PASS. Literal diff saved before any live run.
- [12-01 Arm A conversion]: Mechanical — v1.2 task1/2/3 → 3 numbered single-session steps. No new planning detail. No scaffolded source.
- [12-01 extractor 1-based]: metrics_extractor.py uses enumerate(events, start=1) throughout; ARCHITECTURE.md 0-based snippet explicitly converted. Self-validated with clean+dirty fixtures.
- [13-01 F# canonical command]: `dotnet run -- "<expr>"` — frozen; do not change before any arm is run.
- [13-01 Scala canonical command]: `scala-cli run Calc.scala -- "<expr>"` — frozen; do not change before any arm is run.
- [13-01 F# fairness rule]: Arm A claude-plan DESCRIBES fslex/fsyacc build wiring (FixLineDirectives, compile order) as required steps but embeds NO .fsproj XML, NO Lexer.fsl, NO Parser.fsy, NO Program.fs source. Both arms write all source themselves. F# may FAIL in both arms (OOD) — valid data.
- [13-01 symmetry evidence]: PROMPT-DIFF-fsharp.txt + PROMPT-DIFF-scala.txt both end with CONTROL-BLOCK SYMMETRY: PASS. Literal diffs saved before any live run.
    - [13-02 idle-settle]: Idle-settle (3 consecutive polls with same last_ts) is reliable but runs CAN continue after apparent settle; final event count in committed JSONL is authoritative.
    - [13-02 Rust prompt tokens]: Phase-12 Rust prompts use hardcoded workspace paths, NOT `__WORKDIR__` tokens. Top-up runs must use `sed "s#$OLD_PATH#$NEW_PATH#g"`.
    - [13-02 F# result]: arm-a 1/3 PASS, arm-b 0/3 PASS. OOD confirmed at n=3. For 부록 D: Arm A run-1 PASS shows claude plan CAN help navigate OOD task; but 5/6 runs overall failed on FsLex/FsYacc.
    - [13-02 Scala result]: arm-a 3/3 PASS, arm-b ~3/3 PASS (2 PASS + 1 PARTIAL-PASS). In-distribution; both arms broadly succeed.
    - [13-02 Rust result]: both arms 3/3 PASS. In-distribution; highly reliable.

### Open tech debt (deferrable; carried forward — not yet addressed)

- **TD-2**: 부록 C event-71 → should be event-25 citation. ~5 min sed.
- **TD-3**: 부록 C "events 9–30 (21 events)" should be 22 (inclusive count). Trivial.
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside a code span (부록 C). The one accepted build warning.
- **TD-5**: 부록 C Sources bibliography paths not clickable.
- (v1.2 TD-6/7/8 and v1.3 TD-9/10 were fixed during their respective milestone audits.)

### Candidate next milestones (no commitment)

- EXT-07: cross-language "calculator in 3 languages" comparison appendix (F# / Scala / + future) — now natural since the trilogy is complete.
- EXT-01: more-language worked examples (Go / Python), following the precedent.
- EXT-06: 35B-vs-122B comparison on the Rust or Scala example.
- EXT-08: extend the planning comparison to 122B, or add the SDK `PlanningAgent` as a third arm.
- EXT-02: English translation. EXT-03: "build your own minimal agent" appendix. EXT-04: local-vs-cloud comparison. EXT-05: Rust/Scala with a framework.

### Blockers/Concerns

None. Host toolchains verified (.NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0 + JDK 17). LLM proxy serving qwen-35b/122b/local. Phase 12 is unblocked.

## Session Continuity

Last session: 2026-06-02
Stopped at: Completed 13-02-PLAN.md (all 18 live 35B runs captured + RUN-NOTES + SUMMARY).
Resume file: None — next: run 13-03 (metrics_extractor.py on all 18 JSONLs, honesty gate, comparison.json, CAPTURE-MANIFEST.md).
