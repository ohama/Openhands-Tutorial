# Phase 16: F# FsLex/FsYacc Integer Calculator - Research

**Researched:** 2026-06-04
**Domain:** F# / .NET parser generators (FsLex lexer + FsYacc LALR parser) on .NET 10, macOS, offline
**Confidence:** HIGH

## Summary

This phase builds a single-argument CLI integer calculator in F# using the FsLexYacc toolchain:
a `Lexer.fsl` (FsLex regex-based tokenizer) and a `Parser.fsy` (FsYacc LALR(1) grammar) that are
code-generated into `.fs`/`.fsi` files at build time by MSBuild targets shipped inside the
`FsLexYacc` NuGet package. The generated lexer/parser are then compiled together with a
`Program.fs` that drives them via `FSharp.Text.Lexing.LexBuffer<char>.FromString`.

The make-or-break of this phase is **project wiring**, not algorithmic difficulty. The
toolchain is niche and easy to misconfigure: the `.fsproj` must reference the `FsLexYacc`
package (which auto-imports `FsLexYacc.targets`), declare `<FsYacc>`/`<FsLex>` items with the
correct `--module` flags, and list the **generated** `Compile` items in a strict order
(`Parser.fsi` → `Parser.fs` → `Lexer.fs` → `Program.fs`). The lexer must be built with
`--unicode` because the program feeds it a `LexBuffer<char>`. Operator precedence (`* /` tighter
than `+ -`) and left-associativity (`10-3-2 = 5`) are achieved **structurally** via a stratified
`Expr → Term → Factor` grammar with left-recursive rules — this is more reliable than `%left`
declarations, which have a documented FsYacc bug where they are sometimes not honored.

**Primary recommendation:** Use FsLexYacc 11.3.0 (already cached) with the stratified
`Expr/Term/Factor` grammar that encodes precedence structurally; wire the `.fsproj` with explicit
`--module` flags and the exact compile order `Parser.fsi, Parser.fs, Lexer.fs, Program.fs`;
drive it from `Program.fs` with `LexBuffer<char>.FromString argv.[0]` and evaluate directly in
the grammar's semantic actions (no separate AST needed).

## Standard Stack

The established toolchain for F# lexer/parser generation.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FsLexYacc | 11.3.0 | FsLex (.fsl) + FsYacc (.fsy) generators + MSBuild targets | The canonical, only actively-maintained F# lex/yacc; ships the `FsLexYacc.targets` that auto-run `fslex.dll`/`fsyacc.dll` at build |
| FsLexYacc.Runtime | 11.3.0 | Runtime types `FSharp.Text.Lexing.*` and `FSharp.Text.Parsing.*` | Provides `LexBuffer<char>`, table interpreters the generated code calls into; auto-pulled as a transitive dependency of FsLexYacc |
| FSharp.Core | (bundled w/ .NET 10 SDK) | F# core library | Required by all F# |
| .NET SDK | 10.0.203 | `dotnet build` / `dotnet run` | Host; confirmed installed |

Both packages are **confirmed present** in the local NuGet cache at
`~/.nuget/packages/fslexyacc/11.3.0` and `~/.nuget/packages/fslexyacc.runtime/11.3.0`.
No network is required.

### Supporting
| Component | Where | Purpose | When to Use |
|-----------|-------|---------|-------------|
| `FsLexYacc.targets` | `~/.nuget/packages/fslexyacc/11.3.0/build/FsLexYacc.targets` | Defines `CallFsLex`/`CallFsYacc` MSBuild targets that run before `CoreCompile` | Auto-imported by `<PackageReference Include="FsLexYacc" />`; no manual import needed |
| `fslex.dll` / `fsyacc.dll` | `.../build/fslex/net6.0/` and `.../build/fsyacc/net6.0/` | The actual generator executables (run via `dotnet <tool>.dll`) | Invoked automatically by the targets; tools themselves target net6.0 but run fine under the .NET 10 host |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FsLexYacc | Hand-written recursive-descent parser | Phase REQUIRES FsLex/FsYacc — out of scope; but note a hand-rolled parser is objectively simpler for this tiny grammar |
| Stratified grammar (Expr/Term/Factor) | `%left`/`%right` precedence declarations on a flat `expr OP expr` grammar | `%left` is terser but has a documented FsYacc bug (not always honored) → use stratified grammar for reliability |
| Direct evaluation in actions | Build an AST type then evaluate in Program.fs | AST is cleaner for larger languages but unnecessary here; direct eval is fewer files and fewer failure points |

