# Pitfalls Research

**Domain:** A/B comparison of AI task-planning regimes — Korean mdBook tutorial, v1.4 milestone
**Researched:** 2026-06-01
**Confidence:** HIGH for statistical/honesty traps (established methodology literature); HIGH for project-specific capture pitfalls (confirmed recurring across v1.1, v1.2, v1.3 audits); MEDIUM for OpenHands native-planning mechanism (open unknown until Phase 12 research resolves it)

---

## Critical Pitfalls

### Pitfall 1: Prompt-Wording Asymmetry Invalidates the A/B

**What goes wrong:**
Arm A delivers a Claude-authored task decomposition to OpenHands; Arm B delivers a bare goal. If
anything other than *who produced the plan* differs between the two prompts — tone, specificity of
the goal, language, number of sentences, or included constraints — the comparison confounds
planning quality with prompt quality. The 35B is highly sensitive to prompt phrasing; a longer or
more structured Arm A prompt can improve performance for reasons that have nothing to do with
Claude planning.

**Why it happens:**
The Arm A prompt is naturally longer (it contains a plan). Authors reflexively include extra
context or scaffolding around the plan that Arm B does not get. Arm B may then appear to
underperform simply because it received less information, not because it plans worse.

**How to avoid:**
Define a "control block" that appears identically in both arms: project goal, acceptance criteria
(canonical outputs: 14/20/5 for F#; "hello\n" for Rust; 14/20/5 for Scala), and the IMPORTANT
LocalWorkspace constraint (no file_editor, use heredoc). The *only* addition in Arm A is the
task-decomposition list. Do not add preamble prose around the Arm A plan. Write both prompts
side by side before running either arm and do a diff — any line not attributable to the plan
itself must be removed from Arm A.

**Warning signs:**
- The Arm A prompt is more than one screenful longer than the Arm B prompt when the plan text is
  stripped out.
- Arm A includes phrases like "first do X, then Y" that implicitly constrain sequencing even
  outside the plan list.
- Arm B gets a goal phrased differently from the goal wording Arm A uses.

**Phase to address:** Phase 12 (Design the capture protocol) — prompt templates must be reviewed
and diffed before any arm is run.

---

### Pitfall 2: Cache-Warmth Asymmetry — Arm A Benefits from the Model's KV Cache

**What goes wrong:**
When the 35B runs Arm A (Claude plan → execute), the model has already seen the plan content in
the system or user prompt. Subsequent calls can benefit from prefix-caching if the prompt prefix
overlaps across turns. Arm B, starting from a bare goal, builds its plan mid-run; later calls
have a different prefix structure. If Arm A is run first, the model's KV cache (confirmed present
via `cached_tokens` in usage) may warm up for patterns Arm B does not benefit from. The result is
a spurious latency advantage for whichever arm runs in a warmer cache state.

**Why it happens:**
The local MLX server preserves KV-cache state across requests within a session. The litellm
proxy adds another caching layer. Run order determines which arm benefits.

