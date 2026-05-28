# 부록 B: 트러블슈팅

이 부록은 OpenHands로 F# 계산기를 실제로 빌드하는 과정에서 **실제로 발생한** 문제들을 정리합니다. 각 항목에는 진단 방법과 수정 방법이 포함되어 있습니다. 마지막 절(§4)에서는 원래 계획에서 예상했지만 이번 실행에서는 발생하지 않은 문제들도 솔직하게 기록합니다 — 예상과 현실이 다를 때 그것을 명확히 남기는 것이 독자에게 더 유용하기 때문입니다.

---

## 1. 환경 문제

### REAL-01: Colima 사용 시 DOCKER_HOST 설정 필요

**무엇이 일어났나**

이 튜토리얼을 실행한 머신은 Docker Desktop이 아니라 **Colima**를 사용합니다. Colima에서는 Docker 소켓이 `/var/run/docker.sock`이 아닌 `/Users/ohama/.colima/default/docker.sock`에 위치합니다. OpenHands는 Docker 데몬에 연결하기 위해 소켓을 찾는데, `/var/run/docker.sock`이 존재하지 않으면 에이전트 서버 이미지를 pull하거나 컨테이너를 시작할 수 없습니다.

**진단**

OpenHands 실행 시 도커 데몬 연결 오류가 나타나거나, `docker` 명령 자체가 소켓을 찾지 못하는 경우:

```bash
docker info
# Error: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
```

**수정**

Colima를 먼저 시작하고, `DOCKER_HOST` 환경 변수를 설정합니다:

```bash
colima start --cpu 4 --memory 8 --disk 60

export DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock
docker info   # 정상적으로 응답하면 OK
```

OpenHands 실행 시 인라인으로 지정할 수도 있습니다:

```bash
DOCKER_HOST="unix:///Users/ohama/.colima/default/docker.sock" \
  openhands --headless --json --yolo --override-with-envs -t "..."
```

**독자를 위한 주의 사항**

- Docker Desktop 사용자는 `/var/run/docker.sock`이 자동으로 생성되므로 이 설정이 필요 없습니다.
- Linux에서는 소켓 경로가 다를 수 있습니다. `docker context inspect` 또는 `docker info | grep -i socket`으로 확인하세요.

---

### REAL-02: `--override-with-envs` 옵션 없이는 LLM_* 환경 변수가 무시됨

**무엇이 일어났나**

`LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`를 환경 변수로 설정해도, OpenHands 헤드리스 모드에서 `--override-with-envs` 옵션 없이 실행하면 이 변수들이 **조용히 무시됩니다**. 에이전트는 시작되지만 LLM 호출이 기본(또는 잘못된) 엔드포인트로 라우팅되어 인증 오류나 연결 거부 오류가 발생합니다. 오류 메시지에는 환경 변수가 무시됐다는 힌트가 없습니다.

**진단**

에이전트가 시작되지만 즉시 LLM 관련 오류가 출력되는 경우:

```
Error: Authentication required
# 또는
Error: Connection refused to http://...
```

환경 변수를 올바르게 설정했음에도 이런 오류가 발생하면 `--override-with-envs` 누락을 의심하세요.

**수정**

항상 `--override-with-envs`를 포함해서 실행합니다:

```bash
LLM_MODEL="openai/qwen-local" \
LLM_BASE_URL="http://127.0.0.1:4000/v1" \
LLM_API_KEY="dummy" \
OPENHANDS_SUPPRESS_BANNER=1 \
openhands --headless --json --yolo --override-with-envs \
  -t "작업 내용..." | tee task.jsonl
```

**openai/ 접두사에 대하여**

`LLM_MODEL` 값은 반드시 `openai/qwen-local` 형식이어야 합니다. `openai/` 접두사가 있어야 LiteLLM이 어떤 provider 어댑터를 사용할지 알 수 있습니다. 접두사 없이 `qwen-local`만 지정하면 LiteLLM이 provider를 인식하지 못해 호출이 실패합니다.