**Installation (already satisfied — DO NOT run `dotnet add package` online):**
Add to the `.fsproj` (package restored from cache):
```xml
<ItemGroup>
  <PackageReference Include="FsLexYacc" Version="11.3.0" />
</ItemGroup>
```
`FsLexYacc.Runtime` arrives transitively; do not add it explicitly unless restore complains.

## Architecture Patterns

### Recommended Project Structure
```
arm-c-calc/                 # project dir (single project, single .fsproj)
├── Calc.fsproj             # references FsLexYacc; declares FsYacc/FsLex + compile order
├── Parser.fsy              # FsYacc grammar  → generates Parser.fs + Parser.fsi
├── Lexer.fsl               # FsLex spec      → generates Lexer.fs
└── Program.fs              # [<EntryPoint>]; drives lexer+parser, prints int
```
Generated `Parser.fs`, `Parser.fsi`, `Lexer.fs` appear in the project dir at build time. They are
build artifacts — do not hand-edit, do not commit.

### Pattern 1: The four wiring invariants (THE critical pattern)
**What:** Four things must all be true or the build fails.
**When to use:** Always, for any FsLexYacc project.

1. **Parser declared before Lexer** as MSBuild items — FsYacc emits the token union type that the
   lexer's generated code `open`s, so the parser must generate first.
2. **`--module <Name>` on BOTH** `<FsYacc>` and `<FsLex>` so the generated files have predictable
   module names (`Parser`, `Lexer`) that `Program.fs` and `Lexer.fsl` reference.
3. **Generated `Compile` items in exact order:** `Parser.fsi`, then `Parser.fs`, then `Lexer.fs`,
   then `Program.fs`. (`Parser.fsi` is the signature file FsYacc auto-emits next to `Parser.fs`.)
4. **`--unicode` on `<FsLex>`** because `Program.fs` builds a `LexBuffer<char>` (Unicode). Without
   it, the generated lexer expects `LexBuffer<byte>` and you get a type mismatch at the
   `Parser.start Lexer.tokenize lexbuf` call site.

