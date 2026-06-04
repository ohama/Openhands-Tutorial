# Claude's Task Decomposition — Scala 3 Calculator (Arm A Input)

This is the mechanical conversion of the v1.3 Scala task decomposition (task1-scaffold /
task2-write-calc / task3-buildtest) into a single-session numbered plan. Three steps,
meaning preserved verbatim from the v1.3 task prompts; phrasing adapted for
single-session state handoff only (no new planning detail added, no subtasks
restructured, no ambiguities clarified — Pitfall 7: conversion is mechanical
format-only).

No scaffolded source code is included (unaided discipline: the 35B writes all
source code itself).

---

## Step 1 — Scaffold

Confirm scala-cli is installed and working:
  scala-cli --version

Create a project subdirectory and a minimal smoke-test file:
  mkdir -p calc
  cd calc

Write a file named Hello.scala (using a bash heredoc) with this content:
  @main def hello() = println("SCALA_OK")

Run it:
  scala-cli run Hello.scala

The first run may download compiler artifacts and take 30–60 seconds — that is
normal. Wait for the program output at the end; do not treat download progress lines
as an error and do not retry prematurely.

Expected output: SCALA_OK

Report the scala-cli version and whether SCALA_OK appeared.

Success criterion: `scala-cli --version` runs; `scala-cli run Hello.scala` prints
SCALA_OK. Do not write any calculator code yet.

## Step 2 — Write Calc.scala

After Step 1, the calc/ directory exists and scala-cli is confirmed working. Write a
Scala source file named Calc.scala in calc/.

Calc.scala must evaluate an arithmetic expression given as a single command-line
argument and print the integer result.

Requirements:
- Input: a single command-line argument, e.g. "2+3*4"
- Output: the integer result on its own line, e.g. 14
- Operators: + - * / where * and / bind more tightly than + and -
  (2+3*4 evaluates to 14, not 20)
- Parentheses override the normal precedence ((2+3)*4 evaluates to 20)
- Integer arithmetic only (no floating point)
- Use ONLY the Scala standard library — no external libraries and no build
  dependencies

After writing Calc.scala, show its contents:
  cat Calc.scala

Do NOT run or compile yet — Step 3 handles running and testing.

Success criterion: Calc.scala exists in calc/ and implements the arithmetic parser
with correct precedence and parentheses handling using only the standard library.

## Step 3 — Build and test

After Step 2, Calc.scala exists in calc/. Run it with scala-cli and verify all three
canonical tests.

Run the first test (compilation happens on the first run; fix any compile errors
before running remaining tests):
  scala-cli run Calc.scala -- "2+3*4"

If compilation fails, read the error carefully, fix Calc.scala (using bash
heredoc/printf/tee — NOT file_editor), and retry. Repeat until compilation succeeds.
Report each compiler error encountered and what was changed to fix it.

Once compilation succeeds, run all three canonical tests and capture exact output:
  scala-cli run Calc.scala -- "2+3*4"
  scala-cli run Calc.scala -- "(2+3)*4"
  scala-cli run Calc.scala -- "10-3-2"

Required outputs: 14 / 20 / 5 respectively.

Report results explicitly for each test case: exact output printed, whether it
matched the expected value. If a test prints the wrong number, investigate and fix
Calc.scala if possible, but report the wrong output honestly first. Fix only the
error at hand and report what was changed and why.

Constraints: do NOT add external library dependencies. The whole program must use
only the Scala standard library.

Success criterion: all three canonical tests print the correct integer and exit 0.
An honest failure is more valuable than a fabricated success — if a test fails,
state clearly which case failed and what it printed.
