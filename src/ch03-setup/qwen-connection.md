# 로컬 Qwen 서버 연결

이 장은 OpenHands가 로컬 Qwen LLM 서버를 사용하도록 환경 변수로 설정하는 방법을 다룹니다. `~/.openhands/config.toml` 파일 없이 환경 변수만으로 구성하는 "Mode A" 방식입니다.

---

## 아키텍처 개요

이 튜토리얼의 LLM 스택은 다음과 같이 구성됩니다.

```
OpenHands (CLI 프로세스)
        |
        | HTTP POST /v1/chat/completions
        v
  litellm proxy  (127.0.0.1:4000)   ← launchd com.ohama.litellm
        |
        | model alias: qwen-local
        v
  MLX inference server  (127.0.0.1:8000)   ← launchd com.ohama.qwen36-35b
        |
        | 모델 파일
        v
  /Users/ohama/llm-system/models/qwen36-35b  (Qwen 36B-35B)
```

OpenHands 프로세스는 호스트에서 직접 실행되므로, LLM 엔드포인트는 `127.0.0.1:4000`(loopback)으로 접근합니다. Docker 컨테이너를 경유하지 않기 때문에 `host.docker.internal`이 필요하지 않습니다.

---

## 환경 변수 설정

OpenHands에 LLM을 연결하려면 세 가지 환경 변수가 필요합니다.

| 변수 | 값 | 설명 |
|------|----|------|
| `LLM_MODEL` | `openai/qwen-local` | LiteLLM 제공자 prefix + 모델 alias |
| `LLM_BASE_URL` | `http://127.0.0.1:4000/v1` | litellm proxy endpoint (OpenAI 호환) |
| `LLM_API_KEY` | `dummy` | litellm 인증 없음; 빈 문자열 대신 임의 값 사용 |

### `openai/` prefix의 의미

`LLM_MODEL=openai/qwen-local`에서 `openai/`는 LiteLLM이 사용할 제공자(provider)를 지정합니다. LiteLLM은 이 prefix를 보고 OpenAI 호환 HTTP 포맷으로 요청을 구성합니다. `qwen-local`은 litellm proxy가 `/v1/models`에 노출하는 모델 alias입니다. 이 구조를 사용하면 실제 모델 파일 경로를 노출하지 않고 alias만 지정할 수 있습니다.

---

## 사전 확인: litellm proxy 동작 확인

OpenHands를 실행하기 전에 litellm proxy와 qwen-local 모델이 준비되었는지 확인합니다.

```sh
curl -s http://127.0.0.1:4000/v1/models | \
  python3 -c "import sys,json; d=json.load(sys.stdin); ids=[m['id'] for m in d['data']]; print('MODELS:', ids); assert 'qwen-local' in ids, 'qwen-local MISSING'; print('PASS')"
```

실제 확인된 출력:

```
MODELS: ['qwen-local']
PASS
```

`qwen-local`이 목록에 없으면 `com.ohama.litellm` launchd 에이전트가 실행 중인지 확인합니다(`launchctl list com.ohama.litellm`).

---

## OpenHands 실행 형식

환경 변수는 명령 앞에 인라인으로 지정합니다. **`--override-with-envs` 플래그는 필수**입니다. 이 플래그 없이는 `LLM_*` 환경 변수가 OpenHands에 의해 묵시적으로 무시됩니다.

```sh
OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" \
LLM_BASE_URL="http://127.0.0.1:4000/v1" \
LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/path/to/workdir" \
openhands --headless --json --yolo --override-with-envs \
  -t '태스크 내용'
```

각 플래그의 역할:

- `--headless` — 브라우저 없이 CLI 모드로 실행
- `--json` — 표준 출력에 JSONL 형식 이벤트 출력 (`--headless`와 함께만 동작)
- `--yolo` — 에이전트의 모든 tool call을 자동 승인
- `--override-with-envs` — `LLM_*` 환경 변수를 실제로 적용 (REQUIRED)

---

## 성능 참고

이 튜토리얼의 검증 세션에서 실측된 응답 시간은 다음과 같습니다.

| 태스크 | 실측 소요 시간 |
|--------|---------------|
| `echo OPENHANDS_PING_OK` | 약 15초 |
| `dotnet --version` | 약 14초 |

단순한 단일 tool-call 태스크는 15초 내외였습니다. 복잡한 다단계 빌드(4부의 F# 계산기 예제처럼 여러 tool-call이 순차적으로 발생하는 경우)는 그보다 길어질 수 있습니다. 실행 중에는 터미널이 블록되므로, 긴 태스크의 경우 화면에 출력이 오래 없을 수 있습니다. 이는 정상 동작입니다.

---

다음 장에서는 실제 headless 실행을 테스트하고, 사전 점검 체크리스트를 확인합니다.
