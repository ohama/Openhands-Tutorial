# Feature Research — v1.4 Planning Comparison Study Design

**Domain:** AI-planning A/B comparison study (tutorial chapter research)
**Milestone:** v1.4 — 부록 D "Claude-led vs OpenHands-native task planning"
**Researched:** 2026-06-01
**Confidence:** HIGH (metrics methodology); MEDIUM (repetition norms for micro-studies)

---

## Reframing

For v1.4 the "features" are **study-design elements**: outcome metrics, fairness controls,
plan-characterisation methods, canonical pass criteria, and variance-reporting norms. Each
element feeds what the capture harness must record, what the analysis script must compute,
and what the chapter must honestly disclose.

---

## Table Stakes (Must-Have Study-Design Features)

These are the minimum elements a credible A/B comparison chapter needs. Missing any of them
makes the comparison either unfair or uninterpretable.

### Outcome Metrics

| Metric | Why It Is Table Stakes | Complexity | Notes |
|--------|------------------------|------------|-------|
| **Final canonical-test pass/fail** | The only objective correctness signal. A planning regime that fails the test has produced nothing usable, regardless of efficiency. | LOW | Already defined per example: F# `2+3*4=14`; Rust `curl→hello (exit 0)`; Scala `14/20/5`. Extractable from existing JSONL (TerminalObservation content + exit_code). |
| **Total TerminalAction count** | Primary efficiency signal — how many bash/terminal actions the agent took. Lower = more directed execution. Already extracted from JSONL in prior milestones. | LOW | Count events where `type=="action"` and the action subtype is `TerminalAction` / `IPythonRunCellAction`. Directly comparable across arms. |
| **Total event count (all events)** | Broader efficiency signal that includes non-terminal actions (file writes, message events). Reveals verbosity overhead. | LOW | Count all JSONL events. |
| **Wall-clock active time** | Human-relevant measure of run duration (tutorial readers care about "how long did this take on my hardware"). Computed as last-event timestamp minus first-event timestamp per task, summed. | LOW | Already computed in v1.2 and v1.3 manifests via JSONL timestamps. |
| **Error-fix cycle count** | Counts distinct build/test failures followed by a retry — the most direct measure of plan-execution roughness. A plan that anticipates failure modes should require fewer cycles. | MEDIUM | Define: a failure is an ObservationEvent with `exit_code != 0`; an error-fix cycle is a (failure → subsequent action → eventual success) sequence. Count per task and total per arm. |
| **AgentErrorEvent count** | Counts tool-call failures (e.g. attempted `file_editor` which isn't available). Reveals when the agent tries actions its environment does not support — a planning quality signal. | LOW | Count `type=="error"` events in the JSONL. Prior runs (v1.2, v1.3) already show this as a meaningful signal. |

### Fairness Controls

| Control | Why It Is Table Stakes | Complexity | Notes |
|---------|------------------------|------------|-------|
| **Same model, same version** | If the model differs between arms, you are measuring model differences, not planning differences. | LOW | Both arms: `openai/qwen-35b` via litellm @ `127.0.0.1:4000`. OpenHands SDK v1.21.0 / CLI 1.16.0. Document in each run's manifest. |
| **Same goal wording (semantics)** | The goal statement must specify the same functional requirement for both arms. Arm A can decompose this into sub-prompts; Arm B receives it as a single prompt; but the underlying target must be identical. | MEDIUM | Write a single "canonical goal" for each example (e.g. "Build a minimal Scala 3 arithmetic calculator that evaluates `2+3*4` to `14`…"). Arm A's Claude plan is derived from this. Arm B's single prompt *is* this (possibly lightly expanded for single-shot context). |
| **Clean workspace state per run** | If Arm A leaves a partial build, Arm B inherits it and will perform differently. Each run starts from an empty workspace. | LOW | `rm -rf <workdir> && mkdir <workdir>` before each arm. Document in manifest. |
| **No carry-over context** | Each arm starts a fresh OpenHands session (no prior conversation history). Prompt cache warmth is controlled (see below). | LOW | Each arm is a fresh `openhands` invocation with no `--conversation-id` carry-over. |
| **Same timeout settings** | A tighter timeout on one arm can cause spurious failures unrelated to planning quality. | LOW | Use the same `LLM_TIMEOUT` for both arms. |
| **source=agent check on every ActionEvent** | Required by the project's honesty discipline. Without it, manual interventions cannot be ruled out and the comparison is fabricated. | LOW | Run the existing Python honesty gate script on every JSONL before committing. |

### Plan Characterisation (Qualitative)

| Element | Why It Is Table Stakes | Complexity | Notes |
|---------|------------------------|------------|-------|
| **Save both planning artifacts** | The chapter can only compare plans if both are preserved. Arm A: the Claude-authored task breakdown (the prompt list). Arm B: the OpenHands agent's self-generated plan/decomposition as it appears in the first MessageEvent or the first set of tool calls. | LOW | Commit: (a) `arm-a/plan.md` — the Claude-authored task list verbatim. (b) `arm-b/opening-agent-output.md` — the agent's first planning message extracted from the JSONL. |
| **Task count** | Most visible structural difference between plans. A Claude plan with 3 tasks vs an OpenHands self-plan with 1 (or 7) tasks is immediately legible to readers. | LOW | Count: Arm A — number of `-t <task>` invocations. Arm B — number of distinct subtask headings or "Step N:" blocks in the agent's first message (if any). |
| **Match to scaffold→write→build→test canonical structure** | The prior milestones established this 3–5 task decomposition as the reference for Claude-led planning. Does Arm B's self-plan converge on the same structure, or diverge? | MEDIUM | Binary per phase: does the plan have a recognizable scaffold phase? write phase? build/test phase? Note presence/absence. |
| **Granularity note** | A qualitative sentence on whether the plan is coarse (one big chunk), medium (scaffold/write/test), or fine (sub-task per file, per function). Affects how well individual errors are isolated. | LOW | Not a score — a 1-sentence description of Arm B's decomposition, compared to Arm A's task count. |

### Canonical Test Pass Criteria

These are the exact pass criteria inherited from prior milestones. They must be applied
identically for both Arm A and Arm B, and the result (PASS/FAIL) must be traceable to a
specific ObservationEvent in the JSONL.

| Example | Canonical Pass Criteria | Source |
|---------|------------------------|--------|
| **F# FsLex/FsYacc Calculator** | `dotnet run` on the final source produces `2+3*4 = 14` (or evaluates to `14`), exit code 0. Parentheses test optional but preferred: `(2+3)*4 = 20`. | v1 capture manifest; ch04 chapter |
| **Rust HTTP Server** | `cargo build` succeeds (exit 0), server launches, `curl -s http://localhost:8080/` returns `hello\n` with HTTP 200, exit 0. No external crate dependencies (`[dependencies]` empty in Cargo.toml). | v1.2 capture manifest (RUST-03) |
| **Scala 3 Calculator** | `scala-cli run Calc.scala -- "2+3*4"` → `14` (exit 0), `-- "(2+3)*4"` → `20` (exit 0), `-- "10-3-2"` → `5` (exit 0). Left-associativity verified by the `10-3-2 = 5` case. No external dependencies (`//> using dep` absent). | v1.3 capture manifest (SCAL-03) |

---

## Differentiators (Nice-to-Have Study-Design Features)

These are features that make the chapter more credible and more useful to readers, but
are not strictly required for the comparison to be publishable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Per-call LLM time (avg / min / max)** | Reveals whether one arm generates longer or shorter per-call contexts (which affects latency independently of step count). Already computed in v1.2 and v1.3 manifests from JSONL timestamps (ObservationEvent ts → next ActionEvent ts). | MEDIUM | `avg_llm_gap = mean(action_ts[i+1] - obs_ts[i])` across all (obs, action) pairs in the JSONL. Interpret carefully: longer gaps may reflect longer input contexts, harder reasoning, or both. |
| **Token counts (prompt + completion) per arm** | The most direct measure of compute cost and context growth. A plan that passes context down through sub-prompts vs a single-prompt arm may show very different token profiles. | MEDIUM | Available in JSONL if OpenHands / litellm logs token usage in ObservationEvents. Check whether `usage.prompt_tokens` / `usage.completion_tokens` appear in the JSONL before committing to this metric. If absent from JSONL, skip for v1.4 (extracting from stderr logs is fragile). |
| **Wasted / abandoned action count** | Actions that produce no progress: repeated sed failures that all return exit 0 but change nothing, duplicate build attempts after a confirmed failure. Identifies planning quality at the action level. | HIGH | Requires classifying each TerminalAction outcome (exit code + whether subsequent action retries the same command). Define "wasted" narrowly to avoid subjectivity: an action is wasted if (a) exit=0 but no file change occurred (detectable via content diff), or (b) exit≠0 and the immediately following action is the identical command again. This is complex to compute automatically; manual annotation for 3 examples per arm is feasible. |
| **Recovery-from-error success rate** | Of the error-fix cycles observed, what fraction were successfully resolved within N further actions (vs abandoned / stuck)? A higher recovery rate favors the arm whose plan provides more local error context. | HIGH | `recovery_rate = successful_recoveries / total_error_fix_cycles`. A "stuck" cycle is one where the same error recurs > 3 times without variation in the fix attempt. Feasible for 3 examples; complex to automate. |
| **Time-to-first-correct** | Wall-clock elapsed from start of run to the first JSONL event where the canonical test passes. Distinguishes "passed on first build" from "passed only after extensive iteration." | MEDIUM | Locate the first ObservationEvent where the canonical test output appears (exit=0 + expected string); compute elapsed from first event. For Arm A (multi-task), this is the timestamp of the passing test event in the final task JSONL. For Arm B (single-task), it is within the single JSONL. |
| **Distinct sub-goals attempted** | Counts how many distinct observable objectives the agent pursues (e.g. "create project", "write source", "build", "run curl"). Measures whether the agent self-decomposes even when given a single prompt (Arm B). | MEDIUM | Manual count from the agent's message events and TerminalActions in Arm B. Compare to Arm A's explicit task count. |
| **Repetition: 3 runs per (example × arm)** | The minimal honest repetition count for reporting range/median honestly. See Repetition section below. | HIGH | 3 × 3 examples × 2 arms = 18 total runs. Significantly more capture effort; feasible but costly on local 35B. |
| **Narrative disclosure box in chapter** | A short callout in 부록 D that states exactly: which metrics were computed automatically vs manually, the sample size (n=1 or n=3), what claims are being made (directional observation vs statistically significant finding). | LOW | Template text provided in the chapter outline. Prevents overclaiming. |

---

## Anti-Features (Confounds and Overclaims to Avoid)

These are design choices that appear reasonable but would make the comparison invalid,
misleading, or unfalsifiable. Each is grounded in study-design or agent-evaluation methodology.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Reporting a single run as a statistically significant finding** | Single-run pass@1 estimates vary by 2.2–6.0 percentage points even at temperature 0 on well-established benchmarks (arXiv 2602.07150). On a local 35B with hardware noise, the variance is at least this large. "Arm A was faster by 23 terminal actions" from one run is directional observation, not a finding. | Label single-run results explicitly as "single-run observation (n=1)". Use hedged language: "In this run…" or "Directionally…", not "Arm A requires fewer actions." |
| **Claiming the arm with fewer terminal actions "planned better"** | Action count conflates planning quality with task difficulty variation (which varies across examples). An arm that receives a pre-scaffolded plan (Arm A) may appear more efficient partly because Claude's plan avoids domains the model finds hard, not because multi-step planning is inherently superior. | Report metric values without strong causal attribution. Note confounds explicitly. |
| **Different goal wording for Arm A vs Arm B** | If Arm A's task prompts say "create a project with `cargo new`" but Arm B's single prompt says "write a Rust HTTP server", the arms differ in specificity, not just planning regime. Any efficiency difference could be explained by prompt specificity, not planning. | Write a single canonical goal per example. Derive Arm A tasks from it. Use the canonical goal (minimally expanded for single-shot context) as Arm B's prompt. Keep the prompts in version control for reader inspection. |
| **Warm prompt cache for one arm, cold for the other** | Litellm / the local model may cache partial KV-cache for repeated prefixes. If Arm A's first sub-prompt and Arm B's full prompt start differently, cache warmth differs and per-call timing is not comparable. | Run both arms from a cold cache start (restart litellm proxy or use a unique system-message nonce). Document cache state in the manifest. |
| **Manual intervention in one arm but not the other** | If the operator corrects a file or provides a hint to Arm B (but not Arm A) because Arm B is stuck, the comparison is invalid. The source=agent honesty gate must apply to both arms. | Apply the existing honesty gate (every ActionEvent must have `source=agent`) to all JSONL from both arms before analyzing. |
| **Using different OpenHands versions or timeout settings per arm** | Version differences may change the agent loop's default retry behavior, system prompt, or available tools. Timeout differences directly affect how long the agent persists on an error. | Fix: same OpenHands SDK version, same `LLM_TIMEOUT`, same `--yolo` flag (no human-in-loop interrupts). Document in both manifests. |
| **Measuring only pass/fail and declaring a winner** | Pass/fail is binary. Both arms may pass all canonical tests. The interesting differentiation is in the path (actions, errors, time). A winner-takes-all framing obscures the actual story. | Report all metrics in a table. State clearly which metric each arm "won" on. If both arms pass all tests, say so prominently. Mixed results are the expected outcome and are more honest than a single winner. |
| **Treating "OpenHands-native planning" as a black-box "self-plan"** | Without saving the Arm B agent's first planning message, readers cannot verify what plan the agent actually formed. The chapter makes a claim about "OpenHands' self-generated plan" that is unverifiable. | Commit `arm-b/opening-agent-output.md` — the verbatim first planning message from the JSONL — for every example. Describe the plan in 2–3 sentences and count any visible sub-goals. |
| **Comparing across examples (e.g. F# vs Rust) as if they were replicates** | The three examples (F# / Rust / Scala) differ in task difficulty, toolchain, and domain-distribution for the model. They are not three replicates of the same task; they are three different tasks. | Report arm-by-arm within each example (F#: A vs B; Rust: A vs B; Scala: A vs B). Cross-example observations ("Rust took fewer steps than F# in both arms") are directional only, due to task-difficulty confound. |
| **Omitting failed runs from reporting** | If Arm B fails the canonical test on F# (likely, given the FsLex domain), reporting only the successful arms would bias the comparison. | Report every run. Failure on the canonical test is a valid data point. A "FAIL" in the pass/fail column with a note on what the agent actually produced is the honest form. |

---

## Feature Dependencies

Study-design elements and their authoring dependencies:

```
[Canonical goal wording per example]
    └──required by──> [Arm A: Claude task plan]
    └──required by──> [Arm B: single-shot prompt]

[Arm A task plan] ──drives──> [Arm A capture runs]
[Arm B single-shot prompt] ──drives──> [Arm B capture runs]

[Arm A capture runs] ──produce──> [Arm A JSONL per example]
[Arm B capture runs] ──produce──> [Arm B JSONL per example]

[Arm A/B JSONL] ──feed──> [Metrics harness (terminal actions, events, wall-clock, error cycles)]
[Arm A/B JSONL] ──feed──> [source=agent honesty gate]
[Arm A/B JSONL] ──feed──> [Canonical test pass/fail extraction]

[Arm B JSONL] ──also yields──> [opening-agent-output.md (Arm B's self-plan)]

[All metrics + pass/fail + plan artifacts]
    └──required by──> [부록 D chapter authoring]
```

**Critical ordering constraint:** The canonical goal wording must be finalized before either arm
is run. Any post-hoc change to the goal wording requires re-running both arms (otherwise the
comparison is against different targets).

**Dependency note — Arm A format:** Arm A converts a Claude-authored task list into individual
`-t <task>` invocations (the v1/v1.2/v1.3 pattern). This is already proven. The open question
per PROJECT.md is whether there is a native "OpenHands plan" format that Arm A could use instead
of sequential single-task invocations. Research this before the Arm A capture design is finalized.

---

## Repetition and Variance: Minimum Honest Sample

### What the literature says

Research on stochasticity in agentic evaluations (arXiv 2602.07150; arXiv 2512.06710) shows:

- Single-run pass@1 estimates vary by **2.2–6.0 percentage points** even at temperature 0 on
  frontier models on SWE-Bench-Verified. Non-determinism from inference engines and OS scheduling
  persists even in theoretically deterministic settings.
- For ICC (intraclass correlation) to be meaningful, **n ≥ 8** per cell is recommended for
  simple tasks, **n ≥ 32** for complex reasoning tasks (arXiv 2512.06710).
- The Anthropic engineering blog ("Demystifying Evals for AI Agents") explicitly recommends
  running multiple trials since "model outputs vary between runs," and notes that a 0% pass rate
  across many trials usually signals a broken task, not a broken agent.
- A comprehensive empirical framework comparison (arXiv 2511.00872) presents aggregate metrics
  without per-instance repetition data — a noted limitation.

### The honest minimum for a tutorial micro-study

For a **tutorial appendix** (not a published research paper), the goal is not statistical
significance — it is **honest reporting** and **directional insight**. The following norms apply:

| Scenario | Recommendation | Rationale |
|----------|----------------|-----------|
| **n=1 per (example × arm)** | Acceptable *if* the chapter explicitly labels every result as a single-run observation and uses hedged language ("in this run", "directionally"). | Cost: 6 captures total (3 examples × 2 arms). Minimum viable comparison. |
| **n=3 per (example × arm)** | Preferred for any metric used to make a directional claim. Report range (min–max) and median. Do not report mean/SD at n=3 (misleading precision). | Cost: 18 captures total. Feasible on local 35B but time-intensive (~3–4 hours of compute at 3–6 min/example). |
| **n≥8** | Required for statistical claims. Not appropriate for this tutorial context without substantially more compute. | Out of scope for v1.4. |

**Recommendation for v1.4:** Run **n=3 per (example × arm) where time permits, n=1 minimum**.
Commit to one of the following disclosure levels in 부록 D:

- **Level A (n=1):** "이 결과는 단일 실행(n=1) 관찰입니다. LLM 추론의 비결정성으로 인해 재현 시
  다를 수 있습니다." (This is a single-run observation; results may differ on re-run due to
  LLM non-determinism.)
- **Level B (n=3):** "각 조합을 3회 반복했습니다. 아래 표의 수치는 범위(최솟값–최댓값)와
  중앙값입니다." (Each combination was run 3 times; figures show range and median.)

Do not use Level A language if the chapter makes comparative claims ("Arm A was more efficient")
without explicit hedging. Do not use Level B language for any metric that was only measured once.

### Variance reporting format

For n=3, report as: `median (min–max)`.  
Example: `TerminalActions: 14 (12–17)` — not `14 ± 2.5` (implying normality at n=3).

For n=1, report the single value and label it: `TerminalActions: 14 (단일 실행)`.

---

## MVP Metrics Set (Prioritized for v1.4 Implementation)

### Compute Automatically from JSONL (P1 — must have)

- [ ] **Total TerminalAction count** per arm per example — why essential: primary efficiency signal, already extractable from existing JSONL analysis scripts
- [ ] **Total event count** per arm per example — why essential: broad efficiency signal
- [ ] **Wall-clock active time** per arm per example — why essential: reader-relevant, already computed in prior manifests
- [ ] **Error-fix cycle count** per arm per example — why essential: planning quality signal; requires exit_code scanning
- [ ] **AgentErrorEvent count** per arm per example — why essential: environment-compatibility signal
- [ ] **Canonical test pass/fail** per arm per example — why essential: objective correctness; non-negotiable

### Compute Automatically or with Simple Parsing (P2 — should have)

- [ ] **Avg / min / max LLM-call gap** per arm per example — needs timestamp calculation across (obs, action) pairs; already done in v1.2/v1.3 manifests
- [ ] **Time-to-first-correct** (wall-clock to first passing test event) — locate passing test ObservationEvent; compute delta from first event

### Manual Annotation (P2 — invest if n=1, more important at n=3)

- [ ] **Arm B opening-agent-output.md** — verbatim extract of agent's first planning output from Arm B JSONL
- [ ] **Plan task count** (Arm A: sub-prompt count; Arm B: observable sub-goal count in first message)
- [ ] **Canonical structure match** (scaffold→write→build→test phases present in each plan: YES/NO per phase)

### Compute Only if Token Data Available in JSONL (P3 — defer if absent)

- [ ] **Total prompt + completion tokens** — check for `usage` field in JSONL ObservationEvents before committing to this metric

### Skip for v1.4 (too complex, too low value at n=1)

- Wasted/abandoned action count (requires action-level semantic classification; not worth at n=1)
- Recovery-from-error success rate (too few cycles per run to be meaningful at n=1–3)
- Statistical significance testing (requires n≥8; inappropriate for tutorial chapter)

---

## Competitor / Comparable Study Analysis

| Study/Paper | What It Measures | What This Study Improves On |
|-------------|------------------|-----------------------------|
| arXiv 2511.00872 (Agent Framework Comparison on Code Tasks) | Task success, trajectory steps, correction attempts, token cost — across agent frameworks on uniform LLM | Uses 1,200–300 task instances (no per-instance variance reporting); same LLM per framework (same design principle as v1.4) |
| arXiv 2602.07150 (Randomness in Agentic Evals) | pass@1 variance, ICC, statistical properties of single-run evals on SWE-Bench | Theoretical/statistical; no tutorial/pedagogical context; n=60,000 trajectory dataset |
| Anthropic "Demystifying Evals" | pass@k framework, clean-environment protocol, multi-trial recommendation | Prescriptive guidance, no executed comparison |
| v1.2 CAPTURE-MANIFEST.md (this project) | Wall-clock, TerminalActions, per-call timing, error-fix cycles for 35B Rust run | Single arm (Claude-led only); no comparator arm; already the template for v1.4 metrics |

**v1.4's unique contribution:** applying structured agent-evaluation metrics (efficiency, error-fix
cycles, plan characterisation) to a deliberate A/B planning comparison on the *same model*, within
a tutorial context that demands honest reporting of mixed or inconclusive results.

