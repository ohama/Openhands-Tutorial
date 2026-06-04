# Phase 16 (arm-c / Scala): Scala 3 Integer Calculator - Research

**Researched:** 2026-06-04
**Domain:** Recursive-descent expression parsing in Scala 3 (scala-cli, stdlib only)
**Confidence:** HIGH (every claim below verified empirically against scala-cli 1.14.0 / Scala 3.8.3 / JDK 17 on this machine)

## Summary

This phase builds a single-file `Calc.scala` that takes ONE command-line argument (an integer arithmetic expression) and prints the integer result. The required skill is a hand-rolled recursive-descent parser with correct operator precedence (`*` `/` bind tighter than `+` `-`), left-associativity for `-` and `/`, and parentheses for override. No external libraries, no `build.sbt`, no parser-combinator/fastparse — Scala standard library only.

The standard, verified-correct approach is the classic three-level grammar `expr → term → factor`, where each level handles one precedence tier and left-associativity falls out naturally from a `while` loop (NOT recursion on the same level). I built this exact structure and ran it against all three canonical tests: `2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5` — all pass. The most dangerous bug in this domain is right-associative subtraction (`10-3-2 → 9`), which is *prevented by design* if you use the iterative `while`-loop accumulator pattern rather than recursing right.

**Primary recommendation:** Use a `@main def` entry point taking a single `String` parameter, a hand-written tokenizer producing a `List[String]`, and a recursive-descent parser with `expr/term/factor` levels where `expr` and `term` use a `while`-loop left-fold accumulator. Keep everything as top-level defs or a single class with NO `private` members that `@main` must reach across an instance boundary.

## Standard Stack

This is a deliberately dependency-free phase. The "stack" is the toolchain and the Scala standard library.

### Core
| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| scala-cli | 1.14.0 | Compile + run single `.scala` file | Already installed; `scala-cli run Calc.scala -- "<expr>"` is the canonical invocation |
| Scala | 3.8.3 (default via scala-cli) | Language | Phase mandates Scala 3 |
| JDK | 17 | Runtime | Confirmed present; scala-cli targets JVM 17 |
| Scala stdlib | (bundled) | `String`, `Char.isDigit`, `Char.isWhitespace`, `String.toInt`, `scala.collection.mutable.ListBuffer`, `List.lift` | Everything needed for tokenize + parse |

### Supporting
None. This phase explicitly forbids supporting libraries.

### Alternatives Considered (DO NOT USE — listed only to make the constraint explicit)
| Instead of hand-rolled parser | Could Use | Why NOT here |
|-------------------------------|-----------|--------------|
| recursive descent | `scala-parser-combinators` | External dep — FORBIDDEN by phase constraints |
| recursive descent | `fastparse` | External dep — FORBIDDEN |
| recursive descent | `scala.util.parsing` | Not in Scala 3 stdlib (was removed; lives in separate artifact) — would need a dep anyway |

**Installation:** None. No `build.sbt`, no `//> using dep` directives. The file must compile with `scala-cli run Calc.scala` and nothing else.

## Architecture Patterns

### Recommended File Structure
A single file `Calc.scala` containing, in order:
```
Calc.scala
├── @main def run(arg: String)   # entry point: reads ONE arg, prints eval(arg)
├── def eval(input: String): Int # tokenize then parse
├── def tokenize(s: String)      # String → List[String] of number/operator/paren tokens
└── class Parser(tokens)         # recursive-descent: parseExpr / parseTerm / parseFactor
```
Keep it flat. No package declaration is needed (top-level defs land in the empty package, which `@main` handles fine).

### Pattern 1: `@main` single-argument entry point (VERIFIED)
**What:** Scala 3's `@main` annotation generates a runnable main that maps CLI args to parameters by position and type.
**When to use:** Always, for this phase. A single `String` parameter consumes exactly the one expression arg.
**Example (verified to print 14 / 20 / 5):**
```scala
// Source: empirically verified, scala-cli 1.14.0 / Scala 3.8.3
@main def run(arg: String): Unit =
  println(eval(arg))
```
**Behavior confirmed on this machine:**
- Zero args → scala-cli prints `Illegal command line: more arguments expected` and exits non-zero (clean failure).
- EXTRA args → **silently ignored** (e.g. `-- "1+1" "extra"` printed `2`). This means you canNOT rely on `@main` to reject a second arg. Acceptable for the canonical tests, but note it.

