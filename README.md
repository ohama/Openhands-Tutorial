# 에이전틱 AI 튜토리얼: OpenHands로 배우는 AI 에이전트

OpenHands와 로컬 Qwen LLM을 사용하여 **에이전틱 AI(agentic AI)** 를 배우는 한국어 튜토리얼입니다.

📖 **읽기:** https://ohama.github.io/Openhands-Tutorial/

## 이 튜토리얼은 무엇인가

에이전틱 AI가 무엇인지 개념부터 설명한 뒤, **OpenHands**(로컬 Qwen 35B/122B 모델 위에서 동작)가 실제로 F# FsLex/FsYacc 계산기를 만드는 과정을 따라갑니다 — `plan → write → test → run` 루프를 돌며 스스로 빌드 오류를 고치는 모습까지요. v1.1에서는 동일한 과제를 **35B와 122B 두 모델로 모두 실행**한 결과를 부록 C에 비교했습니다(렉서를 모델이 직접 쓸 수 있는지, 오류-수정 사이클 차이, 실측 속도).

핵심 원칙은 **정직한 실제 실행**입니다. 책에 인용된 명령·출력·에러는 모두 실제 OpenHands 세션의 JSONL 로그에서 그대로 가져온 것이며, 꾸며낸 트랜스크립트가 아닙니다. 무엇이 에이전트의 실제 작업이고 무엇이 미리 제공된 스캐폴딩인지도 솔직하게 밝힙니다(예: 35B는 `.fsl` 렉서를 스캐폴딩으로 제공받았지만 122B는 무지원으로 직접 작성했다는 점을 부록 C 첫 절에서 명시).

각 실행 사이클은 초보자도 흐름을 한눈에 따라갈 수 있도록 **📨 사용자 프롬프트 (User prompt) → ⚙️ 내부 프로세스 (Process) → ✅ 결과 (Result)** 콜아웃 패턴으로 표시했습니다.

## 구성

- **1부 — 에이전틱 AI란 무엇인가:** 반응형 챗봇과의 차이, 핵심 용어(tool calling, agent loop, plan→write→test→run, memory/context)
- **2부 — OpenHands 아키텍처:** V1 SDK의 step() 루프, EventLog, 액션/관찰, 워크스페이스, LiteLLM
- **3부 — 환경 설정:** OpenHands 설치, 로컬 Qwen 서버 연결, 첫 실행 테스트
- **4부 — OpenHands로 F# 계산기 만들기:** 실제 캡처된 실행의 단계별 워크스루(개념↔행동 콜아웃, 에러-수정 서사, 최종 소스, 검증)
- **5부 — 정리와 심화**
- **부록 A — 재현 가이드** / **부록 B — 트러블슈팅** / **부록 C — 모델 비교(35B vs 122B)** *(v1.1 추가)*

## 로컬에서 빌드하기

[mdBook](https://rust-lang.github.io/mdBook/)으로 작성되었습니다.

```bash
# mdBook 설치 (macOS)
brew install mdbook

# 로컬 미리보기 (http://localhost:3000)
mdbook serve --open

# 정적 사이트 빌드 (book/ 에 생성)
mdbook build
```

원본 마크다운은 `src/`에, 목차는 `src/SUMMARY.md`에 있습니다.

## 배포

`main` 브랜치에 push하면 GitHub Actions 워크플로(`.github/workflows/deploy.yml`)가 `mdbook build`를 실행하고 GitHub Pages로 자동 배포합니다.

## 비고

- 이 튜토리얼이 사용한 실제 환경: 헤드리스 macOS(SSH) + **Colima**, OpenHands 1.16 헤드리스 CLI(**LocalWorkspace**), 로컬 **litellm 프록시**(`openai/qwen-35b` / `openai/qwen-122b` @ `127.0.0.1:4000`), 호스트의 .NET 10.
- 실제 측정된 LLM 호출 1회 평균은 **35B ≈ 5.3초**(67 TerminalAction / 356초), **122B ≈ 6.3초**(150 TerminalAction / 1229초)입니다. v1 단계에서 한 차례 추정했던 "약 14–32초/사이클"은 사전 예측치였고 실측값과 다르다는 점을 부록 C에서 함께 정정합니다.
- `.planning/`에는 이 책이 만들어진 전체 과정(계획·연구·검증, 실패했던 첫 시도 기록 포함)과 v1.1 마일스톤 감사 보고서(`v1.1-MILESTONE-AUDIT.md`)가 그대로 공개되어 있습니다 — 정직성이라는 이 프로젝트의 핵심 가치를 따른 것입니다.
