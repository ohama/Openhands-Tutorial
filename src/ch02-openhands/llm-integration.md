# LLM 연동: LiteLLM

1부에서 설명한 'LLM abstraction' 개념이 OpenHands에서 LiteLLM으로 구현됩니다. LiteLLM은 OpenAI, Anthropic, Google, Mistral 등 100개 이상의 LLM 제공자를 단일 Chat Completions API 인터페이스로 추상화합니다. OpenHands는 이 추상화 덕분에 제공자별 코드를 작성하지 않고도 어떤 모델이든 연결할 수 있습니다.

## LiteLLM이 하는 일

```
OpenHands (Conversation.step())
    |
    | messages + tool_schemas
    v
LiteLLM (단일 Chat Completions API)
    |
    +-- openai/...   --> OpenAI 클라이언트 --> GPT-4o, o3 ...
    +-- anthropic/.. --> Anthropic 클라이언트 --> Claude Sonnet ...
    +-- openai/<id>  --> OpenAI 클라이언트 --> 로컬 OpenAI-호환 서버
    |
    v
LLM 응답 (tool_calls 또는 텍스트)
```

제공자 선택은 모델 문자열 앞의 **prefix**로 결정됩니다. 이 튜토리얼에서 사용하는 로컬 Qwen 서버는 OpenAI-호환 API를 제공하므로 `openai/` prefix를 사용합니다.

## 로컬 Qwen 서버 연결 설정 (개념 소개)

이 튜토리얼에서 사용하는 로컬 MLX Qwen 서버를 연결하려면 OpenHands에서 세 가지 값을 설정합니다:

### Custom Model: `openai/<model-id>`

모델 문자열 앞의 `openai/` prefix는 LiteLLM에게 OpenAI 클라이언트 라이브러리를 사용하라고 지시합니다. `<model-id>` 자리에는 엔드포인트가 서빙 중인 실제 모델 이름을 넣습니다. 이 튜토리얼에서는 litellm 프록시가 노출하는 별칭을 사용해 `openai/qwen-local`이 됩니다. `curl http://127.0.0.1:4000/v1/models`로 프록시가 서빙하는 이름을 확인할 수 있습니다.

### Base URL: `http://127.0.0.1:4000/v1`

이 튜토리얼은 OpenHands를 **LocalWorkspace 모드**(헤드리스 CLI)로, 즉 Docker 컨테이너가 아니라 호스트에서 직접 실행합니다. 따라서 LLM 호출도 호스트에서 일어나며 loopback 주소 `127.0.0.1`이 그대로 동작합니다. 포트 `4000`은 호스트의 MLX 서버(`:8000`) 앞단에 있는 litellm 프록시이며, 3부에서 이 2계층 구성(OpenHands → litellm `:4000` → MLX `:8000`)을 자세히 다룹니다.

> 참고: OpenHands를 **Docker 컨테이너 안**(예: `openhands serve` GUI가 쓰는 DockerWorkspace)에서 실행하는 다른 구성에서는, 컨테이너에서 호스트에 닿기 위해 `127.0.0.1` 대신 `host.docker.internal`을 써야 합니다. 이 튜토리얼의 LocalWorkspace 경로에서는 필요하지 않습니다.

### API Key: 임의의 placeholder 문자열

로컬 MLX 서버는 API 키를 검증하지 않습니다. `local-llm`이나 임의의 문자열을 입력하면 됩니다.

## Function Calling

로컬 Qwen 모델은 네이티브 function calling을 지원하는 것이 확인되었습니다(LLM 응답의 `finish_reason: "tool_calls"`). OpenHands는 이를 통해 ActionEvent를 tool call 형태로 주고받습니다.

비네이티브 모델(function calling을 지원하지 않는 모델)을 위해 `NonNativeToolCallingMixin`이라는 텍스트 기반 폴백도 존재하지만, 이 튜토리얼의 Qwen 설정에서는 필요하지 않습니다.

## 다음 단계

실제 설정 단계(환경 변수 `LLM_MODEL` / `LLM_BASE_URL` / `LLM_API_KEY`와 `--override-with-envs`로 헤드리스 CLI를 구성하는 방법, 프록시·MLX 서버 확인 방법)는 3부 '로컬 Qwen 서버 연결'에서 상세히 다룹니다.