### Pattern 2: Three-level recursive-descent grammar (VERIFIED, this is the core skill)
**What:** One parse method per precedence tier. Higher tier = looser binding. Left-associativity comes from a `while` loop that folds left, NOT from right recursion.
**Grammar:**
```
expr   = term   { ("+" | "-") term }     // loosest
term   = factor { ("*" | "/") factor }   // tighter
factor = number | "(" expr ")"           // tightest; parens re-enter at top
```
**Example (verified — all three canonical tests pass with this exact code):**
```scala
// Source: empirically verified against 2+3*4→14, (2+3)*4→20, 10-3-2→5
class Parser(tokens: List[String]):
  private var pos = 0
  private def peek: Option[String] = tokens.lift(pos)
  private def next(): String = { val t = tokens(pos); pos += 1; t }

  def parseExpr(): Int =
    var acc = parseTerm()
    while peek.contains("+") || peek.contains("-") do
      val op = next()
      val rhs = parseTerm()
      acc = if op == "+" then acc + rhs else acc - rhs   // LEFT fold ⇒ 10-3-2 = 5
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
        next()                 // consume "("
        val e = parseExpr()    // parens re-enter at the top of precedence
        next()                 // consume ")"
        e
      case _ =>
        next().toInt
```
Note: `parseExpr` is `public`; `parseTerm`/`parseFactor`/`peek`/`next`/`pos` are `private` to the class and ONLY touched from within the class — this is safe (see Pitfall 4 for the unsafe variant).

### Pattern 3: Simple tokenizer (VERIFIED)
**What:** Walk the string once; accumulate consecutive digits into one number token; emit single-char tokens for operators and parens; skip whitespace.
**Example (verified, handles `"2 + 3 * 4"` → 14 with spaces):**
```scala
// Source: empirically verified
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
```

### Anti-Patterns to Avoid
- **Right recursion for left-associative operators:** writing `parseExpr = parseTerm op parseExpr` makes `-` and `/` right-associative → `10-3-2 → 9` and `8/4/2 → 4`. Use the `while`-loop accumulator instead.
- **Single flat parse loop with no precedence levels:** evaluating left-to-right ignores precedence → `2+3*4 → 20`. You MUST have separate `expr`/`term` levels.
- **Char-by-char `eval` without tokenizing multi-digit numbers:** treating each char as a token breaks `10-3-2` (the `10`). Accumulate digit runs.
- **Precedence-climbing as a first attempt:** it works but is harder to get right by hand and harder to verify. The three-level grammar is the lowest-risk choice here. (Precedence-climbing is fine as an alternative ONLY if the implementer is fluent in it.)

## Don't Hand-Roll

The phase FORBIDS libraries, so "don't hand-roll" inverts: the point is to hand-roll the parser, but do NOT hand-roll the trivial pieces the stdlib already gives you.

| Problem | Don't Build | Use Instead (stdlib) | Why |
|---------|-------------|----------------------|-----|
| Detect a digit char | manual `c >= '0' && c <= '9'` | `c.isDigit` | Verified; cleaner, correct |
| Detect whitespace | manual char compares | `c.isWhitespace` | Verified |
| String → Int | manual digit-accumulation `n*10 + d` | `token.toInt` (Java `Integer.parseInt`) | Verified; throws `NumberFormatException` on bad/overflow input rather than silently truncating |
| Safe lookahead past end of token list | manual index-bounds checks everywhere | `tokens.lift(pos): Option[String]` | Returns `None` past the end; pairs with `.contains("+")` for clean peeking |
| Growable token list | manual array resizing | `scala.collection.mutable.ListBuffer` | Verified |

**Key insight:** The intended "build" is the precedence-correct parser. Everything below it (char classification, int parsing, bounds-safe peeking) is a solved stdlib problem — re-implementing those is where avoidable bugs creep in (especially a hand-written `toInt` that silently overflows).

## Common Pitfalls

