# 완성된 계산기

이 장은 4부의 마무리입니다. 에이전트가 만든 계산기의 완성된 소스를 모두 보여주고, 실제 캡처된 테스트 출력으로 정확성을 검증하며, 이 실행에 대한 솔직한 성능 기록으로 끝맺습니다.

---

## 완성된 소스 (WALK-03)

계산기는 네 개의 파일로 구성됩니다. Parser.fsy와 Program.fs는 에이전트가 직접 작성했습니다. Lexer.fsl과 calc.fsproj는 태스크 프롬프트를 통해 제공된 파일입니다 — 그 이유는 아래 각 파일 설명에서 밝힙니다.

---

### Parser.fsy (에이전트 작성)

에이전트가 task3-parser 단계에서 작성한 FsYacc 문법 파일입니다. 빌드 오류를 4회 자가 수정한 끝에 완성한 최종본입니다.

```fsharp
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

**핵심 포인트:**

- `%left PLUS MINUS` / `%left STAR SLASH` — 두 줄의 우선순위 선언. 나중에 선언된 것이 더 높은 우선순위를 가집니다. STAR/SLASH가 PLUS/MINUS보다 강하게 결합합니다. `%left`는 동일 우선순위 토큰들이 왼쪽 결합임을 의미합니다.
- `%start start` + `%type <int> start` — 진입점과 반환 타입을 별도 줄로 선언합니다. 에이전트는 처음에 `%start <int> start`라는 잘못된 형식을 시도했고 parse error를 받았습니다. 올바른 FsYacc 구문은 두 선언을 분리하는 것입니다.
- 문법 액션 (`$1 + $3` 등) — 이것이 평가(evaluation)입니다. 별도의 평가 모듈이 없습니다. 파서가 문법 규칙을 환원할 때 연산을 직접 수행합니다.

---

### Program.fs (에이전트 작성)

CLI 진입점이자 렉서/파서 연결 코드입니다. task3-parser 중 에이전트가 task 범위를 초과하여 작성했고, task4-evaluator에서 최종 정리됐습니다.

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

**핵심 포인트:**

- `LexBuffer<char>.FromString input` — 에이전트가 task3 중 4번째 빌드 오류(`FS0039: 'LexBuffer<_>' 형식은 'FromText' 필드를 정의하지 않습니다`)에서 자가 수정한 결과입니다. 처음에는 존재하지 않는 `FromText`를 사용했고, 컴파일러 오류 메시지가 `FromString`을 제안했습니다.
- `Parser.start Lexer.tokenize lexbuf` — F# 커리드 호출 스타일. 에이전트가 처음 쓴 `Parser.start(Lexer.tokenize, lexbuf)` 튜플 스타일에서 수정됐습니다.
- `open System` — 최종 코드에서 `System` 네임스페이스를 직접 사용하지 않습니다. 이전 초안에서 남겨진 흔적입니다.

---

### Lexer.fsl (제공됨)

이 파일은 태스크 프롬프트에 전달된 내용을 그대로 복사한 것입니다 (에이전트가 작성하지 않음).

```fsharp
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

이 파일을 제공한 이유는 5부에서 자세히 다루지만, 짧게 요약하면: 시도 1에서 Qwen 3.6 35B 모델이 FsLex .fsl 형식을 올바르게 작성하지 못했습니다. FsLex 문법은 이 모델의 훈련 데이터에서 드문 형식입니다. 3회의 에이전트 실행이 모두 잘못된 .fsl 파일을 생성한 후, 시도 2에서는 렉서를 직접 제공하고 에이전트의 실제 작업을 parser + 빌드 자가 수정으로 집중했습니다.

---

### calc.fsproj (제공됨)

이 파일도 태스크 프롬프트에 제공됐습니다. FixLineDirectives 타겟은 .NET 10 + FsLexYacc 11.3.0 호환성 문제를 해결하는 비직관적인 워크어라운드입니다.

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

`FixLineDirectives` 타겟이 하는 일: fsyacc가 생성하는 `Parser.fs`에는 `# 0 ""` 형태의 라인 디렉티브가 포함됩니다. F# 10 컴파일러는 이 디렉티브를 거부합니다. `sed` 명령으로 `CoreCompile` 이전에 해당 줄을 제거합니다. 이 워크어라운드 없이는 빌드가 실패합니다. 이 비직관적인 부분을 에이전트에게 발견하도록 맡기면 실행이 막혔을 것이므로, 처음부터 올바른 프로젝트 파일을 제공했습니다.

---

## 검증 (VERIFY-01)

> **사용자 프롬프트 (User prompt)**
>
> task5-buildtest.txt: "Build the project and verify its behavior against all required test cases. Run `dotnet build 2>&1`. If the build fails, diagnose, fix, and rebuild. Then run `dotnet run -- "2+3*4"`, `"(2+3)*4"`, `"10-3-2"` and report each result. Required outputs: 14, 20, 5."

