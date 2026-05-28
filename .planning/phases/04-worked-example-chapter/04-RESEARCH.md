# Phase 4 Research: Worked-Example Chapter (4부)

**Written by:** gsd-phase-researcher  
**Date:** 2026-05-28  
**Purpose:** Provide the planner with everything needed to write accurate, evidence-based tasks for the 4부 Korean mdBook chapter. This document is the sole source of truth for facts about the captured run; the planner should not infer anything about the run beyond what is stated here.

---

## 1. Recommended 4부 Chapter File Mapping

The five SUMMARY.md 4부 entries (lines 26-30) map to these files under `src/ch04-calculator/`. The planner should create all five files before wiring SUMMARY.md (per mdBook create-missing=false convention).

| SUMMARY entry | Recommended filename | Core content | Requirements satisfied |
|---|---|---|---|
| 예제 프로젝트 소개 | `intro.md` | What the calculator does (tokenize→parse→evaluate pipeline); the 4-file architecture (Lexer.fsl, Parser.fsy, Program.fs, calc.fsproj); honest scaffolding disclosure up front; connection to ch01 vocabulary preview. | WALK-01 |
| 태스크 계획 단계 | `planning.md` | How we decomposed the work into 5 scoped OpenHands tasks; honest note that Lexer.fsl and calc.fsproj were provided verbatim (with rationale: FsLex is out-of-distribution for 35B); the agent's real scope = Parser.fsy + Program.fs + self-correction. Maps to: Explore/Analyze phases of plan→write→test→run (ch01 vocabulary callout). | WALK-02 (decomposition sub-requirement) |
| 코드 작성 단계 | `writing.md` | Step-by-step walkthrough of task1-scaffold (27 TerminalActions, base64 workaround story) + task3-parser (agent writes Parser.fsy with correct %left precedence from the start); concept callouts for tool calling and agent loop. | WALK-02, WALK-03 (parser/evaluator source embed) |
| 빌드와 테스트 단계 | `build-test.md` | The full error-and-fix narration (4 failures, verbatim error text, observed→decided→corrected format); task4-evaluator (Program.fs final wiring); concept callout for self-correction via observation loop. | WALK-02 (error-and-fix sub-requirement), VERIFY-01, VERIFY-02 |
| 완성된 계산기 | `final.md` | Complete final source embed (all 4 files); exact verification block (build + 3 test cases); honest performance paragraph (attempt 1 failure, attempt 2 timings). | WALK-03, VERIFY-01, VERIFY-02 |

**Notes on assignment:**
- VERIFY-01 and VERIFY-02 appear in both `build-test.md` (where the test output emerges naturally from task5) and `final.md` (where the complete source and official verification block live). The planner should put the authoritative embed in `final.md` and a forward-reference in `build-test.md`.
- The SUMMARY entries are currently empty links `()`. The planner tasks must create files and then wire SUMMARY.md to point at e.g. `ch04-calculator/intro.md`.

---

## 2. Honesty Constraints (MUST be baked into every task that touches these)

### 2A. Scaffolding Disclosure

**What to say:** The calc.fsproj and the Lexer.fsl were provided verbatim to the agent in the task prompts (task1-scaffold.txt and task2-lexer.txt respectively). The agent's genuine work in attempt 2 was:
1. Writing Parser.fsy (FsYacc grammar with correct `%left` precedence)
2. Writing Program.fs (CLI argument parsing + FSharp.Text.Lexing API wiring)
3. Self-correcting 4 build failures in task3 without external help

**Why provided:** FsLex .fsl format is out-of-distribution for the Qwen2.5-35B model. In attempt 1, three separate agent invocations (94+27+16 TerminalActions) all produced invalid FsLex files (added `%%` separator from FsYacc, wrong rule syntax, broken indentation in generated output). After those 3 agents exhausted the retry budget, the correct file was written as Deviation Rule 3.

**Chapter must NOT imply** the agent wrote the lexer from scratch. Chapter should frame it as: "We provided the lexer and project file; the agent's job was the parser, evaluator, and build self-correction."

### 2B. The Real Error-and-Fix (Not a Precedence Bug)

The roadmap originally anticipated a `%left` precedence bug. That did NOT happen. The agent wrote `%left PLUS MINUS` / `%left STAR SLASH` on the first attempt and all three test cases passed immediately after the build succeeded.

