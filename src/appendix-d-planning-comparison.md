# 부록 D: 계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획

이 부록은 v1.4 계획 비교 연구(Planning A/B Study)의 결과를 기록한다. 이 연구의 핵심 질문은 **"전문가가 작성한 계획이 35B의 실행에 도움이 되는가?"** 이다 — Claude가 35B보다 계획을 더 잘 짠다는 주장이 아니다.

**Arm A (전문가 계획 제공):** 프롬프트에 Claude가 작성한 번호 매긴 단계별 계획을 포함시켜 35B가 그 계획에 따라 실행하도록 했다. 두 프롬프트는 동일한 제어 블록(목표, 제약 조건, 정규 테스트)을 공유하며, 유일한 차이는 번호 매긴 계획의 포함 여부다.

**Arm B (자체 계획):** 제어 블록과 목표만 주고, task tracker를 통해 35B가 스스로 계획을 세우고 실행하도록 했다. 계획의 출처(Claude 대 35B)가 독립 변수다.

세 예제(F# FsLex/FsYacc 계산기, Rust HTTP 서버, Scala 3 계산기)에서 각각 두 Arm을 n=3 반복 실행했다. 모든 수치와 주장은 커밋된 `captured-planning/` 아티팩트에서 직접 인용한 것이다.

> **후속 실험 (§6):** 본 2-Arm 연구가 끝난 뒤, GSD 다중 에이전트 파이프라인으로 생성한 **코드 없는** 전문가 계획을 세 번째 조건 **Arm C**로 세 예제 모두(Rust·F#·Scala) 캡처했다(2026-06-04, 각 n=1 단독). 결과는 Arm A 패턴과 일치 — in-distribution(Rust·Scala) PASS, OOD(F#) FAIL. 본 n=3 연구와 카운터밸런스되지 않은 별개 보충 실험이므로 타이밍은 직접 비교하지 않는다 — 자세한 내용은 §6 참조.

---

## 1. 실험 설계

| 항목 | 값 |
|------|-----|
| OpenHands CLI | 1.16.0 |
| 모델 | `openai/qwen-35b` via litellm proxy (`http://127.0.0.1:4000/v1`) |
| 에이전트 | CodeActAgent (기본 headless) |
| 실행 플래그 | `--headless --json --yolo --override-with-envs` |
| 실행 날짜 | 2026-06-02 (실행) / 2026-06-04 (extractor 수정 및 재추출) |
| n (셀당) | 3 |
| 세션 | arm × rep당 단일 OpenHands 호출 |
| 제어 블록 대칭 | 각 예제별 PROMPT-DIFF 파일에 CONTROL-BLOCK SYMMETRY: PASS 확인 |

**카운터밸런스 실행 순서:**

| 예제 | 예제 내 순서 |
|------|-------------|
| F# | Arm B 먼저 (rep 1–3, 위치 1–3), 그 다음 Arm A (rep 1–3, 위치 4–6) |
| Scala | Arm B 먼저 (rep 1–3, 위치 7–9), 그 다음 Arm A (rep 1–3, 위치 10–12) |
| Rust | Arm A 먼저 (rep 2–3, 위치 13–14), 그 다음 Arm B (rep 2–3, 위치 15–16); run-1은 Phase-12 파일럿 |

호스트 툴체인 확인: .NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0 (Scala 3.8.3) + JDK 17.

(출처: `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/CAPTURE-MANIFEST.md` §"Version Block", §"Run Conditions and Counterbalanced Order")

---

## 2. 계획 아티팩트 비교

### 2.1 F# (FsLex/FsYacc 계산기)

**Arm A — Claude의 계획 (5단계)**

Claude의 계획은 v1 F# 태스크 분해를 단일 세션 형식으로 기계적으로 변환한 것이다. FsLexYacc 툴체인의 세부 배선을 명시적으로 설명한다.

> **Arm A 계획 요약 (출처: `fsharp/arm-a/planning-artifact/claude-plan.md`)**
>
> - Step 1: Scaffold — `dotnet new console -F# -o calc`; calc.fsproj를 FsLexYacc 11.3.0으로 배선 (FsYacc `--module` 플래그, FixLineDirectives 타겟 포함, 컴파일 순서: Parser.fsi, Parser.fs, Lexer.fs, Program.fs)
> - Step 2: Lexer.fsl 작성 — FsLex 규칙 구문 명시 (FsYacc 구분자 `%%` 사용 금지); 토큰 이름 명시 (INT/PLUS/MINUS/STAR/SLASH/LPAREN/RPAREN/EOF)
> - Step 3: Parser.fsy 작성 — FsYacc 문법; entry point `start`; 우선순위/결합성 선언
> - Step 4: Program.fs 작성 — 정확한 네임스페이스 `FSharp.Text.Lexing`; `LexBuffer<char>.FromString`
> - Step 5: 빌드 및 테스트 — 반복 오류 수정; 정규 테스트 3개 명시

**Arm B — 35B 자체 계획 (5태스크, 이벤트 #4)**

> **Arm B 계획 요약 (출처: `fsharp/arm-b/planning-artifact/oh-self-plan.md`, TaskTrackerAction 이벤트 #4)**
>
> - Task 1: 프로젝트 구조와 .fsproj 파일 생성 — FsLexYacc 11.3.0 참조 설정
> - Task 2: Lexer (Lexer.fsl) 작성 — 정수, +, -, *, /, 괄호, 공백 처리
> - Task 3: Parser (Parser.fsy) 작성 — 왼쪽 결합 +/-, */는 더 강하게 바인딩, 괄호 오버라이드
> - Task 4: main 프로그램 (Program.fs) 작성 — 명령줄 인수 읽기, 파싱, 평가, 출력
> - Task 5: 빌드 및 정규 테스트 실행 — 테스트: 2+3*4=14, (2+3)*4=20, 10-3-2=5

| 차원 | Arm A (Claude 계획) | Arm B (자체 계획) |
|------|---------------------|-------------------|
| 태스크 수 | 5단계 | 5태스크 |
| 세분도 | 세밀 — Step 1: .fsproj XML 구조, FixLineDirectives 타겟, 컴파일 순서, FsYacc `--module` 플래그 명시; Step 2: FsLex 구문 경고; Step 4: 정확한 네임스페이스 | 거침 — 각 태스크가 파일을 명명하고 파싱 개념(우선순위, 연산자)을 나열하지만 .fsproj 배선, FixLineDirectives, 또는 정확한 FsLex/FsYacc 구문 제약 없음 |
| 순서 | scaffold → 렉서 → 파서 → 프로그램 → 빌드/테스트 | scaffold → 렉서 → 파서 → 프로그램 → 빌드/테스트 |
| Scaffold→Write→Build→Test | FULL (4단계, 각 단계 명시) | PARTIAL (같은 순서이나 빌드+테스트 결합; .fsproj 배선 명세 부족) |

(출처: `captured-planning/PLAN-COMPARISON-QUALITATIVE.md` §1 F# 비교)

---

### 2.2 Rust (HTTP 서버)

**Arm A — Claude의 계획 (3단계)**

> **Arm A 계획 요약 (출처: `rust/arm-a/planning-artifact/claude-plan.md`)**
>
> - Step 1: Scaffold — `cargo new rust-server`; Cargo.toml과 src/main.rs 존재 확인
> - Step 2: 서버 작성 — src/main.rs 재작성: TCP 포트 8080 바인드, `hello\n` 응답, 루프; 표준 라이브러리만 사용
> - Step 3: 빌드 및 테스트 — `cargo build`; 서버 실행; `curl -s http://localhost:8080/`; `hello` exit 0 확인

**Arm B — 35B 자체 계획 (4태스크, 이벤트 #4)**

> **Arm B 계획 요약 (출처: `rust/arm-b/planning-artifact/oh-self-plan.md`, TaskTrackerAction 이벤트 #4)**
>
> - Task 1: Cargo로 Rust 프로젝트 초기화 — Cargo.toml 및 src/main.rs 생성
> - Task 2: main.rs에 HTTP 서버 구현 — std::net::TcpListener로 포트 8080 바인드, HTTP 요청 읽기, `hello\n` 응답, 루프
> - Task 3: 프로젝트 빌드 — `cargo build --release` 실행
> - Task 4: 정규 테스트 실행: `curl -s http://localhost:8080/` — `hello` 출력, exit code 0 확인

| 차원 | Arm A (Claude 계획) | Arm B (자체 계획) |
|------|---------------------|-------------------|
| 태스크 수 | 3단계 | 4태스크 |
| 세분도 | 중간 — Step 2: TcpListener, 포트 8080, `hello\n`, 루프, 표준 라이브러리; Step 3: 빌드+테스트 결합 | 세밀(빌드/테스트) — 자체 계획은 빌드(태스크 3)와 curl 테스트(태스크 4) 분리 |
| 순서 | scaffold → 작성 → 빌드+테스트 | scaffold → 작성 → 빌드 → 테스트 |
| Scaffold→Write→Build→Test | FULL (빌드+테스트 결합이나 둘 다 포함) | FULL (4태스크로 4단계 분리) |

(출처: `captured-planning/PLAN-COMPARISON-QUALITATIVE.md` §2 Rust 비교)

---

### 2.3 Scala (Scala 3 계산기)

**Arm A — Claude의 계획 (3단계)**

> **Arm A 계획 요약 (출처: `scala/arm-a/planning-artifact/claude-plan.md`)**
>
> - Step 1: Scaffold — `scala-cli --version`; `mkdir -p calc`; Hello.scala 작성; `scala-cli run Hello.scala` 실행; SCALA_OK 확인
> - Step 2: Calc.scala 작성 — 재귀 하향 파서, 올바른 우선순위, 정수 산술, 표준 라이브러리만; `cat Calc.scala` 확인
> - Step 3: 빌드 및 테스트 — `scala-cli run Calc.scala -- "2+3*4"` (컴파일); 반복 오류 수정; 3개 정규 테스트 보고

**Arm B — 35B 자체 계획 (4태스크, 이벤트 #6)**

> **Arm B 계획 요약 (출처: `scala/arm-b/planning-artifact/oh-self-plan.md`, TaskTrackerAction 이벤트 #6)**
>
> - Task 1: 재귀 하향 파서로 Calc.scala 작성 — 우선순위 레벨 구조 명시: expr (낮음) → term (중간) → factor (높음), 괄호 지원
> - Task 2: 정규 테스트 1: 2+3*4 → 14 — * 가 +보다 강하게 바인딩 확인
> - Task 3: 정규 테스트 2: (2+3)*4 → 20 — 괄호가 우선순위 오버라이드 확인
> - Task 4: 정규 테스트 3: 10-3-2 → 5 — 왼쪽 결합 뺄셈 확인

| 차원 | Arm A (Claude 계획) | Arm B (자체 계획) |
|------|---------------------|-------------------|
| 태스크 수 | 3단계 | 4태스크 |
| 세분도 | 중간 — Step 1: 명시적 smoke-test 검증(SCALA_OK); Step 2: 표준 라이브러리만 제약; Step 3: 반복 컴파일 수정 루프 | 세밀(테스트) — 3개 정규 테스트를 별개 태스크로 분리; 테스트 주도 구조; scaffold smoke-test 생략 |
| 순서 | scaffold → 작성 → 빌드+테스트 | 작성 → 테스트1 → 테스트2 → 테스트3 (scaffold 없음) |
| Scaffold→Write→Build→Test | FULL (scaffold 명시; 빌드+테스트 결합) | PARTIAL (scaffold 생략; 작성 → 테스트; 빌드 암시적) |

(출처: `captured-planning/PLAN-COMPARISON-QUALITATIVE.md` §3 Scala 비교)

---

### 2.4 계획 구조 요약

| 예제 | Claude 단계 수 | 자체 계획 태스크 수 | 동일 순서? | Claude Scaffold→Write→Build→Test | 자체 계획 Scaffold→Write→Build→Test |
|------|---------------|---------------------|-----------|----------------------------------|--------------------------------------|
| F# | 5 | 5 | YES | FULL | PARTIAL (빌드+테스트 결합; 배선 명세 부족) |
| Rust | 3 | 4 | YES (자체 계획은 빌드/테스트 분리) | FULL | FULL (4태스크로 4단계) |
| Scala | 3 | 4 | 대부분 (자체 계획은 scaffold 생략, 테스트 분리) | FULL | PARTIAL (scaffold 생략, 빌드 암시적) |

**핵심 관찰:** 두 계획 모두 독립적으로 동일한 기본 분해(scaffold/write/build/test)를 선택했다. 주요 차이는 세분도다: Claude의 계획은 FsLexYacc 툴체인 세부사항(F#), CLI 검증 패턴(Scala scaffold), 명시적 반복 빌드-수정 루프(전체)를 추가한다. Scala 자체 계획은 테스트 수준에서 더 세밀한 테스트 주도 변형을 보여준다.

(출처: `captured-planning/PLAN-COMPARISON-QUALITATIVE.md` §Summary Table)

---

## 3. 지표 비교 테이블 (P1/P2)

모든 값은 n=3 반복에서 중앙값 (최솟값–최댓값) 형식. 토큰 열 없음 (JSONL에 `usage` 필드 없음).

### F# (FsLex/FsYacc 계산기)

| 지표 | Arm A (Claude 계획) | Arm B (자체 계획) |
|------|---------------------|-------------------|
| TerminalActions 수 | 80 (77–210) | 74 (52–97) |
| 총 이벤트 수 | 207 (204–456) | 174 (139–227) |
| 벽시계 시간 (초) | 1475.25 (470.16–1852.78) | 486.78 (352.28–695.26) |
| 평균 LLM 호출 간격 (초) | 5.01 (3.60–10.78) | 3.95 (3.11–4.00) |
| 최소 LLM 호출 간격 (초) | 1.30 (1.23–2.19) | 0.88 (0.80–1.49) |
| 최대 LLM 호출 간격 (초) | 37.91 (21.62–70.92) | 25.92 (25.54–40.31) |
| 오류 수정 사이클 수 | 21 (17–28) | 11 (7–14) |
| TaskTracker 관찰 이벤트 수 | 0 (0–0) | 7 (4–8) |
| TaskTracker 액션 이벤트 수 | 0 (0–0) | 7 (5–8) |

### Rust (HTTP 서버)

| 지표 | Arm A (Claude 계획) | Arm B (자체 계획) |
|------|---------------------|-------------------|
| TerminalActions 수 | 12 (12–14) | 13 (12–16) |
| 총 이벤트 수 | 26 (26–30) | 44 (40–50) |
| 벽시계 시간 (초) | 48.30 (42.32–49.32) | 66.79 (59.04–71.48) |
| 평균 LLM 호출 간격 (초) | 2.13 (2.11–2.56) | 2.21 (2.15–2.29) |
| 최소 LLM 호출 간격 (초) | 1.27 (1.12–1.54) | 0.87 (0.77–1.05) |
| 최대 LLM 호출 간격 (초) | 4.87 (4.85–5.28) | 5.07 (5.04–5.14) |
| 오류 수정 사이클 수 | 0 (0–0) | 0 (0–0) |
| TaskTracker 관찰 이벤트 수 | 0 (0–0) | 7 (7–7) |
| TaskTracker 액션 이벤트 수 | 0 (0–0) | 7 (7–8) |

### Scala (Scala 3 계산기)

| 지표 | Arm A (Claude 계획) | Arm B (자체 계획) |
|------|---------------------|-------------------|
| TerminalActions 수 | 37 (21–62) | 13 (8–27) |
| 총 이벤트 수 | 76 (44–132) | 50 (37–83) |
| 벽시계 시간 (초) | 345.67 (304.24–543.95) | 936.16 (868.45–1442.28) |
| 평균 LLM 호출 간격 (초) | 5.43 (4.06–9.86) | 19.76 (12.15–37.50) |
| 최소 LLM 호출 간격 (초) | 1.43 (1.33–2.08) | 1.70 (1.39–2.18) |
| 최대 LLM 호출 간격 (초) | 28.13 (20.47–57.50) | 64.03 (60.70–118.00) |
| 오류 수정 사이클 수 | 6 (3–10) | 2 (2–5) |
| TaskTracker 관찰 이벤트 수 | 0 (0–0) | 5 (5–9) |
| TaskTracker 액션 이벤트 수 | 0 (0–0) | 8 (7–10) |

> **타이밍 주의 (필독):** 모든 벽시계 및 LLM 호출 간격 값은 **JSONL 타임스탬프에서 도출됨**이며, **캐시 온도/실행 순서 교란 변수**를 포함한다. litellm 프록시의 KV/접두사 캐시는 동일 예제 내 후속 실행에서 더 따뜻하게 유지되었다. F#과 Scala에서는 Arm B가 먼저 실행되어 캐시가 더 차가웠고, Arm A가 두 번째로 실행되어 캐시가 더 따뜻했다. Rust 보충 실행에서는 Arm A가 먼저 실행됐다. **이 타이밍 델타를 계획 품질 신호로 해석해서는 안 된다.** Scala의 Arm B 벽시계(중앙값 936s)가 Arm A(345s)보다 훨씬 높은 이유는 거의 전적으로 캐시 온도와 실행 순서 차이로 설명되며, F#의 벽시계 델타는 OOD 태스크 난이도에 의해 교란된다.
>
> (출처: `CAPTURE-MANIFEST.md` §"Timing caveat (mandatory)")

**TaskTracker 확인:** Arm B는 모든 예제에서 task_tracker 이벤트를 방출했다 (F#: 중앙값 7회; Scala: 중앙값 5회; Rust: 중앙값 7회, 3회 반복 모두 일관). Arm A는 모든 예제에서 0회 방출했다 — 에이전트가 제공된 Claude 계획을 설계대로 실행했음을 확인한다.

(출처: `fsharp/comparison.json`, `scala/comparison.json`, `rust/comparison.json`)

---

## 4. 정규 테스트 결과

**PARTIAL-PASS 정의:** Scala Arm B run-3에서 에이전트가 컴파일 오류를 수정한 후 테스트 2+3을 성공적으로 실행했으나, 테스트 1(`2+3*4`)은 수정 후 재실행되지 않았다. 수정된 바이너리가 테스트 1을 통과할 것이라는 근거는 간접적이다. 이를 정직하게 PARTIAL-PASS로 기록한다.

| 예제 | Arm A 정규 통과 | Arm B 정규 통과 |
|------|----------------|----------------|
| F# (n=3) | **1/3** PASS | **0/3** PASS (전체 FAIL) |
| Scala (n=3) | **3/3** PASS | **2/3** PASS + 1 PARTIAL-PASS |
| Rust (n=3) | **3/3** PASS | **3/3** PASS |

### F# 상세 (rep별)

| Rep | Arm A | Arm B |
|-----|-------|-------|
| 1 | PASS (이벤트 #200, #202, #204에서 14/20/5) | FAIL (빌드 오류; 3개 테스트 모두 미실행) |
| 2 | FAIL (빌드/런타임 오류; 456 이벤트) | FAIL (빌드 오류; 테스트 미실행) |
| 3 | FAIL (빌드 성공; 런타임 크래시 exit=134) | FAIL (빌드 오류; 테스트 미실행) |

Arm A run-1 PASS (단일 실행): 이벤트 #200에서 `2+3*4`→14, #202에서 `(2+3)*4`→20, #204에서 `10-3-2`→5.

### Scala 상세 (rep별)

| Rep | Arm A | Arm B |
|-----|-------|-------|
| 1 | PASS (이벤트 #39, #41, #43에서 14/20/5) | PASS (이벤트 #69, #73, #77에서 14/20/5) |
| 2 | PASS (이벤트 #55, #57, #59에서 14/20/5) | PASS (이벤트 #31에서 전체 3개) |
| 3 | PASS (이벤트 #129에서 전체 3개) | PARTIAL-PASS (이벤트 #45에서 테스트 2+3; 테스트 1 미재실행) |

### Rust 상세 (rep별)

| Rep | Arm A | Arm B |
|-----|-------|-------|
| 1 (Phase-12 파일럿) | PASS (이벤트 #25, exit=0) | PASS (이벤트 #31, exit=0) |
| 2 | PASS (이벤트 #21, exit=0) | PASS (이벤트 #37, exit=0) |
| 3 | PASS (이벤트 #21, exit=0) | PASS (이벤트 #45, exit=0) |

(출처: `CAPTURE-MANIFEST.md` §"F# 정규 통과 상세", §"Scala 정규 통과 상세", §"Rust 정규 통과 상세")

---

## 5. 해석

### F# — OOD 주도, 혼합/불확정 결과

F# FsLex/FsYacc는 35B에게 분포 외(OOD) 도메인이다. 6번의 실행 중 5번이 Arm에 관계없이 실패했다. Arm A run-1(단일 실행)의 PASS는 전문가 계획이 OOD 태스크 탐색에 도움이 될 수 있음을 보여준다 — Claude의 계획에 담긴 단계별 FsLex/FsYacc 배선 세부사항이 그 한 번의 성공을 유도했을 가능성이 있다. 그러나 전체 패턴은 OOD 특성이 지배적이다. Arm A가 더 낫다고 결론 짓는 것은 단일 관찰을 과도하게 해석하는 것이다.

### Scala — 두 Arm 모두 대체로 성공; 해석 상 교란 변수

Scala (분포 내)에서는 두 Arm 모두 대체로 성공했다. Arm A: 3/3 PASS. Arm B: 2/3 PASS + 1 PARTIAL-PASS. Arm A의 오류 수정 사이클 중앙값이 더 높았다 (6회 vs 2회). Arm B의 벽시계 시간은 Arm A보다 훨씬 길었지만 (중앙값 936s vs 346s), 이 차이는 거의 전적으로 실행 순서 캐시 온도 차이로 설명되며 계획 품질 신호가 아니다. 두 Arm이 모두 올바른 결과로 수렴했다. Arm B의 자체 계획이 파서 아키텍처(expr/term/factor 계층)를 명시적으로 식별한 것은 Scala가 35B의 분포 내에 있음을 보여준다.

### Rust — 양 Arm 동점; 의미 있는 차이 없음

Rust (분포 내)에서 두 Arm 모두 3/3 PASS, 오류 수정 사이클 0회. 벽시계 차이(Arm A 48s vs Arm B 67s)는 실행 순서 캐시 온도 차이를 반영하며 계획 품질 신호가 아니다. n=3 수준에서 의미 있는 Arm 간 차이가 없다.

### 전체 요약

세 패턴 모두를 함께 보고한다 — 하나만 선택하지 않는다:

- **F#:** 결과가 혼합/불확정이다. OOD 특성이 두 Arm의 성과를 지배했다. 전문가 계획이 1번의 실행에서 OOD 탐색에 도움이 됐을 가능성이 있으나, 5/6 실행이 실패했다.
- **Scala:** 두 Arm 모두 대체로 성공했다 (in-distribution). n=3, 단일 PARTIAL-PASS 차이 수준에서 전문가 계획의 관찰 가능한 이점이 없다.
- **Rust:** 동점 (both 3/3, 오류 수정 없음). 전문가 계획이 인-분포 태스크에서 관찰 가능한 효과를 내지 않았다.

**전반적 결론:** 전문가 계획은 OOD 태스크에서 한 번의 F# 실행을 탐색하는 데 도움이 됐을 가능성이 있다. 인-분포 태스크에서는 n=3 수준에서 관찰 가능한 체계적 이점이 없었다. 이 결과는 혼합적이며 불확정적이다 — 체계적인 Arm A 우위의 증거로 해석해서는 안 된다.

---

## 6. 후속 실험: Arm C — GSD 계획의 코드 없는 버전 (2026-06-04)

위 §1–5의 2-Arm 연구(Arm A 전문가 계획 vs Arm B 자체 계획)가 완료된 후 한 가지 후속 질문이 제기됐다: **전문가 계획을 "사람이 손으로" 작성하는 대신, 구조화된 다중 에이전트 파이프라인(research → plan → verify)으로 생성하면 어떻게 되는가?** 이를 위해 GSD(Get-Shit-Done) 워크플로의 실제 계획 에이전트를 돌려 세 번째 계획을 만들었고, 이를 **Arm C**라 부른다.

이 절은 세 예제 모두(Rust=§6.1–6.7, F#·Scala=§6.8)에 대한 **n=1 단독 보충 캡처**다. §1–5의 본 연구(2026-06-02 캡처, n=3)와는 별개이며, 캐시 온도·실행 순서가 통제되지 않았으므로 **타이밍을 Arm A/B와 직접 비교할 수 없다**. 이 캡처가 답하는 질문은 타이밍 경쟁이 아니라 **"실패 모드를 알려주되 코드를 주지 않는 전문가 계획으로 35B가 과제를 스스로 작성해 통과시킬 수 있는가?"** 라는 feasibility 질문이다. (§6.1–6.7은 Rust 사례로 방법을 상술하고, §6.8이 F#·Scala로 확장하며, §6.9는 정반대 대조 — GSD 플랜을 **코드까지 그대로** 넘기는 Arm C-orig — 로 4-조건 매트릭스를 완성한다.)

### 6.1 동기 — GSD 원본 계획은 정답 코드를 포함한다

GSD 파이프라인(gsd-phase-researcher → gsd-planner → gsd-plan-checker)을 Rust 과제에 돌린 결과, 계획(`01-PLAN.md`)의 구현 단계에 **검증된 ~25줄 Rust 레퍼런스 구현 전체가 그대로 임베드**됐다. 이 원본 계획(이하 **Arm C-orig**)을 그대로 35B에 주면 모델은 코드를 복붙만 하게 되어, "전문가 계획이 35B의 *작성·실행*을 돕는가"라는 독립 변수가 무너진다 — 즉 **본 연구의 측정 도구로 부적합**하다.

따라서 GSD 계획을 **코드 없는 mechanical 버전(이하 Arm C-mech)**으로 변환했다. 이것이 본 절의 Arm C다. 정보량 그라디언트는 다음과 같이 정렬된다:

| 조건 | 전문가 계획 | 실패 모드 가이드 | 정답 코드 | study 사용 가능 |
|------|:---:|:---:|:---:|:---:|
| Arm B (자체 계획) | ✗ | ✗ | ✗ | ✓ (baseline) |
| Arm A (구조만) | ✓ | ✗ | ✗ | ✓ |
| **Arm C-mech** | ✓ | **✓** | ✗ | ✓ |
| Arm C-orig (GSD 원본) | ✓ | ✓ | **✓** | ✗ (복붙) |

→ **Arm A vs Arm C-mech**은 "코드 없음"을 고정한 채, 전문가 계획에 **실패 모드 사전 경고**를 더하는 것의 가치만 분리해 보는 깔끔한 대조다.

### 6.2 GSD 파이프라인 (research → plan → verify)

실제 GSD 에이전트를 순서대로 실행했다:

1. **Research** (gsd-phase-researcher) → `RESEARCH.md` (confidence HIGH). std-only HTTP 서버 관용구와 5가지 함정을 카탈로그화: (1) Content-Length / Connection: close 누락 시 `curl` 행(hang), (2) 요청을 EOF까지 읽으면 데드락, (3) 재시작 시 EADDRINUSE, (4) 헤더에 CRLF 대신 `\n` 사용 시 curl 거부, (5) 연결당 I/O 패닉이 accept 루프를 죽임.
2. **Plan** (gsd-planner) → `01-PLAN.md` (3 태스크: scaffold / implement / test; frontmatter·must_haves 포함).
3. **Verify** (gsd-plan-checker) → **VERIFICATION PASSED** (1회 통과; 비-blocking 관찰 2건 지적: curl 출력의 trailing newline 엄격 미검증, IPv6-localhost 엣지케이스).

### 6.3 코드 없는 변환 (mechanical strip)

GSD `01-PLAN.md`를 다음 규칙으로 변환했다 (전체 기록: `gsd-mechanical-plan.md`):

| 처리 | 내용 |
|------|------|
| **제거** | Rust 소스 전체; 정답 응답 바이트열(`HTTP/1.1 200 OK\r\nContent-Length: 6\r\n…`); std API 이름(`TcpListener::bind`, `read_line`, `write_all` 등); 리터럴 `Content-Length: 6` → "본문 바이트 길이와 일치하는 값" |
| **보존** | GSD의 3-태스크 구조; 범위 통찰("모든 요청에 동일 응답 → 파싱·라우팅·스레딩 만들지 마라"); 5가지 함정을 **HTTP 프로토콜 요구사항·실패 모드 prose**로 |
| **변환** | "이 코드를 써라" → "이 동작을 만족시켜라" (예: `write_all("HTTP/1.1…")` → "올바른 HTTP/1.1 메시지: 상태줄·헤더·빈 줄·본문; 헤더는 CRLF로 종료") |

제어 블록은 본 연구의 캐노니컬 블록과 **byte-identical**임을 diff로 증명했다 (`PROMPT-DIFF.txt` → `CONTROL-BLOCK SYMMETRY: PASS`) — Arm A/B와 동일한 METH-01 대칭 게이트.

### 6.4 Arm C 계획 요약

> **Arm C 계획 요약 (출처: `arm-c/planning-artifact/oh-prompt.txt`, `gsd-mechanical-plan.md`)**
>
> - Step 1: Scaffold — `cargo init` (디렉토리가 이미 존재); Cargo.toml/src/main.rs 생성 확인; **[dependencies] 비어 있음** 확인
> - Step 2: 서버 작성 — *모든 코드를 직접 작성* (요구사항만 제시, 소스 없음). 범위: 모든 요청에 동일 응답, 파싱·라우팅·스레딩 만들지 말 것. HTTP 요구사항: well-formed HTTP/1.1, 헤더는 CRLF, 본문 끝을 알 수 있게(Content-Length=본문 길이 / Connection: close). 루프: 포트는 루프 전 1회 바인드, accept 루프는 스스로 종료하지 않고 단일 불량 연결에서 살아남을 것, 요청을 EOF까지 읽지 말 것(데드락)
> - Step 3: 빌드 및 테스트 — `cargo build`; 오류 시 컴파일러 메시지 읽고 수정·재빌드 반복; 서버 실행 후 `curl` 2회(루프 확인); 정확한 출력·exit code 보고

### 6.5 35B 캡처 결과 (Phase 15)

단일 OpenHands 호출, 격리된 빈 워크스페이스, 본 연구와 동일한 절차·플래그로 실행했다 (2026-06-04, 13:21:59 → 13:23:10 settle).

| 지표 | Arm C (mechanical), n=1 |
|------|--------------------------|
| TerminalActions 수 | 17 |
| 총 이벤트 수 | 36 (MessageEvent:2, ActionEvent:17, ObservationEvent:17) |
| 벽시계 시간 (초) | 66.09 *(Arm A/B와 비교 불가 — §6.7 caveat)* |
| 평균 LLM 호출 간격 (초) | 2.65 (1.14–6.35) |
| 오류 수정 사이클 수 | 3 |
| TaskTracker 관찰/액션 이벤트 수 | 0 / 0 (제공된 계획 실행 — 자체 계획 안 함) |
| 정규 테스트 (curl_hello) | **PASS** (이벤트 #31, exit 0); 2번째 요청도 통과 (루프 생존) |
| Honesty gate (source=agent) | **PASS** (17/17 ActionEvent, 위반 0) |
| Cargo.toml [dependencies] | 비어 있음 (std-only ✓) |

**오류 수정 3건 (모두 실제 self-correction):**

- #11→#12: `cat -A` 잘못된 플래그(macOS) → 평범한 `cat`으로 복구. 코드 오류 아님.
- #15→#16 (exit 101): 미사용 import 컴파일 오류 → `main.rs` 재작성으로 제거.
- #21→#22 (exit 101): `error[E0599]: no method` — `Read` 트레이트 미import 상태로 `.read()` 호출 → `use std::io::{Read, Write}` 추가로 수정.

### 6.6 에이전트가 작성한 소스 — unaided 작성 확인

35B가 작성한 최종 `src/main.rs`는 코드 없는 프롬프트가 **의도적으로 숨긴 GSD 레퍼런스와 다르다**:

| 측면 | GSD 레퍼런스 (숨김) | 35B 작성 (Arm C-mech) |
|------|---------------------|------------------------|
| 요청 읽기 | `BufReader::read_line` | `stream.read(&mut [0u8; 1024])` (고정 버퍼) |
| 바인드 주소 | `127.0.0.1:8080` | `0.0.0.0:8080` |
| 오류 처리 | `main -> io::Result<()>` + `?` | `.expect(...)` |
| 응답 프레이밍 | CRLF + Content-Length + Connection: close | **동일 — 정확히 적용** |

→ 35B는 prose 함정 가이드를 자신만의 std-only Rust로 번역했다. 프레이밍 가이드는 정확히 적용되어(curl 행·데드락 없음) 통과했고, 막힌 곳은 평범한 Rust 컴파일 오류 2건뿐이었으며 스스로 수정했다. **복붙이 아닌 자체 작성**이다.

### 6.7 해석 및 주의사항

- **무엇을 보여주는가:** 정답 코드를 주지 않고 *실패 모드만* 알려주는 전문가 계획으로도, 35B가 std-only Rust HTTP 서버를 스스로 작성해 정규 테스트를 통과했다. Rust가 35B의 분포 내(in-distribution) 도메인이라는 §5(Rust) 관찰과 일관된다.
- **무엇을 보여주지 않는가 (caveat):** 이것은 **n=1 단독 캡처**다. Arm A/B(2026-06-02, n=3)와 카운터밸런스되지 않았고 프록시 캐시 상태가 다르므로 **벽시계·LLM 간격을 Arm A/B와 비교해서는 안 된다**. "Arm C가 더 낫다/나쁘다"는 결론을 내릴 수 없으며, feasibility 관찰일 뿐이다. 정량 비교에는 n>1과 카운터밸런스된 실행 순서가 필요하다.
- first run이 곧 the run이다 — 재실행·cherry-pick·에이전트 소스 수동 수정 없음. honesty gate PASS로 확인.

(출처: `.planning/milestones/v1.5-phases/15-arm-c-mechanical-capture/15-CAPTURE-MANIFEST.md`)

### 6.8 F# + Scala 확장 (Phase 16) — Arm C 3-언어 비교

Rust(§6.1–6.7)에 이어 **F#과 Scala**에도 같은 절차를 적용했다: GSD 파이프라인(research→plan→verify, 둘 다 PASS) → 코드 없는 mechanical 변환(control-block symmetry 둘 다 PASS) → 35B 캡처(각 n=1, 2026-06-04).

**정규 테스트 결과 — Arm A/B/C 3-arm 비교:**

| 예제 | Arm A (Claude 계획, n=3) | Arm B (자체 계획, n=3) | **Arm C-mech (GSD 코드없음, n=1)** |
|------|--------------------------|------------------------|------------------------------------|
| F# (OOD) | 1/3 PASS | 0/3 PASS | **FAIL** |
| Scala (in-dist) | 3/3 PASS | 2/3 + 1 PARTIAL | **PASS** (14/20/5) |
| Rust (in-dist) | 3/3 PASS | 3/3 PASS | **PASS** (§6.5) |

- **F# (OOD): FAIL.** 빌드가 `Lexer.fsl(6): parse error`로 실패 — 35B가 FsLex `.fsl` DSL 문법을 유효하게 작성하지 못했다. 실패 모드를 prose로 상세히 알려줘도 소용없었고, 오히려 두 Phase 13 arm보다 **더 헤맸다**(TerminalActions 213, 오류 수정 37회 vs Arm A 중앙값 80/21). 세션 내 37회 자가 수정으로도 복구하지 못함.
- **Scala (in-dist): PASS.** 35B가 관용적 재귀 하향 계산기(while-loop 좌측 폴드)를 직접 작성, 3/3 통과; 풋프린트는 Arm A와 유사(TerminalActions 37, 오류 수정 2회). 호스트 재실행으로 14/20/5 확인.

**해석:** 실패 모드를 알려주되 코드를 숨기는 전문가 계획(Arm C-mech)은 Arm A와 같은 패턴을 보인다 — **in-distribution(Rust·Scala)에서는 35B를 성공시키지만 OOD(F# FsLex/FsYacc)는 끝내 넘기지 못한다.** 병목은 계획 품질이 아니라 모델이 DSL 문법 자체를 쓸 수 없다는 점이다. **"크기가 아니라 분포"** 명제가 Arm C(코드 없는 전문가 계획) 축에서도 확인된다.

> **주의 (필독):** Arm C 캡처는 모두 **n=1 단독**이며 Phase 13(n=3, 2026-06-02)과 카운터밸런스되지 않았다 — **타이밍/풋프린트를 arm 간 정량 비교해서는 안 되며** PASS/FAIL feasibility 관찰로만 읽어야 한다. 측정 도구(canonical detector)는 Phase 12 버전이 Scala를 오채점하여 **수정된 Phase 13 extractor로 재채점**했고, 두 결과 모두 호스트에서 ground-truth 검증했다.

(출처: `.planning/milestones/v1.5-phases/16-fsharp-scala-gsd-mechanical-arm-c/16-CAPTURE-MANIFEST.md`)

### 6.9 대조 실험: Arm C-orig — GSD 플랜을 코드까지 그대로 넘기면? (Phase 17)

§6.1–6.8의 Arm C-mech는 GSD 플랜에서 **코드를 지운** 버전이었다. 그 정반대로, GSD 플랜을 **레퍼런스 코드까지 그대로** OpenHands 프롬프트로 변환해(`.fsl`/`.fsy`/`.fsproj`/`main.rs`/`Calc.scala` 전부 포함) 35B에 넘기면 어떻게 되는지 캡처했다(2026-06-04, n=1). 진단 질문: **코드를 떠먹이면 F#이 FAIL→PASS로 뒤집히는가?** (= OOD 병목이 "계획 못 따름"인지 "DSL 문법을 못 씀"인지 판별)

**핵심 결과 — F#이 뒤집힌다:**

| F# 조건 | 코드 제공 | 결과 | 오류 수정 사이클 |
|---------|:---------:|------|:----------------:|
| Arm C-mech (§6.8) | ✗ (실패모드 가이드만) | **FAIL** (빌드 실패) | 37 (헛돔) |
| **Arm C-orig (§6.9)** | ✓ (`.fsl`/`.fsy` 전체) | **PASS 3/3** (14/20/5) | 4 (사소한 전사 수정) |

→ 35B가 F#에서 실패한 이유는 **계획을 못 따라서가 아니라 FsLex/FsYacc DSL 문법 자체를 쓸 수 없어서**다. 정확한 `.fsl`/`.fsy` 텍스트를 받아 옮기게 하니 4번의 작은 heredoc 수정만으로 빌드·통과했다(직접 써야 했을 땐 37번 헛돌고 실패).

**전체 4-조건 비교 (정규 테스트 통과):**

| 예제 | Arm A (n=3) | Arm B (n=3) | Arm C-mech 코드없음 (n=1) | Arm C-orig 코드포함 (n=1) |
|------|-------------|-------------|---------------------------|---------------------------|
| F# (OOD) | 1/3 | 0/3 | **FAIL** | **PASS** |
| Scala (in-dist) | 3/3 | 2/3+P | PASS | PASS (오류 수정 0) |
| Rust (in-dist) | 3/3 | 3/3 | PASS | 미완(하니스 버그)\* |

\* **Rust = INCOMPLETE (모델 결과 아님):** 두 번의 시도 모두 OpenHands `ConversationErrorEvent code=MissingStyle`로 중단됐다 — 프롬프트에 박힌 GSD verify 명령 `awk '/^\[dependencies\]/...'`의 백슬래시를 OpenHands CLI가 색상 코드로 잘못 파싱하는 렌더링 버그다. 에이전트가 scaffold 단계를 못 벗어남. **task/모델 실패가 아니므로 PASS/FAIL 미채점.** (Rust는 어차피 코드 없이도(§6.5) 통과하는 가장 덜 흥미로운 cell.)

**해석 — "분포가 아니라 크기" 명제의 첨예화:**
- **in-distribution(Rust·Scala):** 모든 조건이 성공 — 코드 없는 자체 계획(Arm B)조차. 전문가 계획·코드가 추가하는 관찰 가능 이점이 없다(이미 능력이 있음).
- **OOD(F#):** 가르는 선은 **계획 품질이 아니라 코드**다. 코드 없는 모든 조건(Arm B 0/3, Arm C-mech FAIL)은 실패하고, 리터럴 DSL 소스를 떠먹이는 Arm C-orig만 통과한다.
- → OOD DSL에서는 *아무리 좋은 계획*(GSD급·실패모드 인지·코드 없음)으로도 격차를 못 메우고, **오직 코드를 넘길 때만** 통과한다 — 그런데 그건 능력이 아니라 **전사(transcription)**다. 이것이 곧 **Arm C-orig가 측정 도구로 무효한 이유**를 실증한다(정답을 떠먹이므로 능력이 아니라 베껴쓰기를 측정).

> **주의:** Arm C-orig는 **정답 코드를 제공**하는 진단용 캡처이지 능력 측정이 아니다. n=1 단독, Phase 13과 카운터밸런스되지 않음 — 타이밍 비교 불가. 모든 캡처 honesty gate PASS, ground-truth 호스트 검증.

(출처: `.planning/milestones/v1.5-phases/17-arm-c-orig-full-plan-capture/17-CAPTURE-MANIFEST.md`)

---

## 7. 출처 (Sources)

아래는 이 부록의 모든 수치와 주장이 직접 인용한 커밋된 아티팩트 목록이다:

- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/CAPTURE-MANIFEST.md` — 이벤트 번호(1-based), 프레이밍 규칙, 6셀 테이블, 타이밍 주의, Capture Gate 결과
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/comparison.json` — F# P1/P2 중앙값/최솟값/최댓값 지표 (n=3)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/scala/comparison.json` — Scala P1/P2 중앙값/최솟값/최댓값 지표 (n=3)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/comparison.json` — Rust P1/P2 중앙값/최솟값/최댓값 지표 (n=3)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/PLAN-COMPARISON-QUALITATIVE.md` — ANAL-02 정성적 계획 비교
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-a/planning-artifact/claude-plan.md` — F# Arm A Claude 계획 (5단계)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-b/planning-artifact/oh-self-plan.md` — F# Arm B 자체 계획 (이벤트 #4)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/scala/arm-a/planning-artifact/claude-plan.md` — Scala Arm A Claude 계획 (3단계)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/scala/arm-b/planning-artifact/oh-self-plan.md` — Scala Arm B 자체 계획 (이벤트 #6)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/arm-a/planning-artifact/claude-plan.md` — Rust Arm A Claude 계획 (3단계)
- `.planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/arm-b/planning-artifact/oh-self-plan.md` — Rust Arm B 자체 계획 (이벤트 #4)

**§6 Arm C (GSD mechanical) 후속 실험:**

- `.planning/milestones/v1.5-phases/15-arm-c-mechanical-capture/15-CAPTURE-MANIFEST.md` — Arm C 캡처 정본 (실행 조건, honesty gate, 오류 수정 상세, unaided 작성 확인, caveat)
- `.planning/milestones/v1.5-phases/15-arm-c-mechanical-capture/15-SUMMARY.md` — Phase 15 요약
- `.../15-arm-c-mechanical-capture/captured-planning/rust/arm-c/metrics.json` — Arm C P1/P2 지표 (n=1; curl_hello PASS 이벤트 #31, honesty PASS)
- `.../arm-c/planning-artifact/gsd-mechanical-plan.md` — 코드 없는 변환 기록 (제거/보존/변환 규칙)
- `.../arm-c/planning-artifact/oh-prompt.txt` — Arm C 단일 세션 프롬프트 (제어 블록 + 코드 없는 단계)
- `.../arm-c/planning-artifact/PROMPT-DIFF.txt` — 제어 블록 대칭 증거 (CONTROL-BLOCK SYMMETRY: PASS)
- `.../arm-c/planning-artifact/RESEARCH.md` · `gsd-01-PLAN.md` — GSD 파이프라인 원본 산출물 (리서치·계획)
- `.../arm-c/final-source/src/main.rs` — 35B가 직접 작성한 Rust 서버 소스

**§6.8 Arm C — F# + Scala 확장 (Phase 16):**

- `.planning/milestones/v1.5-phases/16-fsharp-scala-gsd-mechanical-arm-c/16-CAPTURE-MANIFEST.md` — F#/Scala Arm C 캡처 정본 (3-arm 비교표, 오채점→수정 detector 재채점, ground-truth 검증, caveat)
- `.../16-.../16-SUMMARY.md` — Phase 16 요약
- `.../16-.../captured-planning/{fsharp,scala}/arm-c/metrics.json` — 재채점 지표 (Scala PASS 3/3; F# FAIL)
- `.../{fsharp,scala}/arm-c/planning-artifact/{RESEARCH.md, 01-PLAN.md, oh-prompt.txt, PROMPT-DIFF.txt}` — GSD 원본 산출물 + 코드 없는 프롬프트 + 대칭 증거
- `.../{fsharp,scala}/arm-c/final-source/` — 35B가 직접 작성한 소스 (Scala Calc.scala PASS; F# Lexer.fsl/Parser.fsy 등 — 빌드 실패)
- `.../{fsharp,scala}/arm-c/test-output.txt` — fresh host ground-truth (Scala 14/20/5 PASS; F# build FAIL)

**§6.9 Arm C-orig — GSD 플랜 코드 포함 (Phase 17):**

- `.planning/milestones/v1.5-phases/17-arm-c-orig-full-plan-capture/17-CAPTURE-MANIFEST.md` — Arm C-orig 정본 (F# FAIL→PASS flip, 4-조건 매트릭스, Rust 하니스 버그 disclosure)
- `.../17-.../17-SUMMARY.md` — Phase 17 요약
- `.../17-.../captured-planning/{fsharp,scala,rust}/arm-c-orig/{metrics.json, planning-artifact/oh-prompt.txt, final-source/, test-output.txt}` — 코드 포함 프롬프트 + 재채점 지표 + 35B 산출물 + ground-truth (F#/Scala PASS; Rust incomplete)
