# OpenHands 설치

이 장은 headless SSH Mac(Apple Silicon)에서 OpenHands CLI를 설치하고, 기본 동작을 확인하는 절차를 다룹니다.

## 전제 조건

이 튜토리얼에서 사용하는 환경은 다음과 같습니다.

- **플랫폼:** macOS Apple Silicon (ARM64), SSH 원격 접속
- **인터페이스:** 브라우저 없이 터미널만 사용 (headless)
- **Python 관리:** [uv](https://docs.astral.sh/uv/) — Rust 기반 빠른 Python 패키지 관리자

브라우저 기반 Web UI(`openhands serve`)를 사용하고 싶다면 Docker가 필요하지만, 이 튜토리얼에서는 headless CLI 경로를 택합니다. 이 경로에서는 Docker가 필요하지 않습니다.

---

## 1단계: uv 설치 확인

OpenHands는 uv를 통해 설치합니다. 먼저 uv가 설치되어 있는지 확인합니다.

```sh
uv --version
```

uv가 없다면 공식 설치 스크립트로 설치합니다.

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 셸을 재시작하거나 `source ~/.zshrc`를 실행해 PATH를 갱신합니다.

---

## 2단계: OpenHands 설치

uv로 OpenHands를 설치합니다. Python 3.12 환경을 명시합니다.

```sh
uv tool install openhands --python 3.12
```

uv는 `~/.local/share/uv/tools/openhands/` 아래에 격리된 가상 환경을 만들고, `openhands` 바이너리를 `~/.local/bin/`에 링크합니다. 설치에는 수십 초가 걸릴 수 있습니다.

---

## 3단계: PATH 설정

uv tool 바이너리가 놓이는 `~/.local/bin`이 PATH에 포함되어 있어야 합니다.

```sh
echo $PATH | tr ':' '\n' | grep local
```

`~/.local/bin`이 출력에 없으면 셸 프로파일(`.zshrc` 또는 `.bashrc`)에 다음 줄을 추가합니다.

```sh
export PATH="$HOME/.local/bin:$PATH"
```

변경 후 `source ~/.zshrc`로 적용합니다.

---

## 4단계: 버전 확인

설치가 성공하면 다음 명령으로 버전을 확인합니다.

```sh
openhands --version
```

예상 출력:

```
OpenHands CLI 1.16.0
```

(내부 SDK 패키지는 v1.21.0이며, CLI 버전 번호는 1.16.0입니다. 이 두 숫자가 다른 것은 정상입니다.)

실제 검증된 출력(배너 포함 전체):

```
[LiteLLM:WARNING]: ...
+----------------------------------------------------------------------+
|  OpenHands SDK v1.21.0                                               |
|  ...                                                                 |
+----------------------------------------------------------------------+

OpenHands CLI 1.16.0
```

배너는 `OPENHANDS_SUPPRESS_BANNER=1` 환경 변수로 숨길 수 있습니다.

---

## 참고: GUI 경로 (이 튜토리얼에서는 사용하지 않음)

`openhands serve` 명령은 `localhost:3000`에서 Web UI를 실행합니다. 이 경로에는 Docker(`/var/run/docker.sock` 마운트)가 필요합니다. SSH headless 환경에서는 브라우저로 접근할 수 없으므로, 이 튜토리얼에서는 headless CLI 경로(`openhands --headless`)만 사용합니다. GUI가 필요하다면 Docker를 갖춘 로컬 데스크톱 환경에서 시도해 보세요.

---

다음 장에서는 로컬 Qwen 서버와 OpenHands를 연결하는 LLM 설정을 다룹니다.
