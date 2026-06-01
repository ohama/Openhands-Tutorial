# 빌드와 테스트 단계

## 들어가며

task3에서 에이전트는 Rust 서버를 빌드하기까지 두 번의 빌드 실패를 겪었습니다. 두 번 모두 에이전트가 사람의 개입 없이 컴파일러 출력을 읽고, 원인을 판단하고, 소스를 수정하고, 재빌드했습니다.

두 오류의 성격은 다릅니다.

- **실패 1**: `format!` 매크로 구문 오류 — task2 heredoc 과정에서 유입된 괄호 누락. 에이전트는 sed로 두 번 수정을 시도했으나 패턴이 맞지 않아 파일이 바뀌지 않았고, 이를 직접 확인한 뒤 전체 파일을 heredoc으로 재작성했습니다.
- **실패 2**: Rust 소유권 오류 — `reader.lines()`를 두 번 호출한 데서 비롯된 진짜 borrow checker 오류. 단일 이터레이터 바인딩으로 수정했습니다.

모든 오류 텍스트와 사건 순서는 `logs/task3-buildtest.jsonl`에서 직접 인용합니다.

---

## 첫 번째 빌드 실패 — `unexpected closing delimiter`

### 관찰 (observed)

에이전트가 처음 `cargo build 2>&1`를 실행했을 때(task3-buildtest.jsonl, 이벤트 #15 TerminalAction / 이벤트 #16 ObservationEvent, exit=101):

```
error: unexpected closing delimiter: `}`
  --> src/main.rs:26:1
   |
22 |     );
   |     - missing open `(` for this delimiter
26 | }
   | ^ unexpected closing delimiter
```

**원인:** task2에서 에이전트가 `format!` 매크로를 작성할 때 heredoc이 괄호를 누락시켰습니다. `format!` 호출에서 여는 `(` 없이 내용이 기록되어 컴파일러가 이를 `}` 블록 종결자로 읽은 것입니다.

### 수정 시도 1 — sed (실패)

에이전트는 이벤트 #17 (TerminalAction)에서 sed로 패턴을 수정하려 했습니다. 이벤트 #17 ObservationEvent는 exit=0을 반환했지만, 에이전트가 이후 파일을 다시 읽어보니 내용이 변경되지 않았습니다. sed 패턴이 실제 파일의 공백 패턴과 달라 아무것도 교체하지 않고 조용히 성공(exit=0)을 반환한 것입니다.

### 수정 시도 2 — sed (실패)

이벤트 #21 (TerminalAction)에서 두 번째 sed 시도가 이루어졌습니다. 역시 exit=0을 반환했으나 파일 내용은 그대로였습니다. 에이전트는 cat으로 파일을 다시 확인해 두 번의 sed가 모두 실패했음을 감지했습니다.

> **사용자 프롬프트**
>
> task3-buildtest.txt 요약: "서버를 빌드하고(`cargo build`), 실행하고(`cargo run &`), curl로 `http://localhost:8080/`에 요청을 보내 응답을 확인하라. 빌드가 실패하면 오류를 진단하고 수정하고 재빌드하라."

> **내부 프로세스 (수정 1의 전체 흐름)**
>
> - 이벤트 #15 (TerminalAction): `cargo build 2>&1` 실행
> - 이벤트 #16 (ObservationEvent, exit=101): `unexpected closing delimiter` 오류 수신
> - 이벤트 #17 (TerminalAction): `sed -i '' 's/.../.../' src/main.rs` 첫 번째 시도 → exit=0이지만 파일 미변경
> - 이벤트 #21 (TerminalAction): `sed -i '' 's/.../.../' src/main.rs` 두 번째 시도 → exit=0이지만 파일 미변경
> - 에이전트가 cat으로 파일을 확인해 sed 두 번 모두 무효함을 감지
> - 이벤트 #23 (TerminalAction): 전체 파일을 heredoc으로 재작성 (`cat > src/main.rs << 'RUSTEOF' ... RUSTEOF`)

> **결과**
>
> sed 수정 두 번 모두 실패(패턴 불일치로 파일 미변경). 에이전트가 직접 감지하고 전체 파일 재작성으로 에스컬레이션. 출처: task3-buildtest.jsonl, 이벤트 #15–#23

이 자가 수정 이야기에서 중요한 점은 에이전트가 sed의 silent 실패를 스스로 감지했다는 것입니다. exit=0이 "파일 변경됨"을 보장하지 않는다는 사실을 에이전트는 cat으로 파일을 다시 읽어 직접 확인했습니다.

---

## 두 번째 빌드 실패 — E0382: use of moved value

### 관찰 (observed)

전체 재작성 후 두 번째 빌드 시도(task3-buildtest.jsonl, 이벤트 #27 TerminalAction / 이벤트 #28 ObservationEvent, exit=101):

```
error[E0382]: use of moved value: `reader`
 --> src/main.rs:9:17
  |
5 |     let reader = BufReader::new(&stream);
  |         ------ move occurs because `reader` has type `BufReader<&TcpStream>`, which does not implement the `Copy` trait
6 |     // Read the request line (first line of the HTTP request)
7 |     let _request_line = reader.lines().next();
  |                                ------- `reader` moved due to this method call
8 |     // Consume remaining header lines until empty line
9 |     for line in reader.lines() {
  |                 ^^^^^^ value used here after move
  |
note: `lines` takes ownership of the receiver `self`, which moves `reader`
 --> /rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/std/src/io/mod.rs:2702:13
```

**원인:** `reader.lines()`를 두 번 호출했습니다. 7번째 줄에서 첫 번째 `.next()` 호출이 `reader`를 `Lines` 이터레이터로 이동시켜 소유권을 가져갑니다. 9번째 줄에서 `reader.lines()`를 다시 호출하려 하지만 `reader`는 이미 이동된 상태입니다. 이것은 Rust borrow checker가 잡아내는 전형적인 소유권 오류입니다.

### 수정 (corrected)

에이전트는 이벤트 #29 (TerminalAction)에서 전체 파일을 heredoc으로 재작성했습니다. 핵심 변경은 다음과 같습니다.

**수정 전:**
```rust
let _request_line = reader.lines().next();
for line in reader.lines() {  // 두 번째 호출 — 소유권 오류
```

**수정 후:**
```rust
let mut lines = reader.lines();            // 단일 이터레이터 바인딩
let _request_line = lines.next();          // 이터레이터 재사용
for line in lines {                        // 같은 이터레이터 계속 사용
```

`reader.lines()`를 한 번만 호출해 `Lines` 이터레이터를 `lines` 변수에 바인딩하고, 이후 `.next()`와 루프 모두 같은 이터레이터를 사용합니다. 소유권이 한 번만 이전되므로 컴파일러 오류가 해소됩니다.

> **내부 프로세스 (수정 2)**
>
> - 이벤트 #27 (TerminalAction): `cargo build 2>&1` 실행
> - 이벤트 #28 (ObservationEvent, exit=101): E0382 오류 수신
> - 이벤트 #29 (TerminalAction): 전체 파일을 heredoc으로 재작성 — `let mut lines = reader.lines()` 단일 이터레이터 패턴

> **결과**
>
> E0382 오류를 컴파일러 메시지만으로 진단하고 올바른 소유권 패턴으로 수정. 출처: task3-buildtest.jsonl, 이벤트 #27–#29

---

## 빌드 성공

세 번째 빌드 시도(task3-buildtest.jsonl, 이벤트 #31 TerminalAction / 이벤트 #32 ObservationEvent, exit=0):

```
Compiling rust-server v0.1.0 (...)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.10s
```

두 번의 자가 수정 끝에 빌드가 성공했습니다.

---

## curl 검증 — 서버 동작 확인

빌드 성공 후 에이전트는 서버를 백그라운드로 실행하고 curl로 응답을 확인했습니다.

에이전트의 curl 명령(task3-buildtest.jsonl, 이벤트 #37 TerminalAction):

```
curl -s http://localhost:8080/ ; echo "EXIT_CODE=$?"
```

응답(이벤트 #38 ObservationEvent, exit=0, content="hello\nEXIT_CODE=0"):

```
hello
EXIT_CODE=0
```

이것이 RUST-03의 일차 실행 성공 증거입니다. 출처: CAPTURE-MANIFEST.md, Curl Outcome 절 — "event #37 (ActionEvent, TerminalAction), event #38 (ObservationEvent, TerminalObservation, exit_code=0, content='hello\nEXIT_CODE=0')"

---

## 호스트 독립 재실행 확인

2026-05-29에 호스트에서 독립적으로 재실행해 에이전트의 실행 결과를 검증했습니다.

```
$ curl -s -i http://localhost:8080/
HTTP/1.1 200 OK
Content-Length: 6
Connection: close

hello
```

curl 종료 코드: 0. 에이전트 캡처와 완전히 일치합니다.

출처: test-output.txt (2026-05-29, macOS Darwin 25.3.0, rustc/cargo 1.95.0)

---

## 빌드·수정 요약

| # | 빌드 | 이벤트 | 오류 | 수정 방법 |
|---|------|--------|------|-----------|
| 1 | 실패 | #16 (exit=101) | `unexpected closing delimiter: }` — format! 괄호 누락 | sed 2회 실패(#17, #21) 후 전체 heredoc 재작성(#23) |
| 2 | 실패 | #28 (exit=101) | `E0382: use of moved value: reader` — reader.lines() 두 번 호출 | 전체 heredoc 재작성(#29): `let mut lines = reader.lines()` 단일 이터레이터 |
| 3 | 성공 | #32 (exit=0) | — | — |

출처: CAPTURE-MANIFEST.md, Error-and-Fix Record

> **개념 ↔ 행동: 액션-관찰 사이클(action-observation cycle)**
>
> 이 두 번의 빌드 실패와 자가 수정은 2부에서 설명한 **액션-관찰 사이클**의 반복입니다. 에이전트가 `cargo build`(ActionEvent)를 실행하면, 컴파일러 출력 전체가 ObservationEvent로 EventLog에 기록됩니다. 그 오류 텍스트가 다음 루프 반복의 프롬프트에 포함되어 LLM이 읽고 수정 코드를 작성합니다. 사람이 오류를 중계해주지 않습니다. 에이전트 루프가 스스로 컴파일러 출력을 읽고 소스를 고칩니다. "자가 수정은 별도로 설계된 기능이 아니라, agent loop와 observation 메커니즘의 자연스러운 결과"(1부 concepts.md) — 이 두 번의 오류 사이클이 바로 그것입니다.
