# 코드 작성 단계

이 장에서는 OpenHands 에이전트가 Rust HTTP 서버의 소스 파일 — `src/main.rs` — 을 실제로 작성하는 과정을 따라갑니다. 에이전트가 어떤 명령을 실행했는지, 어떤 코드를 작성했는지를 캡처된 증거에서 직접 인용합니다.

---

## 스캐폴딩 공개

task2를 시작하기 전에 중요한 사실을 밝힙니다.

- **scaffold-invoked: NO** — 스캐폴드는 발동되지 않았습니다.
- **did-write-server-unaided: YES** — 에이전트는 서버 코드를 비보조 상태로 직접 작성했습니다.
- **unaided-attempts: 1** — 첫 번째 시도에서 작성했습니다.

4부에서 FsLex 렉서 파일을 프롬프트에 제공해야 했던 것과 달리, 이번에는 에이전트가 목표 설명("포트 8080에 바인딩하고, 모든 HTTP 요청에 `hello\n`을 응답하라, std 라이브러리만 사용하라")만으로 코드를 작성했습니다.

출처: CAPTURE-MANIFEST.md, Server Outcome 절

---

## task2 — 에이전트가 서버를 작성하다

> **사용자 프롬프트**
>
> `task2-server.txt` 요약: "Rust 프로젝트 골격이 `rust-server/`에 있다. `src/main.rs`를 재작성하라 — 포트 8080에서 모든 HTTP 요청을 받아 `hello\n` 텍스트와 함께 응답하는 서버를 구현하라. 표준 라이브러리만 사용하라(`Cargo.toml`의 `[dependencies]`는 비어 있어야 한다). 빌드는 이후 태스크가 담당한다."

> **내부 프로세스**
>
> - 이벤트 #7, #8, #9 (TerminalAction): `ls`, `cat Cargo.toml`, `cat src/main.rs`로 기존 프로젝트 구조 파악
> - 이벤트 #13 (TerminalAction): `cat > .../src/main.rs << 'EOF' ... EOF` heredoc으로 43줄 HTTP 서버 작성
> - 이벤트 #16 (TerminalAction → ObservationEvent, exit=0): `cat src/main.rs`로 파일 내용 확인

> **결과**
>
> 16 이벤트, 7회의 TerminalAction, 34.1초. 에이전트가 `TcpListener + BufReader` 패턴을 선택해 43줄의 HTTP 서버를 비보조 상태로 작성했습니다. 출처: task2-server.jsonl, CAPTURE-MANIFEST.md § RUST-02

---

## Cargo.toml — 프로젝트 설정

에이전트가 작성한 서버가 사용하는 Cargo.toml입니다(task1에서 `cargo new`가 생성하고, task2 이후에도 수정되지 않았습니다).

```toml
[package]
name = "rust-server"
version = "0.1.0"
edition = "2024"

[dependencies]
```

핵심 사실:
- 패키지 이름: `rust-server`
- 에디션: `2024` (rustc/cargo 1.95.0의 기본값)
- 외부 의존성: **없음** — `[dependencies]` 섹션이 비어 있습니다

에이전트는 `std::net::TcpListener`와 `std::io::{BufRead, BufReader, Write}` — 모두 Rust 표준 라이브러리 — 만을 사용했습니다. 출처: final-source/Cargo.toml, CAPTURE-MANIFEST.md § Std-only Check

---

## 에이전트가 작성한 서버 코드

아래는 task2에서 에이전트가 작성한 `src/main.rs`입니다(이벤트 #13 heredoc, 이벤트 #16에서 cat으로 검증). task3의 빌드·수정 과정을 거쳐 최종 확정된 버전이 `final-source/src/main.rs`에 기록되어 있으며, 그것을 그대로 인용합니다.

```rust
use std::io::{BufRead, BufReader, Write};
use std::net::TcpListener;

fn handle_client(mut stream: std::net::TcpStream) -> std::io::Result<()> {
    let reader = BufReader::new(&stream);
    let mut lines = reader.lines();
    // Read the request line (first line of the HTTP request)
    let _request_line = lines.next();
    // Consume remaining header lines until empty line
    for line in lines {
        match line {
            Ok(l) if l.is_empty() => break,
            Ok(_) => continue,
            Err(_) => break,
        }
    }

    let body = "hello\n";
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
        body.len(),
        body
    );
    stream.write_all(response.as_bytes())?;
    stream.flush()?;
    Ok(())
}

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").expect("Failed to bind to port 8080");
    println!("Listening on http://0.0.0.0:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if let Err(e) = handle_client(stream) {
                    eprintln!("Error handling client: {}", e);
                }
            }
            Err(e) => eprintln!("Connection failed: {}", e),
        }
    }
}
```

출처: final-source/src/main.rs (43줄)

---

## 코드 해설

에이전트가 선택한 설계를 코드에서 직접 읽을 수 있습니다.

**`handle_client` 함수**

- `BufReader::new(&stream)` — TcpStream의 **참조**로 BufReader를 만듭니다. 소유권을 이전하지 않으므로 나중에 `stream.write_all()`을 호출할 수 있습니다.
- `let mut lines = reader.lines();` — **단일 `Lines` 이터레이터**를 만들어 재사용합니다. `reader.lines()`를 두 번 호출하지 않습니다. (이것이 task3에서의 두 번째 빌드 실패와 그 수정의 핵심입니다 — '빌드와 테스트 단계'에서 상세히 다룹니다.)
- HTTP 요청 라인과 헤더를 읽어 버린 후, 바디 없이 즉시 응답합니다.
- `format!` 매크로로 `HTTP/1.1 200 OK\r\n` 상태 라인, `Content-Length: 6`, `Connection: close`, 빈 줄, 바디 `hello\n`을 하나의 문자열로 조합합니다.

**`main` 함수**

- `TcpListener::bind("0.0.0.0:8080")` — 모든 인터페이스의 8080 포트에 바인딩합니다.
- `listener.incoming()` — 무한 루프로 연결을 받습니다. 첫 번째 요청 후 종료하지 않습니다.

---

> **개념 ↔ 행동: 도구 사용(tool calling)과 파일 편집**
>
> 에이전트가 `src/main.rs`를 작성할 때 "이런 파일을 만들겠습니다"라고 텍스트를 출력하는 것이 아닙니다. 이벤트 #13에서 `TerminalAction`을 emit해 `cat > .../src/main.rs << 'EOF' ... EOF` 명령을 실제로 실행합니다. 이것이 1부에서 설명한 **tool calling(툴 호출)**의 실제 모습입니다 — LLM이 구조화된 호출(이름 + 인자)을 출력해 환경에 행동을 지시합니다(1부 concepts.md). 이벤트 #16의 `cat src/main.rs`(TerminalAction)는 직후 ObservationEvent로 파일 내용이 돌아오는 **액션-관찰 사이클(action-observation cycle)**의 완전한 한 번입니다.
