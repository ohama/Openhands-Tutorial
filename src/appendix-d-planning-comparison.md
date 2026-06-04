# 부록 D: 계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획

이 부록은 v1.4 계획 비교 연구(Planning A/B Study)의 결과를 기록한다. 이 연구의 핵심 질문은 **"전문가가 작성한 계획이 35B의 실행에 도움이 되는가?"** 이다 — Claude가 35B보다 계획을 더 잘 짠다는 주장이 아니다.

**Arm A (전문가 계획 제공):** 프롬프트에 Claude가 작성한 번호 매긴 단계별 계획을 포함시켜 35B가 그 계획에 따라 실행하도록 했다. 두 프롬프트는 동일한 제어 블록(목표, 제약 조건, 정규 테스트)을 공유하며, 유일한 차이는 번호 매긴 계획의 포함 여부다.

**Arm B (자체 계획):** 제어 블록과 목표만 주고, task tracker를 통해 35B가 스스로 계획을 세우고 실행하도록 했다. 계획의 출처(Claude 대 35B)가 독립 변수다.

세 예제(F# FsLex/FsYacc 계산기, Rust HTTP 서버, Scala 3 계산기)에서 각각 두 Arm을 n=3 반복 실행했다. 모든 수치와 주장은 커밋된 `captured-planning/` 아티팩트에서 직접 인용한 것이다.

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

## 6. 출처 (Sources)

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
