# OpenHands 개요

OpenHands는 CodeActAgent를 중심으로 설계된 오픈소스 AI 에이전트 프레임워크입니다. 핵심 설계 원칙은 "코드를 보편적 행동 공간(universal action space)으로 사용한다"는 것입니다. 에이전트는 bash 명령, Python 코드, 브라우저 자동화 스크립트라는 세 가지 형태의 코드로 거의 모든 컴퓨터 작업을 표현할 수 있으며, 이를 통해 수십 가지 도구 스키마를 별도로 정의하지 않아도 됩니다.

## V1 SDK 구조

이 튜토리얼은 OpenHands **V1**(현재 버전)을 기준으로 합니다. V1은 2026년 4월에 deprecated된 V0(모놀리식 sandbox 중심 설계)와 달리, 다음 네 개의 독립 패키지로 구성된 모듈형 SDK입니다:

- **openhands-sdk** — 핵심 Conversation 루프, EventLog, Agent 인터페이스
- **openhands-tools** — CmdRunAction, FileEditAction 등 표준 도구 구현
- **openhands-workspace** — Workspace 추상화 및 DockerWorkspace/LocalWorkspace 구현
- **openhands-agent-server** — CLI·Web UI·HTTP 클라이언트를 위한 서버 레이어

## 주요 컴포넌트 한눈에 보기

OpenHands V1의 핵심 컴포넌트는 다섯 가지이며, 각각은 1부에서 배운 에이전틱 AI 개념과 직접 대응합니다.

```
+-------------------------------------------------------------------+
|                         Conversation                              |
|  (에이전트 루프 소유 -- while not finished: 루프를 실행)          |
|                                                                   |
|   +---------------+   +------------------+   +---------------+   |
|   |     Agent     |   |    EventLog      |   |  LLM(LiteLLM) |   |
|   | (stateless)   |   | (append-only)    |   | (100+ 제공자) |   |
|   +-------+-------+   +------------------+   +-------+-------+   |
|           | step()                                    |           |
|           | ActionEvent emit                          | call()    |
+-------------------------------------------------------------------+
                        | execute_action()
+-------------------------------------------------------------------+
|                        Workspace                                  |
|   +---------------+   +------------------+   +---------------+   |
|   |LocalWorkspace |   | DockerWorkspace  |   |RemoteAPI...   |   |
|   +---------------+   +------------------+   +---------------+   |
+-------------------------------------------------------------------+
```

| 컴포넌트 | 역할 | 1부 용어 대응 |
|----------|------|--------------|
| **Conversation** | `while not finished:` 루프 소유; 상태 관리 | agent loop의 실행 주체 |
| **Agent** | 상태 없음(stateless); `step()` 호출마다 다음 행동 결정 | agent loop 내 추론 단계 |
| **EventLog** | append-only 이벤트 저장소; 삭제 불가 | memory / context |
| **LiteLLM** | 100+ LLM 제공자를 단일 API로 추상화 | LLM abstraction |
| **Workspace** | ActionEvent를 실제로 실행; 결과를 ObservationEvent로 반환 | sandbox / isolation |

각 컴포넌트의 상세 동작은 이어지는 장에서 다룹니다:

- [에이전트 루프 상세](agent-loop.md) — Conversation.step()의 5단계 루프와 EventLog
- [액션과 관찰 타입](actions-observations.md) — ActionEvent/ObservationEvent 타입 목록과 자가 수정
- [런타임과 샌드박스](runtime.md) — DockerWorkspace 내부와 Action Execution Server
- [LLM 연동: LiteLLM](llm-integration.md) — LiteLLM 설정과 로컬 Qwen 연결
