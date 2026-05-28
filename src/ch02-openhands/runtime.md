# 런타임과 샌드박스

[핵심 개념과 용어](../ch01-agentic-ai/concepts.md)에서 다룬 'sandbox / isolation' 개념이 OpenHands에서 DockerWorkspace와 Action Execution Server로 구현됩니다. 이 장에서는 Workspace 추상화 구조와 DockerWorkspace 내부 동작을 살펴봅니다.

## Workspace 추상화

OpenHands의 중요한 설계 결정 중 하나는 Agent 코드가 Workspace 구현체와 완전히 분리된다는 점입니다. Agent는 `execute_action(action)`을 호출할 뿐이며, 그 뒤에서 어떤 Workspace가 동작하는지 알지 못합니다. Workspace는 `Conversation` 객체를 생성할 때 주입(inject)됩니다.

이 추상화 덕분에 동일한 에이전트 코드가 세 가지 환경에서 동일하게 동작합니다:

| Workspace | 격리 수준 | 내부 동작 방식 | 사용 목적 |
|-----------|----------|----------------|----------|
| **LocalWorkspace** | 호스트 프로세스 + 파일시스템 | 도구 함수 in-process 직접 호출 | 개발·테스트 — **이 튜토리얼이 사용** |
| **DockerWorkspace** | 컨테이너 + 내부 HTTP 서버 | FastAPI Action Execution Server | `openhands serve` GUI 기본값 · 격리 실행 |
| **RemoteAPIWorkspace** | 네트워크 RPC | HTTP로 원격 에이전트 서버에 전달 | 클라우드·멀티테넌트 |

> 이 튜토리얼은 **LocalWorkspace**를 사용합니다 — 헤드리스 CLI에서 에이전트가 별도 컨테이너 없이 호스트 위에서 직접 도구(bash/파일 편집)를 실행합니다(3부 참고). 아래의 DockerWorkspace 내부 설명은 OpenHands의 **기본 격리 모델**을 이해하기 위한 것으로, 주로 `openhands serve` GUI에서 쓰입니다. LocalWorkspace는 그 격리를 포기하는 대신 설정이 단순하다는 트레이드오프가 있습니다.

## DockerWorkspace 내부

DockerWorkspace를 선택하면 OpenHands는 Docker 컨테이너를 시작하고, 컨테이너 안에서 다음 구성 요소를 실행합니다:

```
OpenHands (호스트 또는 다른 컨테이너)
    |
    | POST /execute_action (JSON)
    v
+---[ Docker 컨테이너 ]-------------------------------------------+
|                                                                  |
|  FastAPI Action Execution Server                                 |
|    - ActionEvent를 JSON으로 수신                                  |
|    - 실행 결과를 JSON ObservationEvent로 반환                     |
|                                                                  |
|  tmux 기반 지속 bash 세션                                        |
|    - cd 상태가 action 사이에 유지됨                              |
|    - CmdRunAction이 이 세션에서 실행                             |
|                                                                  |
|  지속 IPython 커널                                               |
|    - IPythonRunCellAction이 이 커널에서 실행                     |
|    - %pip install 결과가 세션 내내 유지                          |
|                                                                  |
+------------------------------------------------------------------+
```

**핵심 동작 특성:**

- **JSON 프로토콜:** ActionEvent는 JSON POST 본문으로 전송되고, ObservationEvent는 JSON 응답으로 반환됩니다.
- **tmux 세션:** bash 세션이 지속되므로 `cd /some/dir`로 이동한 후 다음 CmdRunAction도 같은 디렉터리에서 실행됩니다.
- **IPython 커널 지속성:** 한 번 `%pip install` 하면 그 패키지가 세션 내내 사용 가능합니다.

## 개념 매핑: sandbox / isolation

**DockerWorkspace + Action Execution Server = 1부의 'sandbox / isolation' 개념**

컨테이너가 호스트 시스템으로부터 에이전트의 행동을 격리합니다. 에이전트가 파일을 삭제하거나 패키지를 설치해도 호스트 환경에 영향을 주지 않습니다.

용어 주의: 이 튜토리얼에서 'workspace'는 V1 SDK의 Workspace 추상화를 가리킵니다. '샌드박스'라는 단어는 격리 환경이라는 일반적 의미로만 사용하며, V0에서 사용하던 모놀리식 컴포넌트 이름과는 무관합니다.
