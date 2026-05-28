# 빌드와 테스트 단계

## 들어가며

task3에서 에이전트는 Parser.fsy를 완성하기까지 네 번의 빌드 실패를 겪었습니다. 네 번 모두 에이전트가 사람의 개입 없이 오류를 읽고, 판단하고, 수정하고, 다시 빌드했습니다. 이것이 이 책 전체에서 에이전틱 AI의 자율성을 가장 선명하게 보여주는 순간입니다.

중요한 사실을 먼저 밝힙니다. 이 네 번의 실패는 **연산자 우선순위 버그가 아닙니다**. 에이전트는 `%left PLUS MINUS`와 `%left STAR SLASH`를 처음 작성할 때부터 올바르게 선언했습니다. 실패는 FsYacc `%start` 선언 구문에 대한 오해와, F# FSharp.Text.Lexing API(`LexBuffer`)에 존재하지 않는 메서드를 호출한 것에서 비롯된 순수한 빌드 오류입니다.

아래에서 네 번의 실패를 각각 관찰(observed) → 판단(decided) → 수정(corrected) 순서로 따라갑니다. 모든 오류 텍스트는 captured/logs/task3-parser.jsonl과 transcript.md에서 그대로 인용한 것입니다.

---

## 네 번의 빌드 실패와 자가 수정

### 실패 1 — %start 선언 누락

#### 관찰 (observed)

에이전트가 Parser.fsy 초안을 작성하고 처음 `dotnet build 2>&1`를 실행했을 때(transcript.md Task 3 Step 5, event 9), 다음 오류가 나왔습니다:

```
복원 완료(0.2초)
  calc net10.0 2 오류와 함께 실패 (0.3초)
    FSYACC : error FSY000: at least one %start declaration is required
    /Users/ohama/.nuget/packages/fslexyacc/11.3.0/build/FsLexYacc.targets(53,3): error MSB3073: ...명령이 종료되었습니다(코드: 1).

2 오류와 함께 실패 빌드(0.6초)
```

초안 Parser.fsy에는 `%type <int> start`만 있고 `%start` 선언이 빠져 있었습니다.

#### 판단 (decided)

에이전트는 ThinkAction으로 다음과 같이 추론했습니다(transcript.md Task 3 Step 6):

> "The `%start` declaration is missing — I need to add it alongside `%type`:"

#### 수정 (corrected)

에이전트는 Parser.fsy를 다시 작성하며 `%start <int> start`를 `%type <int> start` 위에 추가했습니다. 그런데 이 형태 — `%start <int> start` — 는 유효한 FsYacc 구문이 아니었습니다. 이것이 바로 두 번째 실패의 원인이 됩니다.

---

### 실패 2 — %start &lt;int&gt; start: 잘못된 구문 (parse error)

#### 관찰 (observed)

수정된 Parser.fsy로 다시 빌드했을 때(transcript.md Task 3 Step 8, event 15):

```
복원 완료(0.1초)
  calc net10.0 2 오류와 함께 실패 (0.2초)
    Parser.fsy(16,7): error parse error
    /Users/ohama/.nuget/packages/fslexyacc/11.3.0/build/FsLexYacc.targets(53,3): error MSB3073: ...명령이 종료되었습니다(코드: 1).

2 오류와 함께 실패 빌드(0.5초)
```

`Parser.fsy(16,7): error parse error`는 fsyacc 파서 생성기가 16번째 줄 7번째 문자에서 문법 파일 자체를 파싱하지 못했다는 뜻입니다. `%start <int> start`라는 결합 형태가 FsYacc에서 허용되지 않습니다.

#### 판단 (decided)

에이전트는 ThinkAction으로 다음과 같이 분석했습니다(transcript.md Task 3 Step 9):

> "The issue is having both `%start` and `%type` for the same rule. FsYacc only needs `%start` for the entry point — `%type` is for non-start rules. Let me fix that:"

#### 수정 (corrected)

에이전트는 `%type <int> start`를 제거하고 `%start <int> start`만 남겼습니다. 그러나 이 판단은 틀렸습니다. 문제는 `%type`이 중복된 것이 아니라 `%start <int> start`라는 결합 형태가 무효인 것이었습니다. 세 번째 빌드에서 같은 오류가 다시 나옵니다.

---

### 실패 3 — 같은 parse error, 두 번째 시도

#### 관찰 (observed)

`%type`을 제거한 상태로 다시 빌드했을 때(transcript.md Task 3 Step 10, event 19):

```
복원 완료(0.1초)
  calc net10.0 2 오류와 함께 실패 (0.2초)
    Parser.fsy(16,7): error parse error
    /Users/ohama/.nuget/packages/fslexyacc/11.3.0/build/FsLexYacc.targets(53,3): error MSB3073: ...명령이 종료되었습니다(코드: 1).

2 오류와 함께 실패 빌드(0.5초)
```

실패 2와 동일한 오류입니다.

#### 판단 (decided)

**이 단계에서는 ThinkAction이 기록되지 않았습니다.** transcript.md와 task3-parser.jsonl을 확인하면, 에이전트는 세 번째 빌드에서도 같은 오류를 받은 뒤 추론 기록 없이 곧바로 다른 방법을 시도했습니다: `%start start`와 `%type <int> start`를 별도 줄로 분리하는 방식이었습니다. 판단 과정이 기록으로 남아 있지 않으므로 여기서 인용할 수 없습니다.

#### 수정 (corrected)

에이전트는 Parser.fsy를 다음과 같이 수정했습니다(transcript.md Task 3 Step 11):

```
%start start

%type <int> start
```

