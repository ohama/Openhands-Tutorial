# Phase 3: Capture the OpenHands Run - Context

**Gathered:** 2026-05-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Have OpenHands (headless CLI on `openai/qwen-local`, LocalWorkspace = host) **autonomously build the F# FsLex/FsYacc calculator**, and capture the real session to logs. The run is decomposed into ≥5 scoped tasks, must contain at least one genuine error-and-fix cycle, and must end with the calculator correctly evaluating `2+3*4 → 14`.

This phase CONDUCTS and CAPTURES the run. Writing the walkthrough chapter from the capture is Phase 4; troubleshooting/reproducibility/publish is Phase 5. The proven invocation (from Phase 2 / 02-VERIFICATION-EVIDENCE.md) is:
```
LLM_MODEL="openai/qwen-local" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="<scratch dir>" \
openhands --headless --json --yolo --override-with-envs -t "<task>" | tee <log>.jsonl
```
</domain>

<decisions>
## Implementation Decisions

### Calculator scope & grammar
- Operators: **`+ - * /` with parentheses**. (Unary minus NOT required for v1 of the example.)
- Numbers: **integers only** (cleanest lexer, cleanest precedence demo).
- Invocation: **CLI argument** — `calc "2+3*4"` prints `14`. (Not a REPL — easier to drive/verify headlessly.)
- Success cases that MUST pass: **`2+3*4 = 14` AND `(2+3)*4 = 20`** (proves both precedence and grouping). The agent/build-test task should run both.
- Built with FsLex + FsYacc specifically (FsLexYacc), .NET on host (dotnet 10.0.203), per project constraints.

### Task decomposition & prompting
- **5 scoped tasks**, one OpenHands invocation each, all sharing one working dir so each task sees the prior task's files:
  1. Scaffold the F# project (.fsproj wired for FsLexYacc)
  2. Write the lexer (.fsl)
  3. Write the parser (.fsy)
  4. Write the evaluator + CLI entry (Program.fs, `calc "<expr>"`)
  5. Build & run the test cases (`2+3*4`, `(2+3)*4`)
- Prompt style: **goal + key constraints** — state the goal and hard constraints (use FsLex/FsYacc, integers, CLI arg) but let the agent decide *how*.
- **Do NOT reveal the FsYacc `%left` precedence ordering** in any task prompt. Let the agent write the grammar naively so a precedence bug is likely to surface — this sets up the error-and-fix.

### The error-and-fix moment
- Discovery mechanism: the **build-&-test task (task 5)** runs the cases; if `2+3*4 ≠ 14` (or a build error occurs), the failing output lands in the agent's observation. A **follow-up task** has the agent diagnose and fix, then re-verify.
- A captured error-and-fix cycle is **REQUIRED** to call Phase 3 done (RUN-03). Keep the run that contains one.
- **Stay honest — never fabricate a bug.** Take whatever genuine error occurs. If the naive grammar happens to compile and pass first try, use whatever real error arose elsewhere (build/compile/wiring). Only if a clean run with no error at all results should we re-run (variance) to capture a genuine cycle.
- **One clear error→diagnose→fix→re-verify cycle is enough.** Extra iterations are fine but not required.

### Run capture & retry policy
- Autonomy: **fully unattended** — all 5 tasks run back-to-back with `--yolo`; review the captured logs afterward. (Truest agentic capture; no per-task checkpoints.)
- Project location: **scratch, gitignored** — agent works in `oh-workdir/calc` (already-gitignored `oh-workdir/`). The live generated project is NOT committed.
- Artifacts to KEEP/commit for Phase 4: **per-task JSONL logs + a human-readable transcript + a snapshot of the final source (.fsl/.fsy/.fs/.fsproj) + the build/test output.** (So Phase 4 can write WALK/VERIFY from real evidence even though the working dir itself is scratch.)
- Retry policy: if a task stalls/loops/fails badly on the 35B model, **re-run that task up to ~2x**; if still stuck, adjust that task's prompt and record what was changed.

### Claude's Discretion
- Exact task prompt wording, the working-dir path/structure, temperature/variance handling.
- The exact grammar/AST shape the agent produces (we don't prescribe it).
- Format of the human-readable transcript and the captured-artifacts folder layout.
- How many total run attempts before deciding a capture is "the keeper."
</decisions>

<specifics>
## Specific Ideas

- The error-and-fix should ideally be the classic **operator-precedence bug**: naive FsYacc grammar yields `2+3*4 = 20` (left-to-right) until the agent adds/orders `%left PLUS MINUS` then `%left TIMES DIVIDE`. This is the most instructive cycle — but we let it emerge naturally rather than scripting it.
- Each task is its own `openhands --headless --json --yolo --override-with-envs -t "..."` invocation, tee'd to its own per-task JSONL (e.g. `task1-scaffold.jsonl` … `task5-buildtest.jsonl`, plus any fix-task log) so Phase 4 has clean per-step evidence.
- Honesty is the project's core value — the capture is the real artifact; nothing in it is edited to look better than it was.
</specifics>

<deferred>
## Deferred Ideas

- Unary minus / floating-point support in the calculator — could be a v2 example extension (EXT-01), not this run.
- A REPL interface — out of scope; CLI-arg invocation only.
- Comparing the run against a larger/cloud model — already tracked as EXT-04 (v2).
</deferred>

---

*Phase: 03-capture-the-openhands-run*
*Context gathered: 2026-05-27*