---

### REAL-05: .NET 10 + FsLexYacc 11.3.0 줄 지시자 비호환 — FixLineDirectives 필요

**무엇이 일어났나**

`fslex`와 `fsyacc`가 생성하는 `.fs` 파일에는 `# 0 ""` 형태의 줄 지시자(line directive)가 포함됩니다. F# 10 컴파일러(.NET SDK 10.0.203 포함)는 이 형식의 줄 지시자를 거부하며 `FS0010` 오류를 발생시킵니다. .NET 8에서는 컴파일되던 동일한 문법이 .NET 10에서는 빌드에 실패합니다.

**증상**

Parser.fsy와 Lexer.fsl이 문법적으로 올바른데도 빌드가 실패하는 경우:

```
Parser.fs(1,1): error FS0010: unexpected ... in implementation file
```

**수정**

`calc.fsproj`에 `FixLineDirectives` MSBuild 타깃을 추가해 생성된 `.fs` 파일에서 해당 줄을 제거합니다:

```xml
<Target Name="FixLineDirectives" BeforeTargets="CoreCompile"
        DependsOnTargets="CallFsYacc;CallFsLex">
  <Exec Command="sed -i '' '/^# 0/d' Parser.fs"
        Condition="Exists('Parser.fs')" />
  <Exec Command="sed -i '' '/^# 0/d' Lexer.fs"
        Condition="Exists('Lexer.fs')"  />
</Target>
```

이 타깃은 컴파일 직전에 실행되어 `# 0 ""` 로 시작하는 줄을 모두 삭제합니다. 이후 F# 컴파일러가 정상 처리할 수 있습니다.

**플랫폼 차이**

macOS에서 `sed -i`는 인수가 필요합니다: `sed -i '' '/^# 0/d'`
Linux에서는 인수 없이: `sed -i '/^# 0/d'`

이 튜토리얼의 GitHub Pages 빌드 워크플로우(`ubuntu-latest`)는 mdBook만 빌드하고 F# 프로젝트는 빌드하지 않으므로, 이 수정은 **로컬 개발 환경에만** 해당합니다.

---

## 2. 에이전트 동작 문제

### REAL-03: FsLex 문법이 35B 모델의 학습 데이터 범위 밖 — attempt 1 전체 실패

**무엇이 일어났나**

Qwen2.5-35B 모델은 FsLex(`.fsl`) 문법에 익숙하지 않습니다. FsLex 파일은 `%%` 구분자를 사용하지 않습니다 — 그것은 FsYacc(`.fsy`) 문법입니다. Attempt 1에서 에이전트를 세 번 별도로 실행했지만(94 + 27 + 16 = 137회 TerminalAction), 세 번 모두 유효한 Lexer.fsl 파일을 만들어내지 못했습니다.

**실제 오류 메시지**

```
Lexer.fsl(8): error : Unexpected character '%'
```

에이전트가 FsLex 파일에 `%%`를 추가할 때마다 이 오류가 발생했습니다.

추가로 발생한 문제들:

- `lexeme lexbuf` 함수가 존재하지 않음. 올바른 API는 `LexBuffer<_>.LexemeString lexbuf`
- 헤더 중괄호를 같은 줄에 쓰면(`{ open Parser }`) 생성된 `.fs` 파일에서 2칸 들여쓰기가 발생해 F# light-mode 컴파일 실패

**수정 (attempt 2에서 적용)**

FsLex 파일 내용을 태스크 프롬프트에 직접 제공하고, 에이전트는 parser와 evaluator에만 집중하게 합니다(Deviation Rule 3 적용). 올바른 FsLex 헤더 구조:

```
{
open Parser
open FSharp.Text.Lexing
}

rule tokenize = parse
    | [' ' '\t']      { tokenize lexbuf }
    | ['0'-'9']+      { let s = LexBuffer<_>.LexemeString lexbuf
                        INT (System.Int32.Parse s) }
    | '+'             { PLUS }
    ...
```