이것이 올바른 FsYacc 구문입니다. `%start`는 진입점 심볼을 선언하고, `%type`은 그 심볼의 반환 타입을 선언합니다. 두 선언이 별도 줄에 있어야 합니다. 이 수정 이후 파서 자체는 컴파일에 성공했습니다 — 그러나 새로운 오류가 Program.fs에서 나타났습니다.

---

### 실패 4 — LexBuffer&lt;_&gt;.FromText가 존재하지 않음 (FS0039)

#### 관찰 (observed)

파서가 컴파일된 후 Program.fs에서 새 오류가 발생했습니다(transcript.md Task 3 Step 12, event 25):

```
복원 완료(0.1초)
  calc net10.0 3 오류와 함께 실패 (0.8초)
    /Users/ohama/projs/OpenHandsTests/oh-workdir/calc/Program.fs(11,38): error FS0039: 'LexBuffer<_>' 형식은 'FromText' 필드, 생성자 또는 멤버를 정의하지 않습니다. 다음 중 하나가 필요할 수 있습니다:   FromTextReader   FromBytes   FromString
    ...
3 오류와 함께 실패 빌드(1.1초)
```

에이전트가 task3에서 스스로 작성한 Program.fs 초안에 `LexBuffer<char>.FromText(new StringReader(input))`가 있었는데, FSharp.Text.Lexing API에는 `FromText` 메서드가 존재하지 않습니다. 컴파일러 오류 메시지에서 올바른 대안(`FromString`)을 직접 제시하고 있습니다.

#### 판단 (decided)

에이전트는 ThinkAction으로 다음과 같이 분석했습니다(transcript.md Task 3 Step 13):

> "The parser compiled successfully! The errors are in `Program.fs` — let me fix the API calls:"

오류의 위치를 Parser.fsy가 아니라 Program.fs로 정확히 식별하고, 파서 자체는 이제 올바르다는 것을 인식했습니다.

#### 수정 (corrected)

에이전트는 Program.fs를 다시 작성하며 두 가지를 변경했습니다:

- `LexBuffer<char>.FromText(new StringReader(input))` → `LexBuffer<char>.FromString input`
- `Parser.start(Lexer.tokenize, lexbuf)` → `Parser.start Lexer.tokenize lexbuf` (F# 커리 적용 스타일)

이것이 네 번째이자 마지막 수정이었습니다.

---

## 빌드 성공

네 번째 수정 후 빌드 결과(transcript.md Task 3 Step 14, event 29):

```
복원 완료(0.1초)
  calc net10.0 성공 (0.7초) → bin/Debug/net10.0/calc.dll

성공 빌드(1.0초)
```

빌드 성공 직후 에이전트는 즉시 8개 표현식을 실행해 자체 검증을 수행했습니다(transcript.md Task 3 Step 15):

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

8개 모두 정확한 결과입니다. `10-3-2 = 5`는 좌결합(`%left MINUS`)이 올바르게 작동한다는 증거이고, `1+2*3 = 7`은 곱셈이 덧셈보다 높은 우선순위를 가진다(`%left STAR SLASH`가 `%left PLUS MINUS` 뒤에 선언)는 증거입니다.

이것은 에이전트가 task3 완료 직전 스스로 수행한 인-태스크 검증입니다. 공식 호스트 검증(3개 테스트 케이스: `2+3*4=14`, `(2+3)*4=20`, `10-3-2=5`)은 별도로 task5 이후에 실행된 것으로, 이는 '완성된 계산기' 장에서 다룹니다.

---

> **개념 ↔ 행동: 에이전트 루프와 자가 수정 (agent loop / self-correction)**
>
> 위에서 본 빌드 오류 → 파일 수정 → 재빌드 사이클 4회 반복은 별도로 설계된 "자가 수정 기능"이 아닙니다. 1부에서 배운 agent loop의 자연스러운 결과입니다.
>
> 구체적으로 보면: `dotnet build`를 실행하는 CmdRunAction이 종료되면, 컴파일러 출력(stderr 포함)이 CmdOutputObservation에 담겨 EventLog에 기록됩니다. 다음 루프 반복이 시작될 때 이 ObservationEvent가 LLM의 입력 프롬프트에 포함됩니다. LLM은 오류 메시지를 읽고 수정 ActionEvent(Parser.fsy 재작성을 위한 CmdRunAction)를 emit합니다. 이 과정이 자동으로, 사람의 개입 없이 반복됩니다.
>
> 1부 concepts.md의 표현을 그대로 인용하면: "빌드가 실패하면 오류 메시지를 읽고 수정 코드를 작성하고, 성공하면 테스트를 실행하는 식입니다." 그리고 2부 actions-observations.md에서 설명했듯: "자가 수정은 별도로 설계된 기능이 아니라, agent loop와 observation 메커니즘의 자연스러운 결과입니다."
>
> 핵심은 루프의 자율성입니다. 사람이 "오류가 났으니 고쳐봐"라고 지시하지 않았습니다. 에이전트가 오류를 관찰하고, 스스로 다음 행동을 결정하고, 수정을 실행하고, 다시 빌드를 시도했습니다.

---

## 다음으로

'완성된 계산기' 장에서는 최종 소스 파일 전체와, task5 이후 호스트에서 실행한 공식 검증 블록(`2+3*4=14`, `(2+3)*4=20`, `10-3-2=5`)을 확인할 수 있습니다. 그리고 시도 2의 실제 속도(task별 실행 시간)와 시도 1의 실패 원인에 대한 솔직한 기록도 그 장에 있습니다.