The real error-and-fix is FsYacc/F# build errors in task3-parser.jsonl. Details in Section 3 below.

**Chapter must NOT narrate a precedence bug.** It narrates build-error self-correction.

### 2C. Final Parser.fsy Precedence Expression

The final Parser.fsy (captured/final-source/Parser.fsy) expresses precedence using two separate declarations on separate lines:

```
%start start

%type <int> start
```

AND precedence:

```
%left PLUS MINUS
%left STAR SLASH
```

The combined form `%start <int> start` is what the agent first tried (attempt 2, event 11) — that is invalid FsYacc syntax and caused error parse error at Parser.fsy(16,7). The correct form is `%start start` on one line plus `%type <int> start` on a separate line. This is what the final Parser.fsy contains.

### 2D. Performance Numbers (Replace Stale Estimate)

**WRONG:** Any reference to "~240s/call" must be removed. That estimate does not appear in the captured evidence.

**REAL numbers from the run notes (03-02-RUN-NOTES.md):**

Attempt 2 per-task durations:

| Task | Duration | Events | TerminalActions |
|---|---|---|---|
| task1-scaffold | 3m 6s (07:08:28–07:11:34) | 56 | 27 |
| task2-lexer | 16s (07:14:15–07:14:31) | 6 | 2 |
| task3-parser | 1m 17s (07:14:57–07:16:14) | 34 | 15 |
| task4-evaluator | 45s (07:16:48–07:17:33) | 30 | 14 |
| task5-buildtest | 32s (07:17:57–07:18:29) | 20 | 9 |

**Total wall-clock attempt 2:** ~07:08 to ~07:18 = approximately 10 minutes elapsed (with gaps between tasks for prompt preparation). The run notes say "Task 3 completion at 07:16:14" and "Task 5 completion at 07:18:29", so the full 5-task run spans roughly 10 minutes of elapsed time from first to last task completion. Simple tool-call cycles within tasks ran ~14–15s turnaround (e.g., task2-lexer: 16s total for 2 TerminalActions = ~8s/call).

**Attempt 1 duration and failure:** Approximately 150 minutes total (2026-05-27 date; the exact wall-clock is not stated in the run notes but the volume is: 137+ TerminalActions across 6 logs, with task4-adjusted alone at 94 TerminalActions taking "~20 minutes" as noted). The failure was a systemic knowledge gap: the model (Qwen2.5-35B) could not produce a valid .fsl file despite 3 agent invocations because FsLex syntax is out-of-distribution. Not a speed failure — a capability boundary.

**What VERIFY-02 should say:** Simple tasks (lexer copy-in: 16s; build+test: 32s). More complex tasks (scaffold with file-writing struggles: 3m 6s; parser with 4 build cycles: 1m 17s). Attempt 1 failed after ~150 minutes because the 35B model hit a genuine knowledge boundary (FsLex .fsl format). This is an instructive limits story: the model can self-correct F# API errors but cannot synthesize an FsLex file from scratch.

---

## 3. Error-and-Fix Sequence (Verbatim from Evidence)

**Source:** transcript.md Task 3 section + 03-02-RUN-NOTES.md Error-and-Fix Cycle section.  
**Location in logs:** task3-parser.jsonl, events 9–31 (per run notes: "events 9-30" per CAPTURE-MANIFEST, "events 9-31" per run notes; the discrepancy is minor — the successful build is at event 29/30 depending on counting).

The chapter must use "observed→decided→corrected" structure for each failure. Here is the exact sequence with verbatim evidence available:

---

### Failure 1 — Missing %start declaration

**Observed (verbatim build error, transcript.md Step 5 / event 9):**
```
복원 완료(0.2초)
  calc net10.0 2 오류와 함께 실패 (0.3초)
    FSYACC : error FSY000: at least one %start declaration is required
    /Users/ohama/.nuget/packages/fslexyacc/11.3.0/build/FsLexYacc.targets(53,3): error MSB3073: ...명령이 종료되었습니다(코드: 1).

2 오류와 함께 실패 빌드(0.6초)
```

**Decided (ThinkAction, transcript.md Step 6 thought):**  
"The `%start` declaration is missing — I need to add it alongside `%type`:"

**Corrected:** Agent rewrote Parser.fsy adding `%start <int> start` above `%type <int> start`. (Note: this was the WRONG syntax — it led directly to failure 2.)

