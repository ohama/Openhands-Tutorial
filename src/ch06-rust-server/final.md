# 완성된 Rust 서버

이 장은 6부의 마무리입니다. 에이전트가 작성한 Rust HTTP 서버의 최종 소스를 모두 보여주고, 실제 캡처된 실행 증거로 동작을 확인하며, 솔직한 성능 기록으로 끝맺습니다.

---

## 완성된 소스

### src/main.rs (에이전트 작성, 43줄)

task2에서 비보조 상태로 작성하고, task3에서 두 번의 자가 수정을 거쳐 최종 확정된 서버 코드입니다. `final-source/src/main.rs`에서 그대로 인용합니다.

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

출처: final-source/src/main.rs

### Cargo.toml

```toml
[package]
name = "rust-server"
version = "0.1.0"
edition = "2024"

[dependencies]
```

- 패키지 이름: `rust-server`
- 에디션: `2024`
- 외부 의존성: 없음

출처: final-source/Cargo.toml

---

## 실행 결과 요약

| 항목 | 결과 |
|------|------|
| 빌드 상태 | PASS (두 번의 자가 수정 후) |
| curl 출력 | `hello\n`, exit 0 |
| HTTP 상태 | 200 OK |
| 응답 헤더 | Content-Length: 6, Connection: close |
| 호스트 재실행(2026-05-29) | 일치 |

---

## 타이밍 — 실제 측정값

아래 수치는 JSONL 타임스탬프에서 계산된 실제 측정값입니다. 추정치가 아닙니다.

| 태스크 | 첫 이벤트 | 마지막 이벤트 | 소요 시간 | TerminalActions | 평균 LLM 호출 간격 |
|--------|-----------|---------------|-----------|----------------|-------------------|
| task1-scaffold | 17:43:57 | 17:44:14 | 16.7초 | 4 | 3.4초 |
| task2-server | 17:45:20 | 17:45:54 | 34.1초 | 7 | 5.3초 |
| task3-buildtest | 17:57:16 | 17:58:19 | 62.6초 | 15 | 2.6초 |
| **합계 (active)** | — | — | **113.4초 (~1분 53초)** | **26** | **~3.8초 평균** |

- **LLM 호출당 시간 범위:** 최소 1.2초 ~ 최대 7.7초 (task3 진단 호출이 7.0–7.7초)
- **태스크 간 대기 시간:** task1→task2 약 1분, task2→task3 약 11.4분 (운영자 검토 및 재실행). 위 표의 소요 시간은 에이전트 active 시간만입니다.

출처: CAPTURE-MANIFEST.md, Timing Summary 절

---

## v1 35B 실행과의 비교 (참고)

CAPTURE-MANIFEST.md의 Comparison Hook 절은 이 Rust 실행을 v1 35B F# 계산기 실행과 비교합니다.

- **v1 35B (F# 계산기):** LLM 호출당 평균 ~14–32초 (v1 실행 기록 기준)
- **v1.2 35B (Rust 서버):** LLM 호출당 평균 3.8초

속도 차이의 주된 이유는 태스크의 복잡성 차이입니다. Rust 서버는 단일 소스 파일이고 문법 파서·렉서 디버깅이 없었습니다. F# 계산기는 FsYacc/FsLex DSL 디버깅과 다단계 파일 구성이 필요했습니다. 두 실행의 모델은 같지만(openai/qwen-35b), 태스크 도메인이 다릅니다.

위의 v1 ~14–32초/call 수치는 **v1 F# 실행의 측정값**입니다. 이 Rust 실행에 적용되지 않습니다.

---

## 솔직한 결론

이 실행에서 확인된 사실:

- 35B 모델이 `std::net::TcpListener + BufReader` 패턴을 비보조 상태로 선택해 완동하는 HTTP 서버를 작성했습니다.
- 두 번의 컴파일 오류(format! 구문 오류, E0382 소유권 오류)를 사람의 개입 없이 컴파일러 출력만으로 진단하고 수정했습니다.
- sed 두 번의 silent 실패를 스스로 감지하고 전체 파일 재작성으로 에스컬레이션했습니다.
- 최종 curl 결과: `hello\nEXIT_CODE=0`, exit 0.

4부(F# 계산기)에서 35B 모델이 FsLex `.fsl` 형식을 올바르게 생성하지 못했던 것과 달리, 이번에는 Rust 표준 라이브러리 HTTP 처리를 unaided 1회 시도로 작성했습니다. 같은 모델, 다른 도메인에서 다른 결과 — 이것이 이 예제가 기록하는 관찰된 사실입니다.

---

## Sources / 출처

이 6부에서 인용한 증거 파일 목록입니다.

- `.planning/phases/08-capture-the-35b-rust-http-server-run/captured-rust/CAPTURE-MANIFEST.md` — 실행 메타데이터, 요구사항 매핑, 타이밍, 오류·수정 기록, Comparison Hook
- `.planning/phases/08-capture-the-35b-rust-http-server-run/captured-rust/logs/task1-scaffold.jsonl` — task1 원시 JSONL (10 이벤트, 4 TerminalAction)
- `.planning/phases/08-capture-the-35b-rust-http-server-run/captured-rust/logs/task2-server.jsonl` — task2 원시 JSONL (16 이벤트, 7 TerminalAction)
- `.planning/phases/08-capture-the-35b-rust-http-server-run/captured-rust/logs/task3-buildtest.jsonl` — task3 원시 JSONL (41 이벤트, 15 TerminalAction)
- `.planning/phases/08-capture-the-35b-rust-http-server-run/captured-rust/final-source/src/main.rs` — 최종 43줄 서버 소스
- `.planning/phases/08-capture-the-35b-rust-http-server-run/captured-rust/final-source/Cargo.toml` — 최종 Cargo.toml
- `.planning/phases/08-capture-the-35b-rust-http-server-run/captured-rust/test-output.txt` — 호스트 독립 재실행 결과 (2026-05-29)