**독자를 위한 교훈**

FsLex 문법은 LLM 학습 데이터에서 매우 드뭅니다. 모델이 유효한 `.fsl` 파일을 작성하지 못한다면, 레퍼런스 구현을 프롬프트에 직접 포함시키고 에이전트가 더 잘 아는 영역(parser, evaluator)에 집중하게 하는 것이 효과적입니다.

---

### REAL-04: file_editor 툴 검증 오류 — security_risk 필드 누락

**무엇이 일어났나**

qwen-local 모델이 `file_editor` 또는 `str_replace` 툴을 호출할 때, OpenHands가 요구하는 `security_risk` 필드를 툴 호출 스키마에 포함시키지 않습니다. Attempt 1에서 이 오류가 매번 발생했습니다:

```
Error validating tool 'file_editor': Failed to provide security_risk field in tool 'file_editor'.
```

같은 프롬프트로 재시도해도 결과가 달라지지 않았습니다(task4-evaluator.jsonl과 task4-evaluator-retry1.jsonl 모두 동일 오류).

**원인**

이것은 모델 고유의 동작입니다. qwen-local 모델의 툴 호출 스키마가 `security_risk` 필드를 생략합니다. OpenHands 쪽에서 이 필드를 요구하기 때문에 모든 file_editor 호출이 실패합니다.

**수정**

모든 태스크 프롬프트에 다음 지시문을 추가합니다:

```
IMPORTANT: Create and edit ALL files using ONLY bash shell commands (printf, tee, or
`cat > FILE <<'EOF' ... EOF` with a quoted heredoc). Do NOT use the file_editor /
str_replace tool — it errors in this setup (it requires a security_risk field that
fails validation).
```

Attempt 2에서 모든 태스크 프롬프트에 이 지시문을 포함시킨 결과, file_editor 오류가 단 한 건도 발생하지 않았습니다.

---

## 3. 빌드 오류

### REAL-06: FsYacc %start / %type 문법 오류 + LexBuffer.FromText 존재하지 않음 — 실제 오류-수정 사이클

**무엇이 일어났나**

Attempt 2의 task3(parser 작성)에서 에이전트는 Parser.fsy를 빌드하기까지 네 번의 오류를 거쳤습니다. 이것이 이번 튜토리얼에서 RUN-03으로 기록된 **실제 오류-수정 사이클**입니다(task3-parser.jsonl 이벤트 9–30).

| 시도 | 오류 | 원인 |
|------|------|------|
| 1 | `FSY000: at least one %start declaration is required` | `%type <int> start`는 썼지만 `%start` 선언을 누락 |
| 2 | `Parser.fsy(16,7): error parse error` | `%start <int> start` 형식 사용 — fsyacc는 심볼만 받음 |
| 3 | `Parser.fsy(16,7): error parse error` | 동일한 잘못된 문법으로 다시 시도 |
| 4 | `FS0039: 'LexBuffer<_>' does not define 'FromText'` | `%start` 문법은 마침내 올바르게 수정됐으나 존재하지 않는 API 사용 |

**수정 (이벤트 27–30에서 에이전트가 스스로 수정)**

에이전트는 컴파일러 오류를 읽고, 스스로 올바른 문법을 찾아내 수정했습니다:

1. `%start <int> start` → 두 줄로 분리:
   ```
   %start start
   %type <int> start
   ```

2. `LexBuffer.FromText` → `LexBuffer<char>.FromString`

수정 후 빌드 결과:
```
calc net10.0 성공 (0.7초)
→ bin/Debug/net10.0/calc.dll
```

이 오류-수정 과정의 상세한 서술은 4부의 빌드와 테스트 단계에서 확인할 수 있습니다.

---

## 4. 예상했지만 발생하지 않은 문제

