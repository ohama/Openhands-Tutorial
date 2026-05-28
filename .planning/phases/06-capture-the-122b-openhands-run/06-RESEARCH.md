# Phase 6: Capture the 122B OpenHands Run — Research

**Researched:** 2026-05-28
**Domain:** 122B qwen model capability probe + OpenHands capture protocol adaptation
**Confidence:** HIGH (live probes run; all findings are directly observed, not inferred)

---

## Summary

Phase 6 re-runs the proven v1 FsLex/FsYacc calculator capture on the new 122B local model, with one critical protocol change: the `.fsl` lexer is attempted UNAIDED first (no verbatim content provided). This research covers: (1) a live 122B proxy probe with tool-call verification and speed measurement, (2) unaided-first task prompt adaptation, (3) retry/fallback policy preserving honesty, and (4) capture mechanics and CAPTURE-MANIFEST design for Phase 7.

The 122B model is confirmed up and serving via litellm (`qwen-122b`). Live tool-call test returned a valid `get_weather` function call in 1.39s (cached system prompt). Generation speed on longer outputs measured at ~27–47 tok/s. The stack is identical to v1 (OpenHands 1.16 / SDK 1.21, LocalWorkspace, dotnet 10.0.203, FsLexYacc 11.3.0 in NuGet cache) — no environmental changes needed. The only work in Phase 6 is: write the unaided-first task prompts, run the 5–6 OpenHands tasks, capture JSONL per-task, and commit the artifacts.

**Primary recommendation:** Use the v1 task-prompt structure (6 tasks) with task2-lexer replaced by an unaided-first "write Lexer.fsl yourself" prompt. Keep the `.fsproj` scaffold (FixLineDirectives) provided verbatim as in v1 — that is a toolchain workaround, not a model capability question. Keep the bash-only file-write constraint unchanged. Allow up to 2 unaided attempts before falling back; disclose fallback in CAPTURE-MANIFEST. Expect 122B to generate a plausible FsLex file but with one or more API/syntax bugs (observed in live probe) that will trigger a genuine error-and-fix cycle.

---

## 1. LIVE 122B PROBE — Findings

### 1.1 Proxy / Model Availability

```
GET http://127.0.0.1:4000/v1/models
→ ["qwen-35b", "qwen-122b", "qwen-local"]
```

`qwen-122b` is confirmed present in the proxy model list. **Confidence: HIGH** (direct curl, just now).

### 1.2 Tool-Call Smoke Test

Ran a `get_weather` tool-call test against `qwen-122b`:

```
Request:  POST /v1/chat/completions, model=qwen-122b, 1 tool, tool_choice=auto
Response: finish_reason=tool_calls
          tool_call: get_weather({"city": "Paris"})
          usage: {completion_tokens: 26, prompt_tokens: 284, cached_tokens: 283}
Wall clock (cached): 1.39s
Wall clock (cold, 27-token message): 1.11s
Wall clock (65-token generation): 2.35s  → ~27.7 tok/s
Wall clock (FsLex lexer, ~138 tokens): 4.04s → ~34 tok/s
```

**Tool-call works correctly.** The 122B produced a valid JSON tool_call object matching the function schema. **Confidence: HIGH** (direct curl observation).

### 1.3 Generation Speed vs 35B Comparison

| Model | Wall clock (65-tok gen) | tok/s (rough) |
|-------|------------------------|---------------|
| qwen-35b | 0.90s / 35 tok | ~38.7 tok/s |
| qwen-122b | 2.35s / 65 tok | ~27.7 tok/s |

**Key finding:** 122B is roughly 25–30% slower per token than 35B on this machine. For a task generating 300–600 tokens of reasoning+code, expect 10–20s per LLM call (vs 35B's ~7–14s). For a multi-step agent invocation with 5–15 LLM calls, expect 1–5 minutes per task (vs 35B's ~30s–3 minutes in v1). These are still very usable numbers. No special timeout adjustments are needed beyond the default 500-iteration cap.

**Planner note:** The v1 attempt-2 longest task was task1-scaffold at 3m 6s / 27 TerminalActions. At 122B speed (roughly 2x per-LLM-call overhead given similar step count), budget ~6–8 minutes for a complicated task, up to 15 minutes if 122B gets stuck on lexer debugging. The OpenHands default 500-iteration cap is more than enough.

