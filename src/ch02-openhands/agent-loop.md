# 에이전트 루프 상세

[핵심 개념과 용어](../ch01-agentic-ai/concepts.md)에서 정의한 **agent loop**를 OpenHands는 `Conversation.step()`의 `while not finished:` 루프로 구현합니다. 이 step() 루프가 곧 1부에서 말한 agent loop입니다. 이 장에서는 그 루프가 내부적으로 어떤 5단계를 거치는지, 그리고 EventLog가 어떤 역할을 담당하는지 살펴봅니다.

## 5단계 루프

`Conversation` 객체는 매 반복(iteration)마다 정확히 다섯 단계를 순서대로 실행합니다.

```
while not finished:
    |
    +-- Phase 1: DRAIN PENDING ACTIONS
    |       사용자가 확인(confirm)한 대기 중인 action을 먼저 실행
    |       (WAITING_FOR_CONFIRMATION 상태의 action을 execute로 전환)
    |
    +-- Phase 2: HONOR USER BLOCKS
    |       사용자가 현재 메시지를 거부(reject)했으면 정책에 따라 중단 또는 재시도
    |
    +-- Phase 3: PREPARE LLM PROMPT
    |       1. EventLog에서 LLMConvertibleEvent만 필터링
    |       2. llm_response_id 기준으로 ActionEvent 묶기 (병렬 tool call 지원)
    |       3. 이벤트를 LLM 메시지 형식으로 변환
    |          (system / user / assistant / tool 역할)
    |       4. 이벤트 수가 임계값(기본 80개) 초과 시 condensation 트리거
    |
    +-- Phase 4: CALL LLM WITH RETRY
    |       LiteLLM이 변환된 메시지를 설정된 모델 엔드포인트로 전송
    |       컨텍스트 창 초과(overflow)를 명시적으로 처리; retry 포함
    |
    +-- Phase 5: CLASSIFY AND DISPATCH
            LLM 응답 파싱:
            - tool call  --> ActionEvent 생성 --> Workspace.execute_action() 호출
                            실행 결과 ObservationEvent를 EventLog에 append
            - 텍스트만   --> MessageEvent를 EventLog에 append
```

### 단계별 설명

**Phase 1 (DRAIN):** 이전 반복에서 사용자 확인을 기다리던 action이 있으면 먼저 처리합니다. 대부분의 자율 실행에서는 즉시 통과합니다.

**Phase 2 (USER BLOCK):** 사용자가 현재 진행을 거부했으면 루프를 멈추거나 재시도 정책을 따릅니다.

**Phase 3 (PREPARE):** EventLog 전체를 LLM에게 보낼 메시지 배열로 변환하는 단계입니다. 이벤트 수가 80개를 넘으면 condensation이 트리거됩니다. Condensation은 중간 구간 이벤트를 LLM이 요약한 `CondensationSummaryEvent`로 압축합니다.

**Phase 4 (CALL LLM):** LiteLLM이 메시지 배열과 도구 스키마를 모델 엔드포인트에 POST합니다. 컨텍스트 창이 넘치면 그에 맞게 처리하고, 일시적 오류는 retry합니다.

**Phase 5 (CLASSIFY & DISPATCH):** LLM 응답에 tool call이 포함되면 ActionEvent로 변환해 Workspace에 전달합니다. Workspace가 실행을 마치면 결과를 ObservationEvent로 EventLog에 추가합니다. 응답이 텍스트만이면 MessageEvent로 기록합니다.

## 루프 종료 조건

다음 세 가지 조건 중 하나가 충족되면 루프가 종료됩니다:

1. Agent가 `AgentFinishAction`을 emit — 작업이 완료되었다고 판단
2. 반복 횟수 또는 비용 예산 초과 — `Conversation`에 설정된 상한선 도달
3. 복구 불가능한 오류 — 재시도로 해결할 수 없는 치명적 실패

## EventLog: 메모리와 컨텍스트의 구현체

EventLog는 agent-환경 간 모든 상호작용을 기록하는 **append-only** 이벤트 저장소입니다. 이벤트는 절대 삭제되지 않습니다.

- **불변성:** 한번 기록된 이벤트는 수정하거나 삭제할 수 없습니다.
- **Condensation:** 이벤트 수가 80개(기본값)를 초과하면, 중간 구간을 LLM으로 요약해 `CondensationSummaryEvent`를 생성합니다. 원본 이벤트는 "forgotten"으로 표시될 뿐 삭제되지 않아 결정론적 재생(replay)이 가능합니다.
- **두 범주:** LLM에게 전송되는 **LLM-visible 이벤트** (SystemPromptEvent, MessageEvent, ActionEvent, ObservationEvent, AgentErrorEvent, CondensationSummaryEvent)와 프레임워크 내부용 **internal 이벤트** (ConversationStateUpdateEvent 등)로 나뉩니다.

1부에서 설명한 'memory/context' 개념이 OpenHands에서 EventLog와 condensation으로 구현됩니다. 긴 F# 계산기 작업처럼 수십 번의 반복이 필요한 경우, condensation 덕분에 컨텍스트 창 한도를 초과하지 않고 작업을 이어갈 수 있습니다.