### Pitfall 1: Right-associative subtraction / division (THE signature bug)
**What goes wrong:** `10-3-2` returns `9` instead of `5`; `8/4/2` returns `4` instead of `1`.
**Why it happens:** The parser recurses right (`term - expr`) so it computes `10-(3-2)`.
**How to avoid:** Use the iterative `while`-loop left-fold accumulator in `parseExpr`/`parseTerm` (Pattern 2). Left-folding is correct by construction.
**Warning signs:** `10-3-2` ≠ 5. Always run this canonical test FIRST — it is the discriminating case.

### Pitfall 2: Precedence inversion
**What goes wrong:** `2+3*4` returns `20` instead of `14`.
**Why it happens:** No separation between additive and multiplicative levels, or the levels are nested in the wrong order (factor calling term calling expr in the wrong direction).
**How to avoid:** `expr` loops over `+`/`-` and calls `term`; `term` loops over `*`/`/` and calls `factor`. The tighter-binding operator MUST live at the deeper (inner) level.
**Warning signs:** `2+3*4` ≠ 14.

### Pitfall 3: `@main` argument handling
**What goes wrong:** Reading args wrong, or assuming `args: Array[String]`-style indexing.
**Why it happens:** Mixing the old `def main(args: Array[String])` mental model with the new `@main` annotation.
**How to avoid:** Use `@main def run(arg: String)`. Scala maps the single CLI arg to `arg` directly. Invoke as `scala-cli run Calc.scala -- "2+3*4"` — the `--` separates scala-cli's options from the program's args; without it a leading-dash expression could be misread as an option.
**Verified behaviors:** zero args → clean `Illegal command line` error; extra args → silently ignored (do not depend on rejection). If you instead use `@main def run(args: String*)` you'd get a vararg; not needed here, stick to the single `String`.

### Pitfall 4: `private` access-modifier scoping (the trap the context warns about)
**What goes wrong:** `private value v cannot be accessed as a member of (b : Box) ... can only be accessed from class Box` — compile failure.
**Why it happens:** A `private` member of a CLASS is touched from `@main` (which lives OUTSIDE the class instance). VERIFIED: `class Box: private val v = 99` then `Box().v` from `@main` fails to compile.
**Nuance (VERIFIED):** A top-level `private val` in the SAME file IS reachable from `@main` in that file (top-level `private` means package-private, and both are in the empty package). So the trap is specifically *instance-private class members reached across the instance boundary*, NOT top-level privates.
**How to avoid:** Keep the parser's mutable state (`pos`) and helpers (`peek`, `next`) `private` to the `Parser` class and only call them from inside `Parser`. Expose exactly ONE public entry (`parseExpr`). `@main` should call `eval(arg)` (a top-level def) which constructs the `Parser` and calls only its public method — never reach into a private class member from `@main`.
**Warning signs:** compiler error text `can only be accessed from class <Name>`.

### Pitfall 5: `Int` parsing failure (no silent fallback)
**What goes wrong:** `"abc".toInt` and `"9999999999".toInt` both throw `java.lang.NumberFormatException` at runtime (VERIFIED — overflow is NOT silently truncated).
**Why it happens:** `toInt` delegates to `Integer.parseInt`, which rejects non-digits and any value outside the signed 32-bit range.
**How to avoid:** For the canonical tests (small positive ints) this is fine — no handling needed. If robustness is desired, validate tokens or catch `NumberFormatException`. Do NOT assume out-of-range numbers wrap around.
**Warning signs:** runtime `NumberFormatException: For input string: "..."`.

### Pitfall 6: Unary minus is NOT handled by the basic grammar
**What goes wrong:** `-3+5` or `2*-3` throws `NumberFormatException: For input string: "-"` (VERIFIED) because the tokenizer emits a lone `"-"` token and `parseFactor` calls `"-".toInt`.
**Why it happens:** `factor = number | "(" expr ")"` has no rule for a leading sign.
**Scope note:** The three canonical tests (`2+3*4`, `(2+3)*4`, `10-3-2`) contain NO unary minus, so this is OUT OF SCOPE for passing the phase. Document as a known limitation; do NOT add unary handling unless the phase requirements expand. (If needed later: add `case Some("-") => next(); -parseFactor()` to `parseFactor`.)

