# ANAL-02: Qualitative Plan Comparison — v1.4 Planning A/B Study

Compares Claude's authored plan (Arm A, `claude-plan.md`) vs the 35B agent's
self-plan (Arm B, `oh-self-plan.md`) per example on: task count, granularity,
ordering, and structural match to the scaffold→write→build→test shape.

Study framing: the question is whether an expert-authored plan helps the 35B
execute — NOT "Claude plans better." Both plans are described neutrally below.
Tracker event indices are 1-based per METH-03 (Pitfall 8).

---

## 1. F# (FsLex/FsYacc Calculator)

### Claude's Plan (Arm A, `claude-plan.md`)

5 numbered steps derived from the v1 F# task decomposition:
1. Scaffold (dotnet new + wire calc.fsproj for FsLexYacc 11.3.0 + FixLineDirectives target)
2. Write Lexer.fsl (FsLex rule syntax, token names specified)
3. Write Parser.fsy (FsYacc grammar, entry point `start`, precedence declared)
4. Write Program.fs (CLI entry point, LexBuffer<char>.FromString, exact namespace)
5. Build and test (iterative: fix errors → rebuild; report exact canonical outputs)

### Self-Plan (Arm B, `oh-self-plan.md`, event #4)

5 tasks submitted at event #4 (TaskTrackerAction, initial plan):
1. Create project structure and .fsproj file — Set up F# project with FsLexYacc 11.3.0 reference
2. Create Lexer (Lexer.fsl) for tokenizing expressions — Handle integers, +, -, *, /, parentheses, whitespace
3. Create Parser (Parser.fsy) with precedence rules — Left-associative + and -, * and / bind tighter, parentheses override
4. Create main program (Program.fs) to run parser and print result — Read command-line argument, parse, evaluate, print
5. Build and run canonical tests — Test: 2+3*4=14, (2+3)*4=20, 10-3-2=5

### Comparison Table

| Dimension | Claude's Plan (Arm A) | Self-Plan (Arm B) |
|-----------|----------------------|-------------------|
| Task count | 5 steps | 5 tasks |
| Granularity | Fine — Step 1 specifies .fsproj XML structure, FixLineDirectives target, compile order, and FsYacc `--module` flags; Step 2 specifies token names (INT/PLUS/MINUS/STAR/SLASH/LPAREN/RPAREN/EOF) and FsLex-not-FsYacc syntax warning; Step 4 specifies exact namespace FSharp.Text.Lexing | Coarse — each task names the file and lists the key parsing concepts (precedence, operators) but gives no detail on .fsproj wiring, FixLineDirectives, or exact FsLex/FsYacc syntax constraints |
| Ordering | scaffold → lexer → parser → program → build/test | scaffold → lexer → parser → program → build/test |
| scaffold phase | YES — explicit (Step 1, dotnet new + full .fsproj wiring) | YES — implicit (task 1 mentions FsLexYacc 11.3.0 reference but no wiring detail) |
| write phase | YES — 3 steps (lexer/parser/program), each with exact syntax constraints | YES — 3 tasks (same three files), no exact syntax constraints |
| build phase | YES — iterative build loop with error-fix guidance | YES — combined with test in single task |
| test phase | YES — separate test step with exact verbatim commands | YES — included in task 5 as labels |
| Scaffold→Write→Build→Test match | FULL (4-phase shape, each phase explicit) | PARTIAL (same sequence, but build+test collapsed; .fsproj wiring underspecified) |

### Notes

