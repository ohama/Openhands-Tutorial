# 부록 E: OpenHands 자체 계획 vs GSD 계획(코드 포함) — 계획 내용·정확도·시간

이 부록은 두 가지 **계획 방식**을 정면으로 비교한다. 부록 D의 더 큰 매트릭스에서 이 두 경우만 떼어내 "계획에 무엇이 담겼는지"와 "그 결과(정확도·시간)"를 나란히 본다.

1. **자체 계획 (OpenHands self-plan)** — 35B가 task tracker로 *스스로* 계획을 세우고, 코드도 *스스로* 작성·실행한다. (부록 D의 Arm B)
2. **GSD 계획 + 코드 (GSD plan with code → OpenHands)** — GSD 다중 에이전트 파이프라인(research→plan→verify)이 만든 계획을 **레퍼런스 코드까지 통째로** 프롬프트에 넣어 35B에 넘긴다. 35B는 주어진 코드를 옮겨 쓰고 테스트한다. (부록 D §6.9의 Arm C-orig)

> **⚠ 가장 중요한 전제 (필독):** 두 방식은 측정하는 것이 다르다.
> - **자체 계획**은 모델이 계획·작성·디버깅을 *전부 스스로* 한다 → **모델의 능력**을 측정.
> - **GSD 계획+코드**는 모델에게 **정답 코드를 떠먹인다** → 사실상 **베껴쓰기(전사)**를 측정.
>
> 따라서 정확도가 후자에서 높게 나오는 것은 "계획이 더 좋아서"가 아니라 "답을 줬기 때문"이다. 이 비대칭을 염두에 두고 읽어야 한다. 아래 수치는 모두 커밋된 캡처 아티팩트에서 직접 인용했고, **타이밍은 실행 시점·반복수(n)·프록시 캐시 상태가 달라 arm 간 정밀 비교가 불가**하다(측정값으로만 기록).

| 항목 | 자체 계획 (Arm B) | GSD 계획+코드 (Arm C-orig) |
|------|-------------------|-----------------------------|
| 계획 주체 | 35B 본인 (task tracker) | GSD 파이프라인 (Claude 에이전트들) |
| 코드 제공 | ✗ (스스로 작성) | ✓ (레퍼런스 소스 전체 임베드) |
| 캡처 | 2026-06-02, n=3 (중앙값) | 2026-06-04, n=1 |
| 측정 대상 | 모델의 계획+작성 능력 | 주어진 코드의 전사 |

---

## 1. 계획의 내용

### 1.1 F# (FsLex/FsYacc 계산기)

**자체 계획 (Arm B) — 35B가 만든 5-태스크 목록** (task tracker, 코드 없음):

> 1. 프로젝트 구조와 .fsproj 파일 생성 (FsLexYacc 11.3.0 참조)
> 2. Lexer (Lexer.fsl) 작성 — 정수, + - * /, 괄호, 공백
> 3. Parser (Parser.fsy) 작성 — +/- 왼쪽 결합, */ 더 강하게, 괄호
> 4. main 프로그램 (Program.fs) 작성 — 인수 읽기·파싱·평가·출력
> 5. 빌드 및 정규 테스트 실행

→ 파일 이름과 개념만 나열한다. **FsLex `.fsl` 규칙 문법, FsYacc `.fsy` 문법, .fsproj 배선(컴파일 순서·`--module`·`--unicode`)의 실제 내용은 없다** — 그건 35B가 직접 써야 한다.

**GSD 계획+코드 (Arm C-orig)** — research(HIGH confidence)로 FsLexYacc 배선·함정을 조사한 뒤, 계획 안에 **검증된 `Calc.fsproj` + `Lexer.fsl` + `Parser.fsy` + `Program.fs` 전체 소스**를 그대로 담는다. 35B는 "이 파일들을 heredoc으로 그대로 만들고 빌드·테스트하라"는 지시를 받는다. (즉 `.fsl`/`.fsy` DSL 문법이 완성된 형태로 제공됨.)

### 1.2 Rust (HTTP 서버)

**자체 계획 (Arm B) — 4-태스크:**
> 1. Cargo 프로젝트 초기화 2. `std::net::TcpListener`로 8080 바인드·`hello\n`·루프 3. `cargo build --release` 4. `curl` 정규 테스트

**GSD 계획+코드 (Arm C-orig):** research로 std-only HTTP 프레이밍·함정을 조사한 뒤 **완성된 `main.rs` + `Cargo.toml` 전체**를 계획에 임베드.

### 1.3 Scala (Scala 3 계산기)

**자체 계획 (Arm B) — 4-태스크:**
> 1. 재귀 하향 파서로 Calc.scala 작성 (expr→term→factor, 괄호) 2~4. 정규 테스트 3개(2+3*4→14, (2+3)*4→20, 10-3-2→5)

**GSD 계획+코드 (Arm C-orig):** research(레퍼런스 구현을 직접 실행해 검증)로 좌측결합·`@main`/private 함정을 조사한 뒤 **완성된 `Calc.scala` 전체**를 계획에 임베드.

**요약:** 자체 계획은 *무엇을* 할지(파일·개념)만, GSD 계획+코드는 *정확히 어떤 코드*인지까지 담는다.

---

## 2. 결과: 정확도와 시간