### Pitfall 7: Scala 3 control-syntax requires `do`/`then`
**What goes wrong:** `while (cond) { ... }` is fine, but the new indentation syntax `while cond do ...` and `if c then a else b` require the `do`/`then` keywords.
**Why it happens:** Scala 3's optional-braces syntax. VERIFIED: both brace style (`@main def run(): Unit = { ... }`) and indentation style compile fine — pick one and be consistent. Forgetting `do`/`then` in indentation style is a compile error.
**How to avoid:** Use the exact syntax in the verified Pattern 2/3 snippets above.

## Code Examples

### Complete, verified single-file solution (passes all three canonical tests)
```scala
// Source: empirically verified on scala-cli 1.14.0 / Scala 3.8.3 / JDK 17
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

### Invocation / verification commands (the acceptance gate)
```bash
# Source: empirically verified outputs
scala-cli run Calc.scala -- "2+3*4"    # -> 14
scala-cli run Calc.scala -- "(2+3)*4"  # -> 20
scala-cli run Calc.scala -- "10-3-2"   # -> 5
```

## State of the Art

| Old (Scala 2) | Current (Scala 3.8.3) | Impact |
|---------------|------------------------|--------|
| `object Main { def main(args: Array[String]) = ... }` | `@main def run(arg: String) = ...` | Less boilerplate; one-string param maps the single CLI arg directly |
| Braces mandatory | Optional braces / significant indentation with `then`/`do` | Both compile; pick one style consistently |
| `scala.util.parsing.combinator` shipped in stdlib | Moved OUT to separate `scala-parser-combinators` artifact | Even if libraries were allowed, parser-combinators are no longer "free" — reinforces hand-rolling |

**Deprecated/outdated for this phase:**
- `def main(args: Array[String])` boilerplate — replaced by `@main`. (Still works, but `@main` is idiomatic Scala 3 and shorter.)

## Open Questions

1. **Unary minus / negative numbers**
   - What we know: the basic grammar crashes on `-3` (VERIFIED `NumberFormatException: "-"`).
   - What's unclear: whether the phase ever requires it.
   - Recommendation: OUT OF SCOPE — none of the three canonical tests use it. Leave unimplemented; note as a limitation. One-line fix available if requirements expand.

2. **Malformed-input behavior (unbalanced parens, trailing operators, empty string)**
   - What we know: such inputs will throw (index out of range or `NumberFormatException`) rather than print a friendly error.
   - What's unclear: whether graceful error handling is graded.
   - Recommendation: The canonical tests are all well-formed. Do NOT add error handling unless a requirement demands it — extra code is extra surface for the `@main`/private-scope pitfalls.

3. **Division by zero**
   - What we know: integer `x / 0` throws `ArithmeticException`. Not exercised by canonical tests.
   - Recommendation: leave as default JVM behavior.

## Sources

### Primary (HIGH confidence)
- **Empirical execution on this machine** — scala-cli 1.14.0, Scala 3.8.3, JDK 17, macOS. Every code snippet, every error message, and all three canonical outputs (14 / 20 / 5) were run and observed. This is the highest-confidence source for this phase and supersedes documentation.
  - Verified: full calculator passes canonical tests; `@main` zero-arg error; `@main` extra-arg silent-ignore; top-level `private` reachable from `@main`; class-`private` member NOT reachable from `@main` (exact error text); `.toInt` throws on non-digit and on overflow; integer `/` truncates toward zero; brace and indentation styles both compile; unary `-` crashes.

### Secondary (MEDIUM confidence)
- Scala 3 language reference for `@main` and optional-braces syntax (general knowledge, corroborated by the empirical runs above).

### Tertiary (LOW confidence)
- None required; empirical verification covered all load-bearing claims.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — toolchain versions read from the machine; stdlib-only constraint is explicit and tested (no deps needed).
- Architecture: HIGH — the exact recursive-descent structure was executed and passes all three canonical tests.
- Pitfalls: HIGH — every pitfall (right-assoc bug, precedence, `@main` args, class-`private` scoping, `toInt` failure, unary minus, `then`/`do` syntax) was reproduced empirically with observed error messages.

**Research date:** 2026-06-04
**Valid until:** 2026-09-04 (90 days — Scala 3 / scala-cli are stable; the parsing algorithm is timeless)