**Example `.fsproj` (verbatim target shape):**
```xml
<!-- Source: fsprojects.github.io/FsLexYacc jsonParserExample + thanos.codes -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <!-- 1. Parser FIRST (generates token type the lexer needs) -->
    <FsYacc Include="Parser.fsy">
      <OtherFlags>--module Parser</OtherFlags>
    </FsYacc>
    <!-- 2. Lexer SECOND; --unicode because we feed LexBuffer<char> -->
    <FsLex Include="Lexer.fsl">
      <OtherFlags>--module Lexer --unicode</OtherFlags>
    </FsLex>

    <!-- 3. Generated outputs, in strict compile order -->
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

### Pattern 2: Stratified precedence grammar (Expr → Term → Factor)
**What:** Three grammar levels where left-recursion + structure encode both precedence and
left-associativity, with NO `%left`/`%right` needed.
**When to use:** Whenever correct precedence/associativity matters and you want to avoid the
`%left` reliability bug. This is the right choice for this phase.

- `Expr` handles `+`/`-` (loosest binding).
- `Term` handles `*`/`/` (tighter).
- `Factor` handles atoms: an `INT` or a parenthesized `Expr`.
- **Left-recursive** rules (`Expr: Expr PLUS Term`) give **left-associativity** → `10-3-2`
  parses as `(10-3)-2 = 5`. (A right-recursive rule would wrongly give `10-(3-2)=9`.)

### Anti-Patterns to Avoid
- **Flat `expr: expr OP expr` with a single `OP` token + `%left`:** ambiguous, produces
  shift/reduce conflicts, and depends on the buggy `%left` honoring. The thanos.codes blog uses
  this shape; do NOT copy it for a phase that requires correct precedence — use the stratified
  grammar instead.
- **Right-recursive expression rules:** silently break left-associativity (`10-3-2` → 9). The
  canonical test `10-3-2 → 5` exists precisely to catch this.
- **Omitting `Parser.fsi` from Compile:** FsYacc generates it; if you list `Parser.fs` without the
  `.fsi`, F# may pick up an inferred signature but you lose the intended interface and can hit
  visibility issues. List the `.fsi` first.
- **Manually running `fslex`/`fsyacc` and committing outputs:** unnecessary — the targets run them.
  Hand-edited generated files drift and break.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Tokenizing the input string | Custom char-by-char scanner | `Lexer.fsl` regex rules (FsLex) | Phase requires FsLex; FsLex handles whitespace skipping, multi-digit ints, longest-match for free |
| Operator precedence / associativity | Manual Shunting-yard or precedence climbing in F# | Stratified `Expr/Term/Factor` FsYacc grammar | LALR table handles it correctly; structural grammar is unambiguous and self-documenting |
| Running the generators | `<Exec>` calling `fslex`/`fsyacc` by hand | The auto-imported `FsLexYacc.targets` (`CallFsLex`/`CallFsYacc`) | Targets locate the tool DLLs, pass `-o`, run `dotnet <tool>.dll`, and register outputs for clean — all automatically |
| Building the lex buffer | Reading chars into an array yourself | `LexBuffer<char>.FromString argv.[0]` | One line; correct `Position` tracking and `Unicode` handling |
| Wiring lexer→parser | A manual token queue | `Parser.start Lexer.tokenize lexbuf` | The generated parser pulls tokens from the lexer function on demand |

**Key insight:** Almost everything in this phase is "configuration, not code." The failure modes
are in the `.fsproj` plumbing and the `.fsl`/`.fsy` directives, not in F# logic. Spend planning
effort on the wiring invariants; the actual grammar is ~12 lines.

## Common Pitfalls

### Pitfall 1: Wrong compile order
**What goes wrong:** Build error like "namespace or module Parser is not defined" (in Lexer.fs) or
unresolved token constructors.
**Why it happens:** F# compiles top-to-bottom; the generated lexer `open`s the parser's token type.
If `Lexer.fs` precedes `Parser.fs`, or the `FsLex` item precedes `FsYacc`, the token type isn't
available yet.
**How to avoid:** `FsYacc` item before `FsLex` item; Compile order `Parser.fsi, Parser.fs,
Lexer.fs, Program.fs` — exactly.
**Warning signs:** Compiler complains about `Parser` module/tokens being undefined inside generated
`Lexer.fs`.

### Pitfall 2: Missing `--module` flag
**What goes wrong:** Generated module is named after the file or gets an unexpected name; `Program.fs`
calls `Parser.start` / `Lexer.tokenize` but the module isn't `Parser`/`Lexer`.
**Why it happens:** Without `--module`, FsYacc/FsLex pick a default module name that may not match
what your code references.
**How to avoid:** Always pass `--module Parser` and `--module Lexer` in `<OtherFlags>`. Ensure the
names you reference in `Program.fs`/`Lexer.fsl` match exactly.
**Warning signs:** "The value, namespace, type or module 'Parser'/'Lexer' is not defined."

### Pitfall 3: `LexBuffer<char>` vs `LexBuffer<byte>` mismatch (forgot `--unicode`)
**What goes wrong:** Type error at `Parser.start Lexer.tokenize lexbuf` — the parser expects a
function over `LexBuffer<byte>` but you pass `LexBuffer<char>` (or vice-versa).
**Why it happens:** `LexBuffer<char>.FromString` produces a Unicode buffer; FsLex defaults to a
byte (ASCII) lexer unless `--unicode` is given.
**How to avoid:** Put `--unicode` in the `<FsLex>` `OtherFlags` AND use `LexBuffer<char>.FromString`
in `Program.fs`. Keep them consistent.
**Warning signs:** Type mismatch mentioning `LexBuffer<System.Byte>` vs `LexBuffer<System.Char>`.

### Pitfall 4: Lexer/parser token mismatch
**What goes wrong:** `Lexer.fsl` returns a token constructor (e.g., `TIMES`) that isn't declared in
`Parser.fsy` `%token`, or names differ (`ASTER` vs `TIMES`).
**Why it happens:** Tokens are defined once in the `.fsy` `%token` lines and the lexer must return
exactly those names (it `open`s `Parser`). A typo or a `%token` you forgot to declare breaks it.
**How to avoid:** Declare every token in `Parser.fsy` (`%token <int> INT`, `%token PLUS MINUS TIMES
DIV LPAREN RPAREN EOF`), and return precisely those constructors from `Lexer.fsl`. The integer
literal token must carry data: `%token <int> INT`, returned as `INT(System.Int32.Parse(lexeme))`.
**Warning signs:** "The value or constructor 'TIMES' is not defined" in generated `Lexer.fs`.

### Pitfall 5: Wrong associativity (`10-3-2` gives 9 not 5)
**What goes wrong:** Subtraction/division come out right-associative.
**Why it happens:** Right-recursive grammar rules, or relying on `%left` which FsYacc sometimes
ignores (documented bug, FsLexYacc issue #40 area).
**How to avoid:** Use **left-recursive** stratified rules: `Expr: Expr PLUS Term | Expr MINUS Term |
Term`. Verify against `10-3-2 → 5`.
**Warning signs:** Canonical test `10-3-2` returns 9.

### Pitfall 6: Missing `eof`/EOF handling
**What goes wrong:** Parser never terminates / "parse error" at end of input.
**Why it happens:** The grammar's `%start` rule must consume an explicit `EOF` token, and the lexer
must emit `EOF` on `eof`.
**How to avoid:** Lexer rule `| eof { EOF }`; start rule `start: Expr EOF { $1 }`. Note the FsLex
caveat: do not put a regex with `eof` followed by other chars.
**Warning signs:** Parse errors on otherwise valid input like `"2+3*4"`.

### Pitfall 7: `FsLexOutputFolder` / generated-file location & line directives
**What goes wrong:** `FsLexYacc.targets` writes generated `.fs` to `$(FsLexOutputFolder)` /
`$(FsYaccOutputFolder)`, which are **undefined by default** in the 11.3.0 targets — they resolve to
empty, i.e. the project root. Generated files contain `# line` directives pointing at the `.fsl`/
`.fsy` sources (for error mapping); these are normally fine.
**Why it happens:** The targets reference output-folder properties without defaulting them. With
empty values the generator writes `Parser.fs`/`Lexer.fs` next to the project file (matching the
`<Compile Include="Parser.fs" />` paths), which is what we want — so **do not set those properties**.
**How to avoid:** Leave `FsLexOutputFolder`/`FsYaccOutputFolder` unset so outputs land in the
project root beside the sources; reference plain `Parser.fs`/`Lexer.fs` in `Compile`. Only if a
later need arises (line-directive path problems) add `<OtherFlags>... --light-off</OtherFlags>` or
disable line directives — not needed for this phase.
**Warning signs:** "Could not find file 'Parser.fs'" at compile despite a successful generate step,
or generated files appearing in an unexpected folder. (NOTE: validate the actual output location
on first build — see Open Questions.)

