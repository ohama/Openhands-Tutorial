# 액션과 관찰 타입

[핵심 개념과 용어](../ch01-agentic-ai/concepts.md)에서 배운 'tool calling'과 'observation' 개념이 OpenHands에서 각각 ActionEvent와 ObservationEvent로 구현됩니다. 이 장에서는 그 핵심 사이클과 이 튜토리얼에 등장하는 주요 타입들을 살펴봅니다.

## 핵심 사이클

에이전트와 환경 사이의 모든 상호작용은 다음 세 단계 사이클로 이루어집니다:

```
Agent (step())
    |
    | 1. ActionEvent emit
    |    (예: CmdRunAction, FileEditAction ...)
    v
Workspace.execute_action(action)
    |
    | 2. 실행
    |    (shell 명령, 파일 편집 등)
    v
ObservationEvent
    |
    | 3. EventLog에 append
    v
EventLog (append-only)
    |
    | 4. 다음 Phase 3 PREPARE 때 LLM에 전달
    v
LLM (다음 반복에서 결과를 보고 다음 ActionEvent 결정)
```

이 사이클에서 ActionEvent + LLM에 전달되는 도구 스키마(tool schema)가 1부의 **tool calling** 개념의 OpenHands 구현입니다. ObservationEvent는 1부의 **observation** 개념의 구현입니다.

## 이 튜토리얼의 주요 ActionEvent 타입

F# 계산기를 만드는 과정에서 CodeActAgent는 다음 action 타입들을 사용합니다:

| Action 타입 | 용도 | 생성되는 ObservationEvent |
|-------------|------|--------------------------|
| **CmdRunAction**(command, cwd) | shell 명령 실행 (dotnet build, find, grep 등) | **CmdOutputObservation**: stdout, stderr, exit code |
| **FileWriteAction**(path, content) | 파일 전체 생성 또는 덮어쓰기 | FileWriteObservation |
| **FileEditAction**(path, str_replace) | str_replace 방식 부분 편집 | FileEditObservation: 변경 diff |
| **FileReadAction**(path) | 파일 내용 읽기 | FileReadObservation: 파일 내용 |
| **AgentThinkAction**(thought) | 부수효과 없는 순수 추론 기록 | (없음 — EventLog에만 기록) |
| **AgentFinishAction**(thought, outputs) | 루프 종료 선언 | — |

### ObservationEvent가 담는 것

각 ObservationEvent는 실행 결과를 구조화된 형태로 담습니다:

- `CmdOutputObservation`: stdout 전체 + stderr 전체 + exit code (0이면 성공, 비0이면 오류)
- `FileEditObservation`: 적용된 변경 사항의 diff
- `FileReadObservation`: 파일의 전체 텍스트 내용

## 자가 수정은 기능이 아니라 부수효과

OpenHands의 자가 수정(self-correction) 능력은 별도의 메커니즘이 아닙니다. 관찰 루프의 자연스러운 부수효과입니다.

동작 방식:

1. `CmdRunAction`으로 `dotnet build` 실행
2. 빌드 실패 → `CmdOutputObservation`에 오류 메시지와 `exit code: 1`이 담김
3. ObservationEvent가 EventLog에 append됨
4. 다음 루프 Phase 3에서 이 ObservationEvent가 LLM 메시지에 포함됨
5. LLM이 오류 내용을 보고 수정 `FileEditAction`을 emit
6. 수정된 파일로 다시 `CmdRunAction` 실행

stderr와 exit code가 EventLog에 자동으로 기록되기 때문에, LLM은 다음 프롬프트에서 정확히 무엇이 잘못되었는지 알 수 있습니다. 4부 '빌드와 테스트 단계'에서 F# 계산기를 만들 때 이 사이클이 실제로 일어나는 장면을 볼 수 있습니다.
