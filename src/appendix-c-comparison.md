# 부록 C: 모델 비교 — Qwen2.5-35B vs 122B

이 부록은 이 책의 v1 캡처(Qwen2.5-35B)와 v1.1 캡처(Qwen2.5-122B)를 나란히 놓고, 세 가지 질문에 답한다: 렉서를 스스로 작성할 수 있는가? 오류를 어떻게 고치는가? 얼마나 빠른가? 모든 수치와 주장은 캡처된 JSONL 파일과 RUN-NOTES에서 직접 인용한 것이다. 추정값이나 재구성이 있는 경우 명시한다.

## 실험 설계와 공정성 전제

이 비교는 의도적으로 설계가 다른 두 실행을 대상으로 한다. **이 점을 먼저 밝힌다.**

v1의 35B 실행(attempt 2)은 Lexer.fsl을 task2 프롬프트에 그대로 포함시킨 채 진행했다. 그 이유는 attempt 1에서 세 개의 OpenHands 에이전트(task4-evaluator-adjusted: 94 TerminalActions, task5-buildtest: 27 TerminalActions, task6-lexer-fix: 16 TerminalActions; 합계 137+ TerminalActions)가 모두 FsLex가 아닌 FsYacc 스타일의 `%%` 구분자를 사용한 유효하지 않은 .fsl 파일을 생성하다가 막혔기 때문이다. 이것은 모델 크기가 아니라 FsLex 형식에 대한 훈련 데이터 부족 때문으로 분석되었다. 세 에이전트가 예산을 소진한 뒤, 정직한 블로킹 편차(Deviation Rule 3)로 Lexer.fsl을 직접 제공하는 방식이 선택되었다. (출처: 03-02-RUN-NOTES-attempt1.md § "Root Cause Analysis: FsLex Issues"; captured/CAPTURE-MANIFEST.md § "On the lexer and .fsproj (scaffolded, not agent-authored)")

v1.1의 122B 실행은 이 맥락 위에서 설계되었다: **35B가 하지 못한 일을 122B가 할 수 있는가?** Lexer.fsl을 프롬프트에서 제외하고, 에이전트가 처음부터 스스로 FsLex 파일을 작성하도록 했다. 어떤 API 힌트도 제공하지 않았다. (출처: captured-122b/CAPTURE-MANIFEST.md § "Lexer Outcome (RUN122-01/02)")

따라서 이 비교는 동일 조건의 head-to-head 비교가 아니다. 35B는 렉서가 스캐폴딩된 환경에서, 122B는 렉서를 무지원으로 작성하는 환경에서 평가되었다. 두 모델이 모두 `2+3*4=14`, `(2+3)*4=20`, `10-3-2=5` 세 테스트 케이스를 통과했지만, 그 과정은 의도적으로 다르게 설계되었다.

## 1. 렉서(.fsl) 작성 능력

### 35B — attempt 1의 실패

Qwen2.5-35B는 attempt 1에서 FsLex 파일을 자율적으로 작성하지 못했다. 세 개의 독립된 OpenHands 에이전트 호출이 모두 동일한 패턴으로 실패했다: .fsl 파일에 FsYacc의 `%%` 구분자를 삽입하거나, `[<reflaction:remove>]` 같은 F# 속성 문법을 FsLex 액션 코드로 사용하거나, `lexbuf |> LexBuffer<char> |> lexeme |> string`과 같은 잘못된 렉심 추출 패턴을 시도했다.

근본 원인은 FsLex(.fsl)와 FsYacc(.fsy) 형식에 대한 친숙도 편향이었다. FsLex는 `%%` 구분자 없이 `rule name = parse | ...` 형식을 사용하는데, 에이전트는 yacc/bison 스타일 문법을 기대했다. (출처: 03-02-RUN-NOTES-attempt1.md § "Problem 1: %% separator confusion", line 76–79)