---

## Sources

- [arXiv 2602.07150 — On Randomness in Agentic Evals](https://arxiv.org/pdf/2602.07150) — single-run variance quantification, pass@k vs pass^k reporting framework
- [arXiv 2512.06710 — Stochasticity in Agentic Evaluations (ICC)](https://arxiv.org/html/2512.06710v1) — minimum n for reliable estimates, ICC thresholds, variance decomposition
- [arXiv 2511.00872 — Empirical Evaluation of Agent Frameworks on Code Tasks](https://arxiv.org/html/2511.00872v1) — three-dimension framework (effectiveness / efficiency / overhead); same-LLM fairness control; trajectory steps + correction attempts as primary efficiency metrics
- [Anthropic Engineering — Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — pass@k for single-correct vs pass^k for consistency; clean-environment protocol; multi-trial recommendation
- [Confident AI — Definitive AI Agent Evaluation Guide](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide) — operating envelopes (max steps, token budget, wall-clock timeout); trace-level accounting; step/tool-call counts
- [arXiv 2410.22457 — Dynamic Task Decomposition, Novel Metrics and Dataset](https://arxiv.org/html/2410.22457v1) — five trajectory-quality metrics beyond success rate; granularity axis for task decomposition evaluation
- [v1.2 Capture Manifest — 35B Rust HTTP Server Run](../.planning/milestones/v1.2-phases/08-capture-the-35b-rust-http-server-run/captured-rust/CAPTURE-MANIFEST.md) — established the metrics template (TerminalAction count, wall-clock, per-call timing, error-fix cycles, source=agent gate) now applied to v1.4
- [v1.3 Capture Manifest — 35B Scala Calculator Run](../.planning/milestones/v1.3-phases/10-capture-the-35b-scala-calculator-run/captured-scala/CAPTURE-MANIFEST.md) — timing methodology (avg/min/max LLM-call gap); canonical test criteria (14/20/5); honesty gate

---

*Feature research for: v1.4 Planning Comparison study design (부록 D)*
*Researched: 2026-06-01*
