# 10-02 RUN-NOTES — 35B Scala Calculator Capture

Run date: 2026-06-01. Model: `openai/qwen-35b` via litellm proxy @ 127.0.0.1:4000. OpenHands CLI 1.16.0, --headless --json --yolo. scala-cli 1.14.0 (Scala 3.8.3 default), JDK 17.0.19. Workdir: `oh-workdir-scala/` (gitignored).

Honesty discipline (carried v1/v1.1/v1.2): zero manual edits to agent files; no fabricated output; scaffold disclosed if invoked; the `~14–32s/call` figure is a v1 prediction and is NOT cited as a measurement.

> **Event-numbering convention note:** the per-task event indices in the sections below use **0-based** `enumerate()` positions (a scratchpad convention). The committed `captured-scala/CAPTURE-MANIFEST.md` — **authoritative for all Phase 11 citations** — uses **1-based** JSONL positions (i.e. +1 vs the lists below). The error-and-fix *content* is identical under both. Phase 11 must cite the MANIFEST's numbers, not these.

---

## task1-scaffold

- invocation: `OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL="openai/qwen-35b" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" OPENHANDS_WORK_DIR=".../oh-workdir-scala" openhands --headless --json --yolo --override-with-envs -t "$(cat task-prompts-scala/task1-scaffold.txt)" 2>...task1-scaffold.stderr.log | tee ...task1-scaffold.jsonl`
- wall-clock: 2026-06-01T14:40:30 → 14:41:01 (~31s)
- jsonl-counts: kinds={MessageEvent:2, ActionEvent:9, ObservationEvent:9} TerminalActions=4 FinishAction=false ConvError=false NonZeroExits=0 (settled via final MessageEvent — same as v1/v1.2; no FinishAction is normal for OH 1.16)
- agent-set-up-scala-cli: YES — event #5 `scala-cli --version` (source=agent) and event #15 `cd .../calc && scala-cli run Hello.scala` (source=agent)
- scala_ok-printed: YES — event #16 ObservationEvent, `scala-cli run` command, exit=0, content contains `SCALA_OK`
- disk-state: `calc/Hello.scala` present (Y). Contents: `@main def hello() = println("SCALA_OK")` — **agent used the Scala 3 `@main def` idiom unprompted** (early signal the model emits Scala 3, not Scala 2 `object extends App`).
- outcome: **PASS** — agent verified scala-cli itself and ran a trivial Scala 3 file to SCALA_OK. SCAL-01 self-setup captured.

---

## task2-write-calc (UNAIDED)