세 에이전트의 TerminalAction 횟수: task4-evaluator-adjusted 94회, task5-buildtest 27회, task6-lexer-fix 16회 = 합계 137+ TerminalActions. 모두 `%%` 혼동 또는 FsLex 파싱 오류로 막혔다. (출처: captured/CAPTURE-MANIFEST.md § "Run attempts", line 128)

### 35B — attempt 2: 스캐폴딩 적용

attempt 2에서는 Lexer.fsl 전체 내용을 task2 프롬프트에 포함시켰다. 에이전트는 단순히 그 내용을 파일로 복사하는 작업을 수행했다: 6 events, 2 TerminalActions, 16초. (출처: 03-02-RUN-NOTES.md § Per-Task Outcome Table, line 28 — task2 lexer 16s)

35B가 attempt 2에서 보여준 진정한 자율 능력은 Parser.fsy 작성과 4회의 빌드 오류 자가 수정에 있었다 — Lexer.fsl 작성이 아니었다.

### 122B — 무지원 첫 시도 성공

Qwen2.5-122B는 어떤 FsLex 힌트도 없이 task2-lexer-unaided.jsonl event 9에서 cat heredoc를 사용해 Lexer.fsl을 작성했다. `rule tokenize = parse` 형식을 올바르게 사용했고, `%%` 혼동이 없었다. event 12에서 `cat Lexer.fsl` (exit_code=0)로 파일 내용을 확인했다.

에이전트가 작성한 Lexer.fsl의 최종 완성 버전 (`new string(lexbuf.Lexeme)` 반복 수정 후):

```fsharp
{
open Parser
open FSharp.Text.Lexing

exception LexingError of string
}

rule tokenize = parse
  | [' ' '\t'] { tokenize lexbuf }
  | ['0'-'9']+ { INT (int (new string(lexbuf.Lexeme))) }
  | '+' { PLUS }
  | '-' { MINUS }
  | '*' { STAR }
  | '/' { SLASH }
  | '(' { LPAREN }
  | ')' { RPAREN }
  | eof { EOF }
  | _ { raise (LexingError (sprintf "Unexpected character: %c" (lexbuf.LexemeChar 0))) }
```

(출처: captured-122b/final-source/Lexer.fsl — 전체 내용 그대로 인용)

task2에서 에이전트가 처음 작성한 INT 라인은 `['0'-'9']+ as s { INT (int s) }` 였다 — 구조적으로 유효한 FsLex이나 `as s`가 char[]를 바인딩하므로 `int s`가 타입 불일치를 유발한다. 이 API 오류는 나중에 task5에서 9회 반복으로 수정된다(§2 참고). 하지만 `rule tokenize = parse` 형식 자체는 처음부터 올바르게 작성했다. (출처: captured-122b/CAPTURE-MANIFEST.md § "RUN122-01", line 159–165; task2-lexer-unaided.jsonl events 9, 12)

**핵심 결론:** 35B는 137+ TerminalActions으로도 유효한 FsLex 파일을 생성하지 못했다. 122B는 첫 번째 무지원 시도에서 구조적으로 유효한 FsLex 파일을 작성했다.

## 2. 오류-수정 사이클 비교

### 35B — task3 Parser.fsy의 4회 반복

35B의 자율 오류-수정 사이클은 task3-parser.jsonl (events 9–30)에 완전히 기록되어 있다. (출처: 03-02-RUN-NOTES.md § "Error-and-Fix Cycle (Branch A)", line 48–100)

| 시도 | Event | 오류 | 에이전트의 수정 |
|------|-------|------|----------------|
| 1 | 9→10 | FSY000: %start 누락 | %start start 추가 |
| 2 | 11→16 | parse error | `%start <int> start` (잘못된 FsYacc 문법) → 다시 수정 |
| 3 | 17→20 | parse error 재발 | 또 다른 수정 시도 |
| 4 | 23→26 | FS0039: LexBuffer<_> 에 FromText 없음 | %start/%type 분리 + LexBuffer<char>.FromString으로 수정 |
| — | 29→30 | 성공 | `calc net10.0 성공 (0.7초)` |