> **내부 프로세스 (Process — agent step() 루프)**
>
> - Step 1: 소스 파일 읽기 (`ls`, `cat calc.fsproj`, `cat Lexer.fsl`, `cat Parser.fsy`, `cat Program.fs`) (CmdRunAction)
> - Step 2: `dotnet build 2>&1` 실행 — 빌드 성공(`calc net10.0 성공`) (CmdRunAction)
> - Step 3: `dotnet run -- "2+3*4"` → `14` (CmdRunAction + CmdOutputObservation)
> - Step 4: `dotnet run -- "(2+3)*4"` → `20` (CmdRunAction + CmdOutputObservation)
> - Step 5: `dotnet run -- "10-3-2"` → `5` (CmdRunAction + CmdOutputObservation)

> **결과 (Result)**
>
> 9회의 TerminalAction, 32초 만에 완료. 3개 테스트 케이스 모두 통과. 아래는 호스트에서 직접 재실행해 캡처한 전체 출력입니다(`captured/test-output.txt`). (출처: captured/logs/task5-buildtest.jsonl; 03-02-RUN-NOTES.md § Per-Task Outcome Table)

다음은 5개 태스크 실행 완료 후 호스트에서 직접 실행한 캡처 출력의 전체 내용입니다 (`captured/test-output.txt`):

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

세 케이스 각각의 의미:

**`2+3*4 = 14`** — 연산자 우선순위 테스트. STAR가 PLUS보다 강하게 결합합니다(`%left STAR SLASH`가 `%left PLUS MINUS` 뒤에 선언 = 더 높은 우선순위). `%left` 선언 없는 단순 문법이라면 파서가 모호성을 임의로 해결해 20을 돌려줄 수 있습니다. 14는 `%left STAR SLASH`가 작동하고 있음을 증명합니다.

**`(2+3)*4 = 20`** — 명시적 그룹핑 테스트. `LPAREN expr RPAREN` 규칙이 우선순위를 오버라이드합니다. 괄호 안의 덧셈이 먼저 평가(5)된 후 곱셈이 적용됩니다(5×4=20).

**`10-3-2 = 5`** — 왼쪽 결합성 테스트. `%left MINUS`는 동일 우선순위의 MINUS가 왼쪽부터 결합함을 의미합니다: `(10-3)-2 = 7-2 = 5`. 오른쪽 결합이었다면 `10-(3-2) = 10-1 = 9`가 됩니다. 이 케이스는 `2+3*4`와 `(2+3)*4` 두 케이스를 모두 통과하는 문법도 왼쪽 결합을 보장하지 않으면 틀릴 수 있다는 점에서 독립적으로 중요합니다.

---

## 성능과 한계에 대한 솔직한 기록 (VERIFY-02)

이 튜토리얼은 실제 실행의 솔직한 기록입니다. 두 가지 사실을 그대로 전달합니다.

**시도 2의 실제 속도:** 간단한 태스크는 빠릅니다. task2(렉서 복사)는 16초, task5(빌드+테스트)는 32초가 걸렸습니다. 더 복잡한 task1(스캐폴딩, 파일 쓰기 27회 TerminalActions)은 3분 6초, task3(파서 작성 + 빌드 4회 실패+수정)은 1분 17초였습니다. 5개 태스크 전체 실행 시간은 약 10분입니다.

**시도 1의 실패:** 시도 1은 약 150분간 진행됐지만 실패했습니다. 원인은 속도가 아니라 능력의 경계였습니다. Qwen 3.6 35B 모델은 FsLex .fsl 파일을 올바르게 작성하지 못했습니다 — 3번의 에이전트 실행(94+27+16 TerminalActions)에서 모두 FsYacc 문법의 `%%` 구분자를 FsLex에 삽입하거나, 잘못된 렉심 추출 패턴을 사용했습니다. FsLex 문법은 이 모델의 훈련 데이터에서 드문 형식입니다. 이 문제를 우회하기 위해 시도 2에서는 Lexer.fsl을 태스크 프롬프트에 직접 제공했습니다.

**결론:** 35B 로컬 모델은 F# 컴파일러 오류를 스스로 진단하고 수정할 수 있습니다 (task3의 4회 자가 수정이 그 증거입니다). 그러나 훈련 데이터에서 드문 DSL 형식(.fsl)은 생성하지 못합니다. 이것은 현재 로컬 LLM의 현실적인 능력 지도입니다.

---

## 마무리

독자는 지금까지 실제 로컬 모델 에이전트가 계획을 세우고, FsYacc 파서를 작성하고, 4회의 빌드 오류를 스스로 수정하고, 올바르게 작동하는 계산기를 만들어내는 과정을 목격했습니다. 1부에서 추상적으로 배운 개념들 — tool calling, agent loop, self-correction, 관찰 기반 의사결정 — 이 이제 구체적인 빌드 로그와 오류 메시지와 검증 출력으로 살아있습니다.

5부와 부록에서는 이 실행을 재현하는 방법, 발생할 수 있는 문제와 해결책, 그리고 더 복잡한 에이전트 작업으로 나아가는 방향을 다룹니다.
