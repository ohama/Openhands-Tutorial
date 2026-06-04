---
phase: 16-fsharp-scala-gsd-mechanical-arm-c
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - Calc.fsproj
  - Parser.fsy
  - Lexer.fsl
  - Program.fs
autonomous: true

must_haves:
  truths:
    - "Project builds offline from the NuGet cache (no network) via `dotnet build`"
    - "`dotnet run -- \"2+3*4\"` prints 14 (multiplication binds tighter than addition)"
    - "`dotnet run -- \"(2+3)*4\"` prints 20 (parentheses override precedence)"
    - "`dotnet run -- \"10-3-2\"` prints 5 (subtraction is left-associative)"
  artifacts:
    - path: "Calc.fsproj"
      provides: "MSBuild wiring: FsLexYacc 11.3.0 PackageReference, FsYacc/FsLex items with --module flags, generated Compile items in strict order"
      contains: "FsLexYacc"
    - path: "Parser.fsy"
      provides: "FsYacc stratified Expr/Term/Factor grammar encoding precedence + left-associativity structurally"
      contains: "%token <int> INT"
    - path: "Lexer.fsl"
      provides: "FsLex unicode tokenizer returning Parser token constructors"
      contains: "module Lexer"
    - path: "Program.fs"
      provides: "EntryPoint driving LexBuffer<char> -> Parser.start Lexer.tokenize, printing the int"
      contains: "[<EntryPoint>]"
  key_links:
    - from: "Calc.fsproj"
      to: "Parser.fsy / Lexer.fsl"
      via: "FsYacc item declared BEFORE FsLex item; --module Parser / --module Lexer --unicode"
      pattern: "<FsYacc Include=\"Parser.fsy\">"
    - from: "Calc.fsproj"
      to: "generated Parser.fs/Lexer.fs"
      via: "Compile items in exact order Parser.fsi, Parser.fs, Lexer.fs, Program.fs"
      pattern: "Parser.fsi"
    - from: "Lexer.fsl"
      to: "Parser.fsy tokens"
      via: "open Parser; returns INT/PLUS/MINUS/TIMES/DIV/LPAREN/RPAREN/EOF exactly as declared in %token"
      pattern: "open Parser"
    - from: "Program.fs"
      to: "Parser.start / Lexer.tokenize"
      via: "LexBuffer<char>.FromString argv.[0] |> Parser.start Lexer.tokenize"
      pattern: "Parser.start Lexer.tokenize"
---

<objective>
Build an F# CLI integer calculator using the FsLexYacc toolchain (FsLex `Lexer.fsl` + FsYacc `Parser.fsy`), driven by a `Program.fs` entry point and wired through a single `Calc.fsproj`. It reads one CLI argument, evaluates an integer arithmetic expression (`+ - * /` with `* /` binding tighter, parentheses overriding, integer-only semantics), and prints the integer result.

