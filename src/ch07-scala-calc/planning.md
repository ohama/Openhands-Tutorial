# 태스크 계획 단계

OpenHands로 Scala 3 계산기를 만들기 전에, 작업을 어떻게 나눌지 결정해야 했습니다. 에이전트에게 "Scala 계산기를 만들어라"는 하나의 거대한 프롬프트를 주는 대신, 작업을 **세 개의 독립된 OpenHands 실행**으로 분해했습니다.

---

## 세 개의 태스크로 분해

| 태스크 | 역할 | TerminalActions |
|--------|------|----------------|
| task1-scaffold | scala-cli 설치 확인 + Hello.scala 작성·실행 검증 | 4 |
| task2-write-calc | 70줄 Scala 3 재귀 하강 계산기 작성 (비보조) | 20 |
| task3-buildtest | 빌드·컴파일 오류 자가 수정 + 세 가지 정규 테스트 | 6 |
| **합계** | — | **30** |

출처: CAPTURE-MANIFEST.md, Timing Summary 절 및 Artifact Index

> **이벤트 수·번호 표기 주의:** 위 TerminalAction 수는 CAPTURE-MANIFEST.md의 Timing Summary에 기록된 값입니다. 본 장에서 인용하는 "이벤트 #N"은 매니페스트의 1-based 인덱싱 표기를 따릅니다. 각 JSONL 파일의 원시 줄 번호와 다를 수 있습니다.

---

## task1 — 환경 확인 (scala-cli 검증)

task1의 목적은 단순합니다. scala-cli가 올바르게 설치돼 있는지 확인하고, 간단한 Hello.scala를 작성해 Scala 3 환경이 동작함을 검증하는 것입니다.

> **사용자 프롬프트**
>
> `task1-scaffold.txt` 요약: "작업 디렉토리에서 scala-cli 버전을 확인하고, `calc/` 폴더를 만들어 간단한 Hello.scala(`@main def hello() = println("SCALA_OK")`)를 작성하고 실행하라. 아직 계산기를 작성하지 마라."

> **내부 프로세스**
>
> - 이벤트 #6 (TerminalAction): `scala-cli --version` 실행
> - 이벤트 #7 (ObservationEvent, exit=0): `Scala CLI version: 1.14.0 / Scala version (default): 3.8.3` 응답
> - 이벤트 #12 (TerminalAction): `@main def hello() = println("SCALA_OK")` 내용의 Hello.scala 작성 — Scala 3 `@main` 관용어를 자발적으로 사용
> - 이벤트 #16 (TerminalAction): `scala-cli run Hello.scala` 실행
> - 이벤트 #17 (ObservationEvent, exit=0): `SCALA_OK` 출력

> **결과**
>
> 4회의 TerminalAction, 30.5초. scala-cli 1.14.0 / Scala 3.8.3 환경 확인 완료. `SCALA_OK` 출력으로 Scala 3 `@main` 진입점 동작 검증. 출처: task1-scaffold.jsonl, CAPTURE-MANIFEST.md § SCAL-01

task1이 특히 빠른 이유는 환경 확인만이 목적이기 때문입니다. 에이전트가 scala-cli 버전을 확인하고, `@main def hello()` 관용어를 프롬프트에서 별도 지시 없이도 선택해 Scala 3 진입점을 올바르게 작성했습니다.

---

## task2 — 계산기 코드 작성

task2의 목적은 `Calc.scala`를 Scala 3 재귀 하강 계산기로 작성하는 것입니다. 계산기 코드 작성의 상세한 내용은 '코드 작성 단계' 장에서 다룹니다.

---

## task3 — 빌드와 테스트

task3는 이 예제의 핵심입니다. 에이전트가 컴파일 오류를 진단하고, 자율적으로 수정하고, 세 가지 정규 테스트를 통과했습니다. task3의 상세한 내용은 '빌드와 테스트 단계' 장에서 다룹니다.

---

## 왜 세 태스크로 나눴는가

각 태스크는 독립된 `openhands --headless` 호출입니다. 이전 태스크가 파일시스템에 남긴 결과물을 다음 태스크가 읽습니다. task1이 만든 `calc/` 디렉토리를 task2가 열어 `Calc.scala`를 작성하고, task2가 완성한 소스를 task3가 빌드합니다.

세 태스크의 역할 분리는 에이전트가 각 단계에서 명확한 목표를 가질 수 있도록 합니다. "환경 확인", "코드 작성", "빌드·검증"이 분리되어 있으면 각 태스크의 프롬프트가 집중적이고 짧아집니다.

> **개념 ↔ 행동: 탐색(Explore) → 구현(Implement) → 검증(Verify)**
>
> 이 세 태스크 분해는 1부에서 소개한 **plan → write → test → run** 방법론의 실제 모습입니다.
>
> ```
> task1 (scala-cli 확인)  ←→  Explore   탐색: 환경 파악, Scala 3 진입점 검증
> task2 (Calc.scala 작성) ←→  Implement 구현: 70줄 재귀 하강 계산기 작성
> task3 (빌드+테스트)      ←→  Verify    검증: 컴파일 + 세 가지 정규 테스트
> ```
>
> task3 내부의 컴파일 오류 자가 수정은 Verify → Implement의 자가 수정 사이클 그 자체입니다. 에이전트는 컴파일러 출력(ObservationEvent)을 읽고, 원인(`private` 한정자 문제)을 진단하고, `sed`로 소스를 수정하고, 재컴파일에 성공했습니다. 이것은 "자가 수정은 agent loop와 observation 메커니즘의 자연스러운 결과"(1부 concepts.md)의 실제 사례입니다.
