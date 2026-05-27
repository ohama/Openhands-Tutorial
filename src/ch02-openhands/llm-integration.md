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

모델 문자열 앞의 `openai/` prefix는 LiteLLM에게 OpenAI 클라이언트 라이브러리를 사용하라고 지시합니다. `<model-id>` 자리에는 서버가 서빙 중인 실제 모델 이름을 넣습니다(예: `openai/qwen35b`). 호스트에서 `curl http://127.0.0.1:8000/v1/models`로 정확한 이름을 확인할 수 있습니다.

### Base URL: `http://host.docker.internal:8000/v1`

OpenHands가 Docker 컨테이너 안에서 실행되므로, 호스트의 MLX 서버에 도달하려면 `host.docker.internal` 호스트명을 사용해야 합니다. `127.0.0.1`은 컨테이너 자신을 가리키므로 사용하면 안 됩니다.

### API Key: 임의의 placeholder 문자열

로컬 MLX 서버는 API 키를 검증하지 않습니다. `local-llm`이나 임의의 문자열을 입력하면 됩니다.

## Function Calling

로컬 Qwen 모델은 네이티브 function calling을 지원하는 것이 확인되었습니다(LLM 응답의 `finish_reason: "tool_calls"`). OpenHands는 이를 통해 ActionEvent를 tool call 형태로 주고받습니다.

비네이티브 모델(function calling을 지원하지 않는 모델)을 위해 `NonNativeToolCallingMixin`이라는 텍스트 기반 폴백도 존재하지만, 이 튜토리얼의 Qwen 설정에서는 필요하지 않습니다.

## 다음 단계

실제 설정 단계(OpenHands GUI에서 Custom Model, Base URL, API Key를 입력하는 방법, MLX 서버 실행 방법)는 3부 '로컬 Qwen 서버 연결'에서 상세히 다룹니다.