**How to avoid:**
- For each language (F#, Rust, Scala), run Arm B first (cold cache) and Arm A second — or
  alternate order across languages (B-first for F#, A-first for Rust, B-first for Scala) so the
  cache-warmth effect is distributed and noted.
- Explicitly record `cached_tokens` from each JSONL's LLM usage fields and report them in the
  manifest alongside raw times. If Arm A shows substantially higher `cached_tokens`, flag this
  as a confound in 부록 D.
- The cleanest option: restart the litellm proxy between arms to flush any server-side cache.
  Document in the manifest that the restart was done and at what clock time.

**Warning signs:**
- Arm A per-call latency is noticeably lower than Arm B for calls with similar input length.
- `cached_tokens` in Arm A JSONL is substantially higher than in Arm B.
- Run logs show the litellm proxy was not restarted between arms.

**Phase to address:** Phase 12 (Capture protocol design) — document the restart/ordering
strategy before any run; Phase 13 (Execute runs) — enforce the documented restart.

---

### Pitfall 3: N=1 Run Per Arm — Drawing Conclusions from a Single Noisy Sample

**What goes wrong:**
The 35B is non-deterministic (temperature > 0 in typical OpenHands config). A single run of each
arm is not statistically sufficient to attribute a metric difference to planning regime vs.
natural run-to-run variance. Presenting "Arm A: 2 retries, Arm B: 4 retries" as if planning
causes the difference — without acknowledging this is one draw from a distribution — is
misleading and would not survive peer review in any empirical ML study.

**Why it happens:**
Capturing runs is slow (the 35B takes 3–8s per call, runs take minutes). Running N=3 or N=5
repetitions per arm is 6–10× the total run budget. Authors accept N=1 because it is what they
can practically capture.

**How to avoid:**
- Accept N=1 per arm as a resource constraint and state it explicitly in 부록 D. Frame every
  metric result as a *single-run observation*, not a robust estimate.
- Use language like "In this single captured run, Arm A required X retries vs Arm B's Y" — not
  "Arm A requires fewer retries."
- Do not use confidence intervals, p-values, or "significantly better" language; they are
  unjustified at N=1.
- If two arms produce very similar metric values (e.g., retries differ by 1), explicitly label
  the result "inconclusive — within single-run variance." This is itself a valid and honest
  finding.
- For the tutorial narrative: frame N=1 as a deliberate design choice that matches the
  tutorial's goal (show the methodology of a planning A/B, not produce a generalizable finding).

**Warning signs:**
- Chapter text says "Arm A is more efficient" without a sample-size disclaimer.
- A difference of 1–2 events/retries across arms is treated as meaningful.
- The words "significantly," "consistently," or "reliably" appear without statistical support.

**Phase to address:** Phase 15 (Write 부록 D) — every metric table must include a "single-run
caveat" footnote; the intro paragraph must state N=1.

---

### Pitfall 4: Cherry-Picking the Favorable Run

**What goes wrong:**
If a run of one arm fails badly (the 35B gets stuck in a loop, produces a wrong answer, or times
out), there is a temptation to re-run that arm and use the better result — while keeping the
other arm's first result. This silently cherry-picks in favor of one arm and fabricates a result.
It violates the project's core honesty discipline (source=agent; no manual edits; no fabrication).

**Why it happens:**
Failed runs are frustrating and feel like "noise." The author may rationalize re-running as
"getting a fair result." But in an N=1 comparison, the failed run *is* the result — it shows
exactly the kind of failure that planning regime differences should reveal.

**How to avoid:**
- Adopt the same honesty gate already established for prior milestones: the first capture of each
  arm is the capture, as long as it completes (i.e., the canonical test is attempted, even if it
  fails). Document in the manifest whether the canonical test passed or failed.
- If a run truly cannot complete (e.g., the model hangs indefinitely, not a planning failure but
  an infrastructure failure), the re-run is permitted but must be disclosed: "Arm B for Rust was
  re-run once due to [infrastructure reason]; the first run is archived at [path]."
- The distinction to enforce: infrastructure failure (server crash, timeout on the host) = valid
  re-run trigger; poor planning quality = NOT a valid re-run trigger.

**Warning signs:**
- More than one JSONL capture exists for a given arm/language combination and only one is cited.
- The manifest does not explain why a re-run was done.
- Both arms happen to produce clean results with no retries — statistically implausible for a
  noisy 35B on non-trivial tasks.

**Phase to address:** Phase 13 (Execute runs) — manifest must record first-run vs. re-run status
for every arm; Phase 14 (Verify captures) — honesty gate checks this.

---

### Pitfall 5: Conflating "Fewer Tasks/Subtasks" with "Better Planning"

**What goes wrong:**
Arm A receives a Claude-authored plan that decomposes the goal into N subtasks. Arm B self-plans
and may produce M subtasks where M ≠ N. If the metric harness counts "number of subtasks" or
"plan granularity," a comparison like "Claude made 3 tasks, OpenHands made 1 task, Claude is more
detailed" says nothing about quality. It is a description of the planning *style*, not the
planning *effectiveness*. Conflating granularity with quality is a common mistake in
task-planning research.

**Why it happens:**
Task count is easy to measure. Effectiveness (did the plan lead to correct execution?) is harder.
Authors reach for the easy metric and overinterpret it.

**How to avoid:**
- Distinguish clearly between planning-structure metrics (task count, plan depth, self-planning
  present/absent) and execution-quality metrics (retries, final pass/fail, LLM call count). Only
  the latter measure planning effectiveness.
- In 부록 D, present task-structure data as a *qualitative artifact* (show both plans side by
  side) rather than as a scorable metric.
- Add a note: "A plan with 5 subtasks is not inherently better than a plan with 2 subtasks — what
  matters is whether the agent followed it successfully."

**Warning signs:**
- A metric table has a row for "subtask count" with a "winner" column filled in.
- Chapter text equates "Claude decomposed into 3 tasks, OpenHands into 1 prompt" with "Claude
  planned more carefully."

**Phase to address:** Phase 12 (Metric harness design) — define which metrics are
effectiveness metrics vs. descriptive/structural metrics before data collection.

---

### Pitfall 6: Time Metric Dominated by Cache/Network, Not Planning Quality

**What goes wrong:**
Wall-clock time is an attractive metric because it is concrete. But for a local 35B, wall-clock
time in a single run is dominated by: (a) per-call inference time (varies 1.2–7.7s per call in
prior captures, driven by prompt length and model load), (b) bash execution time (build
commands, cargo compile), and (c) operator pause time between arms. Planning quality has a second-
order effect on time through its influence on call count. If Arm A is faster, it may be because
it had fewer calls — which in turn may be because the goal was easier in that arm's run, not
because Claude planned better.

**Why it happens:**
Time is readily extracted from JSONL timestamps. Authors report it without decomposing it into
inference vs. execution vs. operator-pause components.

**How to avoid:**
- Extract time the same way prior milestones did: LLM-call gaps (ObservationEvent timestamp →
  next ActionEvent timestamp = pure model-thinking time, excludes bash). Report this separately
  from total wall-clock.
- Report at least three time components per arm: (1) total wall-clock, (2) active agent time
  (sum of LLM-call gaps + TerminalAction durations), (3) per-LLM-call average. This lets the
  reader see whether a time difference is from faster calls (cache/hardware) or fewer calls
  (planning effectiveness).
- Explicitly disclose that per-call times can vary by 2–5× across runs on the same hardware
  depending on KV-cache state and model load.

**Warning signs:**
- The only timing metric reported is total wall-clock time.
- No breakdown between model-thinking time and bash-execution time.
- Arm A shows a lower per-LLM-call average than Arm B (cache-warmth confounder not mentioned).

**Phase to address:** Phase 14 (Metrics harness) — harness must extract all three time
components from JSONL; Phase 15 (Write 부록 D) — timing tables must include breakdown columns.

---

### Pitfall 7: The Converter Doing Planning Work — Arm A Advantage From Conversion, Not Claude's Plan

**What goes wrong:**
Arm A requires converting a Claude-authored plan into an OpenHands-consumable format. If the
conversion step adds clarifications, restructures subtasks for OpenHands' style, fills in missing
details, or adjusts the plan based on knowledge of how the 35B tends to respond — then the
"Arm A" run benefits from both Claude's planning *and* the converter's additional editorial work.
The comparison no longer isolates who-planned; it isolates "Claude + human editor vs. OpenHands
alone."

**Why it happens:**
The converter is typically an agent (possibly Claude) or a human, both of whom are tempted to
"improve" the plan in transit. Even well-intentioned format normalization (making subtask
boundaries cleaner, rewording for clarity) counts as additional planning work.

**How to avoid:**
- Define the conversion as a *mechanical* operation only: take Claude's plan structure → emit it
  in the agreed OpenHands prompt format with no additions, no rewording, no judgment calls.
  Document the conversion rule verbatim in the manifest.
- If the conversion is done by a Claude agent, its output must be reviewed and any edits beyond
  format normalization must be logged as deviations from "pure conversion."
- Prefer a fixed conversion schema (e.g., "each Claude subtask becomes a numbered item in the
  prompt, with the subtask's text verbatim") over a free-form translation.
- In 부록 D: disclose the conversion method explicitly. Readers must understand what was
  mechanical vs. editorial.

**Warning signs:**
- The converted Arm A plan contains detail not present in Claude's original plan.
- The conversion agent was given information about how OpenHands/35B works and instructed to
  "make it clear."
- The converted plan is longer or more specific than Claude's original.

**Phase to address:** Phase 12 (Capture protocol design) — define and document the conversion
rule before Claude authors the plan; Phase 13 (Execute) — verify the conversion mechanically
before running Arm A.

---

### Pitfall 8: Fairness Framing — A Stronger Model Authoring the Plan Trivially "Wins"

**What goes wrong:**
Claude (Opus/Sonnet, a frontier model) is dramatically more capable than the local 35B. If Arm A
wins on execution metrics, the naive interpretation is "Claude's plan is better, therefore Claude
is better at planning." But the research question is not "Claude vs. 35B at planning" — it is
"does an externally-authored expert plan help the 35B execute vs. letting the 35B plan itself?"
If the framing conflates these, readers come away thinking they measured model capability when
they measured plan-quality effect on execution.

**Why it happens:**
It is natural to describe Arm A as "Claude planned" and Arm B as "the 35B planned." This phrasing
implies a comparison of planning ability across models, which is not what the experiment
measures (nor can measure cleanly, since Claude does not execute and the 35B does not plan in
Arm A).

**How to avoid:**
- Use a consistent, honest framing throughout 부록 D: **"Arm A: expert-authored plan provided to
  the 35B" vs. "Arm B: 35B given the goal and allowed to self-plan."** The research question is
  "does providing a pre-authored plan to the 35B change how well it executes?" not "is Claude
  better at planning than the 35B?"
- In the opening paragraph of 부록 D, add a framing note: "Arm A does not test Claude's planning
  ability — Claude's role is to produce a starting plan artifact. What is measured is the 35B's
  execution quality when given that artifact vs. when given only the goal."
- If Arm A wins: "The 35B executed more efficiently when given an expert-authored plan" — not
  "Claude is a better planner."
- If Arm B wins or is equal: "The 35B's native self-planning was as effective as an externally
  authored plan for this task" — also a valid, interesting finding.

**Warning signs:**
- 부록 D's title or intro implies the comparison is "Claude vs. 35B."
- A conclusion sentence says "Claude planned better than OpenHands."
- Results are framed as a win/loss for Claude rather than as an effectiveness finding for the 35B.

**Phase to address:** Phase 15 (Write 부록 D) — the framing note must appear in the introduction
and be reviewed at audit time; Phase 12 (Protocol design) — the research question must be
written down in its correct form before any run.

---

### Pitfall 9: Workspace-State Leakage Between Arms or Across Languages

**What goes wrong:**
If Arm A for F# leaves compiled artifacts, partial source, or Cargo/dotnet caches in the
workspace and Arm B for F# runs in the same directory, Arm B inherits state it would not have
from a clean start. This is the same workspace-contamination risk as the v1 "attempt 1 rejected"
event (a manual fix was found in the workspace; that run was discarded). For v1.4, leakage can
be subtler: even a `target/` directory from a prior build can make the 35B's first `cargo build`
faster in Arm B than it was in Arm A, creating a spurious performance difference.

**Why it happens:**
Two arms for the same language naturally use the same or adjacent working directories.
Operators forget to clean up between arms.

**How to avoid:**
- Each arm for each language gets its own clean workspace directory:
  `oh-workdir-arma-fsharp/`, `oh-workdir-armb-fsharp/`, etc.
- Before running each arm, verify the workspace is empty (or freshly created) and log the
  verification in the manifest.
- For compiled languages (F#, Rust, Scala), also clear any global package caches that would
  cause dependency restoration to differ between arms: `~/.nuget/`, `~/.cargo/registry/`,
  `~/.ivy2/`. Or accept that both arms use the cache (warmer for the second arm) and disclose
  this in the manifest.

**Warning signs:**
- Both arms of one language use the same `oh-workdir-*/` directory.
- Arm B's first build is noticeably faster than Arm A's first build (cache warmed).
- The manifest does not list the workspace path and its pre-run state for each arm.

**Phase to address:** Phase 12 (Protocol design) — workspace naming and clean-up procedure
defined; Phase 13 (Execute) — pre-run workspace-empty check logged in manifest.

---

### Pitfall 10: Inter-Run Drift — 35B Behavior Changes Across Multiple Capture Days

**What goes wrong:**
The litellm proxy, MLX server, or OpenHands version may be updated between capturing Arm A and
Arm B (or between capturing F# arms and Rust arms). Even without explicit updates, model
quantization + MLX runtime behavior can drift slightly across sessions. If Arm A is captured on
Day 1 and Arm B on Day 3, a difference in retry count may reflect a version drift, not planning
regime.

**Why it happens:**
Capturing 6 arms (3 languages × 2 arms) takes time. It is tempting to run some arms today and
others tomorrow, especially if a run fails and needs a re-try.

**How to avoid:**
- Capture all arms for a given language in the same session (same day, same litellm/OpenHands/
  MLX versions). Record model versions and commit hashes in each manifest.
- If captures must span days, document the OpenHands CLI version, litellm version, and MLX
  server version for every arm, and note any version change between arms.
- Version the environment: record `openhands --version`, `litellm --version`, and the model file
  path (with mtime or sha256) in the manifest header.

**Warning signs:**
- Manifests for Arm A and Arm B of the same language show different version strings.
- A capture was redone on a different day without noting that OpenHands was updated in between.

**Phase to address:** Phase 13 (Execute) — capture same-day per language; manifest header
requires version block.

---

### Pitfall 11: Manifest Event-Numbering Convention Drift (Recurring Tech Debt)

**What goes wrong:**
In v1.2, events were cited with a mixed numbering convention: the manifest used the raw JSONL
line index (1-based), while chapter text cited 0-based event indices — causing off-by-one errors
(TD-7, TD-8 in the v1.2 audit). In v1.3, the convention was corrected (manifest 1-based, chapter
consistent), but the recurring nature of this error means it will likely appear again in v1.4
when six arm-captures produce six JSONL sets each with potentially different event counts.

**Why it happens:**
JSONL line numbering starts at 1 (line 1 = first event). Python zero-indexes lists. A developer
iterating over events in Python and printing `enumerate(events)` gets 0-based indices. Manifests
and chapter text then inherit whichever indexing the developer used.

**How to avoid:**
- Adopt the v1.3 convention as the v1.4 standard: manifest cites **1-based event numbers**
  (JSONL line 1 = event #1). Any script that generates manifest citations must use `i+1` for the
  event number.
- Add a convention header to each v1.4 manifest: "Event numbers in this manifest are 1-based
  (JSONL line N = event #N). Chapter text must use the same convention."
- The metrics harness must emit 1-based event references in its output tables.

**Warning signs:**
- A JSONL with 36 parseable JSON objects has a manifest citing "event #0" for the first event.
- The first event in a JSONL is described as event #0 in the manifest but event #1 in the chapter.
- The harness uses Python's `enumerate(events)` without `start=1`.

**Phase to address:** Phase 14 (Metrics harness) — harness emits 1-based indices by default;
Phase 15 (Write 부록 D) — audit checks event references against JSONL line numbers.

---

### Pitfall 12: The `~14–32s/call` Prediction Presented as a Measurement

**What goes wrong:**
The v1 project context notes "~14–32s/call" as a pre-run prediction that was **never measured**.
This figure has already been incorrectly cited as a measurement in two milestones (TD-6 in v1.2;
recurred in v1.3 TD-10 with the wrong arithmetic), requiring same-day fixes in both audits.
For v1.4, any per-arm timing comparison tempts authors to use this figure as a baseline. Using
"~14–32s/call" (a prediction) to contextualize v1.4 measured timings would fabricate a
comparison.

**Why it happens:**
The figure appears in the v1 project context document without a clear "PREDICTION, NOT
MEASURED" flag. Subsequent authors copy it as if it were historical measurement data.

**How to avoid:**
- Never cite `~14–32s/call` as a measurement in 부록 D or any v1.4 chapter. If a timing
  baseline is needed, use the derived figures from prior milestones: ~3.8s/call (v1.2 Rust), ~5.0s/call
  (v1.3 Scala). Both are derived from real JSONL timestamps and explicitly flagged as derived.
- If v1.4 arms produce their own timing data, cite them with provenance: "Arm A F# averaged
  X.Xs/call (LLM-call-gap weighted average from captured-arma-fsharp/logs/*.jsonl)."
- Add a note in the v1.4 capture manifest header: "Per-call times in this manifest are derived
  from JSONL timestamps (LLM-call gap method). The pre-run v1 prediction of ~14–32s/call is NOT
  cited here."

**Warning signs:**
- "~14–32s/call" appears anywhere in v1.4 chapter text without the word "prediction."
- A timing comparison says "v1.4 was X× faster than the original ~14–32s/call baseline."
- The manifest lists per-call times without specifying the derivation method (LLM-call gap vs.
  wall-time ÷ count).

**Phase to address:** Phase 14 (Metrics harness) — harness must compute LLM-call gaps from JSONL
timestamps and label its output "derived from JSONL gaps, not pre-run prediction"; Phase 15
(Write 부록 D) — audit checklist item: `~14–32s/call` must not appear as a measurement.

---

### Pitfall 13: Source=Agent Gate Not Applied to Arm A (Plan-Delivery Events)

**What goes wrong:**
Arm A delivers a Claude-authored plan as the initial user prompt. This creates a user-sourced
MessageEvent at the start of each JSONL. The honesty gate checks that every ActionEvent has
`source=agent`. If the gate script is not careful, it may incorrectly flag the initial plan-
delivery MessageEvent (which legitimately has `source=user`) as a violation, causing a false
alarm. Conversely, if an author manually edits a workspace file *after* the plan is delivered
but before the agent acts, those edits will not appear in the JSONL and the gate will not catch
them — creating a silent honesty violation.

**Why it happens:**
The gate checks JSONL ActionEvents for `source=agent`. Manual filesystem edits outside
OpenHands (direct file writes, sed commands on the host) are not recorded as events at all, so
they are invisible to the gate.

**How to avoid:**
- Apply the same gate script from prior milestones: every ActionEvent (not MessageEvent) must
  have `source=agent`. The first event (MessageEvent, `source=user`) is excluded from the check
  — document this exclusion explicitly.
- Add a complementary pre-run workspace snapshot: hash or list all files in the workspace before
  running each arm. After the run, any file not created or modified by events in the JSONL is a
  sign of an out-of-band edit. Log the pre-run hash in the manifest.
- For Arm A: the plan-delivery prompt is a `source=user` MessageEvent — this is correct and
  expected. Do not "fix" it.

**Warning signs:**
- The gate script treats the first MessageEvent as an ActionEvent and flags it.
- Files in the workspace have mtimes older than the first JSONL event (pre-seeded by the author).
- The manifest lists 0 `source≠agent` ActionEvents but the workspace contains a file with
  hand-edited content.

**Phase to address:** Phase 14 (Verify captures) — gate script adapted for Arm A structure;
pre-run workspace snapshot added to protocol.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Running both arms for all 3 languages before writing any manifests | Faster total run time | Manifest details get reconstructed from memory, errors creep in | Never — write the manifest immediately after each arm's run |
| Using wall-clock time as the only timing metric | Simple to extract | Dominated by cache/hardware variance; misleads the planning comparison | Never — always extract LLM-call gaps separately |
| Skipping workspace clean between arms | Saves 2 minutes | Dependency-cache warmth gives Arm B a build-time advantage | Never — always verify clean workspace before each arm |
| Citing `~14–32s/call` as a baseline without flagging it as a prediction | Provides historical context | Fabricates a measurement comparison; violates honesty discipline | Never |
| Converting Claude's plan with free-form rewriting instead of mechanical format-only conversion | Produces a "cleaner" plan | Confounds conversion editorial work with Claude planning quality | Never — conversion must be mechanical |
| Omitting the N=1 caveat from metric comparisons | Conclusions sound stronger | Misleads readers about statistical reliability; invalidates the comparison as evidence | Never — always disclose single-run constraint |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Arm A plan delivery | Embedding the plan inside prose that also changes the tone/length of the prompt | Isolate plan items in a structurally distinct section; control block is identical to Arm B |
| Metrics harness → JSONL | Using Python `enumerate(events)` starting at 0 | Always use `enumerate(events, start=1)` for 1-based manifest event numbers |
| Timing extraction | Dividing total wall-clock by TerminalAction count | Use LLM-call gaps (ObservationEvent ts → next ActionEvent ts); see v1.2 manifest §Timing |
| Arm A vs. Arm B | Running Arm A on one day, Arm B another day without version-pinning | Run both arms for one language in the same session; record versions in manifest |
| Workspace between arms | Sharing the same `oh-workdir-*` directory | Named per arm: `oh-workdir-arma-fsharp/`, `oh-workdir-armb-fsharp/`, etc. |
| Cache between arms | Not restarting litellm proxy between arms | Restart proxy between arms OR run B first, disclose in manifest |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| 6 captures in sequence without session breaks | Final captures are significantly faster (KV cache warm) | Restart litellm proxy between arms; record `cached_tokens` per call | From the 2nd arm onward |
| Reporting aggregate metrics without per-call breakdown | A single slow call skews the average; readers cannot tell | Report min/max/avg LLM-call gap and identify the outlier calls | Any time one call is 3× the median |
| Running Scala last across all milestones (warmer general cache) | Scala run appears faster than F# or Rust on per-call basis | Vary the language order or accept and disclose the confound | If same-day captures ordered consistently F# → Rust → Scala |

---

## "Looks Done But Isn't" Checklist

- [ ] **Arm prompt symmetry:** Arm A and Arm B prompts have been diffed; the only difference is the plan content itself — verify line-by-line.
- [ ] **Workspace clean:** Each arm's workspace directory was empty at run start — verified by listing before the `openhands` invocation and logging in the manifest.
- [ ] **litellm restart:** The litellm proxy was restarted (or run order counterbalanced) between each pair of arms — confirmed in the manifest with a timestamp.
- [ ] **Source=agent gate:** Every ActionEvent in every arm's JSONL has `source=agent` — confirmed by the gate script before any artifact is committed.
- [ ] **Event numbering:** Manifest event citations are 1-based (JSONL line N = event #N) — verified by opening the JSONL and counting to the cited event manually.
- [ ] **No `~14–32s/call` cited as measurement:** Grep the chapter text and manifest for this string; if present, confirm it is explicitly labeled "pre-run prediction, not measured."
- [ ] **N=1 caveat present:** 부록 D introduction explicitly states that each arm was run once and results should not be generalized beyond this single observation.
- [ ] **Arm A framing:** 부록 D does not say "Claude planned better" — it says "the 35B executed [outcome] when given an expert-authored plan vs. when given only the goal."
- [ ] **Conversion record:** The Claude-to-OpenHands plan conversion method is documented verbatim in the Arm A manifest, and the converted plan is archived alongside Claude's original plan.
- [ ] **Version block in every manifest:** Each manifest header lists openhands version, litellm version, and model path (with sha256 or mtime).

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Prompt asymmetry discovered post-run | HIGH | Discard the affected arm's run; redesign prompts; re-run from scratch |
| Cache-warmth not documented | MEDIUM | Add a disclosure to the manifest: "Cache state between arms not controlled; per-call times may reflect cache advantage for [arm]"; flag in 부록 D as a limitation |
| N=1 framing missing | LOW | Add single-run disclaimer to metric tables and introduction before publication |
| Cherry-picked run discovered at audit | HIGH | Restore the original run from git (if archived); replace cherry-picked data; re-derive metrics |
| Wrong event numbering | LOW | Correct the manifest and chapter citations with a sed pass; verify against JSONL line count |
| `~14–32s/call` cited as measurement | LOW | Replace with derived figures from the JSONL manifest; add "pre-run prediction" label |
| Converter added planning content | MEDIUM | Re-examine Claude's original plan and the converted plan; document additions as deviations in the manifest; if significant, consider re-running Arm A with a mechanical conversion |
| Workspace leakage discovered post-run | MEDIUM | Disclose in manifest; if build-time data is a key metric, flag the affected comparison as potentially confounded |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Prompt-wording asymmetry | Phase 12 (Protocol design) | Side-by-side diff of Arm A and Arm B prompts before any run |
| Cache-warmth asymmetry | Phase 12 (Protocol design) + Phase 13 (Execute) | Manifest records litellm restart timestamp; `cached_tokens` logged per call |
| N=1 conclusions | Phase 15 (Write 부록 D) | Audit checks for "significantly," "consistently," "reliably" without statistical justification |
| Cherry-picking | Phase 13 (Execute) + Phase 14 (Verify) | Manifest lists all runs attempted; git log shows first-run artifacts |
| Conflating task count with quality | Phase 12 (Metric harness design) | Metric definitions written down before data collection; structural vs. effectiveness metrics separated |
| Time metric not decomposed | Phase 14 (Metrics harness) | Harness emits wall-clock, active agent time, and per-LLM-call gap as separate columns |
| Converter doing planning work | Phase 12 (Protocol design) + Phase 13 (Execute) | Conversion rule documented; original + converted plans archived side-by-side |
| Arm A framing ("Claude vs. 35B") | Phase 15 (Write 부록 D) | Audit reads 부록 D intro for "Claude planned better" language; corrects to "expert-plan provided" framing |
| Workspace leakage | Phase 12 (Protocol design) + Phase 13 (Execute) | Pre-run workspace-empty log in manifest for each arm |
| Inter-run drift | Phase 13 (Execute) | Manifest version block; same-day capture per language |
| Event-numbering drift | Phase 14 (Metrics harness) + Phase 15 (Chapter) | Harness uses `enumerate(events, start=1)`; audit spot-checks 3 event citations per JSONL |
| `~14–32s/call` as measurement | Phase 14 (Harness) + Phase 15 (Chapter) | Grep for string in chapter text; check manifest provenance labels |
| Source=agent gate (Arm A structure) | Phase 14 (Verify captures) | Gate script adapted to skip MessageEvents; pre-run workspace snapshot in manifest |

---

## Sources

- Established experimental methodology: the pitfalls around N=1 sampling, confound control, and cherry-picking are standard validity threats in empirical software engineering and ML evaluation studies. Relevant frameworks: "Threats to Validity in Empirical Software Engineering" (Wohlin et al., 2000); NeurIPS/ICML evaluation guidelines on single-run reporting.
- v1.2 MILESTONE-AUDIT (2026-06-01): TD-6 (prediction-as-measurement), TD-7 (event count 41 vs 36), TD-8 (off-by-one event indices) — direct evidence for Pitfalls 12 and 11.
- v1.3 MILESTONE-AUDIT (2026-06-01): TD-9 (cross-chapter date), TD-10 (wrong derivation formula) — confirms recurring nature of metric-provenance errors.
- v1 Phase 3 history: "attempt 1 rejected for honesty; a manual fix was found in the workspace" — direct precedent for Pitfall 4 (cherry-picking / workspace contamination).
- v1.2 CAPTURE-MANIFEST §Timing: LLM-call gap method defined (ObservationEvent ts → next ActionEvent ts); shows ~3.8s/call derived figure — the correct way to derive timing (Pitfall 6).
- v1.3 CAPTURE-MANIFEST: manifest event-numbering convention corrected to 1-based after v1.2 TD-7/TD-8 — establishes the convention this pitfall extends.
- Project PROJECT.md Key Decisions table: "per-call timing must cite real measurements, never the v1 `~14–32s/call` pre-run prediction" — formal decision record for Pitfall 12.

---
*Pitfalls research for: v1.4 Planning Comparison (A/B of Claude-led vs. OpenHands-native task planning on 35B, across F#/Rust/Scala)*
*Researched: 2026-06-01*
