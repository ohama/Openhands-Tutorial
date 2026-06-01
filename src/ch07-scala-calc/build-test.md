# 빌드와 테스트 단계

## 들어가며

task3에서 에이전트는 Scala 계산기를 빌드하기까지 하나의 컴파일 오류를 겪었습니다. 에이전트가 사람의 개입 없이 컴파일러 출력을 읽고, 원인을 판단하고, 소스를 수정하고, 재컴파일에 성공했습니다.

오류의 성격: `pos` 필드가 `ExprParser` 클래스에 `private`로 선언되어 있었는데, `@main` 최상위 함수가 `parser.pos`에 직접 접근하려 해서 Scala 3 컴파일러가 이를 거부했습니다. 에이전트는 이 원인을 스스로 진단하고 `sed`로 `private` 한정자를 제거했습니다.

모든 오류 텍스트와 사건 순서는 `logs/task3-buildtest.jsonl` / CAPTURE-MANIFEST.md에서 직접 인용합니다.

---

## 컴파일 오류 — `private var pos` 접근 거부

### 관찰 (observed)

> **사용자 프롬프트**
>
> `task3-buildtest.txt` 요약: "`calc/` 폴더에서 `scala-cli run Calc.scala`로 계산기를 실행하고, `2+3*4` → `14`, `(2+3)*4` → `20`, `10-3-2` → `5`를 확인하라. 빌드가 실패하면 오류를 진단하고 수정하라."

> **내부 프로세스 (오류와 수정의 전체 흐름)**
>
> - 이벤트 #6 (TerminalAction): `cd .../calc && scala-cli run Calc.scala -- "2+3*4" 2>&1` 실행
> - 이벤트 #7 (ObservationEvent, exit=1): COMPILE ERROR 수신 (아래 참조)
> - 이벤트 #8 (TerminalAction): 에이전트 자신의 `sed` 수정 명령 실행
> - 이벤트 #9 (ObservationEvent, exit=0): sed 적용 완료 (빈 출력, 오류 없음)

> **결과**
>
> 컴파일 오류 1회, 에이전트 자가 수정 1회, 재컴파일 성공. 출처: task3-buildtest.jsonl, CAPTURE-MANIFEST.md § Error-and-Fix Record (SCAL-03)

### 이벤트 #7 — 컴파일 오류 전문 (verbatim)

```
Compiling project (Scala 3.8.3, JVM (17))
[error] ./Calc.scala:5:6
[error] variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level definitions in package <empty>.
[error]   private variable pos can only be accessed from class ExprParser.
[error]   if parser.pos < expr.length then
[error]      ^^^^^^^^^^
[error] ./Calc.scala:6:72
[error] variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level definitions in package <empty>.
[error]   private variable pos can only be accessed from class ExprParser.
[error]     throw new IllegalArgumentException("Unexpected character: " + expr(parser.pos))
[error]                                                                        ^^^^^^^^^^
Error compiling project (Scala 3.8.3, JVM (17))
Compilation failed
```

출처: task3-buildtest.jsonl 이벤트 #7 / CAPTURE-MANIFEST.md, Error-and-Fix Record

**근본 원인:** task2에서 에이전트가 `pos`를 `private var pos = 0`으로 선언했는데, `@main` 최상위 함수가 `parser.pos`에 직접 접근하려 했습니다(5번째 줄과 6번째 줄). Scala 3에서 `@main`을 포함한 최상위 정의는 다른 클래스의 `private` 멤버에 접근할 수 없습니다. 이것은 깔끔한, 분포 내(in-distribution) 접근 한정자 실수입니다.

---

### 이벤트 #8 — 에이전트 자신의 수정

에이전트가 컴파일러 오류를 읽고 `private` 한정자가 문제임을 진단한 뒤, 다음 명령을 실행했습니다.

```bash
cd .../calc && sed -i '' 's/private var pos = 0/var pos = 0/' Calc.scala
```

이벤트 #9 (ObservationEvent, exit=0): sed가 성공적으로 적용됐습니다(빈 출력, 오류 없음).

이것은 사람이 개입한 것이 아닙니다. 이벤트 #8은 `source=agent`인 ActionEvent입니다 — 에이전트가 스스로 원인을 진단하고 수정 명령을 선택했습니다.

출처: task3-buildtest.jsonl 이벤트 #8/#9 / CAPTURE-MANIFEST.md, Error-and-Fix Record

