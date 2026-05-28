# 코드 작성 단계

이 장에서는 OpenHands 에이전트가 F# 계산기의 핵심 소스 파일 두 개 — Parser.fsy와 Program.fs — 를 실제로 작성하는 과정을 따라갑니다. 에이전트가 무엇을 입력했는지, 어떤 tool call을 emit했는지, 어떤 결과를 얻었는지를 캡처된 증거에서 직접 인용합니다.

---

## task1 — 프로젝트 스캐폴딩 (요약)

task1은 `calc.fsproj` 프로젝트 파일을 작업 디렉토리에 배치하는 것이었습니다. 에이전트는 56개 이벤트와 27개의 TerminalAction을 사용했지만, 그 대부분은 파일 쓰기 자체의 어려움에서 비롯된 것이었습니다. 셸이 heredoc과 인라인 Python 코드를 반복적으로 훼손했고(따옴표 이스케이프 충돌), 에이전트는 heredoc → Python 인라인 → Python 스크립트 파일 → base64 디코드 → `chr()` 문자 조합 방식으로 전략을 계속 전환했습니다. 3분 6초 만에 올바른 `calc.fsproj`가 배치되었습니다.

이 파일은 태스크 프롬프트에 제공된 내용을 기반으로 작성된 것입니다. `FixLineDirectives` MSBuild 타겟은 .NET 10 + FsLexYacc 11.3.0 조합에서 발생하는 `# 0 ""` 줄 지시자 문제를 해결하는 비직관적인 워크어라운드입니다. 이 스캐폴딩이 완료되었을 때, 에이전트의 실질적인 작업(Parser.fsy 작성)을 위한 준비가 갖춰졌습니다.

---

## task2 — Lexer.fsl 투입 (요약)

task2는 Lexer.fsl을 작업 디렉토리에 복사하는 것이었습니다. 태스크 프롬프트에 렉서 내용이 전달되었고, 에이전트는 2번의 TerminalAction(파일 쓰기 + 검증)으로 16초 만에 완료했습니다. Lexer.fsl은 에이전트가 직접 설계한 것이 아닙니다. 1부의 '태스크 계획 단계'에서 설명했듯, Qwen 3.6 35B 모델이 FsLex .fsl 형식을 올바르게 생성하지 못했기 때문에 프롬프트에 포함시켰습니다.

---

## task3 — 에이전트가 파서를 작성하다

> **사용자 프롬프트 (User prompt)**
>
> task3-parser.txt: "Write Parser.fsy — the FsYacc grammar — for integer arithmetic expressions. Declare tokens INT/PLUS/MINUS/STAR/SLASH/LPAREN/RPAREN/EOF, implement operator precedence (`*`/`/` higher than `+`/`-`), left-associativity, and parentheses. Expose a single entry point `start` of type `int`. Do NOT modify calc.fsproj or Lexer.fsl."

> **내부 프로세스 (Process — agent step() 루프)**
>
> - Step 1 — 환경 탐색: `ls`, `cat calc.fsproj`, `cat Lexer.fsl`으로 토큰 집합과 프로젝트 구조 파악 (CmdRunAction)
> - Step 3 — Parser.fsy 작성: `cat > Parser.fsy <<'EOF'`로 `%left PLUS MINUS` / `%left STAR SLASH` 우선순위 선언 포함한 FsYacc 문법 기록 (CmdRunAction)
> - Step 4 — Program.fs 추가 작성: 빌드 검증을 위해 task 범위를 초과해 CLI 진입점도 작성 (CmdRunAction)
> - Steps 5–14 — 빌드 4회 실패·자가 수정: `dotnet build 2>&1` 실행 → 컴파일러 오류 읽기 → 파일 재작성 → 재빌드 반복 (자세한 내용은 '빌드와 테스트 단계' 장)

> **결과 (Result)**
>
> 15회의 TerminalAction, 1분 17초 만에 Parser.fsy와 Program.fs 작성 완료. 빌드 성공(`calc net10.0 성공 (0.7초)`). 에이전트가 자체 검증으로 8개 표현식을 실행해 모두 정확한 결과 확인. (출처: captured/logs/task3-parser.jsonl events 1–30; captured/CAPTURE-MANIFEST.md § RUN-03)

task3는 에이전트의 실질적인 작업이 집중된 단계입니다. 태스크는 "Parser.fsy를 작성하라"는 것이었지만, 에이전트는 빌드를 검증하기 위해 Program.fs도 스스로 작성했습니다(이것이 나중에 네 번째 빌드 실패의 원인이 됩니다 — 다음 장에서 상세히 다룹니다).

### 에이전트의 첫 번째 행동: 환경 파악

에이전트는 먼저 프로젝트 디렉토리를 탐색했습니다(CmdRunAction: `ls`, `cat calc.fsproj`, `cat Lexer.fsl`). 이것은 1부에서 설명한 plan → write → test → run 방법론의 탐색(Explore) 단계입니다. 에이전트는 렉서가 생성하는 토큰 집합(`INT`, `PLUS`, `MINUS`, `STAR`, `SLASH`, `LPAREN`, `RPAREN`, `EOF`)을 확인한 뒤 파서 작성에 들어갔습니다.

### 에이전트가 Parser.fsy를 작성하다 — 올바른 우선순위 선언을 처음부터

