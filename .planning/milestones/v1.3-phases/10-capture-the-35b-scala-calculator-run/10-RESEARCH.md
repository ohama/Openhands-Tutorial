# Phase 10: Capture the 35B Scala Calculator Run — Research

**Researched:** 2026-06-01
**Domain:** scala-cli toolchain + Scala 3 ADT/pattern-matching + recursive-descent parser + 35B capture protocol
**Confidence:** HIGH (scala-cli facts from official docs + Homebrew formulae; Scala 3 syntax from official docs; parallel structure verified against v1.2 Phase 8 research which was HOST-VERIFIED)

---

## Summary

Phase 10 mirrors the Phase 8 capture protocol (Rust HTTP server) with one language swap: Scala 3 arithmetic calculator instead of Rust HTTP server. The environment is already proven (OpenHands 1.16, litellm 35B, LocalWorkspace). The primary research questions are: (1) scala-cli install/verification on this host, (2) how scala-cli selects the Scala version and how to pin Scala 3, (3) what a correct minimal Scala 3 std-only calculator looks like (scaffold fallback), (4) where the 35B is likely to stumble on Scala 3 idioms, and (5) zero-leak task prompt discipline.

**Key findings:**

- scala-cli 1.14.0 is in Homebrew (`brew install scala-cli`). Host already has Java 17 (OpenJDK 17.0.19), which satisfies scala-cli's JDK requirement.
- scala-cli defaults to the latest stable Scala 3 (currently **3.8.3** as of v1.13.0; v1.14.0 tracks ~3.8.x). A simple `//> using scala 3` directive pins any Scala 3 version. The `run` subcommand is the default — `scala-cli Foo.scala` works.
- A correct minimal implementation is single-file, uses `sealed trait Expr` (preferred over `enum` for nested recursive ADTs), a char-by-char tokenizer, and a standard expr/term/factor recursive-descent grammar. The three canonical tests (`2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5`) verify precedence AND left-associativity.
- Three top likely failure modes: (1) precedence/associativity wrong (right-assoc bug or `*` lower than `+`), (2) Scala 3-vs-2 syntax slip (missing `@main`, using `object extends App`, old `case class` with lowercase extends), (3) `scala-cli` first-run artifact download confusion (model tries `scalac` directly or doesn't wait for download).
- Task decomposition: **3 tasks** — preflight/scaffold (scala-cli project setup + trivial run) → write calculator (unaided) → build-run-verify (compile + run canonical tests).

**Primary recommendation:** 3-task decomposition; task2 prompt describes behavior only (never say "sealed trait", "recursive descent", "precedence levels", "parser function"); canonical 3-test verification in task3.

---

## Part 1: scala-cli — Install, Version, Run Commands, Preflight

### 1.1 Current Version and Install

**scala-cli version: 1.14.0** (as of Homebrew formulae checked 2026-06-01; released 2026-05-14)
Source: https://formulae.brew.sh/formula/scala-cli + https://github.com/VirtusLab/scala-cli/releases/tag/v1.14.0

**Installation methods on macOS (in priority order):**

```bash
# 1. Homebrew (recommended — standard, bottled, verified)
brew install scala-cli

# 2. SDKMAN
sdk install scalacli

# 3. Manual download (arm64 mac)
curl -sSLo /tmp/scala-cli.gz "https://github.com/VirtusLab/scala-cli/releases/download/v1.14.0/scala-cli-aarch64-apple-darwin.gz"
gunzip /tmp/scala-cli.gz
chmod +x /tmp/scala-cli
sudo mv /tmp/scala-cli /usr/local/bin/scala-cli

# 4. VirtusLab tap (community-supported, same result as option 1 but with explicit tap)
brew install Virtuslab/scala-cli/scala-cli
```

**Note on Homebrew formula:** The brew formula for scala-cli (stable 1.14.0) declares a build dependency on `openjdk@17`. This host already has `openjdk@17` (17.0.19) at `/opt/homebrew/opt/openjdk@17/bin/java` — confirmed live.

**Confidence:** HIGH — `brew info scala-cli` run on host during this research session, confirmed 1.14.0.

### 1.2 JDK Management

scala-cli does NOT bundle its own JDK by default. On first use it will:
1. Check for a system JDK on PATH / JAVA_HOME.
2. If none found, it can **download a JDK automatically** via the `--jvm` flag (e.g., `--jvm temurin:17`).
3. The Homebrew formula `build-depends-on: openjdk@17` means installing via brew also installs Java 17 if missing.

**This host:** Java 17.0.19 is already present at `/opt/homebrew/opt/openjdk@17/bin/java` (verified live). scala-cli will use it automatically after `brew install scala-cli`. No `--jvm` flag needed.

**First-run behavior:** On the very first `scala-cli run` after installation, scala-cli downloads the Scala compiler and required artifacts (BSP, zinc, etc.). This prints significant logging output and takes 30–120s depending on network. Subsequent runs use the local cache and are fast (~1–5s). The task prompt for task1 should warn the agent that the first run may take longer than usual.

Source: https://scala-cli.virtuslab.org/docs/cookbooks/introduction/scala-jvm/

### 1.3 Run Commands

```bash
# Check version (also verifies installation):
scala-cli --version
# Output example: Scala CLI version: 1.14.0
#                  Scala version (default): 3.8.3

# Run a single file (two equivalent forms):
scala-cli run Foo.scala     # explicit 'run' subcommand
scala-cli Foo.scala         # 'run' is the default subcommand

# Run with arguments passed to the program:
scala-cli Foo.scala -- arg1 arg2

# Inline code (useful for preflight ping):
scala-cli -e 'println("ok")'

# Compile without running:
scala-cli compile Foo.scala
```

**Confirm:** `scala-cli Foo.scala` and `scala-cli run Foo.scala` are equivalent. The `run` subcommand is the default.

Source: https://scala-cli.virtuslab.org/docs/commands/run/

### 1.4 Preflight Commands (for the host operator — before agent run)

These are the exact commands the operator (you) runs to produce the Phase 10 preflight report:

```bash
# 1. Check scala-cli is installed and print version
scala-cli --version

# 2. Check JDK
java -version

# 3. Trivial run — proves toolchain works end-to-end (parallel to v1.2's cargo run trivial)
echo '@main def hello() = println("PREFLIGHT_OK")' > /tmp/Preflight.scala
scala-cli run /tmp/Preflight.scala
# Expected output: PREFLIGHT_OK  (exit 0)
# Note: first run will download artifacts; subsequent runs are fast

# 4. Check scratch workdir exists and is empty / gitignored
ls oh-workdir-scala/
git check-ignore oh-workdir-scala

# 5. Confirm proxy and model (unchanged from v1.2)
curl -s http://127.0.0.1:4000/v1/models | python3 -m json.tool | grep '"id"'
```

**Preflight PASS criteria:**
- `scala-cli --version` returns `1.14.0` (or newer)
- `java -version` returns `17.x` or newer
- Trivial run prints `PREFLIGHT_OK` and exits 0
- `oh-workdir-scala/` exists, empty, gitignored
- Proxy responds with `qwen-35b` in model list

**Parallel to Phase 8:** Phase 8's preflight was `rustc --version`, `cargo --version`, `lsof -ti :8080`, workdir check, proxy check. Phase 10 preflight replaces Rust checks with scala-cli checks; removes port check (no server needed).

---

## Part 2: Scala 3 Version Selection and Key Syntax

### 2.1 Default Version and Pinning

**Default:** scala-cli defaults to the **latest supported Scala 3 version** — currently `3.8.3` (scala-cli 1.13.0+). scala-cli 1.14.0 tracks Scala 3 Next RC at 3.8.4-RC2, so production default remains `3.8.3`.

**To pin Scala 3** (recommended for reproducibility — add as first line of the `.scala` file):
```scala
//> using scala 3
```
This selects the latest stable Scala 3. To pin a specific version:
```scala
//> using scala 3.8.3
```

**Command-line alternative:**
```bash
scala-cli run Calc.scala --scala 3
# or
scala-cli run Calc.scala -S 3.8.3
```

**Recommendation for task prompts:** Include `//> using scala 3` as a directive in the task prompt's "project setup" step. This is a good practice AND reveals to the planner whether the agent retains or removes it. If the agent removes it and runs on an older Scala 2, the `@main` annotation will fail immediately — making Scala version a visible failure mode.

Source: https://scala-cli.virtuslab.org/docs/cookbooks/introduction/scala-versions/

### 2.2 Scala 3 vs Scala 2 Key Syntax Differences

A 35B model has substantial Scala training data — but much of it is Scala 2.12/2.13. The following are the specific syntax differences most likely to cause drift or errors in this task:

| Syntax Area | Scala 2 (old) | Scala 3 (correct) | Risk Level |
|-------------|---------------|-------------------|------------|
| Entry point | `object App extends App { ... }` or `def main(args: Array[String]): Unit` | `@main def run() = ...` | HIGH — agent may write the old form; it compiles but `extends App` is limited in Scala 3 (deprecated, no arg support) |
| Top-level definitions | Must be inside `object`/`class` | Can appear at top level in `.scala` files | MEDIUM — agent may unnecessarily wrap everything in an object |
| `match` syntax | `x match { case ... }` | `x match { case ... }` (unchanged) OR `x match\n  case ...` (indentation syntax) | LOW — both work, agent likely uses braces form |
| Optional braces | Not applicable | `if condition then ... else ...` (no parens) | MEDIUM — agent may write old `if (cond)` form; works but is Scala 2 style |
| ADT via `enum` | `sealed trait` + `case class` | Either `sealed trait` + `case class` OR `enum` with `case` variants | MEDIUM — enum is new Scala 3, agent may prefer sealed trait (preferred for recursive ADT) |
| `enum` case with params | n/a | `enum Expr:\n  case Num(n: Int)\n  case Add(l: Expr, r: Expr)` | LOW if agent uses sealed trait; HIGH if agent uses enum incorrectly |
| `given`/`using` | `implicit val / implicit def` | `given` / `using` | LOW — not needed for this task |
| Wildcard type | `_` | `?` in Scala 3.3+ (but `_` still accepted) | LOW |
| `case class` extends | `case class Foo(x: Int) extends Bar` | Same | LOW — unchanged |

**Most critical for this task:**
1. `@main` vs `object extends App` — agent must use `@main` for scala-cli compatibility (or a regular `def main(args: Array[String]): Unit`)
2. `enum` vs `sealed trait` for the Expr ADT — either works; `sealed trait` is more idiomatic for recursive ADTs (see §3)
3. Top-level `def` and `val` — Scala 3 allows these at file scope without an enclosing `object`; agent may or may not use this

**Confidence:** HIGH — based on official Scala 3 docs + common 35B training data patterns.

### 2.3 Scala 3 `enum` vs `sealed trait` for Expr ADT

**Both are valid.** For an arithmetic expression AST, both approaches work:

```scala
// Option A: sealed trait (idiomatic for recursive ADTs — recommended for this task)
sealed trait Expr
case class Num(n: Int)         extends Expr
case class Add(l: Expr, r: Expr) extends Expr
case class Sub(l: Expr, r: Expr) extends Expr
case class Mul(l: Expr, r: Expr) extends Expr
case class Div(l: Expr, r: Expr) extends Expr

// Option B: Scala 3 enum (also valid, more concise)
enum Expr:
  case Num(n: Int)
  case Add(l: Expr, r: Expr)
  case Sub(l: Expr, r: Expr)
  case Mul(l: Expr, r: Expr)
  case Div(l: Expr, r: Expr)
```

**Recommendation:** Sealed trait is preferred because:
- It is more familiar to Scala 2-trained models (less likely to have syntax errors).
- Enums with recursive type parameters can trigger edge cases in exhaustiveness checking.
- The v1.3 ROADMAP.md explicitly says "`sealed trait Expr` ADT" — this is the locked decision from the roadmap.

The agent should naturally reach `sealed trait` if not primed. If it chooses `enum`, that is fine and educational — note it in CAPTURE-MANIFEST.

**Exhaustiveness checking:** With `sealed trait`, the Scala 3 compiler will warn if a `match` is non-exhaustive. This is a GOOD tutorial story if it appears. The warning is:
```
match may not be exhaustive.
It would fail on pattern case: [unmatched case]
```
The agent will likely add a wildcard arm `case _ => throw new RuntimeException(...)` to silence this. That is fine.

---

## Part 3: Minimal Idiomatic Scala 3 Calculator (Scaffold Fallback)

This is the reference implementation the planner stages as scaffold-fallback. It is:
- Single file (`Calc.scala`)
- Runnable with `scala-cli run Calc.scala -- "2+3*4"`
- std-only — no external libraries
- Passes all three canonical tests
- Uses `sealed trait Expr` ADT + char-by-char tokenizer + recursive-descent parser (expr/term/factor) + pattern-matching evaluator

**IMPORTANT — scaffold use policy (identical to v1.2):** Stage this file but only provide it to the agent if ALL of the following are true:
1. The agent's compilation fails on the SAME error class across 3+ consecutive attempts with no syntactic variation.
2. The agent is demonstrably stuck (repeated identical fix attempts).
3. The agent is not making progress (same error, same fix, same result cycling).

If the agent writes a working calculator (even with different structure — e.g., using `enum` instead of `sealed trait`, or a different tokenizer approach), do NOT provide the scaffold. The scaffold is a fallback for genuine inability, not a style preference override.

**Disclose in CAPTURE-MANIFEST.md if used.**

```scala
//> using scala 3

sealed trait Expr
case class Num(n: Int)           extends Expr
case class Add(l: Expr, r: Expr) extends Expr
case class Sub(l: Expr, r: Expr) extends Expr
case class Mul(l: Expr, r: Expr) extends Expr
case class Div(l: Expr, r: Expr) extends Expr

// ── Tokenizer ─────────────────────────────────────────────────────────────
enum Token:
  case TNum(n: Int)
  case TPlus, TMinus, TStar, TSlash, TLParen, TRParen, TEOF

import Token.*

def tokenize(s: String): List[Token] =
  var i = 0
  val tokens = collection.mutable.ListBuffer[Token]()
  while i < s.length do
    s(i) match
      case c if c.isWhitespace => i += 1
      case c if c.isDigit =>
        var j = i
        while j < s.length && s(j).isDigit do j += 1
        tokens += TNum(s.substring(i, j).toInt)
        i = j
      case '+' => tokens += TPlus;   i += 1
      case '-' => tokens += TMinus;  i += 1
      case '*' => tokens += TStar;   i += 1
      case '/' => tokens += TSlash;  i += 1
      case '(' => tokens += TLParen; i += 1
      case ')' => tokens += TRParen; i += 1
      case c   => throw new RuntimeException(s"Unexpected char: '$c'")
  tokens += TEOF
  tokens.toList

// ── Recursive-Descent Parser ────────────────────────────────────────────
// Grammar (operator precedence via grammar hierarchy):
//   expr  → term   (( '+' | '-' ) term)*
//   term  → factor (( '*' | '/' ) factor)*
//   factor → NUMBER | '(' expr ')'
//
// Lower in the grammar = higher precedence.
// Left-associativity via left-recursive while loop.

class Parser(tokens: List[Token]):
  var pos = 0

  def peek: Token = tokens(pos)

  def consume(): Token =
    val t = tokens(pos)
    pos += 1
    t

  def expect(t: Token): Unit =
    if peek != t then throw new RuntimeException(s"Expected $t but got $peek")
    consume()

  // expr → term (( '+' | '-' ) term)*
  def expr(): Expr =
    var left = term()
    while peek == TPlus || peek == TMinus do
      val op = consume()
      val right = term()
      left = if op == TPlus then Add(left, right) else Sub(left, right)
    left

  // term → factor (( '*' | '/' ) factor)*
  def term(): Expr =
    var left = factor()
    while peek == TStar || peek == TSlash do
      val op = consume()
      val right = factor()
      left = if op == TStar then Mul(left, right) else Div(left, right)
    left

  // factor → NUMBER | '(' expr ')'
  def factor(): Expr =
    peek match
      case TNum(n) =>
        consume()
        Num(n)
      case TLParen =>
        consume()
        val e = expr()
        expect(TRParen)
        e
      case t => throw new RuntimeException(s"Unexpected token: $t")

// ── Evaluator ────────────────────────────────────────────────────────────
def eval(e: Expr): Int = e match
  case Num(n)    => n
  case Add(l, r) => eval(l) + eval(r)
  case Sub(l, r) => eval(l) - eval(r)
  case Mul(l, r) => eval(l) * eval(r)
  case Div(l, r) => eval(l) / eval(r)

// ── Entry Point ─────────────────────────────────────────────────────────
@main def calc(expression: String): Unit =
  val tokens = tokenize(expression)
  val parser = Parser(tokens)
  val ast    = parser.expr()
  println(eval(ast))
```

**To run the scaffold and verify all three canonical tests:**
```bash
# From the workdir containing Calc.scala:
scala-cli run Calc.scala -- "2+3*4"    # must print: 14
scala-cli run Calc.scala -- "(2+3)*4"  # must print: 20
scala-cli run Calc.scala -- "10-3-2"   # must print: 5
```

**Why `//> using scala 3` is included:** Locks the Scala 3 compiler regardless of future scala-cli default changes. Removes any ambiguity about Scala 2 mode.

**Why left-associativity is correct:** The while-loop approach in `expr()` and `term()` naturally produces left-associative trees. `10-3-2` parses as `Sub(Sub(Num(10), Num(3)), Num(2))` = `(10-3)-2 = 5`.

**Why this is std-only:** Only `scala.collection.mutable.ListBuffer` from the standard library is used. No `import scala.util.parsing.*` or any external dependency.

**Confidence:** HIGH (structure is a canonical text-book recursive-descent parser; algebra verified by manual trace).

---

## Part 4: Task Decomposition + Zero-Leak Prompt Discipline

### 4.1 Proposed 3-Task Split (Parallel to v1.2)

| Task | Name | Goal | Parallel to v1.2 |
|------|------|------|-----------------|
| task1 | scaffold | Create scala-cli project directory, write a trivial `println("ok")` Scala file, run it with `scala-cli run`, confirm it prints "ok" | task1-scaffold (cargo new) |
| task2 | write-calc | Write the arithmetic calculator Scala source file, unaided — no source provided, describe behavior only | task2-server (write src/main.rs) |
| task3 | buildtest | Run `scala-cli run Calc.scala` with all three canonical test inputs; fix if needed; report exact output | task3-buildtest (cargo build + curl) |

**Alternative: 4 tasks** — split task3 into (compile-only) and (run + verify). Use this if the agent confuses compilation errors with runtime errors or if it gets stuck on one aspect. The 3-task version is preferred because scala-cli's `run` command compiles and runs in one step — there is no separate "build" phase.

### 4.2 Zero-Leak Word List for task2

The task2 prompt MUST describe **behavior** (what the calculator should do), NOT **implementation** (what code to write). The following words / phrases **must not appear** in task2's prompt text:

**DO NOT include in task2 prompt:**
- `sealed trait` — leaks the ADT choice
- `case class` — leaks the data representation
- `enum` — leaks the ADT alternative
- `recursive descent` — leaks the parsing technique
- `recursive-descent` — same
- `top-down parser` — same class of parser
- `expr()`, `term()`, `factor()` — leak the function decomposition
- `precedence level` or `precedence layer` — leaks the grammar structure
- `left-associativity` or `left-assoc` — leaks how to handle `10-3-2`
- `Tokenizer`, `tokenize`, `Token` — leaks the lexer class/function name
- `ListBuffer` — leaks the implementation detail
- `pattern matching` — leaks the evaluator technique (though this is harder to avoid entirely)
- `@main` — leaks the entry point annotation
- `//> using scala 3` — leaks the directive (let the agent discover it or not)

**SAFE to include in task2 prompt (describes goal, not implementation):**
- "arithmetic expression string" — describes the input
- "evaluates to an integer" — describes the output type
- "`*` and `/` bind more tightly than `+` and `-`" — describes the required behavior
- "parentheses override normal precedence" — describes the behavior
- "operators of equal precedence associate left-to-right" — describes the behavior (acceptable because it is a REQUIREMENT, not a technique)
- "use only the Scala standard library — no external libraries" — the constraint
- "integer arithmetic only" — scopes the problem
- "`2+3*4` should evaluate to `14`" — the canonical test cases (acceptable to include)
- "show the output of running your program on these three expressions" — the verification request

**Rationale (v1.2 parallel):** v1.2's task2 said "listen on TCP port 8080 and respond to any incoming HTTP request with the text hello" — it described the protocol behavior, not the implementation. Phase 10's task2 should describe the calculator behavior, not the parser implementation technique.

### 4.3 Concrete Task Prompt Starting Text

#### task1-scaffold.txt (draft)
```
Working directory: /Users/ohama/projs/OpenHandsTests/oh-workdir-scala

The directory is empty. Your task: verify that scala-cli is installed and set up a minimal
Scala project here.

Step 1: Confirm scala-cli works.
  scala-cli --version

Step 2: Create a subdirectory for the project and write a minimal Scala file.
  mkdir -p oh-workdir-scala/calc
  cd /Users/ohama/projs/OpenHandsTests/oh-workdir-scala/calc

  Write a file named Hello.scala with this content:
    @main def hello() = println("SCALA_OK")

Step 3: Run it.
  scala-cli run Hello.scala

  Note: The first run may download compiler artifacts and take 30-60 seconds. That is normal.
  Expected output: SCALA_OK

Step 4: Confirm the output and report scala-cli version and whether the run succeeded.

Do not write any calculator code yet — a later task handles that.
```

Rationale: Tells the agent the exact directory and a trivial program to run. `@main` is acceptable here because this is infrastructure setup, not the calculator — the agent sees the scaffold convention but must still design the calculator itself. The "first run may take 30-60 seconds" note prevents the agent from treating a slow first compile as an error and panic-retrying.

#### task2-write-calc.txt (draft)
```
Working directory: /Users/ohama/projs/OpenHandsTests/oh-workdir-scala/calc

IMPORTANT: Create and edit ALL files using ONLY bash shell commands (printf, tee, or
`cat > FILE <<'EOF' ... EOF` with a quoted heredoc). Do NOT use the file_editor /
str_replace tool — it errors in this setup.

A scala-cli project directory exists here (you set it up in a previous step).

Your task: write a Scala source file named Calc.scala that, when given an arithmetic
expression string as a command-line argument, evaluates it and prints the integer result.

Requirements:
- Input: a single command-line argument, e.g. "2+3*4"
- Output: the integer result, e.g. 14
- Operators supported: + - * / with standard precedence (* and / bind more tightly
  than + and -) and left-to-right associativity for equal-precedence operators
- Parentheses override precedence, e.g. (2+3)*4 = 20
- Integer arithmetic only (no floats)
- Use ONLY the Scala standard library — no external libraries or build dependencies

After writing Calc.scala, show its contents with:
  cat Calc.scala

Do not run or compile yet — a later task handles that.
```

#### task3-buildtest.txt (draft)
```
Working directory: /Users/ohama/projs/OpenHandsTests/oh-workdir-scala/calc

IMPORTANT: Use ONLY bash shell commands. Do NOT use the file_editor tool.

A Scala source file Calc.scala exists here. Your task: run it with scala-cli and
verify it produces the correct output for these three test cases:

  scala-cli run Calc.scala -- "2+3*4"    → should print: 14
  scala-cli run Calc.scala -- "(2+3)*4"  → should print: 20
  scala-cli run Calc.scala -- "10-3-2"   → should print: 5

Step 1: Compile and run the first test.
  scala-cli run Calc.scala -- "2+3*4"

If compilation fails, read the error message, fix Calc.scala, and retry. Repeat until
the compilation succeeds or you have exhausted reasonable fixes.

Step 2: Once compilation succeeds, run all three tests.

Step 3: Report results.
State the exact output for each test case, whether it matched the expected output,
and — if you made any fixes — what errors you encountered and what you changed.

Constraints:
- Do not add external library dependencies (no build.sbt, no project/plugins.sbt,
  no scala-parser-combinators, no fastparse).
- If you fix Calc.scala, fix only the error at hand — report what you changed and why.
- Report every compilation error you encountered and how you fixed it.
- Do not modify results to make them appear successful if they are not.
```

---

## Part 5: Likely Failure Modes — 35B on Scala 3 Calculator

These are the anticipated failure modes, ordered by probability and educational value. Confidence: MEDIUM — inferred from 35B behavior pattern (from v1/v1.2) applied to Scala 3 idioms.

| # | Failure Mode | Manifestation | Surface As | Educational Value |
|---|-------------|---------------|-----------|-------------------|
| 1 | **Operator precedence / associativity bug** | Parser gives all ops equal precedence, or uses right-recursion giving right-assoc | `2+3*4 → 20` or `10-3-2 → 9` | HIGH — core parsing concept; same issue seen in v1 F# naive grammar (→9 for 10-3-2) |
| 2 | **Scala 3-vs-2 syntax slip** | Agent writes `object Calc extends App`, doesn't add `@main`, or uses old-style `new` keyword for `case class` construction | Compile error or deprecation warning | MEDIUM — reveals training data distribution |
| 3 | **scala-cli first-run artifact download** | Agent sees verbose output on first compile, interprets it as an error and panics, retries, or runs `scalac` directly | Spurious retry or "scalac: not found" error | MEDIUM — good tutorial moment about scala-cli's first-run behavior |
| 4 | **Exhaustiveness warning on `match`** | Scala 3 compiler warns non-exhaustive match on `eval()` if the sealed trait has cases not covered | Compile warning (not error — still runs) | LOW — agent may add `case _ => ???` wildcard arm |
| 5 | **`toInt` on string without handling whitespace** | Tokenizer fails on " 2+3*4" (leading space) because `"  2".toInt` throws `NumberFormatException` | Runtime exception | MEDIUM — depends on whether the agent trims whitespace |
| 6 | **Mutable index variable confusion in tokenizer** | Agent uses a recursive tokenizer or functional approach, gets index tracking wrong | Infinite loop or missing tokens | LOW — 35B is likely to write a simple while loop |
| 7 | **Division-by-zero on `eval` for `/`** | Agent may or may not handle it — for canonical tests it doesn't matter | Not triggered by canonical tests | LOW — irrelevant to pass/fail |
| 8 | **`//> using scala 3` directive absent** | scala-cli may still default to Scala 3, so this is usually not a problem | No error — just missing version pin | LOW — educational note only |

### Detailed Analysis of Top 3

#### Failure Mode 1: Operator Precedence / Associativity Bug

**What it looks like:** The agent writes a parser where all operators are parsed at the same level (a flat expression loop), or uses right-recursion. This is the SAME class of bug as the Phase 3 F# naive grammar bug.

**Two sub-variants:**
- **Equal precedence (no hierarchy):** `2+3*4` → `(2+3)*4 = 20` (WRONG). Test 1 catches this.
- **Right-associativity (recursive instead of iterative):** `10-3-2` → `10-(3-2) = 9` (WRONG). Test 3 catches this. Note: `2+3*4` may still give `14` even with right-assoc for mixed-precedence operators (same as Phase 3's F# finding) — the third test case is ESSENTIAL.

**Critical implication (same as Phase 3):** `2+3*4 → 14` and `(2+3)*4 → 20` are INSUFFICIENT alone to catch the right-associativity bug. The `10-3-2 → 5` test MUST be included in task3.

**Agent's likely self-correction path:** If `10-3-2 → 9`, the agent will compare expected vs actual. A well-designed agent should recognize "right-assoc bug" from the hint in the expected vs actual discrepancy. The fix is to change from right-recursion to an iterative while loop.

**Example incorrect recursive parser (agent may write this):**
```scala
// RIGHT-RECURSIVE — gives 10-3-2 = 9 (WRONG for left-associativity)
def expr(): Expr =
  val left = term()
  if peek == TPlus then { consume(); Add(left, expr()) }  // ← recursive, not iterative
  else if peek == TMinus then { consume(); Sub(left, expr()) }
  else left
```

**Correct form:** iterative while loop (see scaffold in §3).

#### Failure Mode 2: Scala 3-vs-2 Syntax Slip

**Most likely slip:** `object Calc extends App { ... }` — the Scala 2 entry point idiom.

**Status in Scala 3:** `extends App` still compiles in Scala 3 but `DelayedInit` was dropped; `App` exists in limited form without command-line argument support. The agent needs `@main def calc(expression: String): Unit` to get command-line arguments parsed. If the agent uses `extends App`, `args` is `Array[String]` but it requires `App.args` — subtle difference.

**Safer alternative the agent might write:**
```scala
@main def calc(args: String*): Unit = ...
// or
def main(args: Array[String]): Unit = ...  // object companion required
```

The agent may also emit brace-based syntax (Scala 2 style) rather than indentation syntax — this is fine and compiles in Scala 3 with braces.

#### Failure Mode 3: scala-cli First-Run Artifact Download

**What happens:** On first `scala-cli run`, the tool downloads Zinc incremental compiler, Bloop BSP server, and the Scala compiler JARs. Output is verbose (20-40 lines of download progress). The actual program output appears at the end.

**Risk:** The agent may see the verbose output, not find "SCALA_OK" immediately visible, and retry — causing duplicate runs or confusion.

**Mitigation in task1 prompt:** Include the sentence: "The first run may download compiler artifacts and take 30-60 seconds. That is normal. Wait for the program output at the end."

**Signal in JSONL:** The ObservationEvent content will contain verbose download lines followed by the program output. The agent should look for "SCALA_OK" in the observation content, not just check exit code.

---

## Part 6: Scala 3-vs-2 Detailed Syntax Notes (for chapter honesty story)

The chapter's honesty story is partly "does the model emit Scala 3 idioms or drift to Scala 2?" This table documents the observable signals:

| Observable in Captured Code | Scala 2 | Scala 3 | Verdict |
|---------------------------|---------|---------|---------|
| Entry point | `object X extends App` | `@main def x()` | Scala 2 entry still compiles; command-line arg access differs |
| `new` for case class | `new Add(l, r)` | `Add(l, r)` (no `new`) | Scala 3 allows omitting `new`; both compile |
| ADT | `sealed trait` + `case class` | Same OR `enum` with `case` | `enum` is Scala 3 only |
| `match` without braces | Needs `{...}` in Scala 2 | Optional in Scala 3 | Both compile in Scala 3 |
| `if`/`while` without parens | `if (cond)` | `if cond then` | Both compile in Scala 3 |
| Top-level `def` | Must be in `object` | Can be file-level | Scala 3 only |
| `var` mutation | Same | Same | Unchanged |

**What to look for in CAPTURE-MANIFEST:**
- Does the agent use `@main` or `object extends App`?
- Does the agent use `enum` or `sealed trait`?
- Does the agent use Scala 3 brace-optional syntax or Scala 2 brace-required syntax?

These observations form the "Scala 2 vs Scala 3 idiom" narrative for 7부.

---

## Part 7: Preflight Specifics (for the 10-01 PREFLIGHT plan)

The Phase 10 preflight is a sub-plan (10-01) that runs before the agent tasks. It mirrors Phase 8's 08-01-PREFLIGHT.md.

### Preflight Checklist (what PASS looks like)

```bash
# --- Step 1: scala-cli version ---
$ scala-cli --version
Scala CLI version: 1.14.0
Scala version (default): 3.8.3

# --- Step 2: JDK check ---
$ java -version
openjdk version "17.0.19" ...  (or newer)

# --- Step 3: Trivial run (proves compiler + runtime work end-to-end) ---
$ echo '@main def preflight() = println("PREFLIGHT_OK")' > /tmp/Preflight.scala
$ scala-cli run /tmp/Preflight.scala
[... first-run download output if needed ...]
PREFLIGHT_OK

# --- Step 4: Scratch dir ---
$ mkdir -p oh-workdir-scala
$ ls oh-workdir-scala/     # must be empty
# (add to .gitignore if not already there)
$ git check-ignore oh-workdir-scala  # must return: oh-workdir-scala

# --- Step 5: Proxy ---
$ curl -s http://127.0.0.1:4000/v1/models | python3 -m json.tool | grep '"id"'
# must include: "qwen-35b"
```

**PREFLIGHT GREEN criteria (all must be true):**
1. `scala-cli --version` exits 0, version ≥ 1.14.0
2. `java -version` exits 0, version ≥ 17
3. Trivial `scala-cli run` prints `PREFLIGHT_OK`, exits 0
4. `oh-workdir-scala/` empty and gitignored
5. Proxy lists `qwen-35b`

**If scala-cli not installed:** `brew install scala-cli` (Homebrew formula is confirmed present; installs in ~1-2 minutes on this machine with openjdk@17 already present).

**Port check:** Not needed — no server required for this task (unlike Phase 8's `:8080` check).

**Note on first-run preflight:** The trivial-run in step 3 will trigger the artifact download (if scala-cli is freshly installed). This is expected and GOOD — it pre-warms the cache so the agent's task1 run is fast. Document this in the preflight notes.

---

## Standard Stack

| Component | Version | Purpose | Notes |
|-----------|---------|---------|-------|
| scala-cli | 1.14.0 | Build + run tool | `brew install scala-cli`; Homebrew confirmed 2026-06-01 |
| Scala 3 | 3.8.3 (default) | Language | Pinned with `//> using scala 3` directive |
| JDK | 17.0.19 (host) | Runtime | Already present at `/opt/homebrew/opt/openjdk@17/bin/java` |
| OpenHands CLI | 1.16 | Headless agent invocation | Identical to v1.2 |
| litellm proxy | @ 127.0.0.1:4000 | LLM routing | `openai/qwen-35b` model alias |

**No external Scala libraries — std only (locked decision from v1.3 REQUIREMENTS.md).** Do NOT research `scala-parser-combinators`, `fastparse`, `cats-parse`, `parboiled` — they are explicitly out of scope.

### Workdir Convention (parallel to v1.2)

```
oh-workdir-scala/                  ← new scratch dir (must be gitignored before run)
  calc/                            ← project dir (agent creates this in task1)
    Hello.scala                    ← task1: trivial hello-world run
    Calc.scala                     ← task2: the calculator (agent writes this)
  task1-scaffold.jsonl
  task1-scaffold.stderr.log
  task2-write-calc.jsonl
  task2-write-calc.stderr.log
  task3-buildtest.jsonl
  task3-buildtest.stderr.log
```

**Add to .gitignore before run:** `oh-workdir-scala/`

---

## Architecture Patterns

### Invocation Command (identical to v1.2 except workdir)

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL="openai/qwen-35b" \
  LLM_BASE_URL="http://127.0.0.1:4000/v1" \
  LLM_API_KEY="dummy" \
  OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-scala" \
  openhands --headless --json --yolo --override-with-envs \
  -t "$(cat task-prompts-scala/task1-scaffold.txt)" \
  2>oh-workdir-scala/task1-scaffold.stderr.log \
  | tee oh-workdir-scala/task1-scaffold.jsonl
```

### CAPTURE-MANIFEST.md Required Schema (adapted for Scala)

```markdown
## Run Metadata
- Run date: [date]
- Model: openai/qwen-35b (Qwen2.5-35B via litellm @ http://127.0.0.1:4000/v1)
- OpenHands version: SDK v1.21.0 / CLI 1.16.0
- Workspace: oh-workdir-scala/ (LocalWorkspace, host PTY, gitignored)
- scala-cli version: 1.14.0
- Scala version: 3.8.3 (default; //> using scala 3 directive present: YES/NO)
- JDK: 17.0.19

## Invocation
[exact command used for each task, with prompt file name]

## Per-Task Outcome Table
| Task | JSONL | Duration | Events | TerminalActions | Outcome |
|------|-------|----------|--------|-----------------|---------|
| task1-scaffold | task1-scaffold.jsonl | Xs | N | N | [PASS/FAIL] |
| task2-write-calc | task2-write-calc.jsonl | Xs | N | N | [PASS/FAIL/SCAFFOLDED] |
| task3-buildtest | task3-buildtest.jsonl | Xs | N | N | [PASS/FAIL] |

## Unaided-vs-Scaffolded
- did-write-calc-unaided: YES/NO
- unaided-attempts: N
- scaffold-disclosure: [if scaffolded: what was provided and why; "N/A" if not used]

## Scala 3 Idiom Notes
- entry-point-used: @main / object extends App / other
- adt-style: sealed trait + case class / enum / other
- syntax-style: Scala 3 (brace-optional) / Scala 2 (braces everywhere) / mixed

## Error-and-Fix Record
- error-description: [what compiler or runtime error the agent saw, verbatim]
- fix-description: [what the agent changed]
- location-in-jsonl: [task file, event range]
- iterations: N

## Canonical Test Outcome (SCAL-03)
- input "2+3*4": actual-output=N, expected=14, PASS/FAIL
- input "(2+3)*4": actual-output=N, expected=20, PASS/FAIL
- input "10-3-2": actual-output=N, expected=5, PASS/FAIL
- JSONL citation: [task file, event number]
- all-pass: YES/NO

## Honesty Gate
- all-ActionEvents-source-agent: YES/NO
- manual-edits-to-agent-files: YES/NO (must be NO)
- scaffold-invoked: YES/NO; if YES: which tasks and what was provided
- honesty-gate: PASS/FAIL

## Host Re-Run (operator independent confirmation)
- command: scala-cli run Calc.scala -- "2+3*4"  (etc.)
- output: [verbatim]
- exit-code: 0

## Deviations
[Any deviation from the planned task structure; must include fallback disclosures]
```

---

## Common Pitfalls

### Pitfall 1: Right-Associativity from Recursive Parser
**What goes wrong:** Agent writes a right-recursive `expr()` that gives `10-3-2 = 9` instead of 5.
**Why it happens:** Right-recursion is the natural form of "expr := term '+' expr"; the correct left-assoc form requires an iterative while loop.
**How to avoid (in task prompts):** Include `10-3-2 → 5` as a required test. Do NOT include this in task2 prompt (zero-leak) — only reveal it in task3 as part of the test suite.
**Warning sign:** `10-3-2` outputs 9; `2+3*4` still outputs 14 (same as v1 F# naive grammar).

### Pitfall 2: scala-cli First Run Confusion
**What goes wrong:** Agent sees verbose artifact download output, misreads it as an error, and panics.
**Why it happens:** scala-cli prints 20-40 lines of artifact fetch progress before running the program. If the agent only checks the last line and the program output is buried, it may retry.
**How to avoid:** Include "first run may print download output — wait for the final output line" in task1 prompt.

### Pitfall 3: Missing `@main` / Wrong Entry Point
**What goes wrong:** Agent uses `object Calc { def main(args: Array[String]): Unit = ... }` (valid but requires `object`), or `object Calc extends App` (limited in Scala 3, no proper arg support).
**Why it happens:** `object ... extends App` is deeply embedded in Scala 2 tutorials.
**How to avoid:** Task1 scaffold shows `@main def hello() = println("SCALA_OK")` as a model. This sets the pattern without naming it in task2.
**Actual impact:** `object Calc extends App` compiles and runs but `args` is `App.args`, not a parameter — the agent may write a wrong entry point that silently fails to parse command-line args, causing the calculator to read from wrong input.

### Pitfall 4: Tokenizer integer overflow
**What goes wrong:** Agent writes `s(i).toString.toInt` instead of collecting all digit characters first, giving single-digit parsing only (fails on `10-3-2`).
**Why it happens:** Char-by-char tokenizer for multi-digit numbers requires a separate inner loop or regex. Simple implementation reads one char at a time.
**How to avoid:** Include "10" as part of the test case (the test `10-3-2` naturally exercises multi-digit parsing).

---

## Don't Hand-Roll

This section is N/A for Scala calculator — the whole POINT of Phase 10 is to hand-roll the parser. However, document what MUST NOT be introduced:

| Problem | Don't Introduce | Why It's Banned |
|---------|-----------------|-----------------|
| Parsing arithmetic expressions | `scala-parser-combinators` | Explicitly out of scope; hides the parsing logic from the tutorial |
| Parsing arithmetic expressions | `fastparse`, `cats-parse` | Same reason |
| Build management | `sbt`, `mill` | scala-cli is the chosen build tool; sbt adds unneeded complexity |
| Scala 2.12/2.13 | Any Scala 2 library | Version discipline; Scala 3 only for this milestone |

---

## State of the Art

| Old Approach (v1 F# reference) | Phase 10 Approach | Key Difference |
|--------------------------------|-------------------|----------------|
| FsLex/FsYacc parser generator | Hand-rolled recursive descent | No build-time code generation; single file |
| `dotnet new console` scaffold | `scala-cli` single file | No project template; simpler |
| `.fsproj` XML configuration | `//> using scala 3` directive | Inline directive in source file |
| `dotnet build` then `dotnet run -- "arg"` | `scala-cli run Calc.scala -- "arg"` | Combined compile+run step |
| NuGet package (FsLexYacc) | Zero external packages | Std-only discipline |

---

## Open Questions

1. **scala-cli not installed on this host** — It is NOT currently installed (`which scala-cli` returns empty). The preflight must install it first. This means the preflight will include `brew install scala-cli` as step 0, followed by the trivial run (which will trigger first-run artifact download). The planner should note this in 10-01-PREFLIGHT.
   - What we know: `brew install scala-cli` will install 1.14.0 (confirmed in `brew info`).
   - What's unclear: Whether `brew install scala-cli` also puts `scala-cli` on PATH automatically or needs a brew shellenv step.
   - Recommendation: Add `brew link scala-cli` if needed; verify with `which scala-cli` after install.

2. **scala-cli artifact download during agent's task1** — If the preflight pre-warms the cache (by running the trivial program), the agent's task1 run should use the warm cache and be fast. But if the preflight only verifies `--version` without running, the agent will see the slow first-run download in task1. The recommended approach is to include a real `scala-cli run` in the preflight to pre-warm.
   - Recommendation: Preflight step 3 (`scala-cli run /tmp/Preflight.scala`) pre-warms the cache. Agent task1 should be fast.

3. **scala-cli default Scala version for v1.14.0** — v1.13.0 explicitly set default to 3.8.3. v1.14.0 release notes don't explicitly state the default but reference "Scala 3 Next RC at 3.8.4-RC2" — suggesting production default remains 3.8.3.
   - What we know: v1.13.0 default = 3.8.3. v1.14.0 ≥ v1.13.0.
   - Recommendation: Use `//> using scala 3` directive in both the scaffold (task1) and ensure the agent includes it in Calc.scala (task2). This removes ambiguity.

---

## Sources

### Primary (HIGH confidence — live checks on host)
- `brew info scala-cli` on host (2026-06-01) → confirmed version 1.14.0, not installed, openjdk@17 present
- `java -version` on host (2026-06-01) → openjdk 17.0.19 at `/opt/homebrew/opt/openjdk@17/bin/java`
- `which scala-cli` on host (2026-06-01) → not found (installation required)

### Primary (HIGH confidence — official docs)
- https://formulae.brew.sh/formula/scala-cli — confirmed 1.14.0, install command
- https://github.com/VirtusLab/scala-cli/releases/tag/v1.13.0 — "switches default Scala version to 3.8.3"
- https://github.com/VirtusLab/scala-cli/releases/tag/v1.14.0 — latest release (2026-05-14)
- https://scala-cli.virtuslab.org/docs/commands/run/ — run command syntax, subcommand-optional
- https://scala-cli.virtuslab.org/docs/cookbooks/introduction/scala-versions/ — `//> using scala 3` directive, `--scala` / `-S` flag
- https://scala-cli.virtuslab.org/docs/cookbooks/introduction/scala-jvm/ — JDK auto-download, `--jvm` flag
- https://scala-cli.virtuslab.org/docs/getting_started/ — first-run behavior, artifact download warning
- https://docs.scala-lang.org/scala3/book/methods-main-methods.html — `@main` annotation, `object extends App` deprecated
- https://docs.scala-lang.org/scala3/reference/enums/desugarEnums.html — enum desugaring to sealed trait

### Secondary (HIGH confidence — v1.2 parallel)
- Phase 8 `08-RESEARCH.md` — task decomposition structure, zero-leak prompt discipline, scaffold fallback policy, CAPTURE-MANIFEST schema (all adapted for Scala)
- Phase 3 `03-RESEARCH.md` — canonical 3-test requirement (`10-3-2 = 5` for left-assoc), right-assoc bug analysis, unaided-first protocol

### Tertiary (MEDIUM confidence — web search synthesis)
- https://www.scalamatters.io/post/sealed-traits-vs-enums-for-adts — sealed trait vs enum tradeoffs
- https://kindatechnical.com/scala/enums-adts-and-gadts-in-scala-3.html — enum ADT syntax

---

## Metadata

**Confidence breakdown:**
- scala-cli version and install: HIGH — live `brew info` on host
- JDK state on host: HIGH — live `java -version` on host
- scala-cli run commands: HIGH — official docs
- Default Scala version: HIGH (3.8.3 per v1.13.0 explicit note; v1.14.0 ≥ this)
- Scala 3 syntax differences: HIGH — official Scala 3 docs
- Scaffold implementation: HIGH (canonical recursive-descent pattern; manually verified by tracing)
- Failure modes: MEDIUM — inferred from 35B behavior pattern (v1/v1.2 runs) + Scala-specific analysis
- Task prompt text: HIGH — applies v1.2's zero-leak discipline directly

**Research date:** 2026-06-01
**Valid until:** 30 days (stable stack — scala-cli 1.14.0, Scala 3.8.3, OpenHands 1.16 are all pinned or near-pinned)
**scala-cli NOT installed on host** — must be installed during 10-01 PREFLIGHT before any agent run.