## Code Examples

Verified, near-verbatim from official FsLexYacc docs and Microsoft Learn. Adapted to integer-only
arithmetic with the stratified precedence grammar required by this phase.

### Parser.fsy (stratified, integer-only, correct precedence + left-assoc)
```fsharp
// Source: learn.microsoft.com jomo_fisher calculator + fsprojects jsonParserExample
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
Notes: `$1/$3` are the values of grammar symbols; `/` here is F# integer division (truncating),
satisfying "integer arithmetic only". Left-recursion in `Expr`/`Term` yields left-associativity.

### Lexer.fsl (unicode, returns Parser tokens)
```fsharp
// Source: fsprojects.github.io/FsLexYacc fslex overview + jsonParserExample
{
module Lexer

open FSharp.Text.Lexing
open Parser            // brings INT, PLUS, ... EOF into scope

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
Notes: rule name `tokenize` → generated function `Lexer.tokenize`. Negative numbers are NOT lexed
here (`-` is the MINUS operator); the grammar treats `2-3` as subtraction. Unary minus is out of
scope for the canonical tests.

### Program.fs (single CLI arg → integer result)
```fsharp
// Source: fsprojects.github.io/FsLexYacc jsonParserExample (Program.fs pattern)
module Program

open FSharp.Text.Lexing

[<EntryPoint>]
let main argv =
    let input = argv.[0]                                  // single CLI argument
    let lexbuf = LexBuffer<char>.FromString input         // Unicode → needs --unicode lexer
    let result = Parser.start Lexer.tokenize lexbuf       // drive parser with lexer fn
    printfn "%d" result
    0
```
Notes: `Parser.start` matches the `%start start` rule and `--module Parser`. `Lexer.tokenize`
matches the `rule tokenize` and `--module Lexer`. `%type <int> start` makes `result : int`.

### Build / test commands
```bash
# Build (runs CallFsLex/CallFsYacc automatically, restores from cache)
dotnet build

# Canonical acceptance tests (must pass)
dotnet run -- "2+3*4"     # => 14
dotnet run -- "(2+3)*4"   # => 20
dotnet run -- "10-3-2"    # => 5
```
Offline note: pass `--no-restore` only after a successful restore, or set
`<RestoreSources>` if restore tries the network. Packages are cached, so default restore should
resolve locally.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| F# PowerPack `fslex.exe`/`fsyacc.exe`, manual `<Import>` of targets, `Microsoft.FSharp.Text.Lexing` | `FsLexYacc` NuGet package, auto-imported `FsLexYacc.targets`, `FSharp.Text.Lexing` namespace, `dotnet`-run tool DLLs | ~2015+ (PowerPack deprecated) | Old MSDN/Wikibooks samples use stale namespaces/imports — translate `Microsoft.FSharp.Text.Lexing` → `FSharp.Text.Lexing` and drop manual target imports |
| `LexBuffer<byte>` ASCII default | `LexBuffer<char>` + `--unicode` is the common modern path | — | Most string-based parsing uses char/Unicode; remember the `--unicode` flag |

**Deprecated/outdated:**
- **F# PowerPack & VS template** (the Microsoft Learn jomo_fisher post): grammar pattern is still
  valid and the canonical reference, but the install/template instructions are obsolete — use the
  NuGet `FsLexYacc` package, ignore the PowerPack download steps.
- **`Microsoft.FSharp.Text.Lexing`** namespace: now `FSharp.Text.Lexing` (confirmed in the cached
  runtime DLL).

## Open Questions

1. **Exact generated-file output location with FsLexYacc 11.3.0 targets**
   - What we know: `FsLexYacc.targets` writes to `$(FsLexOutputFolder)`/`$(FsYaccOutputFolder)`,
     which are undefined by default and thus resolve to the project root (beside the `.fsl`/`.fsy`).
     This matches plain `<Compile Include="Parser.fs"/>` paths and is the documented working setup.
   - What's unclear: whether some SDK/target interaction places them under `obj/` instead.
   - Recommendation: On first `dotnet build`, confirm `Parser.fs`, `Parser.fsi`, `Lexer.fs` appear
     in the project root. If they land elsewhere, set `<Compile Include="$(IntermediateOutputPath)
     Parser.fs"/>` accordingly OR define the output-folder properties to `./`. Cheap to verify;
     bake a verification step into the plan.

2. **Does FsYacc 11.3.0 always emit `Parser.fsi`?**
   - What we know: FsYacc generates a `.fsi`/`.fsi` signature alongside `-o Parser.fs`; the
     canonical examples list `Parser.fsi` in Compile.
   - What's unclear: minor edge cases where the `.fsi` is suppressed.
   - Recommendation: Keep `<Compile Include="Parser.fsi"/>` first; if the file is genuinely not
     produced, remove that one line (the `.fs` alone still compiles). Plan should treat the `.fsi`
     line as "include, but be ready to drop if absent."

3. **Division-by-zero / malformed input behavior**
   - What we know: Not exercised by the three canonical tests. F# integer `/` throws
     `DivideByZeroException`; bad tokens hit the lexer's `failwith`.
   - Recommendation: Out of scope — do not add error-handling complexity unless the phase later
     requires it. Keep `Program.fs` minimal.

## Sources

### Primary (HIGH confidence)
- Local NuGet cache `~/.nuget/packages/fslexyacc/11.3.0/` — `FsLexYacc.targets` (read verbatim:
  `CallFsLex`/`CallFsYacc` targets, `BeforeTargets="CoreCompile"`, `--module`-via-OtherFlags
  mechanics), `fslexyacc.nuspec`, tool layout.
- `dotnet fsyacc.dll --help` and `dotnet fslex.dll --help` (run locally) — authoritative flag list:
  `-o`, `--module`, `--unicode`, `--internal`, `--open`, `--lexlib`/`--parslib`.
- `~/.nuget/packages/fslexyacc.runtime/11.3.0/.../FsLexYacc.Runtime.dll` (symbol inspection) —
  confirmed `FSharp.Text.Lexing.LexBuffer\`1.FromString(System.String)`, `LexemeString`,
  `FromChars`, `FromBytes`; namespaces `FSharp.Text.Lexing` / `FSharp.Text.Parsing`.
- fsprojects.github.io/FsLexYacc JSON parser example — complete `.fsproj` ItemGroup, `Lexer.fsl`,
  `Parser.fsy`, `Program.fs` invocation pattern (`LexBuffer<char>.FromString`, `Parser.start
  Lexer.read lexbuf`).
- Microsoft Learn (jomo_fisher) — canonical stratified `Expr/Term/Factor` integer-calculator
  grammar with left-recursion.

### Secondary (MEDIUM confidence)
- thanos.codes "Using FsLexYacc" blog — modern `.fsproj` wiring, `--module`/`--unicode` flags,
  compile-order emphasis, evaluate-in-action pattern (its flat `expr OP expr` grammar deliberately
  NOT adopted due to precedence ambiguity).
- fsprojects.github.io/FsLexYacc fslex overview — `.fsl` file structure, `--unicode` ↔
  `LexBuffer<char>` relationship, `eof` caveat, `_` wildcard.

### Tertiary (LOW confidence)
- WebSearch summaries noting a FsYacc `%left` honoring bug (FsLexYacc issue tracker area) —
  motivates preferring the stratified grammar; not independently reproduced here.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — packages confirmed in local cache; targets/tool flags read directly.
- Architecture / wiring: HIGH — `.fsproj` shape and compile order corroborated by two official
  examples + the actual `FsLexYacc.targets`; one residual unknown (generated-file location) flagged.
- Grammar / precedence: HIGH — stratified pattern is the canonical Microsoft Learn calculator;
  left-recursion → left-assoc is standard LALR theory and directly satisfies `10-3-2 → 5`.
- Pitfalls: HIGH — each pitfall maps to a concrete, source-backed failure mode.

**Research date:** 2026-06-04
**Valid until:** 2026-09-04 (stable, mature toolchain; 90 days)