- Both plans chose the same file-level decomposition (scaffold / lexer / parser / program / test), which is the natural ordering for an FsLexYacc project.
- Claude's plan provides technical detail that addresses known 35B failure modes: the FixLineDirectives target (which removes # 0 line directives that .NET 10 rejects), the exact compile order (Parser.fsi before Lexer.fs), and the exact FsLex rule syntax warning. None of this detail appears in the self-plan.
- The self-plan's task notes are accurate at a high level (mentions precedence rules, operator set) but omit the FsLexYacc toolchain specifics that proved critical. This matches the pattern where an OOD task exposes the gap: the self-plan is topically correct but technically underspecified.
- Neither plan included any source code (per fairness rule). Both arms wrote all source themselves.
- Run outcomes: Arm A 1/3 PASS (run-1); Arm B 0/3 PASS. The claude plan helped in run-1 (the step-by-step detail likely guided successful wiring), but the OOD nature of FsLex/FsYacc dominated across runs 2–3.

---

## 2. Rust (HTTP Server)

### Claude's Plan (Arm A, `claude-plan.md`)

3 numbered steps derived from the v1.2 Rust task decomposition:
1. Scaffold — `cargo new rust-server`; verify Cargo.toml and src/main.rs exist
2. Write server — Rewrite src/main.rs with TcpListener on port 8080, respond `hello\n`, loop; stdlib only
3. Build and test — `cargo build --release`; start server; `curl -s http://localhost:8080/`; verify `hello` exit 0

### Self-Plan (Arm B, `oh-self-plan.md`, event #4)

4 tasks submitted at event #4 (TaskTrackerAction, initial plan):
1. Initialize Rust project with Cargo — Create Cargo.toml with empty dependencies and src/main.rs
2. Implement HTTP server in main.rs — Use std::net::TcpListener to bind port 8080, read HTTP requests, respond with 'hello\n', loop
3. Build the project — Run cargo build --release
4. Run canonical test: curl -s http://localhost:8080/ — Verify output is 'hello' with newline, exit code 0

### Comparison Table

| Dimension | Claude's Plan (Arm A) | Self-Plan (Arm B) |
|-----------|----------------------|-------------------|
| Task count | 3 steps | 4 tasks |
| Granularity | Coarse-to-medium — Step 2 specifies TcpListener, port 8080, `hello\n`, loop, stdlib; Step 3 combines build + test | Fine for build/test — Self-plan separates build (task 3) from curl test (task 4) |
| Ordering | scaffold → write → build+test | scaffold → write → build → test |
| scaffold phase | YES — explicit (cargo new, verify) | YES — explicit (cargo new, Cargo.toml) |
| write phase | YES — single step with full HTTP server spec | YES — single task with same spec |
| build phase | YES — included in Step 3 | YES — explicit separate task |
| test phase | YES — included in Step 3 with exact curl command | YES — explicit separate task with exact curl command |
| Scaffold→Write→Build→Test match | FULL (build+test collapsed into one step, but both present) | FULL (all 4 phases as 4 separate tasks) |

### Notes

- The self-plan is slightly more granular than Claude's plan (4 steps vs 3 by separating build from test). Both capture the same essential steps.
- Both plans specify the same technical implementation: TcpListener, port 8080, `hello\n`, loop, stdlib.
- The self-plan's task 2 notes are nearly identical to Claude's Step 2 spec; the 35B independently identified the correct stdlib approach.
- Rust is in-distribution for the 35B; both arms produced correct implementations in all 3 reps. The plan quality difference had no observable effect on outcome at this task difficulty.
- Task tracker status updates at events #6, #16, #22, #26, #38 show the agent diligently updating each step through in_progress → done.

---

## 3. Scala (Scala 3 Calculator)

### Claude's Plan (Arm A, `claude-plan.md`)

3 numbered steps derived from the v1.3 Scala task decomposition:
1. Scaffold — `scala-cli --version`; `mkdir -p calc`; write Hello.scala; run it; verify SCALA_OK
2. Write Calc.scala — Recursive descent parser with precedence; integer arithmetic; stdlib only; show cat Calc.scala
3. Build and test — `scala-cli run Calc.scala -- "2+3*4"` (compilation here, fix errors); then all 3 canonical tests; report exact outputs

### Self-Plan (Arm B, `oh-self-plan.md`, event #6)

