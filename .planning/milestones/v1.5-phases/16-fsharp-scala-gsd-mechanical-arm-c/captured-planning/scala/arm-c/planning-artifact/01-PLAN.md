---
phase: 16-scala-integer-calculator
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - Calc.scala
autonomous: true

must_haves:
  truths:
    - "scala-cli run Calc.scala -- \"2+3*4\" prints 14 (multiplication binds tighter than addition)"
    - "scala-cli run Calc.scala -- \"(2+3)*4\" prints 20 (parentheses override precedence)"
    - "scala-cli run Calc.scala -- \"10-3-2\" prints 5 (subtraction is LEFT-associative, not 9)"
    - "Calc.scala compiles and runs with scala-cli alone — no build.sbt, no //> using dep, no external libraries"
    - "@main entry reads exactly one CLI arg (the expression string) and prints the integer result"
  artifacts:
    - path: "Calc.scala"
      provides: "@main entry, eval, tokenize, and recursive-descent Parser (expr/term/factor)"
      min_lines: 40
      contains: "@main def run"
  key_links:
    - from: "@main def run"
      to: "eval(arg)"
      via: "println(eval(arg))"
      pattern: "println\\(eval\\("
    - from: "eval"
      to: "Parser.parseExpr"
      via: "Parser(tokenize(input)).parseExpr()"
      pattern: "Parser\\(tokenize"
    - from: "parseExpr / parseTerm"
      to: "left-associativity"
      via: "while-loop left-fold accumulator (acc = acc op rhs), NOT right recursion"
      pattern: "while peek\\.contains"
---

<objective>
Build a single-file Scala 3 integer calculator, `Calc.scala`, that takes ONE command-line
argument (an integer arithmetic expression) and prints the integer result. Supports `+ - * /`
with `*` and `/` binding tighter than `+` and `-`, parentheses to override precedence, and
correct LEFT-associativity for `-` and `/`. Scala standard library ONLY — no external deps,
no `build.sbt`, no `//> using` directives.

Purpose: This is the arm-c / Scala leg of the mechanical-arm calculator trilogy. It exercises a
hand-rolled recursive-descent parser (the intended skill) using nothing but the Scala 3 stdlib.

Output: One file, `Calc.scala`, runnable via `scala-cli run Calc.scala -- "<expr>"`.
</objective>

<context>
@/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1.4-phases/16-fsharp-scala-gsd-mechanical-arm-c/captured-planning/scala/arm-c/planning-artifact/RESEARCH.md

# Environment (verified in RESEARCH.md):
#   scala-cli 1.14.0, Scala 3.8.3 (default), JDK 17, macOS.
#   File creation constraint: write Calc.scala via bash heredoc/printf only (no file_editor).
#
# The RESEARCH.md above is PRESCRIPTIVE and empirically verified — its complete solution passes
# all three canonical tests. Use it as the source of truth. The reference implementation is
# reproduced in Task 1's action so the executor can write it verbatim.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write Calc.scala (tokenizer + recursive-descent parser + @main)</name>
  <files>Calc.scala</files>
  <action>
Create `Calc.scala` in the working directory using a bash heredoc (NOT file_editor — file
creation is restricted to bash heredoc/printf in this environment). Write the file with a
quoted heredoc delimiter (e.g. `cat > Calc.scala <<'EOF'`) so that `$`, backticks, and other
shell metacharacters in the Scala source are NOT expanded by the shell.

Write this EXACT, empirically-verified implementation (from RESEARCH.md — it passes all three
canonical tests). Structure, in order: `@main def run` → `eval` → `tokenize` → `class Parser`.

```scala
// Scala 3 integer calculator — stdlib only, single file, run with scala-cli.
// 2+3*4 -> 14   (2+3)*4 -> 20   10-3-2 -> 5
@main def run(arg: String): Unit =
  println(eval(arg))

def eval(input: String): Int =
  val parser = Parser(tokenize(input))
  parser.parseExpr()

def tokenize(s: String): List[String] =
  val buf = scala.collection.mutable.ListBuffer[String]()
  var i = 0
  while i < s.length do
    val c = s(i)
    if c.isWhitespace then i += 1
    else if c.isDigit then
      val start = i
      while i < s.length && s(i).isDigit do i += 1
      buf += s.substring(start, i)
    else
      buf += c.toString
      i += 1
  buf.toList

class Parser(tokens: List[String]):
  private var pos = 0
  private def peek: Option[String] = tokens.lift(pos)
  private def next(): String = { val t = tokens(pos); pos += 1; t }

  def parseExpr(): Int =
    var acc = parseTerm()
    while peek.contains("+") || peek.contains("-") do
      val op = next()
      val rhs = parseTerm()
      acc = if op == "+" then acc + rhs else acc - rhs
    acc

  private def parseTerm(): Int =
    var acc = parseFactor()
    while peek.contains("*") || peek.contains("/") do
      val op = next()
      val rhs = parseFactor()
      acc = if op == "*" then acc * rhs else acc / rhs
    acc

  private def parseFactor(): Int =
    peek match
      case Some("(") =>
        next()
        val e = parseExpr()
        next()
        e
      case _ =>
        next().toInt
```

