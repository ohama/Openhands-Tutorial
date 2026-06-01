# 태스크 계획 단계

OpenHands로 Rust HTTP 서버를 만들기 전에, 작업을 어떻게 나눌지 결정해야 했습니다. 에이전트에게 "Rust HTTP 서버를 만들어라"는 하나의 거대한 프롬프트를 주는 대신, 작업을 **세 개의 독립된 OpenHands 실행**으로 분해했습니다.

---

## 세 개의 태스크로 분해

| 태스크 | 역할 | 이벤트 수 | TerminalActions |
|--------|------|-----------|----------------|
| task1-scaffold | `cargo new rust-server` 실행 + 프로젝트 구조 확인 | 10 | 4 |
| task2-server | `src/main.rs` 작성 (HTTP 서버 코드) | 16 | 7 |
| task3-buildtest | 빌드 + 오류 2회 자가 수정 + `cargo run` + curl 검증 | 36 | 15 |
| **합계** | — | **62** | **26** |

출처: CAPTURE-MANIFEST.md, RUST-01 표

> **이벤트 수·번호 표기 주의:** 위 "이벤트 수"는 각 JSONL의 파싱 가능한 JSON 이벤트 객체 수입니다(task1 10, task2 16, task3 36). CAPTURE-MANIFEST.md는 task3를 "41 이벤트"로 적었는데, 이는 마지막 이벤트까지의 원시 줄 번호를 센 값입니다 — JSONL에는 JSON 객체와 배너·stderr 텍스트가 섞여 있습니다. TerminalAction 수(task3 15)는 두 방식에서 동일합니다. 본 장에서 인용하는 "이벤트 #N"은 매니페스트의 줄 기반 인덱싱 표기를 따릅니다(JSON 객체의 N번째 위치와는 다를 수 있습니다).

---

## task1 — 프로젝트 생성 (`cargo new`)

task1의 목적은 단순합니다. `cargo new rust-server` 명령으로 Rust 프로젝트 골격을 만드는 것입니다.

> **사용자 프롬프트**
>
> `task1-scaffold.txt` 요약: "작업 디렉토리에서 `cargo new rust-server`를 실행해 Rust 프로젝트를 생성하라. 그런 다음 생성된 구조(`ls`, `cat Cargo.toml`, `cat src/main.rs`)를 확인하라. 아직 파일을 수정하지 마라."

> **내부 프로세스**
>
> - 이벤트 #7 (TerminalAction): `cd .../oh-workdir-rust && cargo new rust-server` 실행 → 프로젝트 생성
> - 이어지는 TerminalAction들: `ls`, `cat Cargo.toml`, `cat src/main.rs`로 생성된 구조 확인

> **결과**
>
> 10 이벤트, 4회의 TerminalAction, 16.7초. `rust-server/Cargo.toml`(name = "rust-server", edition = "2024", 빈 [dependencies])과 `rust-server/src/main.rs`(기본 Hello World 템플릿) 생성 완료. 이벤트 #12 ObservationEvent에서 Cargo.toml 내용 확인됨. 출처: task1-scaffold.jsonl

task1이 특히 빠른 이유는 `cargo new`가 단순한 명령 하나이기 때문입니다. F# 계산기의 task1(3분 6초, 27회 TerminalAction)과 달리, 에이전트가 파일 쓰기에 어려움을 겪을 이유가 없었습니다.

---

## task2 — 서버 코드 작성

task2의 목적은 `src/main.rs`를 HTTP 서버로 재작성하는 것입니다.

---

## task3 — 빌드와 테스트

task3는 이 예제의 핵심입니다. 에이전트가 코드를 빌드하고, 컴파일러 오류 두 번을 진단하고, 자율적으로 수정하고, 최종적으로 curl로 서버를 검증했습니다. task3의 상세한 내용은 '빌드와 테스트 단계' 장에서 다룹니다.

---

## 왜 세 태스크로 나눴는가

각 태스크는 독립된 `openhands --headless` 호출입니다. 이전 태스크가 파일시스템에 남긴 결과물을 다음 태스크가 읽습니다. task1이 만든 `rust-server/` 디렉토리를 task2가 열어서 `src/main.rs`를 재작성하고, task2가 완성한 소스를 task3가 빌드합니다.

세 태스크의 역할 분리는 에이전트가 각 단계에서 명확한 목표를 가질 수 있도록 합니다. "프로젝트 생성", "코드 작성", "빌드·검증"이 분리되어 있으면 각 태스크의 프롬프트가 집중적이고 짧아집니다.

> **개념 ↔ 행동: 탐색(Explore) → 구현(Implement) → 검증(Verify)**
>
> 이 세 태스크 분해는 1부에서 소개한 **plan → write → test → run** 방법론의 실제 모습입니다.
>
> ```
> task1 (cargo new)   ←→  Explore   탐색: 환경 파악, 프로젝트 골격 생성
> task2 (write)       ←→  Implement 구현: src/main.rs HTTP 서버 작성
> task3 (build+test)  ←→  Verify    검증: cargo build + curl 동작 확인
> ```
>
> task3 내부의 두 번의 빌드 실패는 Verify → Implement의 자가 수정 사이클 그 자체입니다. 에이전트는 컴파일러 출력(ObservationEvent)을 읽고, 소스를 수정하고(ActionEvent), 다시 빌드하는 반복을 거쳐 빌드 성공에 도달했습니다. 이것은 "자가 수정은 agent loop와 observation 메커니즘의 자연스러운 결과"(1부 concepts.md)의 실제 사례입니다.
