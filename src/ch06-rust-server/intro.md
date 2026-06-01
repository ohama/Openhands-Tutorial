# 예제 프로젝트 소개

6부에서 OpenHands는 Rust HTTP 서버를 만듭니다. 이것은 4부의 F# 계산기에 이어지는 두 번째 "다른 워킹 예제"입니다. 같은 35B 모델, 같은 에이전트 루프 — 그러나 이번에는 전혀 다른 언어와 도메인입니다.

---

## 무엇을 만드는가

목표는 단순합니다. `GET /` 요청에 `hello\n`을 응답하는 **최소한의 Rust HTTP 서버**입니다.

```
$ curl http://localhost:8080/
hello
```

서버는 `0.0.0.0:8080`에 바인딩하고, 접속을 무한 루프로 받아들이며, 각 요청에 다음 응답을 반환합니다.

```
HTTP/1.1 200 OK
Content-Length: 6
Connection: close

hello
```

외부 크레이트(crate)는 전혀 사용하지 않습니다. `Cargo.toml`의 `[dependencies]` 섹션은 비어 있습니다. 에이전트는 Rust 표준 라이브러리(`std::net::TcpListener`, `std::io::{BufRead, BufReader, Write}`)만으로 이 서버를 작성해야 합니다.

---

## 실행 정보

| 항목 | 값 |
|------|-----|
| 모델 | openai/qwen-35b (Qwen2.5-35B, litellm 프록시 경유) |
| 실행일 | 2026-05-28 |
| OpenHands 버전 | SDK v1.21.0 / CLI 1.16.0 |
| Rust 버전 | rustc/cargo 1.95.0 |
| 태스크 수 | 3 (task1: 프로젝트 생성, task2: 서버 작성, task3: 빌드·테스트) |

출처: CAPTURE-MANIFEST.md, Run Metadata 절

---

## 이 예제의 가설

CAPTURE-MANIFEST.md의 Comparison Hook 절은 다음을 기록합니다.

> v1에서 35B 모델은 FsLex `.fsl` 파일을 unaided(비보조 상태)로 올바르게 생성하지 못했습니다 — 세 번의 별도 에이전트 실행(94 + 27 + 16 회의 TerminalAction)이 모두 실패했습니다. v1.2에서 같은 35B 모델은 Rust HTTP 서버를 unaided 1회 시도로 작성했습니다(task2-server.jsonl, 이벤트 #13).

이것은 모델의 실력이 절대적이지 않다는 것을 보여줍니다. Rust는 이 모델의 훈련 데이터에서 FsLex보다 훨씬 일반적입니다. 같은 모델이라도 도메인에 따라 결과가 달라집니다.

---

> **개념 ↔ 행동: 에이전트 루프와 자가 수정**
>
> 6부의 실행 기록은 1부에서 설명한 **에이전트 루프(agent loop)**의 실제 모습입니다. 에이전트는 목표를 한 번에 달성하지 않습니다. task3에서 두 번의 빌드 실패를 컴파일러 출력(ObservationEvent)으로 읽고, 각각 스스로 진단하고, 코드를 다시 작성하고, 재빌드했습니다. "자가 수정은 별도로 설계된 기능이 아니라, agent loop와 observation 메커니즘의 자연스러운 결과"(1부 concepts.md) — 이 서버 빌드 과정이 그 자연스러운 결과의 실제 모습입니다.

---

## 솔직한 공개: 스캐폴딩에 대하여

4부(F# 계산기)에서는 FsLex 렉서 파일과 프로젝트 파일을 프롬프트에 제공해야 했습니다. 이번 6부에서는 다릅니다.

- **scaffold-invoked: NO** — 스캐폴드는 발동되지 않았습니다.
- **did-write-server-unaided: YES** — 에이전트는 task2에서 서버 코드를 비보조 상태로 직접 작성했습니다.

Cargo.toml 자체는 `cargo new` 명령이 자동 생성했습니다(task1). 에이전트가 목표 설명만으로 `TcpListener + BufReader` 조합을 선택하고 43줄의 HTTP 서버를 작성한 것이 이 예제의 핵심입니다.

출처: CAPTURE-MANIFEST.md, Server Outcome 절