Critical points (DO NOT deviate — these are the verified pitfalls from RESEARCH.md):
- LEFT-associativity comes from the `while`-loop left-fold accumulator (`acc = acc op rhs`).
  Do NOT recurse right (`term op parseExpr`) — that gives `10-3-2 → 9`, the signature bug.
- Precedence tiers MUST be separated: `parseExpr` loops `+ -` and calls `parseTerm`; `parseTerm`
  loops `* /` and calls `parseFactor`. The tighter operator lives at the deeper level. Flattening
  gives `2+3*4 → 20`.
- `parseExpr` is the ONLY public member of `Parser`; `pos`, `peek`, `next`, `parseTerm`,
  `parseFactor` stay `private` and are touched only from inside `Parser`. `@main` calls the
  top-level `eval`, never a `private` class member (reaching an instance-`private` member from
  `@main` is a compile error: "can only be accessed from class Parser").
- No `package` declaration. No `build.sbt`. No `//> using` directives. Scala stdlib only.
- Scala 3 indentation syntax requires `then`/`do` keywords — keep them as written.
- Do NOT add unary-minus, malformed-input, or div-by-zero handling: out of scope, and extra code
  is extra surface for the `@main`/private-scope pitfalls. The three canonical inputs are all
  well-formed.

After writing, print the file back (`cat Calc.scala`) to confirm the heredoc captured the source
intact (no shell expansion, indentation preserved).
  </action>
  <verify>
`test -f Calc.scala` succeeds. `cat Calc.scala` shows the four parts in order (`@main def run`,
`def eval`, `def tokenize`, `class Parser`) with `while peek.contains("+")` present (the
left-fold loop) and no `//> using` / `package` / `build.sbt` references. Compile cleanly:
`scala-cli compile Calc.scala` exits 0 with no errors.
  </verify>
  <done>
Calc.scala exists in the working directory, contains the verbatim reference implementation, and
compiles with `scala-cli compile Calc.scala` (exit 0).
  </done>
</task>

<task type="auto">
  <name>Task 2: Run the three canonical acceptance tests</name>
  <files>Calc.scala</files>
  <action>
Run each canonical invocation and confirm the EXACT expected integer output. Use `--` to separate
scala-cli's options from the program arg (so a leading-dash expression is not misread as an
option), exactly as in RESEARCH.md:

```bash
scala-cli run Calc.scala -- "2+3*4"     # expect: 14
scala-cli run Calc.scala -- "(2+3)*4"   # expect: 20
scala-cli run Calc.scala -- "10-3-2"    # expect: 5
```

Run `"10-3-2"` and confirm `5` FIRST-class — it is the discriminating left-associativity case
(`9` means right-recursion crept in). Then `"2+3*4" → 14` confirms precedence, and
`"(2+3)*4" → 20` confirms parentheses.

If any output is wrong, do NOT hand-edit the output or paper over it — fix `Calc.scala` to match
the verified reference (re-check the left-fold loop and the expr/term/factor tier ordering), then
re-run all three. All three must pass on the same unmodified file.

Optionally collapse into one check:
```bash
for pair in "2+3*4=14" "(2+3)*4=20" "10-3-2=5"; do
  expr="${pair%=*}"; want="${pair##*=}"
  got=$(scala-cli run Calc.scala -- "$expr")
  [ "$got" = "$want" ] && echo "PASS $expr -> $got" || echo "FAIL $expr -> $got (want $want)"
done
```
  </action>
  <verify>
All three commands print exactly `14`, `20`, `5` respectively (trailing newline only, no extra
output). The loop variant prints three `PASS` lines and zero `FAIL` lines.
  </verify>
  <done>
`2+3*4 → 14`, `(2+3)*4 → 20`, and `10-3-2 → 5` all pass against the single unmodified Calc.scala.
</done>
</task>

</tasks>

<verification>
- `scala-cli compile Calc.scala` exits 0 (compiles clean, no external deps resolved).
- Three canonical tests pass: `2+3*4→14`, `(2+3)*4→20`, `10-3-2→5`.
- `grep -E '//> using|^package |build\.sbt' Calc.scala` returns nothing (stdlib-only, single-file).
- `grep -c 'while peek.contains' Calc.scala` returns 2 (left-fold loops present in expr and term —
  the structural guarantee of left-associativity).
</verification>

<success_criteria>
- A single file `Calc.scala` evaluates an integer arithmetic expression passed as one CLI arg and
  prints the integer result.
- Operator precedence (`* /` over `+ -`), parentheses override, and LEFT-associativity all correct.
- Scala stdlib only — no `build.sbt`, no `//> using dep`, no external libraries; runs with
  `scala-cli run Calc.scala -- "<expr>"`.
- All three canonical acceptance tests pass against the same unmodified file.
</success_criteria>

<output>
After completion, create `01-SUMMARY.md` in this planning-artifact directory:
/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1.4-phases/16-fsharp-scala-gsd-mechanical-arm-c/captured-planning/scala/arm-c/planning-artifact/01-SUMMARY.md
Record: file created (Calc.scala), the three canonical test outputs observed, and confirmation
that no external dependencies or build files were used.
</output>
