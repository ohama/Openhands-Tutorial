이 부록은 독자가 이 책에서 캡처한 실행 — OpenHands가 로컬 Qwen 서버를 이용해 F# FsLex/FsYacc 계산기를 자율적으로 계획·빌드·테스트하는 과정 — 을 그대로 재현할 수 있도록 필요한 모든 정보를 담고 있다. 아래의 전제 조건, 스택 점검, 실행 명령, 태스크 프롬프트, 예상 출력을 순서대로 따라가면 동일한 결과를 얻을 수 있다.

---

## 전제 조건

다음 표의 컴포넌트를 모두 갖춰야 한다. 버전은 실제 캡처 환경 기준이다.

| 컴포넌트 | 버전 | 비고 |
|---|---|---|
| macOS (Apple Silicon) | 최신 | 실행 환경은 헤드리스 SSH Mac이었다. Intel Mac이나 Linux에서도 소소한 조정으로 사용할 수 있다. |
| Colima 또는 Docker Desktop | Colima 최신 | Colima 사용자는 `colima start --cpu 4 --memory 8 --disk 60`을 먼저 실행한다. Docker Desktop 사용자는 `DOCKER_HOST` 설정을 생략한다. |
| uv | 최신 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| OpenHands CLI | v1.16.0 (SDK v1.21.0) | `uv tool install openhands --python 3.12`; 바이너리는 `~/.local/bin`에 설치된다. |
| .NET SDK | 10.0.203+ | `dotnet --version`이 10.x를 출력해야 한다. 에이전트는 LocalWorkspace (호스트 PTY) 를 사용하므로 호스트 PATH의 `dotnet`을 직접 쓴다. |
| litellm proxy | 127.0.0.1:4000 에서 실행 중 | `litellm --config /path/to/config.yaml`; 모델 alias `qwen-local`을 노출해야 한다. |
| Qwen2.5-35B 이상 | MLX 또는 vLLM 경유 | tool calling을 지원해야 한다 (`finish_reason: "tool_calls"`). proxy가 `openai/qwen-local`로 라우팅한다. |
| FsLexYacc 11.3.0 | NuGet 캐시 | `~/.nuget/packages/fslexyacc/11.3.0/`에 미리 캐시되어 있으면 `dotnet restore`가 네트워크 없이 동작한다. |

**Docker와 LocalWorkspace에 대한 참고:** 이 실행에서 OpenHands는 LocalWorkspace 모드(Docker 컨테이너 없이 호스트 PTY에서 직접 실행)를 사용했다. 따라서 Docker는 OpenHands의 primary 실행 경로에 필수적이지 않다. 단, Colima 사용자는 OpenHands가 Docker 데몬을 찾을 수 있도록 `DOCKER_HOST`를 설정해야 한다.

---

## 스택 점검

실행 전에 아래 명령으로 각 컴포넌트가 정상인지 확인한다.

```bash
# Docker 데몬 확인
docker run hello-world
# 정상: "Hello from Docker!" 메시지가 출력된다.

# OpenHands 버전 확인
openhands --version
# 정상: "SDK v1.21.0 / CLI 1.16.0" 형태의 출력이 나온다.

# litellm proxy + 모델 alias 확인
curl -s http://127.0.0.1:4000/v1/models | python3 -m json.tool | grep '"id"'
# 정상: "id": "qwen-local" 항목이 포함된다.

# LLM tool calling 기본 확인
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-local","messages":[{"role":"user","content":"Say hello"}]}' \
  | python3 -m json.tool | grep '"content"'
# 정상: content 필드에 모델 응답 텍스트가 들어있다.

# .NET SDK 버전 확인
dotnet --version
# 정상: 10.0.203 이상의 버전 번호가 출력된다.
```

---

## 실행 명령

아래가 이 책의 캡처 실행에 사용한 정확한 env-var 헤드리스 호출이다.

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" \
LLM_BASE_URL="http://127.0.0.1:4000/v1" \
LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/path/to/your/oh-workdir" \
openhands --headless --json --yolo --override-with-envs \
  -t "$(cat task1-scaffold.txt)" \
  2>task1-scaffold.stderr.log | tee task1-scaffold.jsonl
```

이 패턴을 각 태스크마다 반복하되, 프롬프트 파일과 로그 파일 이름만 교체한다
(예: `task2-lexer.txt` / `task2-lexer.jsonl`).

**Colima 사용자**는 env 블록 맨 위에 다음 줄을 추가한다.

```bash
DOCKER_HOST="unix:///Users/$(whoami)/.colima/default/docker.sock" \
```

**주요 플래그 설명:**

- `--override-with-envs` — 필수. 이 플래그 없이는 `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY` 환경 변수가 조용히 무시된다. 에러 메시지도 없어서 디버깅이 매우 어렵다. 부록 B의 REAL-02 항목을 참고한다.
- `LLM_MODEL="openai/qwen-local"` — `openai/` 접두사가 필수다. litellm이 어느 provider 어댑터를 사용할지 이 접두사로 판단한다. 접두사 없이 `qwen-local`만 쓰면 라우팅에 실패한다.
- `--yolo` — 에이전트가 사용자 확인 없이 자율적으로 명령을 실행한다.
- `--headless --json` — UI 없이 실행하고 JSONL 이벤트를 stdout에 출력한다.
- `OPENHANDS_SUPPRESS_BANNER=1` — ASCII 배너를 숨겨 `tee` 출력을 깔끔하게 유지한다.

각 호출은 **메모리가 없는 새 대화**다. 이전 태스크에서 디스크에 작성한 파일은 남아있지만, 에이전트는 `ls`/`cat`으로 직접 발견해야만 알 수 있다.

---

## 태스크 프롬프트

캐노니컬 프롬프트 파일은 저장소 내 다음 경로에 커밋되어 있다.

```
.planning/phases/03-capture-the-openhands-run/task-prompts/
  00-INVOCATION.md        ← 호출 패턴 및 태스크별 로그 파일명 참조
  task1-scaffold.txt      ← dotnet new + 정확한 calc.fsproj 내용 (FixLineDirectives)
  task2-lexer.txt         ← 완성된 Lexer.fsl 내용 (에이전트가 작성하지 않고 제공된 것)
  task3-parser.txt        ← FsYacc 문법 명세 (행동 결과 기준, %left 힌트 없음)
  task4-evaluator.txt     ← Program.fs CLI 연결 명세
  task5-buildtest.txt     ← 빌드 + 3-케이스 테스트 검증