에이전트는 CmdRunAction을 통해 다음 내용을 `Parser.fsy`에 기록했습니다(transcript.md Task 3 Step 3):

```
cat > Parser.fsy << 'EOF'
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
EOF
```

중요한 사실이 있습니다. **에이전트는 `%left PLUS MINUS`와 `%left STAR SLASH`를 처음부터 올바르게 작성했습니다.** 우선순위 선언이 누락된 적이 없고, 잘못된 선언을 수정한 적도 없습니다. 연산자 우선순위는 에이전트가 직면한 문제가 아니었습니다. 에이전트가 겪은 빌드 실패는 모두 FsYacc 문법 선언 구문(`%start`)과 F# API 호출(`LexBuffer`)에 관한 것이었습니다 — 이것은 다음 장('빌드와 테스트 단계')에서 상세히 다룹니다.

### 에이전트가 task 범위를 넘어 Program.fs도 작성하다

task3의 공식 범위는 Parser.fsy였습니다. 그런데 에이전트는 빌드가 실제로 통과하는지 확인하기 위해 Program.fs도 스스로 작성했습니다(transcript.md Task 3 Step 4). 에이전트의 판단은 "파서를 작성했으면 실제로 빌드해서 확인해야 한다"는 것이었고, 그러려면 Program.fs가 필요했습니다. 이것은 에이전트가 명시적 지시 없이 스스로 태스크 범위를 확장한 관찰된 행동입니다 — plan → write → test → run 방법론에서 에이전트가 자발적으로 Verify 단계를 실행하려 한 것입니다.

Program.fs 초안에서 에이전트는 `LexBuffer<char>.FromText(new StringReader(input))`라는 존재하지 않는 API를 사용했는데, 이것이 직접적으로 네 번째 빌드 실패(`FS0039`)를 유발했습니다. 에이전트는 이 오류도 스스로 수정했습니다.

---

> **개념 ↔ 행동: 툴 호출 (tool calling)**
>
> 에이전트가 `dotnet build`를 실행하는 것은 1부에서 배운 tool calling의 구체적인 사례입니다. 에이전트는 "빌드해보겠습니다"라는 텍스트를 출력하는 것이 아니라, CmdRunAction(`command: dotnet build 2>&1`)을 emit해 실제 명령을 실행합니다. 마찬가지로 Parser.fsy를 만들 때도 텍스트로 "이런 파일을 만들겠습니다"라고 쓰는 것이 아니라, CmdRunAction(`command: cat > Parser.fsy << 'EOF' ...`)을 emit해 파일을 직접 작성합니다.
>
> 1부 concepts.md의 표현을 그대로 인용하면: "LLM이 일반 텍스트를 출력하는 대신, 구조화된 호출(이름 + 인자)을 출력해 환경에 행동을 지시합니다." 이 장에서 에이전트가 파일을 만들고 빌드를 실행하는 모든 순간이 바로 그것입니다.

---

> **개념 ↔ 행동: 메모리와 컨텍스트 (memory / context window)**
>
> 이 튜토리얼에서 각 태스크는 별도의 OpenHands 헤드리스 실행입니다 — task1, task2, task3 각각이 독립적인 프로세스로 실행됩니다. 이전 태스크의 EventLog는 다음 태스크와 공유되지 않습니다. 그런데 task3의 에이전트는 task2가 만든 Lexer.fsl을 읽을 수 있었습니다(Step 1의 `cat Lexer.fsl` 출력에서 확인). task5의 에이전트는 앞선 태스크들이 작성한 모든 파일을 빌드할 수 있었습니다.
>
> 이 "기억"은 LLM의 컨텍스트 창이나 EventLog에 있는 것이 아닙니다. 파일시스템(LocalWorkspace)에 있습니다. 이것은 1부에서 정의한 memory 개념의 경계를 보여줍니다: EventLog는 하나의 세션(하나의 OpenHands 실행) 안에서만 유지되고, 세션 간 "기억"은 외부 저장소 — 여기서는 호스트 파일시스템 — 에 의존합니다. 에이전트가 파일을 만드는 행위(FileWriteAction, CmdRunAction으로 cat > ...)는 단순히 현재 태스크를 진행하는 것 이상입니다: 다음 태스크가 읽을 수 있는 지속적인 상태를 기록하는 것이기도 합니다.

---

## 최종 Parser.fsy — 전체 소스 (WALK-03)

아래는 에이전트가 4번의 빌드 수정 사이클을 거쳐 도달한 최종 Parser.fsy입니다. captured/final-source/Parser.fsy에서 그대로 인용합니다.

주목할 점은 산술 연산이 별도의 평가기(evaluator) 모듈 없이 문법 액션 코드에서 직접 수행된다는 것입니다: `$1 + $3`, `$1 - $3`, `$1 * $3`, `$1 / $3`. 파서가 파싱과 평가를 동시에 수행합니다.

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

`%start start`와 `%type <int> start`가 별도 줄로 분리된 형태인 것에 주목하세요. 에이전트는 처음에 `%start <int> start`라는 결합 형태를 시도했지만, 이것은 유효한 FsYacc 구문이 아니었습니다. 세 번의 빌드 실패 끝에 이 분리 형태에 도달했습니다. 그 과정은 '빌드와 테스트 단계'에서 자세히 다룹니다.

최종 Program.fs는 '완성된 계산기' 장에서 전체 소스와 함께 확인할 수 있습니다.
