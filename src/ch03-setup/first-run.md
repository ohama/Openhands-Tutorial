# 첫 실행 테스트

이 장은 OpenHands headless 실행을 처음으로 테스트하는 절차를 다룹니다. 검증된 두 가지 확인 태스크(echo ping과 dotnet 버전 확인)를 통해 에이전트 tool-call 경로가 정상인지 검증합니다.

---

## 사전 점검 체크리스트

실행 전 다음 네 가지를 순서대로 확인합니다.

### 1. OpenHands CLI 버전 확인

```sh
openhands --version
```

성공 신호: `OpenHands CLI 1.16.0` 출력.

### 2. litellm proxy + qwen-local 모델 확인

```sh
curl -s 127.0.0.1:4000/v1/models | \
  python3 -c "import sys,json; d=json.load(sys.stdin); ids=[m['id'] for m in d['data']]; print(ids)"
```

성공 신호: `['qwen-local']` 목록에 `qwen-local` 존재.

### 3. Headless echo ping (tool-call 경로 검증)

아래의 "echo ping 실행" 절을 실행하고, JSONL 출력에 `OPENHANDS_PING_OK`가 포함되는지 확인합니다.

성공 신호: ObservationEvent의 content에 `OPENHANDS_PING_OK` 텍스트 존재, exit_code 0.

### 4. Headless dotnet 버전 확인 (host PATH 검증)

아래의 "dotnet 확인 실행" 절을 실행하고, JSONL 출력에 `10.0.` 버전이 포함되는지 확인합니다.

성공 신호: ObservationEvent의 content에 `10.0.203` (또는 유사한 10.0.x 버전) 텍스트 존재.

---

## 작업 디렉터리 준비

headless 실행 결과물을 저장할 디렉터리를 미리 만들어 둡니다.

```sh
mkdir -p /Users/ohama/projs/OpenHandsTests/oh-workdir
```

`OPENHANDS_WORK_DIR` 환경 변수로 이 디렉터리를 에이전트에게 알립니다. 에이전트의 LocalWorkspace PTY는 호스트 사용자의 디렉터리를 그대로 사용합니다.

---

## Echo Ping 실행

에이전트가 실제로 tool call(TerminalAction)을 수행하는지 검증하는 가장 간단한 테스트입니다.

### 실행 명령

```sh
OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" \
LLM_BASE_URL="http://127.0.0.1:4000/v1" \
LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir" \
openhands --headless --json --yolo --override-with-envs \
  -t 'Run the bash command: echo OPENHANDS_PING_OK' \
  2>/Users/ohama/projs/OpenHandsTests/oh-workdir/ping.stderr.log \
  | tee /Users/ohama/projs/OpenHandsTests/oh-workdir/ping.jsonl
```

### JSONL 읽는 법

`--json` 플래그를 사용하면 표준 출력에 한 줄에 하나씩 JSON 이벤트가 출력됩니다. 다음 두 이벤트가 핵심입니다.

**ActionEvent (에이전트가 내린 tool call 결정):**

`"kind": "ActionEvent"`, `"action": {"command": "echo OPENHANDS_PING_OK", "kind": "TerminalAction"}` 를 담은 줄이 등장하면, 에이전트가 LLM을 통해 정확한 명령을 결정했음을 의미합니다.

실제 캡처된 ActionEvent (검증 세션 2026-05-27, ping.jsonl 7번째 줄):

```json
{
  "action": {
    "command": "echo OPENHANDS_PING_OK",
    "kind": "TerminalAction"
  },
  "tool_name": "terminal",
  "kind": "ActionEvent"
}
```

**ObservationEvent (실행 환경의 응답):**

`"kind": "ObservationEvent"`, `"observation": {"content": [{"text": "OPENHANDS_PING_OK"}], "exit_code": 0, "kind": "TerminalObservation"}` 를 담은 줄이 등장하면, 에이전트의 tool call이 실제 호스트 PTY에서 실행되었음을 의미합니다.

실제 캡처된 ObservationEvent (ping.jsonl 8번째 줄, 핵심 필드):

```json
{
  "observation": {
    "content": [{"type": "text", "text": "OPENHANDS_PING_OK"}],
    "exit_code": 0,
    "kind": "TerminalObservation"
  },
  "kind": "ObservationEvent"
}
```

검증 결과: `exit_code: 0`, content text `OPENHANDS_PING_OK` 확인 → **PING PASS**.

---

## dotnet 버전 확인 실행

에이전트 PTY(LocalWorkspace)가 호스트 PATH를 상속하는지 검증합니다.

### 실행 명령

```sh
OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" \
LLM_BASE_URL="http://127.0.0.1:4000/v1" \
LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir" \
openhands --headless --json --yolo --override-with-envs \
  -t 'Run the bash command: dotnet --version' \
  2>/Users/ohama/projs/OpenHandsTests/oh-workdir/dotnet.stderr.log \
  | tee /Users/ohama/projs/OpenHandsTests/oh-workdir/dotnet.jsonl
```

### 검증된 동작

에이전트는 bare `dotnet --version` 명령을 그대로 실행했습니다. PATH fallback(절대 경로 `/opt/homebrew/bin/dotnet` 지정)은 필요하지 않았습니다. 검증 세션에서 LocalWorkspace PTY는 호스트 사용자의 PATH를 상속했고, `/opt/homebrew/bin`이 포함되어 있었습니다.

실제 캡처된 ObservationEvent (dotnet.jsonl, 핵심 필드):

```json
{
  "observation": {
    "content": [{"type": "text", "text": "10.0.203"}],
    "exit_code": 0,
    "kind": "TerminalObservation"
  },
  "kind": "ObservationEvent"
}
```

검증 결과: `exit_code: 0`, content text `10.0.203` 확인 → **DOTNET PASS**.

---

## 실행 시간 참고

이 튜토리얼의 검증 세션(2026-05-27)에서 실측된 소요 시간입니다.

| 태스크 | 시작 → 종료 | 소요 시간 |
|--------|------------|---------|
| echo OPENHANDS_PING_OK | 17:00:13 → 17:00:28 | 15초 |
| dotnet --version | 17:00:45 → 17:00:59 | 14초 |

단일 tool-call의 단순 태스크는 약 15초 내외였습니다. 4부에서 다룰 F# 계산기 예제처럼 계획, 코드 작성, 빌드, 테스트가 연속으로 이루어지는 복잡한 태스크는 tool-call이 여러 번 발생하므로 더 길어질 수 있습니다. headless 실행은 완료될 때까지 터미널을 블록하며, `--timeout` 플래그는 제공되지 않습니다.

---

## 다음 단계

네 가지 체크리스트 항목이 모두 통과되면, 이 환경에서 OpenHands가 로컬 Qwen LLM과 함께 실제 tool call을 수행할 준비가 된 것입니다. 4부에서는 이 검증된 headless 경로를 사용하여 F# FsLex/FsYacc 계산기를 에이전트가 직접 계획하고 구현하는 과정을 살펴봅니다. 4부의 내용은 현재 집필 중입니다.
