# 예제 프로젝트 소개

7부에서 OpenHands는 Scala 3 산술 계산기를 만듭니다. 이것은 4부의 F# 계산기, 6부의 Rust HTTP 서버에 이어지는 세 번째 "다른 워킹 예제"입니다. 같은 35B 모델, 같은 에이전트 루프 — 그러나 이번에는 Scala 3과 손으로 작성한 재귀 하강 파서(recursive-descent parser)입니다.

---

## 무엇을 만드는가

목표는 단순합니다. 정수 산술 표현식을 평가하는 **최소한의 Scala 3 명령줄 계산기**입니다.

```
$ scala-cli run Calc.scala -- "2+3*4"
14

$ scala-cli run Calc.scala -- "(2+3)*4"
20

$ scala-cli run Calc.scala -- "10-3-2"
5
```

세 가지 결과가 모두 올바릅니다. 연산자 우선순위(`*`가 `+`보다 먼저)와 왼쪽 결합(left-associativity: `10-3-2 = (10-3)-2 = 5`, `10-(3-2) = 9`가 아님)이 정확하게 처리됩니다.

계산기는 외부 의존성이 전혀 없습니다. `scala.*` 표준 라이브러리만 사용하며, `//> using dep` 지시어도, 파서 조합자(parser-combinator) 라이브러리도, 파서 생성기(parser generator)도 없습니다.

---

## 실행 정보

| 항목 | 값 |
|------|-----|
| 모델 | openai/qwen-35b (Qwen2.5-35B, litellm 프록시 경유 @ 127.0.0.1:4000) |
| 실행일 | 2026-06-01 |
| OpenHands 버전 | SDK v1.21.0 / CLI 1.16.0 |
| scala-cli 버전 | 1.14.0 |
| Scala 버전 | 3.8.3 (scala-cli 기본값; `//> using scala` 지시어 없음) |
| JDK | 17.0.19 |
| 태스크 수 | 3 (task1: 환경 확인, task2: 계산기 작성, task3: 빌드·테스트) |

출처: CAPTURE-MANIFEST.md, Run Metadata 절

---

## 이 예제의 가설 — 계산기 삼부작 완성

CAPTURE-MANIFEST.md의 Comparison Hook 절은 다음을 기록합니다.

> v1에서 35B 모델은 FsLex `.fsl` 파일을 unaided(비보조 상태)로 올바르게 생성하지 못했습니다 — 세 번의 별도 에이전트 실행(94 + 27 + 16 회의 TerminalAction)이 모두 실패했습니다. FsLex 렉서는 프롬프트에 텍스트 그대로 제공(스캐폴드)됐습니다. v1.3에서 같은 35B 모델은 Scala 3 재귀 하강 계산기를 unaided 1회 시도로 작성했습니다(task2-write-calc.jsonl).

이것은 모델의 실력이 절대적이지 않다는 것을 보여줍니다. 문제는 계산기 자체가 아니라 **파서 생성기 DSL(FsLex/FsYacc)이라는 특정 형식의 지식**이었습니다. 손으로 작성하는 재귀 하강 파서는 이 모델의 훈련 데이터에서 일반적인 패턴입니다.

7부는 이 계산기 삼부작의 마지막 장입니다.

| 버전 | 예제 | 언어 | 파서 방식 | 비보조 여부 |
|------|------|------|-----------|-------------|
| v1 (4부) | F# 계산기 | F# | FsLex/FsYacc DSL | **스캐폴드 필요** (94+27+16 TA 실패) |
| v1.2 (6부) | Rust HTTP 서버 | Rust | 해당 없음 | unaided (1회) |
| v1.3 (7부) | Scala 3 계산기 | Scala 3 | 손 작성 재귀 하강 | **unaided (1회)** |

같은 35B 모델이 FsLex 렉서를 작성하지 못했던 것과 달리, 동일한 목표의 계산기를 Scala로 비보조 상태로 완성했습니다. 이것이 7부가 기록하는 핵심 관찰입니다.

---

> **개념 ↔ 행동: 에이전트 루프와 자가 수정**
>
> 7부의 실행 기록은 1부에서 설명한 **에이전트 루프(agent loop)**의 실제 모습입니다. 에이전트는 목표를 한 번에 달성하지 않습니다. task3에서 컴파일 오류(`private var pos` 접근 오류)를 컴파일러 출력(ObservationEvent)으로 읽고, 스스로 원인을 진단하고, `sed` 명령으로 수정하고, 재컴파일에 성공했습니다. "자가 수정은 별도로 설계된 기능이 아니라, agent loop와 observation 메커니즘의 자연스러운 결과"(1부 concepts.md) — 이 계산기 빌드 과정이 그 자연스러운 결과의 실제 모습입니다.

---

## 솔직한 공개: 스캐폴딩에 대하여

- **scaffold-invoked: NO** — 스캐폴드는 발동되지 않았습니다.
- **did-write-calc-unaided: YES** — 에이전트는 계산기 코드를 비보조 상태로 직접 작성했습니다.

폴백 스캐폴드(task2-calc-scaffold.txt)는 만일을 위해 준비됐으나, 에이전트가 task2에서 계산기를 직접 완성했기 때문에 한 번도 사용되지 않았습니다. 이것은 숨기지 않고 그대로 기록합니다.

출처: CAPTURE-MANIFEST.md, Calculator Outcome 절