**Evidence quality:** ThinkAction text is present verbatim in transcript.md Step 6.

---

### Failure 2 — Invalid %start <int> start syntax (parse error)

**Observed (verbatim build error, transcript.md Step 8 / event 15):**
```
복원 완료(0.1초)
  calc net10.0 2 오류와 함께 실패 (0.2초)
    Parser.fsy(16,7): error parse error
    /Users/ohama/.nuget/packages/fslexyacc/11.3.0/build/FsLexYacc.targets(53,3): error MSB3073: ...명령이 종료되었습니다(코드: 1).

2 오류와 함께 실패 빌드(0.5초)
```

**Decided (ThinkAction, transcript.md Step 9 thought):**  
"The issue is having both `%start` and `%type` for the same rule. FsYacc only needs `%start` for the entry point — `%type` is for non-start rules. Let me fix that:"

**Corrected:** Agent rewrote Parser.fsy with only `%start <int> start` (removing `%type <int> start`). This was STILL invalid — the combined `%start <int> start` form is not valid FsYacc syntax.

**Evidence quality:** ThinkAction text is present verbatim in transcript.md Step 9.

---

### Failure 3 — Same parse error, second attempt

**Observed (verbatim build error, transcript.md Step 12 / event 19 — same error text):**
```
복원 완료(0.1초)
  calc net10.0 2 오류와 함께 실패 (0.2초)
    Parser.fsy(16,7): error parse error
    /Users/ohama/.nuget/packages/fslexyacc/11.3.0/build/FsLexYacc.targets(53,3): error MSB3073: ...명령이 종료되었습니다(코드: 1).

2 오류와 함께 실패 빌드(0.5초)
```

**Decided:** No ThinkAction text recorded for this step in transcript.md. The agent simply tried a different form: separating `%start start` and `%type <int> start` onto individual lines.

**Corrected:** Agent rewrote Parser.fsy with `%start start` on one line, `%type <int> start` on the next. This is the CORRECT FsYacc syntax. The parser itself now compiled. But a new error surfaced in Program.fs.

**Evidence quality:** No ThinkAction for this specific step. The chapter should narrate: "The agent tried separating the declarations — no reasoning was recorded for this attempt, but the parser accepted the grammar."

---

### Failure 4 — LexBuffer<_>.FromText does not exist

**Observed (verbatim build error, transcript.md Step 12 / event 25):**
```
복원 완료(0.1초)
  calc net10.0 3 오류와 함께 실패 (0.8초)
    /Users/ohama/projs/OpenHandsTests/oh-workdir/calc/Program.fs(11,38): error FS0039: 'LexBuffer<_>' 형식은 'FromText' 필드, 생성자 또는 멤버를 정의하지 않습니다. 다음 중 하나가 필요할 수 있습니다:   FromTextReader   FromBytes   FromString
    ...
3 오류와 함께 실패 빌드(1.1초)
```

**Decided (ThinkAction, transcript.md Step 13 thought):**  
"The parser compiled successfully! The errors are in `Program.fs` — let me fix the API calls:"