Event 30 빌드 성공 출력: `calc net10.0 성공 (0.7초) → bin/Debug/net10.0/calc.dll`

세 가지 실제 오류: `%start` 선언 누락, `%start <int> start` 잘못된 FsYacc 문법, `LexBuffer.FromText` 존재하지 않는 API. 모두 에이전트가 컴파일러 출력을 읽고 자율적으로 진단하고 수정했다. (출처: captured/logs/task3-parser.jsonl events 9–30; captured/CAPTURE-MANIFEST.md § "RUN-03")

### 122B — task5 Lexer API의 9회 반복

122B의 오류-수정은 더 긴 경로를 걸었다. 핵심 문제: task2에서 작성한 `['0'-'9']+ as s { INT (int s) }`의 `as s`가 char[] (문자열이 아님)를 바인딩하므로 `int s`가 FS0001 타입 불일치를 유발한다. 에이전트는 `FSharp.Text.Lexing` 네임스페이스의 올바른 API를 모르는 상태에서 9회 반복으로 수렴했다.

참고: 이 렉서 오류는 task5 이전에도 이미 등장했다 — task3-parser.jsonl events 24, 42, 46에서 에이전트가 `dotnet build`를 실행할 때 `FSLEX: error FSL000: The macro s is not defined` 오류가 나타났다. 에이전트는 그 수정을 task5로 미뤘다. (출처: captured-122b/CAPTURE-MANIFEST.md § "Error-and-Fix Record (RUN122-03)", line 96–98)

| # | Event | 에이전트의 INT 라인 | 관찰된 오류 |
|---|-------|---------------------|-------------|
| 0 | 12 | `as s { INT (int s) }` (task2에서 상속) | FS0001, FS0039 |
| 1 | 18 | `rule tokenize lexbuf = parse` + `Lexing.matched` | FS0038 (lexbuf 이중 바인딩), FS0001 |
| 2 | 30 | `rule tokenize = parse` + `Lexing.matched lexbuf` | FS0001, FS0039 |
| 3 | 40 | `tokenize lexbuf` 재귀 + `Lexing.matched lexbuf` | FS0039 |
| 4 | 50 | `FSharp.Text.Lexing.matched` | FS0039 (matched 존재하지 않음) |
| 5 | 56 | `Lexing.matchedText` | FS0039 (matchedText 존재하지 않음) |
| 6 | 60 | 전체 네임스페이스 + `matchedText` | FS0039 |
| 7 | 66 | `lexbuf.ToString()` | exit_code=134 런타임 크래시 (toString이 타입 이름 반환) |
| 8 | 70 | `lexbuf.Lexeme` | FS0193 (char array → int 변환 불가) |
| **9** | **74** | **`new string(lexbuf.Lexeme)`** | **빌드 성공** |

event 71에서 에이전트의 추론:
> "`lexbuf.Lexeme` returns a char array. Let me convert it to a string:"

최종 작동 INT 라인: `| ['0'-'9']+ { INT (int (new string(lexbuf.Lexeme))) }` (출처: captured-122b/CAPTURE-MANIFEST.md § "Error-and-Fix Record (RUN122-03)", line 93; task5-buildtest.jsonl events 12–74)

### 질적 비교

| 항목 | 35B (task3) | 122B (task5) |
|------|------------|--------------|
| 반복 횟수 | 4회 | 9회 |
| Event 범위 | events 9–30 (21 events) | events 12–74 (62 events) |
| 오류 영역 | FsYacc 선언 문법 + 가짜 API 1개 | FSharp.Text.Lexing API 전체 탐색 |
| 런타임 크래시 포함 | 없음 | 있음 (exit_code=134, iter 7) |
| 자율성 | 완전 자율 | 완전 자율 |