정확도 = 정규 테스트 통과(`2+3*4`/`(2+3)*4`/`10-3-2` 또는 `curl→hello`). 시간 = JSONL 타임스탬프 도출 벽시계. 자체 계획은 n=3 중앙값(최소–최대), GSD+코드는 n=1.

| 예제 | 방식 | 정확도 | 벽시계 시간(초) | 오류 수정 사이클 |
|------|------|:------:|----------------:|:----------------:|
| **F#** | 자체 계획 (n=3) | **0/3 FAIL** | 486.78 (352–695) | 11 |
| | GSD+코드 (n=1) | **3/3 PASS** | 495.62 | 4 |
| **Rust** | 자체 계획 (n=3) | **3/3 PASS** | 66.79 (59–71) | 0 |
| | GSD+코드 (n=1) | **미완**\* | n/a | n/a |
| **Scala** | 자체 계획 (n=3) | **2/3 PASS + 1 PARTIAL** | 936.16 (868–1442) | 2 |
| | GSD+코드 (n=1) | **3/3 PASS** | 99.9 | 0 |

\* **Rust GSD+코드 = 미완(모델 결과 아님):** 두 번의 시도 모두 OpenHands CLI의 `ConversationErrorEvent code=MissingStyle` 렌더링 버그(프롬프트에 박힌 `awk '/^\[dependencies\]/...'` 검증 명령의 백슬래시를 색상 코드로 오파싱)로 scaffold 단계에서 중단됐다. task/모델 실패가 아니라 하니스 버그라 PASS/FAIL 미채점.

---

## 3. 해석

### F# — 가장 선명한 대비 (능력의 한계가 드러나는 곳)
자체 계획은 **0/3 전패**: 35B는 스스로 계획을 잘 세웠지만(파일·개념은 맞음) **FsLex/FsYacc DSL 문법 자체를 써내지 못했다**. 그런데 GSD가 **완성된 `.fsl`/`.fsy` 코드를 떠먹이자 3/3 통과**(오류 수정도 11→4회로 급감). → **병목은 "계획"이 아니라 "DSL 작성 능력"**이다. 계획을 누가 세우든, 코드를 못 쓰면 OOD 과제는 실패한다.

### Rust·Scala — in-distribution이라 자체 계획만으로 충분
자체 계획이 Rust 3/3, Scala 2/3+PARTIAL로 **이미 대체로 성공**한다(35B의 분포 내 언어). 코드를 떠먹여도 추가되는 정확도 이점이 본질적으로 없다(Scala는 둘 다 통과, Rust는 자체 계획이 깔끔히 통과하고 GSD+코드는 하니스 버그로 미완).

### 시간 (주의해서 읽을 것)
GSD+코드의 Scala 벽시계(99.9s)가 자체 계획(936s)보다 짧은데, 이는 **(a) 답을 줘서 탐색·시행착오가 없고 (b) 캐시·실행순서·n이 달라서**가 섞인 결과다 — **계획 품질 신호로 해석 불가**. F#은 양쪽 모두 비슷한 시간대(~490s)인데, 자체 계획은 그 시간을 헛되이 헤매다 실패했고, GSD+코드는 같은 시간에 전사·빌드해 통과했다.

### 결론
- **자체 계획**은 모델의 진짜 능력을 보여준다: in-distribution(Rust·Scala)은 스스로 충분, OOD(F#)는 스스로 불가.
- **GSD 계획+코드**가 더 "정확"해 보이는 것은 **계획이 우월해서가 아니라 정답 코드를 제공했기 때문**이다 — F#의 0/3→3/3 반전이 그 증거다. 이는 능력이 아니라 전사를 측정한다.
- 한 문장: **"좋은 계획"은 모델이 이미 쓸 수 있는 언어에서만 무료로 따라온다. 못 쓰는 언어(OOD DSL)에서는 계획이 아니라 코드 자체를 줘야 통과하며, 그건 더 이상 모델의 능력이 아니다.**

이 부록은 부록 D(전체 4-조건 비교)의 두 극단 — "전부 스스로"(자체 계획) vs "답까지 제공"(GSD+코드) — 을 떼어내 본 것이다. 가운데 지점(Claude 계획만, GSD 코드 없는 계획만)은 부록 D §2–§6 참조.

---

## 4. 출처 (Sources)

- **자체 계획 (Arm B), n=3** — `.planning/milestones/v1.4-phases/13-full-study-fsharp-scala-analysis/captured-planning/{fsharp,rust,scala}/`
  - `arm-b/planning-artifact/oh-self-plan.md` — task tracker 자체 계획(verbatim)
  - `{lang}/comparison.json` — 정확도·벽시계·오류 수정 사이클(중앙값/최소–최대)
- **GSD 계획+코드 (Arm C-orig), n=1** — `.planning/milestones/v1.5-phases/17-arm-c-orig-full-plan-capture/`
  - `17-CAPTURE-MANIFEST.md` — F# FAIL→PASS flip, 4-조건 매트릭스, Rust 하니스 버그 disclosure
  - `captured-planning/{fsharp,scala}/arm-c-orig/{metrics.json, planning-artifact/oh-prompt.txt, final-source/, test-output.txt}`
- 더 큰 맥락(Arm A·B·C-mech·C-orig 4-조건): [부록 D §6](appendix-d-planning-comparison.md)
