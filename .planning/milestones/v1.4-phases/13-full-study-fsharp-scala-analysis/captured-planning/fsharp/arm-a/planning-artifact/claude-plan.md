# Claude's Task Decomposition — F# FsLexYacc Calculator (Arm A Input)

This is the mechanical conversion of the v1 F# task decomposition (task1-scaffold /
task2-lexer / task3-parser / task4-evaluator / task5-buildtest) into a single-session
numbered plan. Five steps, meaning preserved verbatim from the v1 task prompts;
phrasing adapted for single-session state handoff only (no new planning detail added,
no subtasks restructured, no ambiguities clarified — Pitfall 7: conversion is
mechanical format-only).

FAIRNESS NOTE: No lexer source (Lexer.fsl), no parser source (Parser.fsy), no
Program.fs source, and no .fsproj XML body is embedded in this plan. FsLex/FsYacc is
out-of-distribution for the 35B and it may FAIL in BOTH arms — that is valid data.
The ONLY difference between Arm A and Arm B is that this plan supplies the task
decomposition and names the fslex/fsyacc build steps; neither arm receives
pre-supplied source code.

---

## Step 1 — Scaffold

Run `dotnet new console -lang F# -o calc` in the working directory to create the
project skeleton. This creates calc/ with calc.fsproj and Program.fs.

Wire calc/calc.fsproj for FsLexYacc 11.3.0 by rewriting it to include:
- An `<FsYacc Include="Parser.fsy">` item with `--module Parser` in OtherFlags.
- An `<FsLex Include="Lexer.fsl">` item with `--unicode --module Lexer` in
  OtherFlags.
- A `<PackageReference Include="FsLexYacc" Version="11.3.0" />` item.
- A compile order `<Compile>` group listing: Parser.fsi, Parser.fs, Lexer.fs,
  Program.fs (F# compile order matters; Parser.fsi/.fs must precede Lexer.fs because
  Lexer opens Parser).
- A `<Target Name="FixLineDirectives">` that runs after CallFsYacc and CallFsLex and
  strips `# 0` line directives that fsyacc emits and that the .NET 10 F# compiler
  rejects. Use sed to remove those lines from Parser.fs and Lexer.fs.

Do NOT paste ready-to-use .fsproj XML — write the file yourself using a bash heredoc.

Create an empty placeholder Parser.fsy:
  cd calc && touch Parser.fsy

Verify the scaffold:
  ls calc/
  cat calc/calc.fsproj

Success criterion: calc/ contains calc.fsproj, Program.fs, Parser.fsy; calc.fsproj is
wired for FsLexYacc 11.3.0 with the FixLineDirectives target and the correct compile
order. Do not build yet.

## Step 2 — Write Lexer.fsl

After Step 1, calc/ exists with the wired .fsproj. Create calc/Lexer.fsl — the FsLex
lexer source — that tokenizes integer arithmetic expressions.

Write a lexer (FsLex syntax, NOT FsYacc syntax — FsLex does NOT use %% section
separators). The lexer must:
- Open the Parser module and FSharp.Text.Lexing.
- Define a lexing rule called `tokenize` that matches: whitespace (skip), integer
  literals (['0'-'9']+, parse to int and emit INT token), + - * / ( ) operator
  characters (each emitting the corresponding token), eof (emit EOF), and unexpected
  characters (failwith an error).
- Use the token names that the parser (Step 3) will declare: INT (carrying an int),
  PLUS, MINUS, STAR, SLASH, LPAREN, RPAREN, EOF.

After writing, show `cat calc/Lexer.fsl`. Do not build yet.

Success criterion: Lexer.fsl exists and uses FsLex rule syntax; token names match
what the parser will declare.

## Step 3 — Write Parser.fsy

After Step 2, Lexer.fsl exists. Write calc/Parser.fsy — the FsYacc grammar — for
integer arithmetic expressions.

The parser must:
- Declare the tokens: INT (carrying an int value), PLUS, MINUS, STAR, SLASH, LPAREN,
  RPAREN, EOF.
- Define a grammar over integer arithmetic with the four operators and parentheses.
  Semantic actions should compute and return an int directly (no separate AST needed).
- Expose a single entry point named `start` of type int: use `%start start` and
  `%type <int> start`; `start` parses an `expr` followed by EOF.
- Enforce precedence: * and / bind more tightly than + and -; all operators associate
  left-to-right (so 10-3-2 = 5, not 9).
- Handle parenthesized subexpressions normally.

After writing, show `cat calc/Parser.fsy`. Do not build yet.

Success criterion: Parser.fsy is written; it declares the correct tokens, the correct
entry point `start`, and enforces precedence/associativity.

## Step 4 — Write Program.fs

After Step 3, calc/ has Lexer.fsl, Parser.fsy, and the wired .fsproj. Rewrite
calc/Program.fs — the CLI entry point — so the calculator works end-to-end.

Program.fs must:
- Read exactly one command-line argument (the arithmetic expression as a string).
- If the wrong number of arguments is given, print a usage message to stderr and exit
  with a nonzero exit code.
- Open `FSharp.Text.Lexing` (this exact namespace — NOT Microsoft.FSharp.Text.Lexing,
  which does not exist in .NET 10).
- Create a LexBuffer<char> from the argument string using LexBuffer<char>.FromString.
- Call `Parser.start Lexer.tokenize lexbuf` to parse and evaluate.
- Print the integer result (and only the result) to stdout, followed by a newline.

The invocation must be: `dotnet run -- "2+3*4"` prints `14`.

After writing, show `cat calc/Program.fs`. Do not build yet.

Success criterion: Program.fs reads argv.[0], lexes and parses with the generated
modules, and prints the integer result.

## Step 5 — Build and test

After Step 4, calc/ has all four source files. Build the project and verify all
canonical tests.

Build:
  cd calc && dotnet build 2>&1

If the build fails, read the compiler error carefully, fix the relevant source file
using bash-only edits (heredoc/printf/tee — NOT file_editor), and rebuild. Repeat
until the build succeeds. Report each error encountered and what was changed to fix it.

Run all three canonical tests verbatim and report exact outputs + exit codes:
  dotnet run -- "2+3*4"
  dotnet run -- "(2+3)*4"
  dotnet run -- "10-3-2"

Required outputs: 14 / 20 / 5 respectively.

Report the EXACT output and exit code for each test. If a test prints the wrong
number, state that clearly — an honest failure is more valuable than a fabricated
success.

Success criterion: all three canonical tests print the correct integer and exit 0. If
not, state which tests failed and what they printed.