**Corrected:** Agent rewrote Program.fs changing `LexBuffer<char>.FromText(new StringReader(input))` to `LexBuffer<char>.FromString input`, and changed `Parser.start(Lexer.tokenize, lexbuf)` to `Parser.start Lexer.tokenize lexbuf` (F# curried application style).

**Evidence quality:** ThinkAction text is present verbatim in transcript.md Step 13. The agent correctly identified the error was in Program.fs, not Parser.fsy, and identified the exact API substitution needed.

---

### SUCCESS — Build succeeded

**Observed (verbatim build output, transcript.md Step 14):**
```
복원 완료(0.1초)
  calc net10.0 성공 (0.7초) → bin/Debug/net10.0/calc.dll

성공 빌드(1.0초)
```

**Post-fix validation (transcript.md Step 15):**
Agent ran 8 test expressions immediately after:
```
1+2*3 = 7
10-3-2 = 5
(10-3)-2 = 5
10-(3-2) = 9
2*3+4 = 10
(2+3)*4 = 20
100/10/2 = 5
1+2+3+4+5 = 15
```
All correct. This was NOT part of the formal test output (that's in task5); it was the agent's own in-task validation.

---

### Additional context: task3 also wrote Program.fs (out-of-scope agent behavior)

The task3-parser task was scoped to write Parser.fsy. The agent also wrote Program.fs (CmdRunAction at transcript.md Task 3 Step 4). This introduced the LexBuffer.FromText error (failure 4) because the agent used a non-existent API. The chapter should note this as observed genuine agent behavior: the agent exceeded its task scope to verify the build, which led to the fourth self-correction cycle.

---

## 4. Concept-to-Action Callout Candidates

These are grounded in the ch01/ch02 vocabulary. Each callout should appear as a boxed or highlighted element in the chapter, linking the concrete action to the abstract concept.

### Callout A: Tool Calling

**Where in the run:** Every `dotnet build`, `cat`, `ls` command executed by the agent (e.g., transcript.md Task 3 Step 5: `dotnet build 2>&1`).

**ch01 vocabulary wording (concepts.md):** "LLM이 일반 텍스트를 출력하는 대신, 구조화된 호출(이름 + 인자)을 출력해 환경에 행동을 지시합니다." / "OpenHands에서 tool calling은 ActionEvent의 형태로 구체화됩니다. CmdRunAction은 셸 명령을 실행하고..."

**Callout text suggestion:** "에이전트가 `dotnet build`를 실행하는 것은 tool calling의 구체적인 사례입니다. 에이전트는 텍스트로 '빌드해보겠습니다'라고 쓰는 게 아니라, CmdRunAction(`command: dotnet build`)을 emit해 실제로 명령을 실행합니다. 1부에서 배운 tool calling이 바로 이것입니다."

**ActionEvent type:** CmdRunAction (per actions-observations.md table).

### Callout B: Agent Loop / Self-Correction as Loop Behavior

**Where in the run:** The 4-failure cycle in task3. Build fails → error in ObservationEvent → next loop iteration → agent reads error → rewrites file → rebuild. This is the `Conversation.step()` while-loop in action.

**ch01 vocabulary wording (concepts.md):** "루프가 자율적이라는 점입니다. 사람이 '이제 다음 단계로 가라'고 지시하지 않아도, 에이전트가 관찰 결과를 보고 스스로 다음 행동을 결정합니다. 빌드가 실패하면 오류 메시지를 읽고 수정 코드를 작성하고..."

**ch02 vocabulary wording (actions-observations.md):** "OpenHands의 자가 수정(self-correction) 능력은 별도의 메커니즘이 아닙니다. 관찰 루프의 자연스러운 부수효과입니다."

**Callout text suggestion:** "빌드 오류 → 파일 수정 → 재빌드 사이클이 4회 반복됩니다. 이것은 별도로 설계된 '자가 수정 기능'이 아닙니다. CmdOutputObservation에 담긴 컴파일러 오류 메시지가 다음 루프 반복의 LLM 입력에 포함되고, LLM이 그것을 읽고 수정 ActionEvent를 emit하는 것입니다 — agent loop의 자연스러운 결과입니다."

### Callout C: Memory / Context — Persisted Files Across Task Invocations

**Where in the run:** Each of the 5 tasks is a separate OpenHands headless invocation. Yet task3 can read Lexer.fsl written by task2, and task5 can build the files written in tasks 1-4. The "memory" across invocations is not in the LLM's context window — it is in the filesystem (LocalWorkspace).

**ch01 vocabulary wording (concepts.md):** "에이전트 루프가 반복될수록 해야 할 일이 쌓입니다. 어떤 파일을 만들었는지... 이것이 memory(메모리)와 context window(컨텍스트 창)의 역할입니다." / "OpenHands는 모든 상호작용을 EventLog에 순서대로 기록합니다."

**Callout text suggestion:** "각 태스크는 별도의 OpenHands 실행입니다 — 이전 태스크의 EventLog가 공유되지 않습니다. 그런데 task3은 task2가 만든 Lexer.fsl을 읽을 수 있습니다. 이 '기억'은 LLM의 컨텍스트 창이 아니라 파일시스템(LocalWorkspace)에 있습니다. 이것은 memory 개념의 경계를 보여줍니다: EventLog는 한 세션 안에서만 유지되고, 세션 간 기억은 외부 저장소(파일)에 의존합니다."

### Callout D: Plan → Write → Test → Run (the 4-phase methodology visible across 5 tasks)

**Where in the run:** The 5-task decomposition maps directly to the methodology. Task 1 (scaffold = Explore), Task 3 (write parser = Implement), Task 5 (build+test = Verify). The test→fail→rewrite in task3 is the Verify→back-to-Implement cycle.

**ch01 vocabulary wording (concepts.md):** "에이전트가 복잡한 작업을 수행할 때, 곧바로 코드를 작성하지 않습니다... 탐색(Explore) → 분석(Analyze) → 구현(Implement) → 검증(Verify)"

**Callout text suggestion:** "다섯 개의 태스크 분해는 1부의 plan→write→test→run 방법론과 정확히 대응합니다. task1(탐색·스캐폴딩) = Explore, task3(파서 작성) = Implement, task5(빌드+테스트) = Verify. 그리고 task3 내부의 4회 빌드 실패는 Verify→Implement의 자가 수정 사이클입니다."

---

## 5. Final Source to Embed (WALK-03)

All files confirmed from `captured/final-source/`. Exact content follows.

### Parser.fsy (agent-authored — the core artifact)

Precedence is expressed using two separate lines: `%left PLUS MINUS` and `%left STAR SLASH`. The entry point uses the two-part form `%start start` / `%type <int> start` (on separate lines) — the agent arrived at this form after 3 failed attempts with the combined `%start <int> start` syntax.

Full content (39 lines):
```
%{
%}

%token <int> INT
%token PLUS
%token MINUS
%token STAR
%token SLASH
%token LPAREN
%token RPAREN
%token EOF

%left PLUS MINUS
%left STAR SLASH

%start start

%type <int> start

%%

start:
    | expr EOF
        { $1 }

expr:
    | INT
        { $1 }
    | expr PLUS expr
        { $1 + $3 }
    | expr MINUS expr
        { $1 - $3 }
    | expr STAR expr
        { $1 * $3 }
    | expr SLASH expr
        { $1 / $3 }
    | LPAREN expr RPAREN
        { $2 }
```

### Program.fs (agent-authored)

Final form uses `LexBuffer<char>.FromString` (not `FromText`) and F# curried call style for `Parser.start`:

```fsharp
open System
open FSharp.Text.Lexing

[<EntryPoint>]
let main argv =
    if Array.length argv <> 1 then
        eprintfn "Usage: calc <expression>"
        1
    else
        let input = argv.[0]
        let lexbuf = LexBuffer<char>.FromString input
        let result = Parser.start Lexer.tokenize lexbuf
        printfn "%d" result
        0
```

Note: the final `open System` is present but `System` is not actually used in the final code — the agent included it from an earlier draft. The chapter can note this without editorializing.

### Lexer.fsl (provided verbatim — NOT agent-authored)

```
{
open Parser
open FSharp.Text.Lexing
}

rule tokenize = parse
    | [' ' '\t']
        { tokenize lexbuf }
    | ['0'-'9']+
        { let s = LexBuffer<_>.LexemeString lexbuf
          let v = System.Int32.Parse s
          INT v }
    | '+'        { PLUS }
    | '-'        { MINUS }
    | '*'        { STAR }
    | '/'        { SLASH }
    | '('        { LPAREN }
    | ')'        { RPAREN }
    | eof        { EOF }
    | _
        { let c = LexBuffer<_>.LexemeString lexbuf
          failwithf "Unexpected character '%s'" c }
```

Chapter MUST label this file: "이 파일은 태스크 프롬프트에 전달된 내용을 그대로 복사한 것입니다 (에이전트가 작성하지 않음)."

### calc.fsproj (provided verbatim — NOT agent-authored)

The FixLineDirectives target is the key non-obvious piece:

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
      <OtherFlags>--unicode --module Lexer</OtherFlags>
    </FsLex>
  </ItemGroup>

  <!-- REQUIRED WORKAROUND for .NET 10 + FsLexYacc 11.3.0:
       fsyacc generates "# 0 """" line directives that F# 10 compiler rejects.
       Strip them with a post-generation sed step. -->
  <Target Name="FixLineDirectives" BeforeTargets="CoreCompile" DependsOnTargets="CallFsYacc;CallFsLex">
    <Exec Command="sed -i '' '/^# 0/d' Parser.fs" Condition="Exists('Parser.fs')" />
    <Exec Command="sed -i '' '/^# 0/d' Lexer.fs" Condition="Exists('Lexer.fs')" />
  </Target>

  <ItemGroup>
    <!-- Compile order matters in F#: Parser.fsi/.fs must precede Lexer.fs (Lexer opens Parser) -->
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

Chapter MUST label this: "이 파일도 태스크 프롬프트에 제공됐습니다. FixLineDirectives 타겟은 .NET 10 + FsLexYacc 11.3.0 호환성 문제를 해결하는 비직관적인 워크어라운드입니다."

---

## 6. Exact Verification Block (VERIFY-01)

**Source:** `captured/test-output.txt` (the authoritative post-run host check).

```
=== Calculator Correctness Test ===

Build:
  복원할 프로젝트를 확인하는 중...
  복원할 모든 프로젝트가 최신 상태입니다.
  calc -> /Users/ohama/projs/OpenHandsTests/oh-workdir/calc/bin/Debug/net10.0/calc.dll

빌드했습니다.
    경고 0개
    오류 0개

경과 시간: 00:00:00.95

Test cases:
2+3*4 = 14
(2+3)*4 = 20
10-3-2 = 5
```

**Explanation of each case (for chapter prose):**
- `2+3*4 = 14`: STAR binds tighter than PLUS (`%left STAR SLASH` declared after `%left PLUS MINUS` = higher precedence). A grammar without `%left` would give 20 (wrong).
- `(2+3)*4 = 20`: Explicit grouping overrides precedence rules via the `LPAREN expr RPAREN` grammar rule.
- `10-3-2 = 5`: Left-associativity: (10-3)-2 = 5, not 10-(3-2) = 9. The `%left MINUS` declaration enforces left-associativity.

Additionally, task3 step 15 (transcript.md) shows the agent's own in-task validation with 8 expressions (all correct). The chapter may reference this as the agent's self-check, distinct from the formal host verification.

---

## 7. Honest Performance Paragraph (VERIFY-02)

This paragraph must appear in `final.md` (and optionally referenced in `build-test.md`). It must use only numbers from the captured evidence.

**Draft paragraph (Korean, for chapter inclusion):**

---

**성능과 한계에 대한 솔직한 기록**

이 튜토리얼은 실제 실행의 솔직한 기록입니다. 두 가지 사실을 그대로 전달합니다.

**시도 2의 실제 속도:** 간단한 태스크는 빠릅니다. task2(렉서 복사)는 16초, task5(빌드+테스트)는 32초가 걸렸습니다. 더 복잡한 task1(스캐폴딩, 파일 쓰기 27회)은 3분 6초, task3(파서 작성 + 빌드 4회 실패+수정)은 1분 17초였습니다. 5개 태스크 전체 실행 시간은 약 10분입니다.

**시도 1의 실패:** 시도 1은 약 150분간 진행됐지만 실패했습니다. 원인은 속도가 아니라 능력의 경계였습니다. Qwen2.5-35B 모델은 FsLex .fsl 파일을 올바르게 작성하지 못했습니다 — 3번의 에이전트 실행(94+27+16 TerminalActions)에서 모두 FsYacc 문법의 `%%` 구분자를 FsLex에 삽입하거나, 잘못된 렉심 추출 패턴을 사용했습니다. FsLex 문법은 이 모델의 훈련 데이터에서 드문 형식입니다. 이 문제를 우회하기 위해 시도 2에서는 Lexer.fsl을 태스크 프롬프트에 직접 제공했습니다.

**결론:** 35B 로컬 모델은 F# 컴파일러 오류를 스스로 진단하고 수정할 수 있습니다 (task3의 4회 자가 수정이 그 증거입니다). 그러나 훈련 데이터에서 드문 DSL 형식(.fsl)은 생성하지 못합니다. 이것은 현재 로컬 LLM의 현실적인 능력 지도입니다.

---

**Evidence sources for all numbers:**
- 16s, 32s, 3m 6s, 1m 17s, ~10 min: 03-02-RUN-NOTES.md Per-Task Outcome Table timestamps
- 150 min, 94+27+16 TerminalActions: 03-02-RUN-NOTES-attempt1.md JSONL Log Files Summary + "~20 minutes" note for task4-adjusted
- The FsLex failure modes: 03-02-RUN-NOTES-attempt1.md Root Cause Analysis section

---

## 8. Thin Evidence Flags

The planner should be aware of these gaps:

1. **No ThinkAction for failure 3 (second parse-error attempt):** The agent made another attempt without a recorded reasoning step. The chapter cannot quote a decision rationale for this specific iteration. Narrate as: "에이전트는 세 번째 빌드에서도 같은 오류를 받았습니다. 이번에는 추론 기록 없이 곧바로 다른 방법을 시도했습니다: `%start start`와 `%type <int> start`를 별도 줄로 분리하는 방식이었습니다."

2. **Task 1 (scaffold) is verbose but not the chapter's focus:** 27 TerminalActions were mostly the agent struggling with file-writing (heredoc corruption, base64, Python script approaches). This is mentioned in planning.md as "the agent's file-writing challenges" but should not be narrated in full detail — it's not the interesting part of the run.

3. **No timing evidence for attempt 1 wall-clock total:** The run notes say task4-adjusted took "~20 minutes" (killed), but the total 150-minute estimate for attempt 1 is an approximation. The chapter should say "approximately" rather than citing a precise figure.

4. **task4-evaluator is not the "evaluator" in the traditional sense:** The agent in task4 largely found that Program.fs was already correct from task3 (the agent had written it out-of-scope during task3), read the parser interface file, and then wrote a slightly cleaner version of Program.fs. The chapter's "코드 작성 단계" should present this accurately: task4 confirmed and refined the CLI wiring.

5. **The term "evaluator" for Program.fs:** In the chapter architecture description, the "evaluate" step is handled by the F# arithmetic in the parser grammar actions (`$1 + $3` etc.), not by a separate evaluator module. Program.fs is the CLI entry point and lexer/parser wiring. The chapter should not imply there is a separate evaluator; the grammar actions ARE the evaluation.

---

## 9. File Paths for Planner Reference

All paths below are confirmed to exist:

| File | Absolute path |
|---|---|
| CAPTURE-MANIFEST | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/captured/CAPTURE-MANIFEST.md |
| Transcript | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/captured/transcript.md |
| Test output | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/captured/test-output.txt |
| Parser.fsy (final) | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/captured/final-source/Parser.fsy |
| Program.fs (final) | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/captured/final-source/Program.fs |
| Lexer.fsl (final) | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/captured/final-source/Lexer.fsl |
| calc.fsproj (final) | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/captured/final-source/calc.fsproj |
| Run notes attempt 2 | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/03-02-RUN-NOTES.md |
| Run notes attempt 1 | /Users/ohama/projs/OpenHandsTests/.planning/phases/03-capture-the-openhands-run/03-02-RUN-NOTES-attempt1.md |
| ch01 concepts | /Users/ohama/projs/OpenHandsTests/src/ch01-agentic-ai/concepts.md |
| ch02 agent-loop | /Users/ohama/projs/OpenHandsTests/src/ch02-openhands/agent-loop.md |
| ch02 actions-observations | /Users/ohama/projs/OpenHandsTests/src/ch02-openhands/actions-observations.md |
| SUMMARY.md | /Users/ohama/projs/OpenHandsTests/src/SUMMARY.md |
| Output dir (create) | /Users/ohama/projs/OpenHandsTests/src/ch04-calculator/ |

---

## 10. Summary for Planner

**The 5 chapter files** under `src/ch04-calculator/`: intro.md, planning.md, writing.md, build-test.md, final.md.

**The 4 critical honesty constraints:**
1. Lexer.fsl and calc.fsproj were provided — do not imply agent wrote them.
2. No precedence bug — agent wrote correct `%left` from the start; real error-and-fix is build errors.
3. Performance: ~10 min attempt 2, ~150 min attempt 1 (failure), not "~240s/call".
4. No invented transcripts — every quoted command/output from transcript.md or test-output.txt.

**The 4 build failures** in task3 are the chapter's heart:
- FSY000 missing %start → added (wrong form %start <int> start)
- Parser.fsy(16,7) parse error → tried removing %type (still wrong form)
- Same parse error again → separated correctly as `%start start` + `%type <int> start`
- FS0039 LexBuffer.FromText → changed to LexBuffer<char>.FromString

**The 4 concept callouts** (ch01→ch04):
- Tool calling = CmdRunAction for dotnet build
- Agent loop = the 4-failure self-correction cycle
- Memory/context = filesystem persistence across separate task invocations
- Plan→write→test→run = the 5-task decomposition structure

**Evidence quality:** ThinkAction text is available for failures 1, 2, and 4. No ThinkAction for failure 3 — narrate without quoting rationale.
