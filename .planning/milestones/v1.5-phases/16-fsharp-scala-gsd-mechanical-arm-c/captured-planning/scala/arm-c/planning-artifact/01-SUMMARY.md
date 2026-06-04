# 01-SUMMARY — Scala Calculator (Calc.scala)

## File Created

- **Calc.scala** — single-file Scala 3 integer calculator (stdlib only, no external dependencies, no `build.sbt`, no `//> using` directives)

## Implementation

Hand-rolled recursive-descent parser with three precedence tiers:

| Tier | Method | Operators |
|------|--------|-----------|
| 1 (highest) | `parseFactor` | literals, parenthesised sub-expressions |
| 2 | `parseTerm` | `*`, `/` (left-associative via `while`-loop fold) |
| 3 (lowest) | `parseExpr` | `+`, `-` (left-associative via `while`-loop fold) |

Run via: `scala-cli run Calc.scala -- "<expression>"`

## Canonical Test Results

| Expression | Expected | Actual | Status |
|------------|----------|--------|--------|
| `2+3*4` | 14 | 14 | PASS |
| `(2+3)*4` | 20 | 20 | PASS |
| `10-3-2` | 5 | 5 | PASS |

All three canonical acceptance tests pass against the single unmodified `Calc.scala`.

## Verification Checks

- `scala-cli compile Calc.scala` — exit 0, no errors
- `grep -E '//> using|^package |build\.sbt' Calc.scala` — no matches (stdlib-only)
- `grep -c 'while peek.contains' Calc.scala` — returns 2 (left-fold loops in `parseExpr` and `parseTerm`)

## Dependencies

- **None** — Scala standard library only. No external libraries, no `build.sbt`, no `//> using` directives.