이 튜토리얼을 설계할 때 발생할 것으로 예상했던 문제들이 있습니다. 정직하게 기록하자면, 그 중 여러 가지는 이번 실제 실행에서 발생하지 않았습니다. 예상과 현실의 차이를 명확히 남기는 것이 이후에 같은 환경을 구성하는 독자에게 더 유용합니다.

---

### host.docker.internal vs 127.0.0.1 — 적용되지 않음

**예상:** OpenHands가 Docker 컨테이너 안에서 실행될 경우, 에이전트에서 호스트의 LiteLLM 프록시에 접근하려면 `127.0.0.1` 대신 `host.docker.internal`을 사용해야 한다고 예상했습니다.

**실제:** 이 설정에서는 **적용되지 않았습니다**. OpenHands를 `LocalWorkspace` 모드로 실행하면 에이전트가 Docker 컨테이너 안이 아니라 **호스트 프로세스**로 실행됩니다. 따라서 `127.0.0.1:4000`으로 LiteLLM 프록시에 직접 연결됩니다. `host.docker.internal`은 OpenHands 자체가 Docker 컨테이너 내부에서 실행되고, LLM이 호스트에 있는 경우에만 필요합니다.

---

### 타임아웃 / 재시도 폭주 — 발생하지 않음

**예상:** 로컬 LLM 응답 시간이 길어서 타임아웃이 반복적으로 발생하고, 에이전트가 재시도를 반복하는 상황을 예상했습니다. 초기 계획서에 "240초 이상"이라는 추정치가 등장하기도 했습니다.

**실제:** 타임아웃 오류는 한 건도 발생하지 않았습니다. 실제로 측정된 툴 호출 사이클당 응답 시간은 **약 14–32초**였습니다. "240초"는 측정되지 않은 최악의 경우 추정치였으며, 실제 실행에서는 해당하지 않았습니다. 이 숫자를 실제 수치로 인용하지 마세요.

---

### .NET SDK가 샌드박스에 없음 — 적용되지 않음

**예상:** OpenHands가 Docker 샌드박스 내부에서 실행되는 경우, 샌드박스에 .NET SDK가 없어서 `dotnet` 명령이 실패할 것으로 예상했습니다. 커스텀 Docker 이미지 또는 별도의 샌드박스 구성이 필요할 것으로 봤습니다.

**실제:** 이 설정에서는 **적용되지 않았습니다**. `LocalWorkspace` 모드에서는 에이전트가 호스트 PTY를 그대로 사용합니다. 호스트 `PATH`를 그대로 상속하므로, 호스트에 설치된 `dotnet 10.0.203`이 에이전트에서 바로 사용 가능했습니다. 별도의 Docker 이미지나 샌드박스 설정이 필요 없었습니다.

---

### FsYacc %left 연산자 우선순위 버그 — 발생하지 않음

**예상:** 에이전트가 `%left PLUS MINUS`와 `%left STAR SLASH` 선언을 누락해서 연산자 우선순위와 결합법칙이 잘못 적용되는 버그가 발생할 것으로 예상했습니다. 예를 들어 `10-3-2`가 5 대신 9를 반환하거나, `2+3*4`가 14 대신 20을 반환하는 경우입니다.

**실제:** **발생하지 않았습니다**. Attempt 2에서 에이전트는 처음부터 `%left PLUS MINUS`와 `%left STAR SLASH` 선언을 올바르게 작성했습니다. 세 가지 테스트 케이스(`2+3*4 = 14`, `(2+3)*4 = 20`, `10-3-2 = 5`)가 모두 첫 빌드부터 올바른 결과를 냈습니다.

`%left` 선언은 여전히 FsYacc 문법의 핵심입니다. 만약 grammar에서 예상과 다른 계산 결과가 나온다면(특히 좌결합 연산자가 관련된 경우), `%left` 선언이 누락됐거나 순서가 잘못됐는지 먼저 확인하세요. 이번 실행에서는 해당 버그가 표면화되지 않았을 뿐입니다.