4 tasks submitted at event #6 (TaskTrackerAction, initial plan):
1. Create Calc.scala with recursive descent parser — Implement tokenizer and recursive descent parser with proper precedence: expr (low) -> term (medium) -> factor (high), plus parentheses support
2. Test canonical test 1: 2+3*4 → 14 — Verify * binds tighter than +
3. Test canonical test 2: (2+3)*4 → 20 — Verify parentheses override precedence
4. Test canonical test 3: 10-3-2 → 5 — Verify left-associative subtraction

### Comparison Table

| Dimension | Claude's Plan (Arm A) | Self-Plan (Arm B) |
|-----------|----------------------|-------------------|
| Task count | 3 steps | 4 tasks |
| Granularity | Medium — Step 1 includes explicit smoke-test verification (SCALA_OK); Step 2 calls out stdlib-only constraint and cat verification; Step 3 specifies iterative compile-fix loop | Fine for testing — Self-plan splits 3 canonical tests into separate tasks; implements a test-driven shape; omits scaffold smoke-test |
| Ordering | scaffold → write → build+test | write → test1 → test2 → test3 (no explicit scaffold) |
| scaffold phase | YES — explicit (verify scala-cli, Hello.scala smoke test) | NO — no scaffold step; jumps directly to writing Calc.scala |
| write phase | YES — Step 2 specifies recursive descent, precedence, stdlib-only | YES — Task 1 specifies recursive descent, precedence levels (expr/term/factor) explicitly |
| build phase | YES — included in Step 3 with iterative fix guidance | IMPLICIT — compilation happens on first test run |
| test phase | YES — Step 3 specifies canonical test commands verbatim | YES — 3 separate tasks, each labeled with expected output |
| Scaffold→Write→Build→Test match | FULL (scaffold explicit; build+test in one step) | PARTIAL (scaffold absent; write → tests; build implicit) |

### Notes

- The self-plan shows a different structural choice: it omits the scaffold step (scala-cli smoke test) and instead uses a test-driven decomposition where each canonical test is a separate task. This is a valid alternative decomposition.
- The self-plan's task 1 explicitly names the precedence level structure (expr/term/factor), which is the correct recursive descent parser design. This is technically accurate and more specific than Claude's Step 2 in terms of parser architecture.
- Claude's plan adds the scaffold smoke-test (SCALA_OK verification) as insurance against toolchain issues; the self-plan assumes scala-cli works and goes straight to implementation.
- The self-plan's test-as-tasks structure enabled the agent to track progress precisely: task tracker events #42, #70, #74, #78 show each test completing in sequence.
- Run outcomes: Arm A 3/3 PASS; Arm B 2/3 PASS + 1 PARTIAL-PASS. Both arms broadly succeeded on this in-distribution task. The scaffold omission in Arm B had no observable negative effect.

---

## Summary Table — Cross-Example

| Example | Claude steps | Self-plan tasks | Same ordering? | Scaffold→Write→Build→Test (Claude) | Scaffold→Write→Build→Test (Self) |
|---------|-------------|-----------------|----------------|-------------------------------------|----------------------------------|
| F# | 5 | 5 | YES | FULL | PARTIAL (build+test collapsed; wiring underspecified) |
| Rust | 3 | 4 | YES (self adds build/test split) | FULL | FULL (4 phases as 4 tasks) |
| Scala | 3 | 4 | MOSTLY (self omits scaffold, splits tests) | FULL | PARTIAL (scaffold absent, build implicit) |

**Key finding:** The orderings are consistent across arms — both plans independently choose the same fundamental decomposition (scaffold/create/build/test). The primary difference is granularity: Claude's plan adds FsLexYacc toolchain specifics (F#), CLI-verification patterns (Scala scaffold), and explicit iterative build-fix loops (both). The self-plan in Scala shows a test-driven variant that is architecturally sound and more fine-grained at the test level. Neither plan included source code; all source was written by the 35B itself.