```

**핵심 설계 선택:**

- **task1-scaffold.txt**: `FixLineDirectives` MSBuild 타깃이 포함된 `calc.fsproj`를 verbatim으로 제공한다. .NET SDK 10.0.203과 FsLexYacc 11.3.0 사이의 비호환성(fsyacc/fslex가 생성하는 `# 0 ""` 줄 지시문을 F# 10 컴파일러가 거부함)을 에이전트가 만나기 전에 미리 우회한다.

- **task2-lexer.txt**: `Lexer.fsl` 전체 내용을 verbatim으로 제공한다. 이유: FsLex 문법(`.fsl` 형식)은 35B 모델에게 out-of-distribution이다. Attempt 1에서 3번의 별도 에이전트 호출(94+27+16 = 137 TerminalAction)이 모두 유효하지 않은 Lexer.fsl을 생성했다(FsYacc에서만 쓰는 `%%` 구분자를 추가하는 등). 이 경험 후 Deviation Rule 3으로 lexer를 제공하는 방식을 택했다.

- **task3-parser.txt**: 행동 결과("`10-3-2 = 5`", "`2+3*4 = 14`")를 명세하되, `%left`를 언급하지 않는다. 에이전트가 올바른 연산자 우선순위 선언을 스스로 발견하도록 한다.

- **모든 프롬프트 공통**: 다음 파일 편집 지시 블록이 포함된다.

```
IMPORTANT: Create and edit ALL files using ONLY bash shell commands (printf, tee, or
`cat > FILE <<'EOF' ... EOF` with a quoted heredoc). Do NOT use the file_editor /
str_replace tool — it errors in this setup (it requires a security_risk field that
fails validation).
```

이 지시가 없으면 qwen-local 모델의 `file_editor` / `str_replace` 도구 호출이 다음 오류로 실패한다.

```
Error validating tool 'file_editor': Failed to provide security_risk field in tool 'file_editor'.
```

---

## 예상 출력

5번 태스크 완료 후 호스트에서 직접 실행한 캡처 결과다. 재현 실행에서도 이 출력이 나와야 한다.

```
=== Calculator Correctness Test ===

Build:
  복원할 프로젝트를 확인하는 중...
  복원할 모든 프로젝트가 최신 상태입니다.
  calc -> /Users/ohama/projs/OpenHandsTests/oh-workdir/calc/bin/Debug/net10.0/calc.dll

빌드했습니다.
    경고 0개
    오류 0개

경과 시간: 00:00:00.95

Test cases:
2+3*4 = 14
(2+3)*4 = 20
10-3-2 = 5
```

세 테스트 케이스의 의미:

- `2+3*4 = 14` — 연산자 우선순위 정확 (`STAR`가 `PLUS`보다 강하게 결합)
- `(2+3)*4 = 20` — 괄호 그루핑이 우선순위를 재정의
- `10-3-2 = 5` — 왼쪽 결합성 정확 (`(10-3)-2 = 5`, `10-(3-2) = 9`가 아님)

**실행 요약 (Attempt 2):**

| 항목 | 값 |
|---|---|
| 총 태스크 수 | 5 |
| 재시도 | 0 |
| 총 이벤트 | 146개 (5개 JSONL 로그 합계) |
| 총 TerminalAction | 67개 |
| task1 소요 시간 | 3분 6초 |
| task2 소요 시간 | 16초 |
| task3 소요 시간 | 1분 17초 |
| task4 소요 시간 | 45초 |
| task5 소요 시간 | 32초 |
| 전체 소요 시간 | 약 6분 |

실측 tool-call 사이클 타이밍은 회당 14–32초였다.

**에러-앤-픽스 사이클 (task3-parser.jsonl, events 9–30):**

task3에서 에이전트는 4번의 빌드 실패를 겪은 뒤 스스로 수정했다. 이것이 이 책 4부에서 다루는 진짜 에러-앤-픽스 사이클이다.

```
Attempt 1: FSY000 at least one %start declaration is required
Attempt 2: Parser.fsy(16,7): error parse error   [%start <int> start is invalid]
Attempt 3: Parser.fsy(16,7): error parse error   [same error]
Attempt 4: FS0039 LexBuffer<_> does not define 'FromText'
Attempt 5: Build succeeded — calc net10.0 성공 (0.7초)
```

에이전트는 각 빌드 오류를 읽고, 해당 줄과 오류 코드를 파악하고, 파일을 수정한 뒤 재시도했다. 4번의 실패 후 `%start start` / `%type <int> start`를 별도 줄에 분리하고 `LexBuffer.FromText`를 `LexBuffer<char>.FromString`으로 교체해 빌드에 성공했다. 외부 도움 없이 자율적으로 이루어진 수정이다.

---

*참고: 부록 B(트러블슈팅)에는 Attempt 1 전체 실패 분석, 각 실패 모드의 증상과 해결 방법, 그리고 예상했지만 실제로는 발생하지 않은 문제들의 정직한 기록이 담겨있다.*