둘 다 진정한 자율 복구다. 122B가 탐색한 영역 — `FSharp.Text.Lexing`의 렉심 추출 API — 은 35B가 직면한 FsYacc 선언 오류보다 객관적으로 더 좁고 문서화가 적은 탐색 공간이었다.

## 3. 처리 속도 측정 (정직한 보고)

이 절에서는 두 측정값의 **방법론적 차이**를 명확히 밝힌다. 두 수치를 직접 비교하면 안 된다.

### 122B — JSONL 타임스탬프 직접 측정

측정 방법: ObservationEvent 타임스탬프 → 다음 ActionEvent 타임스탬프 = 순수 모델 사고 시간(bash 실행 시간 제외). (출처: captured-122b/CAPTURE-MANIFEST.md § "Timing Summary (CMP-01)", line 125–141)

| Task | 시작 | 종료 | 합계 | TerminalActions | 평균 LLM-call 간격 |
|------|------|------|------|-----------------|-------------------|
| task1-scaffold | 12:32:31 | 12:35:19 | 167.5s (2.8분) | 20 | 6.6s |
| task2-lexer-unaided | 12:43:14 | 12:44:12 | 57.7s (1.0분) | 7 | 3.2s |
| task3-parser | 12:53:59 | 12:58:12 | 252.3s (4.2분) | 37 | 5.5s |
| task4-evaluator | 13:04:21 | 13:10:24 | 362.7s (6.0분) | 47 | 6.6s |
| task5-buildtest | 13:18:35 | 13:25:04 | 389.0s (6.5분) | 39 | 7.0s |
| **합계** | — | — | **1229.2s (20.5분)** | **150** | **6.3s 평균** |

per-call 범위: 1.8s 최소 — 46.6s 최대(오류 진단 중 긴 추론).

### 35B — 파생 추정값 (직접 측정 아님)

35B의 03-02-RUN-NOTES.md는 task 단위 wall-time만 기록하며, LLM-call 단위 타임스탬프를 따로 집계하지 않았다. 아래 수치는 task wall-time ÷ TerminalAction count로 파생된 근사값이다. bash 실행 시간을 포함하며, 122B와 같은 방식(ObservationEvent → 다음 ActionEvent)으로 측정한 순수 모델 사고 시간이 아니다. (출처: 03-02-RUN-NOTES.md § "Per-Task Outcome Table", line 25–34)

| Task | 소요 시간 | TerminalActions | 파생 평균 (wall ÷ TA) |
|------|----------|-----------------|----------------------|
| task1-scaffold | 186s (3m 6s) | 27 | ~6.9s |
| task2-lexer | 16s | 2 | ~8.0s |
| task3-parser | 77s (1m 17s) | 15 | ~5.1s |
| task4-evaluator | 45s | 14 | ~3.2s |
| task5-buildtest | 32s | 9 | ~3.6s |
| **합계** | **356s (5.9분)** | **67** | **~5.3s 파생 평균** |

**측정 한계:** 이 파생 평균은 bash 실행 시간이 포함된 wall-time 기준이므로 122B의 직접 측정값과 동등하게 비교할 수 없다. 또한 task2 (16s, 2 TA)는 프롬프트에서 복사한 파일을 쓰는 작업이라 LLM 추론 비용이 거의 없다 — 이 태스크가 파생 평균을 왜곡할 수 있다.

### 정직한 비교 결론

**두 모델 모두 이 하드웨어에서 약 5–7s/call 범위에 있다.** 122B 직접 측정 6.3s/call, 35B 파생 추정 ~5.3s/call. 그러나 두 수치는 측정 방법이 달라 직접 비교가 불가능하다는 점을 다시 강조한다.

총 경과시간 차이(35B 356s vs 122B 1229s)는 **호출당 지연이 아니라 호출 횟수**에서 비롯된다:

- 35B: 67 TerminalActions (렉서 스캐폴딩 덕분에 lexer 오류-수정 없음)
- 122B: 150 TerminalActions (9회 lexer API 오류-수정 사이클이 주된 추가 비용)

122B CAPTURE-MANIFEST.md의 vs-35B-speed 코멘트는 35B에 대해 "~14–32s/call" 수치를 인용하지만, 이 수치는 06-RESEARCH.md §1.3의 사전 예측(pre-run prediction)이지 attempt 2의 실제 측정값이 아니다. 본 부록은 실제 attempt 2 데이터(파생 ~5.3s/call)를 사용한다. "~14–32s" 수치를 35B의 실측값으로 주장하는 것은 사실과 다르다.

## 4. 최종 소스 코드 차이

### Lexer.fsl — INT 토큰 라인

| 모델 | INT 추출 라인 | 출처 |
|------|--------------|------|
| 35B (스캐폴딩 제공) | `let s = LexBuffer<_>.LexemeString lexbuf` / `INT (System.Int32.Parse s)` | captured/final-source/Lexer.fsl |
| 122B (자체 작성) | `INT (int (new string(lexbuf.Lexeme)))` | captured-122b/final-source/Lexer.fsl |

35B의 Lexer.fsl INT 블록 (verbatim):

```fsharp
    | ['0'-'9']+
        { let s = LexBuffer<_>.LexemeString lexbuf
          let v = System.Int32.Parse s
          INT v }
```

122B의 Lexer.fsl INT 라인 (verbatim):

```fsharp
  | ['0'-'9']+ { INT (int (new string(lexbuf.Lexeme))) }
```

35B 스캐폴딩은 상위 API(`LexBuffer<_>.LexemeString`)를 사용한다 — FsLexYacc 공식 helper 메서드다. 122B는 9회 시도 끝에 하위 형식(`lexbuf.Lexeme` char array → `new string(...)` → `int`)으로 수렴했다. 두 형식 모두 동일한 결과를 산출한다.

### Parser.fsy — 문법 구조 차이

| 항목 | 35B | 122B |
|------|-----|------|
| 문법 구조 | flat `expr` (term/factor 계층 없음) | `expr → term → factor` 명시적 계층 |
| 단항 마이너스 | 없음 | `factor: \| MINUS factor { -$2 }` (별도 단항 연산자 토큰 선언 없이 재귀 규칙으로 처리) |
| `%token<int>` 표기 | `%token <int> INT` (공백 있음) | `%token<int> INT` (공백 없음) |
| `%start`/`%type` | 별도 라인 (`%start start` + `%type <int> start`) | 동일 |
| 헤더 블록 | `%{ %}` (빈 헤더) | 없음 |

35B Parser.fsy (verbatim):

```ocaml
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

122B Parser.fsy (verbatim):

```ocaml
%token<int> INT
%token PLUS
%token MINUS
%token STAR
%token SLASH
%token LPAREN
%token RPAREN
%token EOF

%start start
%type <int> start

%left PLUS MINUS
%left STAR SLASH

%%

start:
    | expr EOF { $1 }

expr:
    | expr PLUS term    { $1 + $3 }
    | expr MINUS term   { $1 - $3 }
    | term              { $1 }

term:
    | term STAR factor  { $1 * $3 }
    | term SLASH factor { $1 / $3 }
    | factor            { $1 }

factor:
    | INT               { $1 }
    | LPAREN expr RPAREN      { $2 }
    | MINUS factor            { -$2 }