- invocation: same headless pattern with `task-prompts-scala/task2-write-calc.txt` → `task2-write-calc.jsonl`
- wall-clock: 2026-06-01T14:42:16 → 14:45:11 (~2m55s)
- jsonl-counts: kinds={MessageEvent:2, ActionEvent:20, ObservationEvent:20} TerminalActions=20 FinishAction=false ConvError=false NonZeroExits=(writes only)
- did-write-calc-unaided: **YES**
- unaided-attempts: 1
- scaffold-invoked: **NO**
- agent wrote Calc.scala via bash heredoc/printf (all source=agent): write ActionEvents at #5, #11, #29, #31, #33, ... (7 write events — agent built/rewrote the file iteratively within task2)
- Calc.scala line count: 70
- Calc.scala description: **Idiomatic Scala 3.** Entry point `@main def calc(args: String*)` (Scala 3 `@main`, NOT `object extends App`). `class ExprParser(input: String):` using Scala 3 significant-indentation / `:` syntax; `if … then … else`, `while … do`, `peek() match { case Some('+') => … }` throughout. Hand-rolled recursive descent: `parseExpression` (`+`/`-`) → `parseTerm` (`*`/`/`) → `parseFactor` (digits / parenthesised sub-expr). Correct operator precedence. **Left-associative** via `var left = parseTerm(); while true do … left = left + right` loop (so `10-3-2` should evaluate to 5 — the model did NOT fall into the naive right-recursive associativity bug the research anticipated).
- scala-idiom note: the model emitted **Scala 3** unprompted and consistently (matches the task1 `@main def` signal). No Scala 2 `object extends App` slip.
- minor in-task detour (not a failure): early write events (#5/#11) briefly contained non-Scala / Python-flavoured fragments (`import os`, `lines = [`) — the agent self-corrected within task2 and the final on-disk Calc.scala is clean Scala 3.
- **latent compile bug (source inspection — to be discovered in task3, NOT pre-fixed):** `pos` is declared `private var pos = 0` (line 10) but `@main` accesses `parser.pos` (lines 5–6). This should produce a compile error (private member access) that the agent must self-correct in task3. Left as-is — no operator edit. Recorded here as an observation; task3 captures what actually happens.
- outcome: **UNAIDED SUCCESS** — plausible, mostly-correct idiomatic Scala 3 calculator written with no help. SCAL-02 unaided-first satisfied; proceed to task3 for compile + the three canonical tests.

---

## task3-buildtest

- invocation: same headless pattern with `task-prompts-scala/task3-buildtest.txt` → `task3-buildtest.jsonl`
- wall-clock: 2026-06-01T14:52:18 → 14:52:48 (~30s; warm cache, efficient fix)
- jsonl-counts: kinds={MessageEvent:2, ActionEvent:7, AgentErrorEvent:1, ObservationEvent:6} TerminalActions=6 FinishAction=false (settled via final MessageEvent)
- deviation (harmless, same as v1.2): event #2 AgentErrorEvent — agent tried the `file_editor` tool, got a validation error, and recovered by using bash (`cat` then `scala-cli`/`sed`). Not a run failure.

### Error-and-fix sequence (the core 7부 material)
1. event #5 (ActionEvent, source=agent): `scala-cli run Calc.scala -- "2+3*4"`
2. **event #6 (ObservationEvent, exit=1) — GENUINE COMPILE ERROR:** `./Calc.scala:5:6 ... variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level` — the private-`pos` access bug from the unaided task2 source.
3. **event #7 (ActionEvent, source=agent) — AGENT'S OWN FIX:** `sed -i '' 's/private var pos = 0/var pos = 0/' Calc.scala` (made `pos` non-private). event #8 (exit=0) confirms the sed applied.
4. event #9 (ActionEvent) / **event #10 (ObservationEvent, exit=0): `2+3*4` → `14`** (compiled + ran clean)
5. event #11 / **event #12 (exit=0): `(2+3)*4` → `20`**
6. event #13 / **event #14 (exit=0): `10-3-2` → `5`** (left-associative — correct)

### canonical-test-results (SCAL-03 — verbatim from task3 JSONL)
| input | expected | actual | exit | event | result |
|-------|----------|--------|------|-------|--------|
| `2+3*4` | 14 | `14` | 0 | #10 | PASS |
| `(2+3)*4` | 20 | `20` | 0 | #12 | PASS |
| `10-3-2` | 5 | `5` | 0 | #14 | PASS |

- compile-status: **PASS after 1 self-corrected compile error** (private-member access → `sed` to drop `private`)
- all-pass: **YES** (14 / 20 / 5)

---

## Final Summary

- did-write-calc-unaided: **YES** (idiomatic Scala 3, unaided attempt 1)
- scaffold-invoked: **NO** (the fallback was staged but never triggered)
- compile-status: **PASS** after exactly one genuine error-and-fix cycle
- canonical-test-results: `2+3*4 → 14` (#10), `(2+3)*4 → 20` (#12), `10-3-2 → 5` (#14) — all PASS, all exit 0, all real terminal ObservationEvents
- all-pass: **YES**
- error-and-fix narrative: ONE genuine compile error — `variable pos cannot be accessed ... from the top-level` (task3 event #6, exit 1), caused by `pos` being `private` in the agent's unaided source while `@main` accessed `parser.pos`. Agent self-corrected via `sed` removing `private` (event #7), recompiled, and all three tests passed. (Also: a harmless `file_editor` AgentErrorEvent at #2, recovered to bash — same as v1.2.)
- scala-idiom-notes: **Scala 3 throughout, unprompted.** Entry point `@main def calc(args: String*)` (not `object extends App`). `class ExprParser(input: String):` with significant-indentation / `:` blocks; `if/then/else`, `while/do`, `peek() match { case Some('+') => ... }`. Hand-rolled recursive descent (expr → term → factor), correct precedence, left-associative loops. NO Scala 2-vs-3 slip occurred.
- timing (REAL measured wall clock — the legacy ~14–32s/call figure is a v1 PREDICTION and is NOT cited here as a measurement): task1 ~31s (4 TA) · task2 ~2m55s (20 TA) · task3 ~30s (6 TA). Total active agent time across the three tasks ≈ 3m56s; 30 TerminalActions total.
- deviations: (1) file_editor AgentErrorEvent at task3 #2 (recovered to bash); (2) brief non-Scala/Python-flavoured fragment early in task2 (self-corrected within task2). No library-add attempts; no `scalac`-direct attempts; no scaffold needed.
- honesty-check: **zero manual edits to agent files; no fabricated success.** Every fix (the `sed` on Calc.scala) was the agent's own ActionEvent (source=agent). Honesty-gate preview across all JSONLs: 36 ActionEvents, 0 with source≠agent = PASS.