---

## 정규 테스트 — 세 가지 검증 (수정 후)

`private` 제거 후, 에이전트는 세 가지 정규 테스트를 순서대로 실행했습니다.

### 테스트 1: `2+3*4` → `14` (연산자 우선순위)

이벤트 #10 (TerminalAction): `scala-cli run Calc.scala -- "2+3*4" 2>&1`

이벤트 #11 (ObservationEvent, exit=0) — verbatim:

```
Compiling project (Scala 3.8.3, JVM (17))
Compiled project (Scala 3.8.3, JVM (17))
14
```

`*`가 `+`보다 먼저 계산됩니다: `3*4 = 12`, 이어서 `2+12 = 14`. **PASS**

### 테스트 2: `(2+3)*4` → `20` (괄호)

이벤트 #12 (TerminalAction): `scala-cli run Calc.scala -- "(2+3)*4" 2>&1`

이벤트 #13 (ObservationEvent, exit=0) — verbatim:

```
20
```

(캐시된 컴파일 — 결과만 출력됨)

괄호 안의 `2+3 = 5`를 먼저 계산하고, 이어서 `5*4 = 20`. **PASS**

### 테스트 3: `10-3-2` → `5` (왼쪽 결합)

이벤트 #14 (TerminalAction): `scala-cli run Calc.scala -- "10-3-2" 2>&1`

이벤트 #15 (ObservationEvent, exit=0) — verbatim:

```
5
```

(캐시된 컴파일 — 결과만 출력됨)

왼쪽 결합: `(10-3)-2 = 7-2 = 5`. 오른쪽 결합이었다면 `10-(3-2) = 9`가 됩니다. **PASS**

출처: task3-buildtest.jsonl 이벤트 #10–#15 / CAPTURE-MANIFEST.md, Canonical Test Outcome

---

## 오류와 수정 요약

| # | 이벤트 | 유형 | 설명 | 수정 방법 |
|---|--------|------|------|-----------|
| 1 | #7 (exit=1) | 컴파일 오류 | `private var pos` — `@main`에서 private 멤버 접근 불가 | 이벤트 #8: `sed 's/private var pos = 0/var pos = 0/'` |
| — | #9 (exit=0) | 수정 확인 | sed 적용 완료 | — |
| — | #11 (exit=0) | 첫 재컴파일 성공 | `2+3*4 → 14` PASS | — |
| — | #13 (exit=0) | `(2+3)*4 → 20` | PASS (캐시) | — |
| — | #15 (exit=0) | `10-3-2 → 5` | PASS (캐시, 왼쪽 결합) | — |

출처: CAPTURE-MANIFEST.md, Error-and-Fix Record

---

## 호스트 독립 재실행 확인

2026-06-01T06:03:25Z에 호스트에서 독립적으로 재실행해 에이전트의 실행 결과를 검증했습니다.

```
$ scala-cli run Calc.scala -- "2+3*4"
14
(exit: 0)

$ scala-cli run Calc.scala -- "(2+3)*4"
20
(exit: 0)

$ scala-cli run Calc.scala -- "10-3-2"
5
(exit: 0)
```

- scala-cli 1.14.0 / Scala 3.8.3 — 에이전트 실행과 동일 환경
- **host-rerun-matches-agent-capture: YES**

출처: test-output.txt (2026-06-01T06:03:25Z)

---

> **개념 ↔ 행동: 액션-관찰 사이클(action-observation cycle)과 자가 수정**
>
> 이 컴파일 오류와 자가 수정은 2부에서 설명한 **액션-관찰 사이클**의 한 번입니다. 에이전트가 `scala-cli run`(이벤트 #6, ActionEvent)을 실행하면, 컴파일러 출력 전체가 이벤트 #7 ObservationEvent로 EventLog에 기록됩니다. 그 오류 텍스트(`variable pos cannot be accessed...`)가 다음 루프 반복의 프롬프트에 포함되어 LLM이 그것을 읽고 수정 명령(`sed`, 이벤트 #8)을 선택합니다. 사람이 오류를 중계해주지 않습니다. 에이전트 루프가 스스로 컴파일러 출력을 읽고 소스를 고칩니다. "자가 수정은 별도로 설계된 기능이 아니라, agent loop와 observation 메커니즘의 자연스러운 결과"(1부 concepts.md) — 이 한 번의 오류 사이클이 바로 그것입니다.