```

(출처: captured/final-source/Parser.fsy — 35B; captured-122b/final-source/Parser.fsy — 122B)

122B의 문법이 더 구조화되어 있고(`expr → term → factor` 계층) 단항 마이너스 규칙(`| MINUS factor { -$2 }`)을 추가한다. 그러나 **정답성 차이는 없다** — 둘 다 14/20/5 세 테스트 케이스를 통과한다. 스타일 선택이지 "더 나은" 코드라는 주장이 아니다.

## 5. 결론

두 모델 모두 세 테스트 케이스를 통과했다:

- 35B: captured/logs/task5-buildtest.jsonl (FinalMsg — 8개 케이스 전체 정답); 03-02-RUN-NOTES.md Per-Task Outcome Table line 31
- 122B: captured-122b/logs/task5-buildtest.jsonl events 76 (14), 78 (20), 80 (5); captured-122b/test-output.txt (호스트 재실행 확인)

**핵심 차별점은 렉서 작성 능력이다.** 35B는 attempt 1에서 137+ TerminalActions을 소모하고도 유효한 FsLex 파일을 생성하지 못했고, Lexer.fsl 스캐폴딩이 필요했다. 122B는 무지원으로 처음 시도에서 구조적으로 올바른 FsLex 파일을 작성했다 — `rule tokenize = parse` 형식, `%%` 혼동 없음. (출처: captured-122b/CAPTURE-MANIFEST.md § "vs-35B-lexer"; task2-lexer-unaided.jsonl event 9)

**오류-수정 깊이에서도 차이가 있다.** 35B는 4 iterations / 21 events로 FsYacc 선언 문법과 가짜 API 하나를 수정했다. 122B는 9 iterations / 62 events로 FSharp.Text.Lexing의 렉심 추출 API를 처음부터 탐색하며 런타임 크래시(exit_code=134)도 경험했다. 두 경우 모두 완전한 자율 복구다. (출처: captured/logs/task3-parser.jsonl events 9–30; captured-122b/logs/task5-buildtest.jsonl events 12–74)

**속도는 모델 크기와 비례하는 큰 격차가 관찰되지 않았다.** 두 모델 모두 약 5–7s/call 범위로 측정되었다(122B: 직접 측정 6.3s/call; 35B: wall-time 기반 파생 ~5.3s/call). 총 경과시간 차이(356s vs 1229s)는 호출당 지연이 아니라 호출 횟수(67 vs 150 TerminalActions)에서 비롯된다.

**한계:** 35B 데이터는 attempt 2 기준이며 렉서가 스캐폴딩된 설정이다. 더 큰 모델이 작은 모델보다 "더 낫다"는 일반화는 이 단일 사례에서 지지되지 않으며, 이 부록의 범위를 넘는다. 이 비교는 두 모델 간 특정 능력 차이(FsLex 파일 작성 능력)를 정직하게 기록하는 것을 목적으로 한다.

## 출처 (Sources)

아래는 이 부록의 모든 주장이 직접 인용한 파일 목록이다:

- `.planning/phases/06-capture-the-122b-openhands-run/captured-122b/CAPTURE-MANIFEST.md`
- `.planning/phases/06-capture-the-122b-openhands-run/captured-122b/final-source/Lexer.fsl`
- `.planning/phases/06-capture-the-122b-openhands-run/captured-122b/final-source/Parser.fsy`
- `.planning/phases/06-capture-the-122b-openhands-run/captured-122b/logs/task2-lexer-unaided.jsonl`
- `.planning/phases/06-capture-the-122b-openhands-run/captured-122b/logs/task5-buildtest.jsonl`
- `.planning/phases/06-capture-the-122b-openhands-run/captured-122b/test-output.txt`
- `.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/CAPTURE-MANIFEST.md`
- `.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/final-source/Lexer.fsl`
- `.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/final-source/Parser.fsy`
- `.planning/milestones/v1-phases/03-capture-the-openhands-run/captured/logs/task3-parser.jsonl`
- `.planning/milestones/v1-phases/03-capture-the-openhands-run/03-02-RUN-NOTES.md`
- `.planning/milestones/v1-phases/03-capture-the-openhands-run/03-02-RUN-NOTES-attempt1.md`