### 1.4 122B FsLex Knowledge Probe

Tested with a task-prompt-style FsLex lexer request:

```
Response: wrote a cat heredoc to calc/Lexer.fsl with:
  - Correct header: { open Parser; open System }
  - rule token = parse (correct FsLex rule syntax — NOT %% separator)
  - Correct patterns: [' ' '\t'], ['0'-'9']+ as s, '+', '-', '*', '/', '(', ')', eof, _
  - INT (int s)  ← WRONG: should be System.Int32.Parse or LexBuffer<_>.LexemeString
  - Lexing.lexemeChar lexbuf 0  ← WRONG API (correct: LexBuffer<_>.LexemeString)
  - Indented header content inside { } ← potential indentation issue
```

**Analysis:** 122B knows the FsLex format (rule/parse structure, no %% separator — the exact thing that defeated 35B). However, it uses incorrect F# APIs for lexeme access (`int s` on a char array, `Lexing.lexemeChar`). These are build-time errors that would cause `FS0001`/`FS0039` errors on first `dotnet build`. The agent would see these errors and likely attempt fixes — this constitutes a genuine error-and-fix opportunity.

**Prediction:** 122B will write a syntactically plausible FsLex file (avoiding the 35B's `%%` failure) but with 1–2 API bugs. After seeing the build error, it has a good chance of self-correcting. This is NOT a guaranteed failure like the 35B's fundamental format confusion — it's a recoverable bug.

**Confidence: MEDIUM** (one probe; actual OpenHands run behavior may differ based on full agent context and tool call loop).

---

## 2. UNAIDED-FIRST TASK DECOMPOSITION

### 2.1 Overall Structure — 6 Tasks (Unchanged from v1)

The v1 task decomposition proved correct. Keep the same 6-task structure:

| Task # | Name | Prompt | Change vs v1 |
|--------|------|--------|--------------|
| task1 | scaffold | task1-scaffold.txt | None — .fsproj provided verbatim, bash-only constraint |
| task2 | lexer (UNAIDED) | task2-lexer-unaided.txt | **REPLACE v1 task2** — no verbatim lexer provided |
| task3 | parser | task3-parser.txt | None — copy v1 exactly |
| task4 | evaluator | task4-evaluator.txt | None — copy v1 exactly (bash-only variant) |
| task5 | build&test | task5-buildtest.txt | None — copy v1 exactly |
| task6 | fix (conditional) | task6-fix.txt | None — only used if task5 fails |

**JSONL naming (separate from v1):**
```
oh-workdir-122b/task1-scaffold.jsonl
oh-workdir-122b/task2-lexer-unaided.jsonl    ← unaided attempt
oh-workdir-122b/task2-lexer-scaffold.jsonl   ← only if fallback taken
oh-workdir-122b/task3-parser.jsonl
oh-workdir-122b/task4-evaluator.jsonl
oh-workdir-122b/task5-buildtest.jsonl
oh-workdir-122b/task6-fix.jsonl              ← only if needed
```

### 2.2 Task 1 — Scaffold: Keep .fsproj Provided (CORRECT CALL)

The FixLineDirectives workaround in the .fsproj is a .NET 10 + FsLexYacc 11.3.0 toolchain compatibility bug — not a model capability question. Providing it is correct because:

1. The question being tested is: can 122B write a valid FsLex lexer?
2. The FixLineDirectives target is equally unknown to both models; it's not part of either model's judgment.
3. Without it, the build will fail on `# 0 ""` line directives regardless of lexer quality — creating noise that obscures the real capability signal.
4. v1 provided the .fsproj; providing it here preserves a fair comparison.

**Decision: CONFIRMED** — provide the .fsproj verbatim via the scaffold task prompt, exactly as v1 task1-scaffold.txt. No change needed.

v1 task1-scaffold.txt can be used without modification, with one update: change `OPENHANDS_WORK_DIR` from `/Users/ohama/projs/OpenHandsTests/oh-workdir` to `/Users/ohama/projs/OpenHandsTests/oh-workdir-122b`.

### 2.3 Task 2 — Unaided Lexer: Exact Prompt Design

This is the only new prompt. It must:
- Tell the agent the .fsproj and Parser.fsy exist.
- Specify the token names the agent MUST use (same names as the parser will declare — critical for lexer/parser agreement).
- NOT provide any lexer source code.
- Specify FsLex constraints (bash-only writes, no file_editor).
- Tell the agent the FsLex file format constraints (no `%%`, rule/parse structure) — RATIONALE: the 35B failed because it didn't know FsLex format. The question for 122B is whether it can write correct lexer CODE, not whether it knows the obscure `%%` vs FsLex distinction. However, to keep the test meaningful, do NOT give hints beyond what a knowledgeable user would say.

**Recommended prompt for task2-lexer-unaided.txt:**

```
Working directory: /Users/ohama/projs/OpenHandsTests/oh-workdir-122b

IMPORTANT: Create and edit ALL files using ONLY bash shell commands (printf, tee, or
`cat > FILE <<'EOF' ... EOF` with a quoted heredoc). Do NOT use the file_editor /
str_replace tool — it errors in this setup (it requires a security_risk field that
fails validation).

An F# FsLexYacc project scaffold exists in the calc/ subdirectory. Start by running:

  cd calc
  ls
  cat calc.fsproj

The project has calc.fsproj (wired for FsLex/FsYacc with --unicode --module Lexer flags)
and Parser.fsy (a placeholder). The .fsproj expects FsLex to read Lexer.fsl and generate
Lexer.fs. The parser (task 3) will declare and use these exact token names:
  INT (of int), PLUS, MINUS, STAR, SLASH, LPAREN, RPAREN, EOF

Your task: Write calc/Lexer.fsl — the FsLex lexer source — that tokenizes integer
arithmetic expressions.

Requirements:
- Open Parser in the header block (the token names are declared there).
- Open FSharp.Text.Lexing in the header block (needed for LexBuffer access).
- Skip whitespace (space and tab).
- Match one or more digits and return INT carrying the parsed integer value.
  Use LexBuffer<_>.LexemeString lexbuf to get the matched string, then parse to int.
- Match '+', '-', '*', '/', '(', ')' and return PLUS, MINUS, STAR, SLASH, LPAREN, RPAREN.
- Match eof and return EOF.
- Match any unexpected character with a failwithf error.

FsLex syntax note: FsLex (.fsl files) does NOT use %% section separators (that is FsYacc
syntax). FsLex format is: { header code } then rule name = parse | pattern { action } ...
The rule name for this project must be: tokenize (so Parser.start calls Lexer.tokenize).

After writing Lexer.fsl, confirm it with:
  cat Lexer.fsl

Constraints:
- Do NOT create or modify calc.fsproj.
- Do NOT write Parser.fsy yet — only Lexer.fsl is needed in this task.
- Do NOT attempt to build yet — the parser source is not written yet.
```

**Rationale for API hint (`LexBuffer<_>.LexemeString lexbuf`):** The live probe showed 122B uses wrong APIs (`int s` on char array, `Lexing.lexemeChar`). Without this hint, the lexer will build-fail on the first `dotnet build` attempt with an API error rather than a logic error — this is noise, not signal. Including the API hint keeps the test focused on "can 122B write FsLex logic?" rather than "does 122B know an obscure F# Lexing API?". The `%%` note prevents the same fundamental confusion that defeated 35B (format, not logic).

**Alternative (harder, more revealing):** Omit both the `LexBuffer<_>.LexemeString` hint and the `%%` note — pure unaided. Accept that the run may need more fix iterations. If the planner wants maximum honesty/difficulty, this is fine but increases run time and retry complexity.

**Recommended: include the API hint and %% note** — this tests the right thing (FsLex rule logic) and gives the agent a fair shot at succeeding without repeated trivial API errors.

### 2.4 Task 3 — Parser: Unchanged

v1 task3-parser.txt is correct as-is. The token names in the prompt must match the names in the unaided Lexer.fsl — which we've specified in task2, so they match. No change needed.

### 2.5 Task 4 — Evaluator: Use Bash-Only Variant

Use v1 task4-evaluator.txt (the original), NOT task4-evaluator-adjusted.txt. The original already says "IMPORTANT: ... bash heredocs only ... do NOT use file_editor". This is the correct baseline behavior confirmed to work in v1 attempt 2.

Update workdir reference: `oh-workdir-122b` instead of `oh-workdir`.

### 2.6 Task 5 — Build&Test: Unchanged

v1 task5-buildtest.txt is correct. Update workdir reference only.

### 2.7 Task 6 — Conditional Fix: Unchanged

v1 task6-fix.txt. Used only if task5 fails. Update workdir reference.

---

## 3. RETRY / FALLBACK POLICY

### 3.1 Unaided Lexer Retry Budget

| Attempt | Condition | Action |
|---------|-----------|--------|
| task2 attempt 1 | Always | Run unaided-first prompt; capture JSONL as task2-lexer-unaided.jsonl |
| task2 attempt 2 | If attempt 1 STUCK or completely wrong (no valid FsLex syntax, e.g., .fsy content) | Retry with slightly more explicit prompt; capture as task2-lexer-unaided-retry.jsonl |
| fallback | If 2 unaided attempts both fail to produce a parseable Lexer.fsl | Provide v1 lexer verbatim (task2-lexer-scaffold.txt = v1 task2-lexer.txt); DISCLOSE in manifest |

**Fallback threshold — operational definition:**
- A "failed" unaided attempt = the Lexer.fsl produced by the agent causes `dotnet build` to fail with a LEXER error (not a parser or evaluator error), AND the agent's JSONL shows it got stuck (no FinishAction, OR same repeated commands, OR ConversationErrorEvent).
- If the agent produces a Lexer.fsl that fails build but the agent SELF-CORRECTS within the same task run — that is NOT a failure; it's a genuine error-and-fix. Let it succeed.
- If the build error is in Lexer.fs (generated) and traceable to a wrong API call in Lexer.fsl, that counts as self-correctable — give the agent task5 build&test to discover and fix it.

**Key rule:** Build errors that happen in task5 (not task2) are NORMAL error-and-fix — not a lexer failure. The unaided attempt "succeeds" if the agent writes a syntactically valid Lexer.fsl in task2, even if the generated Lexer.fs needs fixing in task5.

### 3.2 Honesty-Preserving Fallback Disclosure

If fallback is taken, the CAPTURE-MANIFEST must record:

```markdown
### Lexer Outcome: SCAFFOLDED (fallback)
- Unaided attempt 1 result: [brief description of failure, e.g., "agent produced FsYacc-style %% separators"]
- Unaided attempt 2 result: [if tried, brief description]
- Fallback: v1 Lexer.fsl provided verbatim (same content as 35B run) via task2-lexer-scaffold.txt
- Disclosure: The 122B could not write a valid FsLex lexer unaided. Scaffolding was provided.
  RUN122-02 requirement: PARTIAL (run captured, outcome disclosed).
```

If unaided attempt succeeds (even with build errors fixed in later tasks):

```markdown
### Lexer Outcome: UNAIDED SUCCESS
- Unaided attempt: 1 (or 2)
- Agent-written Lexer.fsl: [brief description of what the agent wrote]
- Lexer build errors (if any): [description, e.g., "wrong API — fixed in task5"]
- RUN122-01: PASS (lexer was agent-authored, not provided)
```

**The rule on manual edits:** Zero manual edits to agent-written files between tasks. If the agent produces a broken Lexer.fsl, the next task prompt can tell the agent "the build failed with [specific error]" so it can self-fix — but no human-edited replacement. This is the v1 attempt-1 lesson: the manual lexer fix in attempt-1 was classified as a deviation and attempt-1 was discarded. Same rule applies here.

### 3.3 Retry Policy for Non-Lexer Tasks

Same as v1 B7 retry policy (from 03-RESEARCH.md):

| Situation | Detected by | Action |
|-----------|-------------|--------|
| Task completed, tests pass | FinishAction + correct outputs | Keep log; move to next task |
| Task completed, tests fail | FinishAction + wrong output | Add task6-fix with failing output shown |
| MaxIterations | ConversationErrorEvent in JSONL | Retry task up to 2x; then split |
| Agent stuck | No FinishAction, repeated commands | Retry with more explicit prompt |
| No TerminalActions at all | Zero TA events | Agent misunderstood; rewrite prompt |

---

## 4. CAPTURE MECHANICS

### 4.1 Scratch Workdir

Use `oh-workdir-122b/` — entirely separate from `oh-workdir/` (35B run lives there).

- Path: `/Users/ohama/projs/OpenHandsTests/oh-workdir-122b/`
- Must be added to `.gitignore` (alongside `oh-workdir/`) before the run starts.
- Subdirectory for calc project: `oh-workdir-122b/calc/`
- JSONL files land directly in `oh-workdir-122b/` (same pattern as v1 `oh-workdir/`)

**Add to .gitignore:**
```
oh-workdir-122b/
```

Confirm gitignore works before running: `git check-ignore oh-workdir-122b` should return `oh-workdir-122b`.

### 4.2 Invocation Command

Proven v1 invocation with model alias swapped:

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL="openai/qwen-122b" \
  LLM_BASE_URL="http://127.0.0.1:4000/v1" \
  LLM_API_KEY="dummy" \
  OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-122b" \
  openhands --headless --json --yolo --override-with-envs \
  -t "$(cat task-prompts-122b/task1-scaffold.txt)" \
  2>oh-workdir-122b/task1-scaffold.stderr.log \
  | tee oh-workdir-122b/task1-scaffold.jsonl
```

Repeat pattern for each task, substituting the task file name and JSONL output name.

Note: `--override-with-envs` is required for the env-var LLM config to take effect. This is proven in v1.

### 4.3 Per-Task JSONL Naming Convention

```
oh-workdir-122b/task1-scaffold.jsonl
oh-workdir-122b/task1-scaffold.stderr.log
oh-workdir-122b/task2-lexer-unaided.jsonl        ← first attempt (always)
oh-workdir-122b/task2-lexer-unaided.stderr.log
oh-workdir-122b/task2-lexer-unaided-retry.jsonl  ← only if retry needed
oh-workdir-122b/task2-lexer-scaffold.jsonl       ← only if fallback taken
oh-workdir-122b/task3-parser.jsonl
oh-workdir-122b/task3-parser.stderr.log
oh-workdir-122b/task4-evaluator.jsonl
oh-workdir-122b/task4-evaluator.stderr.log
oh-workdir-122b/task5-buildtest.jsonl
oh-workdir-122b/task5-buildtest.stderr.log
oh-workdir-122b/task6-fix.jsonl                  ← only if task5 fails
```

**JSONL naming records the attempt history** — the file names themselves are evidence (e.g., presence of `task2-lexer-unaided-retry.jsonl` proves 2 unaided attempts were made before accepting outcome).

### 4.4 Detecting Lexer-Written-Unaided vs Scaffolded

From the JSONL:
- **Unaided signal:** task2-lexer-unaided.jsonl contains TerminalAction events writing to `Lexer.fsl` AND the content is agent-generated (not the verbatim v1 lexer). Check: `grep -o '"command":"[^"]*Lexer.fsl[^"]*"' task2-lexer-unaided.jsonl | head -5` — presence means agent wrote the file. Content differs from v1 provided lexer.
- **Scaffolded signal:** task2-lexer-scaffold.jsonl exists (file name itself is the record).
- **What to look for in agent-written lexer:** presence of `rule tokenize = parse` and FsLex pattern syntax (not `%%`). Differences from v1 lexer (different API call, different whitespace regex, etc.) are proof it's agent-authored.

Python snippet to extract agent-written Lexer.fsl content from JSONL for verification:
```python
import json
events = [json.loads(l) for l in open('oh-workdir-122b/task2-lexer-unaided.jsonl') if l.strip().startswith('{')]
for e in events:
    if e.get('kind') == 'ActionEvent':
        cmd = e.get('action', {}).get('command', '')
        if 'Lexer.fsl' in cmd or 'lexer.fsl' in cmd.lower():
            print('WROTE Lexer.fsl via:', cmd[:200])
```

### 4.5 Measuring Per-Call Timing from JSONL

The JSONL timestamp field on each event allows timing measurement:

```python
import json, dateutil.parser
events = [json.loads(l) for l in open('oh-workdir-122b/task3-parser.jsonl') if l.strip().startswith('{')]
action_times = {}
for e in events:
    if e.get('kind') == 'ActionEvent':
        action_times[e['id']] = e['timestamp']
    elif e.get('kind') == 'ObservationEvent':
        act_id = e.get('action_id')
        if act_id and act_id in action_times:
            t0 = dateutil.parser.parse(action_times[act_id])
            t1 = dateutil.parser.parse(e['timestamp'])
            dt = (t1 - t0).total_seconds()
            print(f'{e["observation"]["command"][:60]}: {dt:.1f}s')
```

This gives per-action timing — the LLM inference time is the gap between TerminalAction emission and TerminalObservation receipt (which includes command execution time, but bash commands are near-instantaneous for most ops).

**What Phase 7 needs from Phase 6 timing data:**
- Per-call wall clock for each TerminalAction → TerminalObservation pair (all tasks)
- Total wall clock per task (first event timestamp to last event timestamp in each JSONL)
- These numbers go into CMP-01 (speed comparison chapter)

### 4.6 Committed Artifacts Structure

After the run, commit under:
```
.planning/phases/06-capture-the-122b-openhands-run/captured/
├── CAPTURE-MANIFEST.md
├── logs/
│   ├── task1-scaffold.jsonl
│   ├── task2-lexer-unaided.jsonl
│   ├── task2-lexer-unaided-retry.jsonl  (if exists)
│   ├── task2-lexer-scaffold.jsonl       (if fallback taken)
│   ├── task3-parser.jsonl
│   ├── task4-evaluator.jsonl
│   ├── task5-buildtest.jsonl
│   └── task6-fix.jsonl                  (if used)
├── transcript.md                         (human-readable summary per task)
├── final-source/
│   ├── calc.fsproj
│   ├── Lexer.fsl
│   ├── Parser.fsy
│   └── Program.fs
└── test-output.txt                       (host re-run of 3 test cases)
```

This mirrors the v1 `03-capture-the-openhands-run/captured/` structure exactly, making Phase 7's comparison work straightforward.

### 4.7 CAPTURE-MANIFEST Required Fields (for Phase 7)

The CAPTURE-MANIFEST.md must record (Phase 7 CMP-01/CMP-02 consume these):

```markdown
## Run Metadata
- Run date: [date]
- Model: openai/qwen-122b (Qwen2.5-122B via litellm @ http://127.0.0.1:4000/v1, :8001)
- OpenHands version: SDK v1.21.0 / CLI 1.16.0
- Workspace: oh-workdir-122b/ (LocalWorkspace, host PTY)

## Lexer Outcome (RUN122-01/02)
- did-lexer-unaided: YES/NO
- unaided-attempts: N
- lexer-description: [brief description of what agent wrote, or "v1 scaffold used"]
- fallback-disclosure: [if scaffolded, why + what was provided]

## Error-and-Fix Record (RUN122-03)
- error-description: [what went wrong, agent-seen error messages]
- fix-description: [what the agent changed to fix it]
- location-in-jsonl: [task file, event range]

## Test Results (RUN122-03)
- 2+3*4: [actual output]
- (2+3)*4: [actual output]
- 10-3-2: [actual output]
- all-pass: YES/NO

## Timing Summary (CMP-01)
- task1-scaffold: total [Xs]
- task2-lexer: total [Xs] (N TerminalActions)
- task3-parser: total [Xs] (N TerminalActions)
- task4-evaluator: total [Xs] (N TerminalActions)
- task5-buildtest: total [Xs] (N TerminalActions)
- per-LLM-call-avg: [Xs] (from ObservationEvent gaps)
- total-run: [Xs]

## Comparison Hook (for Phase 7)
- vs-35B-lexer: [35B couldn't write FsLex unaided; 122B did/did not]
- vs-35B-error-fix: [comparison of error complexity]
- vs-35B-speed: [122B ~Xs/call vs 35B ~14-32s/call from v1 RUN-NOTES]
```

---

## 5. WHAT IS ONLY KNOWABLE FROM THE ACTUAL RUN

These items cannot be pre-determined — record them during execution:

1. **Did 122B write a valid FsLex lexer in task2?** The live probe suggests it will write plausible FsLex syntax but with API bugs. Whether those bugs are in the header (which can cause indentation issues in generated Lexer.fs) or in the rule actions (which cause type errors) affects how many fix iterations are needed.

2. **Will the build error be in Lexer.fsl or Parser.fsy?** Both are plausible. If 122B writes both task2 (lexer) and has issues in task3 (parser), the error-and-fix story may be different from v1.

3. **Per-task wall clock times** — only from actual JSONL timestamps.

4. **Did 122B handle the FixLineDirectives correctly?** Task1 provides the .fsproj verbatim, so this should just work — but if the agent modifies .fsproj (as v1 attempt-1 task3 agent did), it's a new observation to document.

5. **Did 122B use file_editor (triggering security_risk errors)?** The bash-only prompt constraint is expected to prevent this, but verify in the JSONL (look for AgentErrorEvent with `file_editor`).

**During execution:** Check each JSONL after it lands. If unexpected behavior occurs (agent modifying wrong file, using file_editor, getting stuck immediately), document in RUN-NOTES.md before moving to the next task.

---

## Standard Stack (Unchanged from v1)

| Component | Version | Notes |
|-----------|---------|-------|
| OpenHands CLI | 1.16 | `openhands --headless --json --yolo --override-with-envs` |
| OpenHands SDK | 1.21.0 | LocalWorkspace; agent runs on host, no container |
| litellm proxy | @ 127.0.0.1:4000 | qwen-122b → :8001 (launchd: com.ohama.qwen122b) |
| Model alias | openai/qwen-122b | Served as OpenAI-compatible API |
| dotnet | 10.0.203 | On host path; agent uses directly |
| FsLexYacc | 11.3.0 | In NuGet cache at ~/.nuget/packages/fslexyacc/11.3.0/ |

**NuGet cache:** FsLexYacc 11.3.0 is in local cache from v1 run. `dotnet add package FsLexYacc` or `dotnet restore` will be instantaneous (no network needed).

---

## Common Pitfalls (from v1 + live probe)

### Pitfall 1: Agent Writes FsYacc-Style Content in Lexer.fsl
**What goes wrong:** Agent uses `%%` separator or `%token` declarations in Lexer.fsl (yacc habits).
**Why it happens:** Strong training data for yacc/bison overshadows FsLex-specific knowledge.
**How to avoid:** Task2 prompt includes the `%%` note and `rule tokenize = parse` structure description.
**Detection:** `grep '%%' oh-workdir-122b/calc/Lexer.fsl` → non-empty = problem.

### Pitfall 2: Wrong Lexeme Extraction API
**What goes wrong:** Agent uses `int lexbuf.Lexeme` or `Lexing.lexemeChar` instead of `LexBuffer<_>.LexemeString lexbuf`.
**Why it happens:** The F# FsLexYacc API is obscure; the task2 prompt includes the correct API name to prevent this.
**Detection:** Build error `FS0039` or `FS0001` in Lexer.fs.

### Pitfall 3: Agent Modifies Lexer.fsl During Parser Task
**What goes wrong:** Task3 agent violates "Do NOT modify Lexer.fsl" and corrupts it.
**Why it happens:** v1 attempt-1 task3 agent did exactly this (added `[<reflaction:remove>]` annotations).
**How to avoid:** Keep the constraint in task3 and task4 prompts. Do NOT mention Lexer.fsl except to say "do not touch it."
**Detection:** After task3 JSONL lands, run `cat oh-workdir-122b/calc/Lexer.fsl` and verify it matches what task2 produced.

### Pitfall 4: file_editor Tool Errors
**What goes wrong:** Agent uses file_editor without security_risk field → AgentErrorEvent → task fails.
**Why it happens:** 122B may default to file_editor; the bash-only constraint prevents this.
**Detection:** `grep '"file_editor"' task3-parser.jsonl` → AgentErrorEvents present.
**Recovery:** If task fails due to file_editor, retry with explicitly strengthened bash-only constraint.

### Pitfall 5: indented header causing F# module error in generated Lexer.fs
**What goes wrong:** Agent writes `{    open Parser }` (indented content inside `{}`). FsLex generates the content indented in Lexer.fs, causing `error FS0222: file must start with namespace or module declaration` or similar indentation error.
**Why it happens:** Observed in v1 attempt-1 (header indentation from FsLex generation).
**How to avoid:** The task2 prompt says `open FSharp.Text.Lexing` (at column 0 in examples); agent usually follows the example indentation shown.
**Detection:** Build error FS0222 or FS0003 in generated Lexer.fs.

---

## Open Questions

1. **Will 122B succeed unaided in 1 or 2 attempts?**
   - What we know: Live probe shows 122B knows FsLex format but has API bugs. The API hint in the task2 prompt should prevent the main API error.
   - What's unclear: Whether 122B will produce a syntactically valid `.fsl` that compiles through to a working lexer.
   - Recommendation: Run unaided attempt with the recommended task2 prompt. Observe task2 JSONL and check `Lexer.fsl` content before proceeding to task3.

2. **Will 122B generate more or fewer error-fix iterations than 35B in parser/evaluator tasks?**
   - What we know: 35B took 4 iterations in task3-parser. 122B may be better at FsYacc.
   - What's unclear: 122B could also get stuck on something different.
   - Recommendation: Monitor task3 JSONL for FinishAction; if 186+ events and no FinishAction (like v1 attempt-1), kill and retry.

3. **Can the 122B inference speed measurement be extracted from JSONL timestamps accurately?**
   - What we know: JSONL events have ISO8601 timestamps. TerminalAction → TerminalObservation gap includes bash command time. For `dotnet build` this is 5–30s; for simple commands it's <0.1s. LLM inference time is the gap between TerminalObservation (returned to model) and next TerminalAction (model generates next command).
   - What's unclear: Exact attribution of LLM time vs command time in each event gap.
   - Recommendation: Compute ObservationEvent → next ActionEvent gap (that's pure LLM time). This is what Phase 7 needs for the speed comparison.

---

## Sources

### Primary (HIGH confidence — live probes run during this research session)
- Direct `curl http://127.0.0.1:4000/v1/models` → confirmed qwen-122b present
- Direct Python tool-call test → confirmed tool_calls finish_reason, valid JSON function call
- Direct speed measurements → 1.11–10.59s depending on generation length; ~27–47 tok/s

### Secondary (HIGH confidence — from v1 captured runs on this same machine)
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/03-RESEARCH.md` — FsLexYacc 11.3.0 + .NET 10 toolchain facts (verified by live build on this machine)
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/03-02-RUN-NOTES-attempt1.md` — 35B FsLex failure (attempt 1)
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/03-02-RUN-NOTES.md` — 35B success with scaffolded lexer (attempt 2)
- `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/CAPTURE-MANIFEST.md` — v1 artifact map

### Tertiary (MEDIUM confidence — FsLex API behavior from live probe + v1 evidence)
- Live probe of 122B on FsLex writing task → observed format awareness, API bugs (`int s`, `Lexing.lexemeChar`)
- v1 attempt-1 notes on FsLex indentation bug → confirmed cause in 03-02-RUN-NOTES-attempt1.md

---

## Metadata

**Confidence breakdown:**
- 122B proxy up / tool-call works: HIGH — directly observed
- 122B speed (~27-47 tok/s, 1.1–10.6s per call): HIGH — measured
- 122B FsLex knowledge (plausible format, wrong API): MEDIUM — one probe, not a full agent run
- Unaided-first task prompt design: HIGH — based on v1 failure analysis + live probe findings
- Retry/fallback policy: HIGH — same logic as v1, no new unknowns
- JSONL capture mechanics: HIGH — identical to v1 (same OpenHands version, same LocalWorkspace)

**Research date:** 2026-05-28
**Valid until:** This research is tied to specific software versions (OpenHands 1.16, litellm serving qwen-122b, dotnet 10.0.203, FsLexYacc 11.3.0) and measured live. Valid as long as these versions are unchanged (~30 days or until system update).