Purpose: This is the arm-c (F#) implementation of the cross-language GSD mechanical-arm comparison. The make-or-break is **project wiring**, not algorithm difficulty — the FsLexYacc toolchain is niche and easy to misconfigure. Precedence and left-associativity are encoded **structurally** via a stratified `Expr → Term → Factor` grammar (not `%left`, which has a documented FsYacc honoring bug).

Output: Four source files (`Calc.fsproj`, `Parser.fsy`, `Lexer.fsl`, `Program.fs`) that build offline and pass all three canonical tests.
</objective>

<execution_context>
All file creation MUST use bash heredoc/printf (no file_editor available in this environment).
.NET 10 SDK on macOS. FsLexYacc 11.3.0 is present in the local NuGet cache
(`~/.nuget/packages/fslexyacc/11.3.0` and `~/.nuget/packages/fslexyacc.runtime/11.3.0`).
Do NOT run `dotnet add package` or anything that hits the network — restore resolves from cache.
</execution_context>

<context>
@/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1.4-phases/16-fsharp-scala-gsd-mechanical-arm-c/captured-planning/fsharp/arm-c/planning-artifact/RESEARCH.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Author the four source files (fsproj wiring + grammar + lexer + driver)</name>
  <files>Calc.fsproj, Parser.fsy, Lexer.fsl, Program.fs</files>
  <action>
Create all four files in the project directory using bash heredoc (quoted delimiter to prevent
shell interpolation of `$1`, `$3`, etc. in the grammar actions). The project is a single F#
console project. Honor the FOUR WIRING INVARIANTS from RESEARCH.md — getting any one wrong fails
the build:
  1. `<FsYacc>` item declared BEFORE `<FsLex>` item (FsYacc emits the token type the lexer opens).
  2. `--module Parser` on FsYacc and `--module Lexer --unicode` on FsLex.
  3. Generated Compile items in EXACT order: `Parser.fsi`, `Parser.fs`, `Lexer.fs`, `Program.fs`.
  4. `--unicode` on FsLex because Program.fs feeds a `LexBuffer<char>` (Unicode).

**Calc.fsproj** (verbatim shape — do not reorder ItemGroup entries):
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <FsYacc Include="Parser.fsy">
      <OtherFlags>--module Parser</OtherFlags>
    </FsYacc>
    <FsLex Include="Lexer.fsl">
      <OtherFlags>--module Lexer --unicode</OtherFlags>
    </FsLex>

    <Compile Include="Parser.fsi" />
    <Compile Include="Parser.fs" />
    <Compile Include="Lexer.fs" />
    <Compile Include="Program.fs" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="FsLexYacc" Version="11.3.0" />
  </ItemGroup>
</Project>
```
Do NOT add an explicit `FsLexYacc.Runtime` PackageReference — it arrives transitively. Do NOT set
`FsLexOutputFolder`/`FsYaccOutputFolder` — leaving them unset writes generated files to the project
root, matching the plain `Parser.fs`/`Lexer.fs` Compile paths.

**Parser.fsy** (stratified grammar — left-recursive for left-associativity, NO `%left`):
```
%{
%}

%token <int> INT
%token PLUS MINUS TIMES DIV LPAREN RPAREN EOF

%start start
%type <int> start

%%

start:
    | Expr EOF                 { $1 }

Expr:
    | Expr PLUS  Term          { $1 + $3 }
    | Expr MINUS Term          { $1 - $3 }
    | Term                     { $1 }

Term:
    | Term TIMES Factor        { $1 * $3 }
    | Term DIV   Factor        { $1 / $3 }
    | Factor                   { $1 }

Factor:
    | INT                      { $1 }
    | LPAREN Expr RPAREN       { $2 }
```
Note: `/` is F# integer (truncating) division — satisfies integer-only. Left-recursion in Expr/Term
gives left-associativity (`10-3-2` → `(10-3)-2` = 5). Do NOT make these rules right-recursive.

**Lexer.fsl** (unicode; returns exactly the tokens declared in Parser.fsy):
```
{
module Lexer

open FSharp.Text.Lexing
open Parser

let lexeme (lexbuf: LexBuffer<_>) = LexBuffer<_>.LexemeString lexbuf
}

let digit      = ['0'-'9']
let int        = digit+
let whitespace = [' ' '\t']
let newline    = '\r' | '\n' | "\r\n"

rule tokenize = parse
    | whitespace  { tokenize lexbuf }
    | newline     { tokenize lexbuf }
    | int         { INT (System.Int32.Parse (lexeme lexbuf)) }
    | '+'         { PLUS }
    | '-'         { MINUS }
    | '*'         { TIMES }
    | '/'         { DIV }
    | '('         { LPAREN }
    | ')'         { RPAREN }
    | eof         { EOF }
    | _           { failwithf "Unexpected character: %s" (lexeme lexbuf) }
```
Token names returned here MUST match the `%token` declarations exactly (INT, PLUS, MINUS, TIMES,
DIV, LPAREN, RPAREN, EOF). Rule name `tokenize` → generated `Lexer.tokenize`. `-` is the MINUS
operator only; unary/negative-number lexing is out of scope for the canonical tests.

**Program.fs** (single CLI arg → integer result):
```fsharp
module Program

open FSharp.Text.Lexing

[<EntryPoint>]
let main argv =
    let input = argv.[0]
    let lexbuf = LexBuffer<char>.FromString input
    let result = Parser.start Lexer.tokenize lexbuf
    printfn "%d" result
    0
```
`Parser.start` matches `%start start` + `--module Parser`; `Lexer.tokenize` matches `rule tokenize`
+ `--module Lexer`. `LexBuffer<char>` requires the lexer's `--unicode` flag (invariant 4).
  </action>
  <verify>
Confirm all four files exist with expected anchors:
`ls Calc.fsproj Parser.fsy Lexer.fsl Program.fs` and
`grep -q 'FsLexYacc' Calc.fsproj && grep -q '%token <int> INT' Parser.fsy && grep -q 'open Parser' Lexer.fsl && grep -q 'Parser.start Lexer.tokenize' Program.fs && echo WIRED`.
Also confirm Compile order: `grep -n 'Compile Include' Calc.fsproj` shows Parser.fsi, Parser.fs, Lexer.fs, Program.fs in that order.
  </verify>
  <done>Four files exist; fsproj has FsYacc-before-FsLex, `--module`/`--unicode` flags, and the exact Compile order; grammar is left-recursive stratified; lexer returns the declared tokens; Program drives `Parser.start Lexer.tokenize` over a `LexBuffer<char>`.</done>
</task>

<task type="auto">
  <name>Task 2: Build offline, verify generated-file location, run the three canonical tests</name>
  <files>(no new files — build + run only)</files>
  <action>
Run `dotnet build` from the project directory. The `FsLexYacc.targets` (auto-imported by the
PackageReference) run `CallFsLex`/`CallFsYacc` before CoreCompile, generating `Parser.fs`,
`Parser.fsi`, and `Lexer.fs` into the project root. Restore resolves from the local NuGet cache —
do NOT add `--no-restore` on the first build (let restore populate from cache), and do NOT pass any
flag that forces network access.

Handle the known open questions from RESEARCH.md proactively:
  - **Generated-file location (Pitfall 7 / Open Question 1):** After a successful generate step, if
    the build errors with "Could not find file 'Parser.fs'" (or similar), check whether the targets
    wrote the generated files under `obj/` instead of the project root. If so, point the Compile
    items at the actual location (e.g. `<Compile Include="$(IntermediateOutputPath)Parser.fs" />`)
    OR define `<FsLexOutputFolder>./</FsLexOutputFolder>` and `<FsYaccOutputFolder>./</FsYaccOutputFolder>`.
    Prefer confirming the root location first (`ls Parser.fs Parser.fsi Lexer.fs`).
  - **`Parser.fsi` emission (Open Question 2):** If the build fails specifically because
    `Parser.fsi` was not generated, remove the single `<Compile Include="Parser.fsi" />` line and
    rebuild (`Parser.fs` alone still compiles).

Once the build succeeds, run the three canonical acceptance tests and compare output exactly:
```bash
dotnet run -- "2+3*4"     # expect: 14
dotnet run -- "(2+3)*4"   # expect: 20
dotnet run -- "10-3-2"    # expect: 5
```
If `10-3-2` prints 9, associativity is wrong — confirm the grammar rules are LEFT-recursive
(`Expr: Expr MINUS Term`), not right-recursive. If `2+3*4` prints 20, precedence is wrong — confirm
the stratified Expr/Term/Factor levels are intact. Use `--no-build` on the run commands after the
first successful build to avoid redundant rebuilds.
  </action>
  <verify>
`dotnet build` exits 0. Then all three assertions hold exactly:
`[ "$(dotnet run --no-build -- '2+3*4')" = "14" ]`,
`[ "$(dotnet run --no-build -- '(2+3)*4')" = "20" ]`,
`[ "$(dotnet run --no-build -- '10-3-2')" = "5" ]`.
Generated files present: `ls Parser.fs Lexer.fs` succeeds (location confirmed).
  </verify>
  <done>Build succeeds offline from cache; all three canonical tests print exactly 14, 20, 5 respectively; generated lexer/parser files are present at the resolved location and wired into the build.</done>
</task>

</tasks>

<verification>
- `dotnet build` completes with exit code 0 using only the local NuGet cache (no network).
- Precedence: `2+3*4` → 14 (not 20).
- Parentheses: `(2+3)*4` → 20.
- Left-associativity: `10-3-2` → 5 (not 9).
- The four wiring invariants are all satisfied (FsYacc-before-FsLex, --module flags, Compile order, --unicode).
</verification>

<success_criteria>
- All four source files exist and are correctly wired (Calc.fsproj, Parser.fsy, Lexer.fsl, Program.fs).
- Project builds offline; FsLex/FsYacc generators run via the auto-imported targets.
- All three canonical tests pass with exact integer output (14, 20, 5).
- No hand-edited generated files; no network-dependent restore; no `%left`-based precedence.
</success_criteria>

<output>
After completion, create `01-SUMMARY.md` in the same planning-artifact directory recording:
final file list, resolved generated-file location, the exact build command used, and the three
canonical test results (input → output).
</output>
