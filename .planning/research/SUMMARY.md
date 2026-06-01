# Project Research Summary — v1.4 Planning Comparison (부록 D)

**Project:** OpenHands 아젠틱 AI 튜토리얼 — v1.4 milestone: 계획 방식 비교 A/B study
**Domain:** A/B capture study of task-planning regimes (Claude-led vs. OpenHands-native) on local Qwen 35B, published as 부록 D of the Korean mdBook
**Researched:** 2026-06-01
**Confidence:** HIGH (stack verified at runtime; metrics methodology grounded in literature; architecture confirmed against real JSONL artifacts; pitfalls confirmed against recurring audit history)

---

## Executive Summary

The v1.4 milestone is a **captured A/B comparison**, not new application code. Arm A embeds a Claude-authored numbered task plan inside the OpenHands headless prompt (`-f plan.txt` or a pre-written `.agents_tmp/PLAN.md`); the CodeActAgent executes it in one session. Arm B passes only the goal to the same CodeActAgent with "Plan your own implementation steps using the task tracker, then execute them," allowing it to self-decompose via TaskTrackerTool, whose `TaskTrackerObservation` events appear in the JSONL stream as the capturable planning artifact. There is no native OpenHands plan-file format in the headless CLI — the PlanningAgent (introduced v1.5.0, present in v1.16.0) is SDK-only and read-only; it cannot execute. All six captures (3 examples × 2 arms: F#, Rust, Scala) use the default CodeActAgent via the established `openhands --headless --json --yolo --override-with-envs` invocation.

The recommended approach is a three-phase structure: Phase 12 builds the harness and pilots both arms on the simplest example (Rust HTTP server); Phase 13 runs the full study on F# and Scala; Phase 14 writes and publishes 부록 D. The critical dependency is prompt symmetry — both arms must share an identical "control block" (goal wording, acceptance criteria, IMPORTANT bash-only constraint, canonical test inputs/outputs) with the *only* difference being whether the task decomposition is pre-supplied (Arm A) or withheld (Arm B). Any additional prose around the Arm A plan, or any difference in goal specificity, invalidates the comparison.

Key risks cluster around four honesty and methodology traps: (1) prompt-wording asymmetry — detected by a side-by-side diff of both prompts before any run; (2) timing confounds from KV-cache warmth — mitigated by restarting the litellm proxy between arms or counterbalancing run order; (3) N=1 statistical noise — addressed by n=3 runs with median+range reporting as the preferred policy, n=1 with explicit single-run hedging as the acceptable floor; and (4) the Arm A framing rule — 부록 D must ask "does an expert-authored plan help the 35B execute?" not "does Claude plan better than the 35B?", since Claude does not execute and the 35B does not plan in Arm A. Inconclusive results are valid findings and must be reported as such.

---

## Key Findings

### Recommended Stack — Arm A and Arm B Invocations

**OpenHands CLI 1.16.0 / SDK v1.21.0** (runtime-verified on this machine). Both arms use the established headless invocation pattern.

**Arm A (Claude-led, file-seeded — RECOMMENDED):**

```bash
# Step 1: Claude writes the numbered task plan
python3 generate_arm_a_plan.py --goal <example> --out /tmp/armA-<example>/plan.txt

# Step 2: OpenHands executes it in one session
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openai/qwen-35b LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy \
  OPENHANDS_WORK_DIR=/tmp/armA-<example> \
  openhands --headless --json --yolo --override-with-envs \
    -f /tmp/armA-<example>/plan.txt \
    2>err-armA.log | tee out-armA.jsonl
```

Alternative A2: pre-write `.agents_tmp/PLAN.md` with the SDK five-section structure (OBJECTIVE / CONTEXT SUMMARY / APPROACH OVERVIEW / IMPLEMENTATION STEPS / TESTING AND VALIDATION) and pass `-t "Read .agents_tmp/PLAN.md and implement all steps exactly as described."` A2 produces a visible plan file artifact in the workspace — stronger tutorial narrative.

**Arm B (OpenHands-native, self-plan):**

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openai/qwen-35b LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy \
  OPENHANDS_WORK_DIR=/tmp/armB-<example> \
  openhands --headless --json --yolo --override-with-envs \
    -t "<canonical-goal-block>
First, create your own step-by-step implementation plan using the task tracker, then execute each step." \
    2>err-armB.log | tee out-armB.jsonl
```

The phrase "create your own step-by-step implementation plan using the task tracker" nudges the agent to emit `TaskTrackerAction` events with `command: "plan"`, producing `TaskTrackerObservation` events — the capturable Arm B planning artifact.

**Hard constraints verified against CLI 1.16.0:**
- No `--agent-type` or `--plan-mode` flag exists. PlanningAgent is SDK-only, inaccessible from headless CLI.
- Do NOT use `temperature=0.0` (LiteLLM issue #4131). Use `temperature=0.2` + `seed=42` via `config.toml [llm]`.
- Do NOT use `--resume` between arms (contaminates baseline). Always fresh invocations.
- Do NOT split Arm A into per-task invocations (the v1.2/v1.3 pattern) — this defeats the study design.
- `max_message_chars=30000`: keep Arm A plans concise, or use the PLAN.md file-reference approach (A2).

### Recommended Metric Set and Repetition Policy

**P1 — Compute automatically from JSONL (must have):**

| Metric | JSONL source | Planning signal |
|--------|-------------|-----------------|
| Total TerminalAction count | `kind=="ActionEvent"`, `source=="agent"`, `tool_name=="terminal"` | Primary efficiency signal |
| Total event count | all events | Verbosity overhead |
| Wall-clock active time | last_event_ts − first_event_ts | Reader-relevant |
| Error-fix cycle count | nonzero-exit ObservationEvent → next agent ActionEvent pairs | Plan execution roughness |
| AgentErrorEvent count | `kind=="AgentErrorEvent"` | Environment-compatibility signal |
| Canonical test pass/fail | ObservationEvent content + exit_code | Objective correctness; non-negotiable |

**P2 — Compute with simple parsing (should have):**
- Avg/min/max LLM-call gap: `ObservationEvent.timestamp → next ActionEvent.timestamp` (model-thinking time, excludes bash execution) — already proven in v1.2/v1.3 manifests
- Time-to-first-correct: timestamp of first passing canonical test event minus first event timestamp

**P2 — Manual annotation (should have):**
- `oh-self-plan.md`: verbatim first planning output from Arm B JSONL (first MessageEvent or AgentThinkAction with `tool_name==""`, early in stream)
- Plan task count: Arm A = numbered step count; Arm B = visible sub-goal count in first agent message
- Canonical structure match: scaffold / write / build / test phases present (YES/NO per phase, qualitative)

**P3 — Only if token data is present in JSONL (defer if absent):**
- Total prompt + completion tokens (check for `usage` field in JSONL ObservationEvents in Phase 12 pilot before committing)

**Skip for v1.4:** wasted/abandoned action classification (too subjective at n=1); recovery-from-error rate (too few cycles per run); statistical significance testing (requires n≥8).

**Repetition policy:**
- Preferred: **n=3** per (example × arm) = 18 total runs; report `median (min–max)`, e.g. `TerminalActions: 14 (12–17)`. Do not report mean or SD at n=3 (implies false normality).
- Acceptable floor: **n=1** — label every result `(단일 실행)` and use hedged language: "In this single captured run…" not "Arm A requires fewer actions."
- Inconclusive is valid: if metric differences are within single-run variance (e.g., retries differ by 1), label the result "inconclusive — within single-run variance." This is an honest and publishable finding.
- Never use "significantly," "consistently," or "reliably" without statistical justification.

**Variance reporting format:** `median (min–max)` at n=3. Single value labeled `(단일 실행)` at n=1.

### Harness and Artifact Layout

```
.planning/milestones/v1.4-phases/
└── 12-planning-comparison-harness/
    └── captured-planning/
        ├── CAPTURE-MANIFEST.md          # top-level: study design, both arms, all 3 examples
        ├── fsharp/
        │   ├── arm-a/
        │   │   ├── logs/run.jsonl
        │   │   ├── planning-artifact/
        │   │   │   ├── claude-plan.md   # Claude's task decomposition (verbatim input)
        │   │   │   └── oh-prompt.txt    # converted prompt fed to OpenHands
        │   │   ├── final-source/
        │   │   ├── test-output.txt      # fresh host re-run of canonical tests
        │   │   └── metrics.json
        │   ├── arm-b/
        │   │   ├── logs/run.jsonl
        │   │   ├── planning-artifact/
        │   │   │   ├── oh-goal-prompt.txt
        │   │   │   └── oh-self-plan.md  # extracted from JSONL (first agent planning output)
        │   │   ├── final-source/
        │   │   ├── test-output.txt
        │   │   └── metrics.json
        │   └── comparison.json
        ├── rust/   (same structure)
        └── scala/  (same structure)

oh-workdir-planning/    # gitignored scratch
  arm-a/rust/  arm-b/rust/  arm-a/fsharp/  arm-b/fsharp/  arm-a/scala/  arm-b/scala/
```

**Key scripts:**
- `metrics_extractor.py` — parses JSONL, computes all P1/P2 metrics, emits `metrics.json`. Real JSONL schema (confirmed from v1.3 capture): `kind`, `source`, `timestamp`, `tool_name`, `action.kind`, `observation.exit_code`, `observation.content` (list of `{type,text}` dicts). **Event numbers are 1-based throughout** — use `enumerate(events, start=1)`.
- Comparison table builder — combines three `comparison.json` files into the cross-example Markdown table for 부록 D.

**Canonical pass criteria (inherited verbatim from prior milestones):**

| Example | Pass criterion |
|---------|---------------|
| F# FsLex/FsYacc | `dotnet run` → `2+3*4 = 14` (exit 0); `(2+3)*4 = 20` preferred |
| Rust HTTP server | `cargo build` exit 0; `curl` → `hello\n` HTTP 200 exit 0; no external crate deps |
| Scala 3 calculator | `scala-cli run Calc.scala -- "2+3*4"` → `14`; `-- "(2+3)*4"` → `20`; `-- "10-3-2"` → `5` |

### Architecture Approach

The harness reuses the established OpenHands headless capture pipeline verbatim (invocation pattern, JSONL tee, honesty gate, `captured-*/` commit structure) and adds two new components: the Arm A prompt converter and the Arm B self-plan extractor.

The converter is a **mechanical** operation only: Claude's plan structure → numbered items in the OH prompt with the shared control block prepended, verbatim text, no additions, no rewording. Any editorial judgment during conversion confounds the comparison (converter doing planning work = Arm A effectively has two planners, not one). The self-plan extractor scans the first 5–10 events in the Arm B JSONL for the first `MessageEvent` or `AgentThinkAction` (`tool_name==""`) and saves its content verbatim as `oh-self-plan.md`.

**Major components:**
1. **Arm A prompt builder** — Claude's task decomposition → single OH-consumable prompt; control block identical to Arm B (goal, constraints, canonical tests)
2. **Arm B prompt builder** — control block + "Plan your own steps using the task tracker, then execute"
3. **Headless invocation** — one invocation per arm per example; strict per-arm-per-example workspace isolation
4. **Honesty gate** — every ActionEvent must have `source=agent`; the initial `source=user` MessageEvent is excluded from the check; pre-run workspace snapshot (file listing or hash) detects out-of-band edits invisible to the gate
5. **metrics_extractor.py** — produces `metrics.json` per arm per example; 1-based event indices throughout
6. **Comparison table builder** — `comparison.json` per example + cross-example Markdown table for 부록 D

**Single-session constraint:** Both arms are ONE OpenHands invocation each. Multi-invocation splits (the v1.2/v1.3 per-task pattern) would give Arm A multiple sessions while Arm B has one — structurally unfair and defeating the study design.

### Critical Pitfalls

**Critical — invalidate the comparison if triggered:**

1. **Prompt-wording asymmetry** — If anything beyond the plan itself differs between Arm A and Arm B prompts (tone, specificity, sentence count, goal wording), the comparison measures prompt quality not planning regime. Fix: write both prompts side by side, do a literal diff, strip any Arm A line not attributable to the plan content itself. Address in Phase 12 before any run.

2. **N=1 conclusions without hedging** — "Arm A: 2 retries, Arm B: 4 retries" is a single-run observation, not a finding. Single-run pass@1 estimates vary ±2.2–6.0pp even at temperature 0 on frontier models (arXiv 2602.07150). Fix: n=3 preferred; n=1 requires explicit single-run caveat on every metric. Never use "significantly," "consistently," or "reliably" at n=1.

3. **Timing confound from KV-cache warmth** — Whichever arm runs second benefits from prefix-caching (confirmed `cached_tokens` in usage). Fix: restart litellm proxy between each arm pair, or counterbalance run order across examples (Arm B first for F#, Arm A first for Rust, Arm B first for Scala). Report `cached_tokens` per call if available. Address in Phase 12 protocol design.

4. **Arm A framing rule: "does an expert plan help the 35B execute" NOT "Claude plans better"** — Claude does not execute; the 35B does not plan in Arm A. The research question is whether providing an expert-authored plan changes the 35B's execution quality. Fix: 부록 D opening paragraph must state the correct research question. Audit checklist item. If Arm A wins: "The 35B executed more efficiently with an expert-authored plan." If Arm B wins or ties: "The 35B's native self-planning was as effective as an externally authored plan."

**Important — significant quality risk:**

5. **Converter doing planning work** — If the Arm A conversion adds detail, restructures subtasks, or clarifies ambiguities beyond format normalization, Arm A has two planners. Fix: "each Claude subtask → one numbered item, verbatim text, no additions"; document the conversion rule in the manifest; archive both the original plan and the converted prompt.

6. **Workspace-state leakage between arms** — Arm B running in the same directory as Arm A inherits build artifacts or compiler caches. Even `target/` from a prior Cargo build makes Arm B's first `cargo build` spuriously faster. Fix: strict per-arm-per-example workspace directories; pre-run workspace-empty verification logged in manifest.

7. **Carried honesty discipline: source=agent gate on all six JSONLs** — The initial `source=user` MessageEvent in Arm A (plan delivery) is correct and expected — do not flag it. Manual filesystem edits after plan delivery are invisible to the gate; the pre-run workspace snapshot catches them.

8. **Manifest event-numbering drift (recurring tech debt)** — v1.2 and v1.3 both had off-by-one errors (TD-7, TD-8, TD-10) from mixing 0-based Python enumerate with 1-based JSONL line numbers. Fix: manifest cites **1-based event numbers** (JSONL line N = event #N); `metrics_extractor.py` uses `enumerate(events, start=1)`; manifest header states the convention.

9. **`~14–32s/call` is a pre-run prediction, never a measurement** — Cited incorrectly as measurement data in two prior milestones (TD-6, TD-10). For v1.4 timing baselines, use derived figures from real JSONL: ~3.8s/call (v1.2 Rust), ~5.0s/call (v1.3 Scala). Grep chapter text for `~14–32s/call` at audit time; must be labeled "pre-run prediction, not measured" if present.

---

## Implications for Roadmap

Suggested phase structure: 3 phases (12, 13, 14).

### Phase 12: Harness + Rust Pilot (both arms)

**Rationale:** Establish the harness and validate that both arms capture cleanly before committing to 4 more invocations. Rust is the correct pilot: one source file, trivial `curl` test, no grammar files, fastest to run (~15–25 min estimated).
**Delivers:**
- Both arm prompt templates (control block + plan vs. goal), reviewed by side-by-side diff before any invocation
- `oh-workdir-planning/` gitignore entry; per-arm-per-example workspace directories initialized empty
- Arm A Rust invocation + JSONL captured; Arm B Rust invocation + JSONL captured
- `metrics_extractor.py` validated against both Rust JSONLs
- `captured-planning/rust/arm-a/metrics.json`, `arm-b/metrics.json`, `rust/comparison.json` committed
- Honesty gate PASS on both Rust JSONLs
**Capture gate:** Both Rust `metrics.json` committed with `honesty_gate = PASS` AND `canonical_tests.curl_hello.pass` recorded (PASS or FAIL, not null).
**Avoids:** Pitfalls 1 (prompt symmetry diff), 6 (workspace isolation), 3 (cache warmth — litellm restart documented).
**Research flag:** If Arm B does not emit `TaskTrackerObservation` events, adjust the Arm B prompt phrasing and re-pilot before proceeding to Phase 13.

### Phase 13: F# and Scala Full Study (both arms, same-day per language)

**Rationale:** Blocked on Phase 12 pilot gate. F# is the hardest (FsLex/FsYacc domain); Scala is intermediate. Each language's two arms must be captured in the same session (same day, same versions) to avoid inter-run drift.
**Delivers:**
- Arm A and Arm B invocations for F# (same-day capture)
- Arm A and Arm B invocations for Scala (same-day capture)
- All six `metrics.json` files (Rust from Phase 12 + F# + Scala)
- All three `comparison.json` files
- `captured-planning/CAPTURE-MANIFEST.md` (top-level study manifest with version block)
- Honesty gate PASS on all six JSONLs
**Capture gate:** All six `metrics.json` committed with `honesty_gate = PASS` AND all `canonical_tests` populated (not null — PASS or FAIL, but not null). Failure on canonical tests is valid data.
**Avoids:** Pitfall 10 (inter-run drift — same-day per language; manifest version block required); Pitfall 4 (cherry-picking — first run is the run, infrastructure re-runs disclosed); Pitfall 7 (conversion documented before running).
**Research flag:** F# arms may both fail canonical test — valid finding, report as FAIL with agent output. Pre-confirm Claude's F# plan explicitly covers `fslex`/`fsyacc` invocation.

### Phase 14: 부록 D Chapter + Publish

**Rationale:** Blocked on Phase 13 full-study capture gate. Chapter written verbatim from committed capture data — no fabrication, no retrofitting.
**Delivers:**
- `src/appendix-d-planning-comparison.md`: comparison table (example × metric × arm-a × arm-b × delta), per-arm planning artifact excerpts, qualitative observations, honest interpretation of mixed/inconclusive results
- `src/SUMMARY.md` updated to wire 부록 D after 부록 C
- `mdbook build` clean; push to main; verify live on GitHub Pages
**Avoids:** Pitfall 8 (Arm A framing — opening paragraph states correct research question); Pitfall 3 (N=1 caveat on every metric table or n=3 range reporting); Pitfall 12 (`~14–32s/call` grep at audit time).
**Research flag:** Standard patterns (established mdBook + Pages deploy pipeline); no research-phase needed.

### Phase Ordering Rationale

- **Pilot gates the full study.** 4 additional invocations at 15–40 min each = 1–3 hours. A prompt-format bug discovered after all 6 runs requires scrapping and re-running. Piloting on Rust (Phase 12) surfaces issues while only 2 invocations have been sunk.
- **Both arms per language must be captured in one session.** Across-day version drift (Pitfall 10) is eliminated by this constraint. Phase structure enforces it: Phase 12 = Rust both arms same day; Phase 13 = F# both arms same day, then Scala both arms same day.
- **Chapter (Phase 14) strictly after capture gate (Phase 13).** Writing prose before all captures are committed is the direct path to fabrication — the project's core honesty discipline prohibits it.
- **Canonical goal wording must be finalized in Phase 12 before any arm is run.** Post-hoc changes to goal wording require re-running both arms.

### Research Flags

Phases needing deeper investigation:
- **Phase 12 (pilot):** TaskTracker activation on Qwen 35B at the specific prompt phrasing is unverified. If Arm B does not emit `TaskTrackerAction`/`TaskTrackerObservation` events, the Arm B planning artifact falls back to the first agent MessageEvent — investigate prompt phrasing during pilot before committing to the full study.
- **Phase 13 (F#):** FsLex/FsYacc domain knowledge is likely to challenge Arm B. Pre-confirm Claude's F# plan covers `fslex`/`fsyacc` invocation explicitly so Arm A is not also blocked.

Phases with standard patterns (skip research):
- **Phase 14** (mdBook authoring + Pages deploy): established pipeline from v1.0–v1.3.
- **Metrics extraction** (Phases 12+13): JSONL schema confirmed from real v1.3 captures; `metrics_extractor.py` fully specified in ARCHITECTURE.md.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | CLI 1.16.0 and SDK v1.21.0 verified at runtime; CLI flags confirmed via `--help`; Planning Agent and TaskTrackerTool confirmed against GitHub API source; `config.toml` temperature/seed confirmed. `LLM_TEMPERATURE`/`LLM_SEED` via `--override-with-envs` is LOW — use `config.toml` instead. |
| Features (study design) | HIGH | Metric methodology grounded in arXiv 2602.07150, 2512.06710, 2511.00872, Anthropic eval blog. Repetition norms (n=3 preferred, n=1 floor) consistent with prior milestones. Canonical pass criteria inherited verbatim from v1.2/v1.3. |
| Architecture | HIGH | JSONL schema confirmed by direct inspection of v1.3 captured JSONL. Invocation pattern proven across 4 prior milestones. `metrics_extractor.py` grounded in real event types. Single-session constraint justified by OpenHands architecture. |
| Pitfalls | HIGH (critical); MEDIUM (edge cases) | Prompt asymmetry, N=1 noise, timing confound, Arm A framing are confirmed failure modes from methodology literature and project audit history. TaskTracker behavior on Qwen 35B at the specific prompt is unverified (MEDIUM). |

**Overall confidence:** HIGH for study design and harness; MEDIUM for the prediction that Arm B reliably self-plans via TaskTracker — the key empirical unknown that Phase 12 pilot is designed to resolve.

### Gaps to Address

- **TaskTracker activation on Qwen 35B:** Does "using the task tracker" reliably trigger `TaskTrackerAction` events in Arm B? Test in Phase 12 pilot; adjust the Arm B prompt phrasing if needed before proceeding to Phase 13.
- **F# failure scenario:** If both arms fail the F# canonical test, the comparison has two FAIL cells for F#. Valid data; must be anticipated and reported honestly. Pre-confirm Claude's F# plan covers `fslex`/`fsyacc` invocation.
- **Token data in JSONL:** Whether `usage.prompt_tokens`/`usage.completion_tokens` appear in the JSONL ObservationEvents is unverified — check in Phase 12 pilot before committing to reporting P3 metrics.
- **LLM_TEMPERATURE/LLM_SEED via env var:** Inferred from naming convention but not runtime-tested. Use `config.toml [llm]` for temperature and seed.
- **Arm A prompt length vs. `max_message_chars=30000`:** Verify Claude's F# plan (5 tasks) stays within the character limit when passed via `-f` or `-t`.

---

## Sources

### Primary (HIGH confidence — runtime-verified or GitHub API source-read)
- `openhands --version` and `openhands --help` on host — CLI 1.16.0; confirmed flags
- `OpenHands SDK v1.21.0` startup banner — SDK version
- `openhands-tools/openhands/tools/preset/planning.py` (GitHub API) — `get_planning_agent()`, `PlanningFileEditorTool`, `.agents_tmp/PLAN.md` path
- `frontend/src/types/v1/core/base/action.ts`, `observation.ts`, `common.ts` (GitHub API) — `TaskTrackerAction`, `TaskTrackerObservation`, `TaskItem` structure
- `tests/sdk/config/test_llm_config.py` (GitHub API) — `temperature`, `seed`, `top_p` in LLM config
- `config.template.toml` (GitHub API) — `[llm]` section; temperature/seed keys
- `tests/sdk/conversation/test_repo_root_project_skills.py` (GitHub API) — AGENTS.md injection mechanism
- `examples/01_standalone_sdk/24_planning_agent_workflow.py` (GitHub API) — two-phase SDK pattern; PLAN.md path
- Real JSONL schema: v1.3 captured `task3-buildtest.jsonl` (2026-06-01, direct inspection)
- v1.2 CAPTURE-MANIFEST.md — LLM-call gap timing method (~3.8s/call derived); error-fix cycle definition
- v1.3 CAPTURE-MANIFEST.md — 1-based event-numbering convention; Scala canonical criteria; ~5.0s/call derived

### Secondary (MEDIUM confidence — methodology literature)
- arXiv 2602.07150 — single-run pass@1 variance (±2.2–6.0pp at temperature 0); pass@k vs pass^k framework
- arXiv 2512.06710 — minimum n for reliable ICC estimates (n≥8 simple, n≥32 complex reasoning)
- arXiv 2511.00872 — three-dimension agent evaluation framework; same-LLM fairness control; trajectory steps as primary efficiency metric
- Anthropic Engineering — "Demystifying Evals for AI Agents" — pass@k, clean-environment protocol, multi-trial recommendation
- arXiv 2410.22457 — five trajectory-quality metrics beyond success rate; granularity axis for task decomposition
- v1.2/v1.3 milestone audits — TD-6 (prediction-as-measurement), TD-7/TD-8 (off-by-one event indices), TD-9/TD-10 (metric provenance) — direct evidence for Pitfalls 12 and 11
- v1 Phase 3 history — "attempt 1 rejected; manual fix found in workspace" — direct precedent for cherry-picking pitfall

### Tertiary (LOW confidence — inferred, needs runtime validation)
- `LLM_TEMPERATURE`/`LLM_SEED` as env var names via `--override-with-envs` — consistent with naming convention, not runtime-tested; use `config.toml`
- TaskTrackerAction emission rate on Qwen 35B at the "using the task tracker" prompt phrasing — unverified; Phase 12 pilot resolves this

---

*Research completed: 2026-06-01*
*Milestone: v1.4 Planning Comparison (부록 D)*
*Ready for roadmap: yes — 3 phases (12/13/14) with capture gates and pilot-first discipline*
