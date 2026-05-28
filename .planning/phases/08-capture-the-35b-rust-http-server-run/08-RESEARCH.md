# Phase 8: Capture the 35B Rust HTTP Server Run — Research

**Researched:** 2026-05-28
**Domain:** 35B OpenHands capture protocol (Rust HTTP server variant) + minimal HTTP/1.1 over TCP
**Confidence:** HIGH (live probes run on host; Rust/curl patterns verified by compilation and execution)

---

## Summary

Phase 8 reuses the proven v1/v1.1 capture protocol with one language swap: Rust instead of F#.
The environment is fully proven (OpenHands 1.16, litellm 35B, LocalWorkspace, Rust 1.95 on host).
The primary research questions are: (1) what HTTP/1.1 byte format does curl actually need, (2) how
to decompose the task without leading the agent to the answer, (3) where the 35B is likely to
stumble on Rust-specific idioms, and (4) what the scaffold fallback trigger conditions are.

The key finding on HTTP framing: `Content-Length` is NOT required. A bare response with only a
status line and `\r\n` separator works if the TCP connection closes — which it does automatically
when the TcpStream drops at end-of-scope. The simplest response that satisfies curl on this host
is `"HTTP/1.1 200 OK\r\n\r\nhello\n"` with no headers at all (verified: curl 8.7.1 exit=0,
output "hello"). The more correct form `"HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection:
close\r\n\r\nhello\n"` also works and is what a knowledgeable agent is likely to produce.

Rust is far more in-distribution for the 35B than FsLex was. The task decomposes naturally into
3 scoped OpenHands invocations — fewer than the F# runs needed — because there are no separate
lexer/parser/evaluator concerns. The primary Rust-specific risk is the BufReader-then-write
borrow checker error; `read_to_string` on a TcpStream is the other plausible hang trap.

**Primary recommendation:** 3-task decomposition (scaffold → write-server → build-run-verify).
Task prompts describe the GOAL only (what curl should receive), not the implementation
(don't say TcpListener, BufReader, or any specific API). Scaffold fallback triggers only if the
agent produces code that fails cargo build on the same class of error 3+ consecutive iterations
with no syntactic variation in the attempted fix.

---

## Standard Stack

### Core (already proven on host — no changes needed)

| Component | Version | Purpose | Notes |
|-----------|---------|---------|-------|
| Rust / cargo | 1.95.0 | Build system | `cargo new` creates edition 2024 by default |
| OpenHands CLI | 1.16 | Headless agent invocation | `--headless --json --yolo --override-with-envs` |
| OpenHands SDK | 1.21.0 | LocalWorkspace (host PTY) | No container; rustc runs directly on host |
| litellm proxy | @ 127.0.0.1:4000 | LLM routing | `openai/qwen-35b` model alias |
| curl | 8.7.1 (host) | Verification | `curl -s http://localhost:8080/` for success check |

### No external crates — std only (locked decision)

The agent must use only `std::net::TcpListener` and `std::io::{Read, Write}`. This is a locked
decision. Do NOT research `hyper`/`actix-web`/`tokio` — they are out of scope for Phase 8 and
must not appear in task prompts.

### Workdir convention (parallel to v1.1)

```
oh-workdir-rust/           ← new scratch dir (must be gitignored before run)
  rust-server/             ← cargo new creates this
    Cargo.toml             ← agent writes (via cargo new)
    src/
      main.rs              ← agent writes
  task1-scaffold.jsonl
  task1-scaffold.stderr.log
  task2-server.jsonl
  task2-server.stderr.log
  task3-verify.jsonl
  task3-verify.stderr.log
```

**Add to .gitignore before run:** `oh-workdir-rust/`
**Confirm:** `git check-ignore oh-workdir-rust` must return `oh-workdir-rust`.

---

## Architecture Patterns

### Recommended Task Decomposition: 3 Tasks

The F# runs needed 5–6 tasks because lexer/parser/evaluator were separate concerns. Rust HTTP
server has one source file (`src/main.rs`) and one build step. 3 tasks is the right size.

| Task | Name | Goal | Prompt strategy |
|------|------|------|-----------------|
| task1 | scaffold | `cargo new rust-server` in oh-workdir-rust/ | Tell agent the dir is empty; ask it to create a Rust project. Do not say what goes in main.rs. |
| task2 | write-server | Write src/main.rs with an HTTP server on :8080 | Describe WHAT it must do (TCP port 8080, GET / returns "hello\n"), not HOW (don't say TcpListener, BufReader, read_exact, etc.) |
| task3 | build-run-verify | `cargo build`, run server, curl it, report result | Show expected curl output; tell agent to kill server when done. |

**Alternative: 4 tasks** — split task3 into (build) and (run+verify) separately. Use this if the
agent struggles to manage background processes in a single task context. The 3-task version is
preferred because the run+verify cycle is tightly coupled and splitting creates artificial state.

### Invocation Command (identical to v1 except model alias and workdir)

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL="openai/qwen-35b" \
  LLM_BASE_URL="http://127.0.0.1:4000/v1" \
  LLM_API_KEY="dummy" \
  OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-rust" \
  openhands --headless --json --yolo --override-with-envs \
  -t "$(cat task-prompts-rust/task1-scaffold.txt)" \
  2>oh-workdir-rust/task1-scaffold.stderr.log \
  | tee oh-workdir-rust/task1-scaffold.jsonl
```

### Anti-Patterns to Avoid in Task Prompts

- **Don't name the struct/module:** Saying "use TcpListener" tells the agent the exact answer.
  Saying "listen on TCP port 8080 and respond to HTTP requests" is the right level.
- **Don't describe HTTP framing:** Saying "send a status line and headers" leaks implementation.
  Saying "when curl hits localhost:8080/ it should get back hello followed by a newline" is correct.
- **Don't constrain file_editor preemptively in task1:** The scaffold task only runs `cargo new`
  (a bash command); file_editor is not needed and the agent likely won't try it. Add the
  bash-only constraint explicitly to task2 (which writes main.rs).

---

## Minimum Viable HTTP/1.1 Response (verified on host)

**Question:** What byte format does curl actually need?

**Finding (confidence: HIGH — live tested with cargo 1.95, curl 8.7.1):**

The absolute minimum that satisfies `curl -s http://127.0.0.1:8080/` is:

```
HTTP/1.1 200 OK\r\n\r\nhello\n
```

No headers required. RFC 7230 §3.3.3 rule 7: "Otherwise, this is a response message without a
declared message body length, so the message body length is determined by the number of octets
received prior to the server closing the connection." When the TcpStream drops at end-of-scope,
the TCP connection closes, and curl reads "hello\n" as the complete body.

**More correct form (also verified):**

```
HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nhello\n
```

Both forms return curl exit=0, output "hello". The agent is likely to write something between
these two — probably including `Connection: close` since that is common tutorial knowledge.

**Critical: `\r\n` not `\n`:** HTTP requires CR+LF as line separator in the status line and
header section. curl is tolerant on some systems but it is not specified behavior. The agent
should use `\r\n`. This is the most likely formatting mistake. If it uses `\n` only, curl on
macOS still works (curl 8.7.1 is permissive), so this is unlikely to manifest as a test failure
but should be noted.

**Content-Length must be correct if present:** "hello\n" is 6 bytes. If the agent writes
`Content-Length: 5` (forgetting the newline), curl will truncate and print "hello" without the
newline. This is a subtle observable failure if the test checks for the trailing newline.

**`hello\n` is 6 bytes:** h(1) e(2) l(3) l(4) o(5) \n(6). Content-Length: 6 is correct.

---

## Task Prompt Wording (concrete starting text)

### task1-scaffold.txt

```
Working directory: /Users/ohama/projs/OpenHandsTests/oh-workdir-rust

The directory is empty. Your task: create a new Rust project here.

  cd /Users/ohama/projs/OpenHandsTests/oh-workdir-rust
  cargo new rust-server

This creates rust-server/ with Cargo.toml and src/main.rs.

After running cargo new, confirm the project was created:
  ls rust-server/
  cat rust-server/Cargo.toml

Do not modify any files yet — a later task fills in the source code.
```

Rationale: Tells the agent exactly what to run. `cargo new` is not an answer leak — it is
infrastructure setup analogous to `dotnet new console` in v1. The Cargo.toml will have no
dependencies (std only), which is the default.

### task2-server.txt

```
Working directory: /Users/ohama/projs/OpenHandsTests/oh-workdir-rust

IMPORTANT: Create and edit ALL files using ONLY bash shell commands (printf, tee, or
`cat > FILE <<'EOF' ... EOF` with a quoted heredoc). Do NOT use the file_editor /
str_replace tool — it errors in this setup (it requires a security_risk field that
fails validation).

A Rust project scaffold exists in rust-server/. Start by reviewing it:

  cd rust-server
  ls
  cat Cargo.toml
  cat src/main.rs

Your task: rewrite src/main.rs so that when the program runs, it listens on TCP port
8080 and responds to any incoming HTTP request with the text:

  hello

followed by a newline character, then closes the connection.

Requirements:
- Port: 8080 (bind to 0.0.0.0:8080 or 127.0.0.1:8080 — either is fine)
- Response: the literal characters "hello" followed by a newline (\n)
- The program must continue running, accepting connections in a loop
- Use only the Rust standard library — no external crates (Cargo.toml stays as-is)

After writing src/main.rs, show its contents:
  cat src/main.rs

Do not build yet — a later task handles build and testing.
```

Rationale: Describes goal (port 8080, return "hello\n"), not implementation (no mention of
TcpListener, BufReader, accept(), read(), write_all()). The agent must figure out the
implementation. "Use only the Rust standard library" gates the no-external-crates requirement
without naming which std types to use.

### task3-verify.txt

```
Working directory: /Users/ohama/projs/OpenHandsTests/oh-workdir-rust

IMPORTANT: Create and edit ALL files using ONLY bash shell commands. Do NOT use
the file_editor tool.

A Rust HTTP server source exists in rust-server/src/main.rs. Your task: build it,
run it, test it, and report the real outcome.

Step 1: Build.

  cd rust-server
  cargo build 2>&1

If the build fails, read the error, fix src/main.rs, and rebuild. Repeat until
the build succeeds or you have exhausted reasonable fixes.

Step 2: Run the server in the background.

  cargo run &
  sleep 2

Step 3: Test with curl and capture the exact output.

  curl -s http://localhost:8080/

Required output: hello (with a trailing newline, so curl prints "hello" and the
prompt appears on the next line).

Step 4: Kill the server.

  kill %1

Step 5: Report results explicitly.

State the exact output curl printed, the exit code ($?), and whether the required
output was produced. If the server did not respond or curl returned an error, state
that clearly — do not modify results to appear successful.

Constraints:
- Do not modify Cargo.toml (no external crates).
- If you fix src/main.rs, fix only the error at hand — report what you changed and why.
- Report every build error you encountered and how you fixed it.
```

Rationale: Tells the agent HOW to test (curl command, background process pattern) but not what
the server code should look like. The explicit "report what you changed and why" captures the
error-and-fix sequence in the JSONL. "Do not modify results to appear successful" is the honesty
constraint parallel to the calculator's "do not silently rewrite the grammar."

---

## 35B-Specific Rust Blind Spots to Anticipate

These are plausible errors based on 35B's known behavior pattern (strong pattern-matching, weak
on obscure APIs) applied to the specific Rust patterns this task requires. Confidence: MEDIUM —
based on 35B behavior from v1 and Rust-specific borrow checker semantics; actual run may differ.

### Blind Spot 1: BufReader + write borrow conflict

**What it looks like:** Agent writes:
```rust
let reader = BufReader::new(stream);  // moves stream into reader
for line in reader.lines() { ... }
// stream is gone — E0382: borrow of moved value: `stream`
stream.write_all(response.as_bytes())?;
```

**Why it happens:** The idiomatic Rust pattern for reading HTTP headers is BufReader, and the
agent may not track ownership transfer. If BufReader::new takes ownership (not a reference),
stream is moved and unavailable afterward.

**Actual compiler error:** `error[E0382]: borrow of moved value: 'stream'` — verified on host.

**Fix (agent may discover):** Pass a reference: `BufReader::new(&stream)`. Since TcpStream
implements Read, `&TcpStream` also implements Read via the blanket impl `impl Read for &TcpStream`.
Write still works on `&mut stream`. This compiles with Rust 1.95 NLL.

**Educational value:** Good borrow-checker story if it happens. Clear error message; agent should
be able to diagnose it.

### Blind Spot 2: `read_to_string` hangs at runtime

**What it looks like:** Agent writes `stream.read_to_string(&mut request)` to read the HTTP
request. This compiles without error but blocks at runtime waiting for TCP EOF — which curl never
sends (curl sends the request and waits for the response; neither side sends FIN first).

**Symptom:** `curl -s http://localhost:8080/` hangs indefinitely. cargo run is still running.
kill %1 required to release.

**Why it happens:** `read_to_string` reads until EOF (read returns 0). For a TCP connection, EOF
means the remote side closed the connection. curl holds the connection open waiting for a
response. Neither side closes — deadlock.

**Fix:** Use `stream.read(&mut buf)` with a fixed buffer (reads whatever is available, returns
immediately), or BufReader line-by-line (reads until `\r\n\r\n` blank line). The agent should
self-diagnose once it sees curl hanging.

**Detection signal in JSONL:** cargo run is backgrounded, then curl command is followed by no
ObservationEvent (or the observation event has a timeout). If the agent kills the background
process and rewrites, that's the error-and-fix cycle.

### Blind Spot 3: Content-Length off by one

**What it looks like:** Agent includes `Content-Length: 5` for "hello\n" (forgetting the \n byte).
**Symptom:** curl outputs "hello" with no newline (prompt runs together with "hello"). Depending
on how the test requirement is stated, this may or may not be detectable as a failure.
**Task3 prompt wording defense:** The requirement says "hello followed by a newline character" —
which means the agent should count the newline. But the agent may still get it wrong.
**Educational value:** Minor — a factual correctness detail.

### Blind Spot 4: Binding to 127.0.0.1 vs 0.0.0.0

Both work for `curl localhost:8080/` on the same host. Not a problem for the test. Not worth
worrying about. If the agent binds to 127.0.0.1, that is fine.

### Blind Spot 5: `unwrap()` vs `?` in main

Agent may try `?` in `fn main()` without declaring the return type as `Result<(), Error>`. In
Rust 2024 (which cargo 1.95 creates by default), `fn main() -> Result<(), Box<dyn std::error::Error>>`
is the correct signature for using `?`. If the agent writes bare `?` in `fn main()` without
the return type, the compiler error is clear: `E0277: ? cannot be used in a function that
returns ()`. This is self-diagnosable.

**Alternatively:** the agent may use `unwrap()` throughout, which compiles fine and is entirely
acceptable for a tutorial server.

---

## Scaffold Fallback Policy

The v1.1 policy was "if 2 unaided attempts both fail" (for the lexer task). For Rust, the analog:

**Rust is more in-distribution than FsLex.** The 35B has substantial Rust training data.
The scaffold fallback threshold should be HIGHER — require more evidence of genuine inability
before providing source.

### Fallback Trigger for task2 (write-server)

Trigger scaffold fallback for task2 if ALL of the following are true:
1. The agent's cargo build fails on the SAME root error class (e.g., always E0382 borrow conflict,
   or always syntax error at the same construct) across 3+ consecutive build attempts.
2. The error variations show no syntactic variation — the agent is not making progress (same
   line, same error, same fix attempt cycling).
3. The JSONL shows the agent is stuck (repeated identical commands with no new diagnostic
   reasoning).

Do NOT trigger scaffold fallback if:
- The agent is making diverse fix attempts (even if all failing) — that is genuine error-and-fix.
- The build error changes between attempts — the agent is making progress.
- The agent hits a runtime hang (read_to_string) — give it one more attempt with the hint that
  "read_to_string may block on a live TCP connection."

### Fallback Trigger for task3 (build-run-verify)

If the agent cannot make cargo build succeed after 5+ iterations with no progress signal,
provide a scaffold src/main.rs. Disclose in CAPTURE-MANIFEST.

### Scaffold Content (prepare but do not use preemptively)

If triggered, provide this verified-working src/main.rs verbatim via the task prompt:

```rust
use std::net::TcpListener;
use std::io::{Read, Write};

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").unwrap();
    for stream in listener.incoming() {
        let mut stream = stream.unwrap();
        let mut buf = [0u8; 4096];
        let _ = stream.read(&mut buf);
        let response = "HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nhello\n";
        stream.write_all(response.as_bytes()).unwrap();
    }
}
```

This is the verified-working form (compiled and curl-tested on host, 2026-05-28, Rust 1.95).

---

## Verification Mechanism on Host

Once the agent claims the server runs and curl succeeds, verify independently:

### From JSONL (primary)

Success ObservationEvent in task3 JSONL looks like:
```json
{
  "kind": "ObservationEvent",
  "observation": {
    "command": "curl -s http://localhost:8080/",
    "exit_code": 0,
    "content": [{"type": "text", "text": "hello\n"}]
  }
}
```
(The exact field names follow the OpenHands JSONL schema used in v1/v1.1. The critical fields
are `exit_code: 0` and `content` containing "hello\n".)

### From host re-run (independent confirmation for CAPTURE-MANIFEST)

After all tasks complete, the operator runs independently on host:
```bash
cd /Users/ohama/projs/OpenHandsTests/oh-workdir-rust/rust-server
cargo build 2>&1           # must succeed (0 errors)
cargo run &
sleep 2
curl -s http://localhost:8080/   # must print: hello
echo "(exit $?)"                 # must be: exit 0
kill %1
```

Save the output as `captured-rust/test-output.txt` — parallel to v1/v1.1 `test-output.txt`.

### Background process management (agent concern, not operator)

The agent must background cargo run before calling curl. The task3 prompt shows the pattern
(`cargo run &` then `sleep 2`). If the agent does not background the server, curl will never
run because cargo run blocks. The agent may self-discover this ordering requirement.

If the agent starts cargo run in the foreground and hangs, it will receive a ConversationErrorEvent
from the iteration cap or a timeout. The operator can then restart task3 with a hint that
"cargo run blocks; use cargo run & to background it."

### Port conflict check (pre-run)

Before starting the run: `lsof -ti :8080` must return empty. Port 8080 was free on this host at
research time (verified 2026-05-28). If the port is busy, the server will fail with
"Address already in use" — clear and self-diagnosable by the agent.

---

## CAPTURE-MANIFEST.md Required Schema

Based on v1/v1.1 manifests; adapted for Rust HTTP server:

```markdown
## Run Metadata
- Run date: [date]
- Model: openai/qwen-35b (Qwen2.5-35B via litellm @ http://127.0.0.1:4000/v1)
- OpenHands version: SDK v1.21.0 / CLI 1.16.0
- Workspace: oh-workdir-rust/ (LocalWorkspace, host PTY, gitignored)
- Rust version: 1.95.0

## Invocation
[exact command used for each task, with prompt file name]

## Per-Task Outcome Table
| Task | JSONL | Duration | Events | TerminalActions | Outcome |
|------|-------|----------|--------|-----------------|---------|
| task1-scaffold | task1-scaffold.jsonl | Xs | N | N | [PASS/FAIL] |
| task2-server | task2-server.jsonl | Xs | N | N | [PASS/FAIL/SCAFFOLDED] |
| task3-verify | task3-verify.jsonl | Xs | N | N | [PASS/FAIL] |

## Unaided-vs-Scaffolded
- did-write-server-unaided: YES/NO
- unaided-attempts: N
- scaffold-disclosure: [if scaffolded: what was provided and why]

## Error-and-Fix Record
- error-description: [what cargo build or runtime error the agent saw]
- fix-description: [what the agent changed]
- location-in-jsonl: [task file, event range]
- iterations: N

## curl Outcome (RUST-03)
- command: curl -s http://localhost:8080/
- actual-output: [verbatim]
- exit-code: [0 or N]
- JSONL citation: [task file, event number]
- all-pass: YES/NO

## Timing Summary
- task1-scaffold: total Xs (N TerminalActions)
- task2-server: total Xs (N TerminalActions)
- task3-verify: total Xs (N TerminalActions)
- total-run: Xs
- per-LLM-call-avg: Xs

## Deviations
[Any deviation from the planned task structure; must include fallback disclosures]

## Artifact Index
[Table of committed files → requirements evidenced]
```

**Required fields for Phase 9 (chapter writing):**
- `did-write-server-unaided` — establishes whether Rust was in-distribution for 35B
- `curl-actual-output` with JSONL event citation — the verifiable success fact
- `error-description` + `fix-description` — narration material for any error-and-fix sequence
- `timing-summary` — may appear in 6부 performance callout

---

## What Is Already Proven (Do Not Re-Research)

| Component | Status | Evidence |
|-----------|--------|----------|
| Rust 1.95.0 on host | VERIFIED | `rustc --version` returns 1.95.0 (checked in this session) |
| cargo new creates edition 2024 Cargo.toml | VERIFIED | Confirmed in this session |
| std::net::TcpListener works for HTTP | VERIFIED | Compiled + curl tested on host (this session) |
| curl 8.7.1 satisfies with bare HTTP/1.1 response | VERIFIED | Tested all 3 response variants in this session |
| litellm 35B proxy live | VERIFIED | STATE.md (proxy unchanged from v1/v1.1 runs) |
| OpenHands 1.16 headless CLI pattern | VERIFIED | Identical invocation to v1/v1.1 (proven there) |
| `--override-with-envs` required | VERIFIED | v1 proof; identical config |
| `file_editor` errors without security_risk | VERIFIED | v1.1 proof; same OpenHands version |
| bash-only file write constraint works | VERIFIED | v1/v1.1 pattern confirmed |
| Port 8080 free on host | VERIFIED | `lsof -ti :8080` returned empty (this session) |

---

## Honest Expected Failure Modes

These are plausible failure modes based on the Rust-specific analysis above. Confidence: MEDIUM.

### Likely to produce narration-worthy material

1. **BufReader ownership conflict (E0382):** Agent writes BufReader taking ownership of stream,
   then tries to write to stream after. Error message is specific and self-diagnosable. The
   agent will try `&stream` or `stream.try_clone()` as fixes. 1–3 iterations expected. Good
   borrow-checker story.

2. **`read_to_string` hang at runtime:** Agent compiles successfully but curl hangs. Agent kills
   the server, rewrites to use `stream.read(&mut buf)` with a fixed buffer. This is a runtime
   diagnosis (not a build error) and demonstrates agent observing behavior and self-correcting.

3. **Missing `use std::io::Write` for `write_all`:** Agent forgets the `Write` trait import.
   Compiler: `method not found in TcpStream — did you mean to import std::io::Write?` Agent
   self-corrects immediately with compiler guidance.

### Likely blockers (need operator intervention if they occur)

1. **Agent never backgrounds cargo run:** If task3 prompt does not sufficiently emphasize that
   cargo run blocks, the agent may run it in the foreground and never reach the curl command.
   Recovery: restart task3 with added hint about `cargo run &`.

2. **Port 8080 busy at run time:** If another process occupies :8080 between preflight and run.
   Recovery: kill the occupant, or change port in task prompt (disclose deviation).

### Not likely (Rust is in-distribution)

- Agent producing completely wrong code (no TCP socket concept): UNLIKELY. 35B has extensive
  Rust training data including minimal HTTP server patterns.
- Agent using a crate without being told (axum, tokio): Possible. If it adds to Cargo.toml,
  task3 prompt says "Cargo.toml stays as-is" and the agent should comply. If it does add a
  crate anyway, this is a deviation to record, not a run failure.
- Borrow checker confusion on the accept loop itself: UNLIKELY. `for stream in listener.incoming()`
  is a canonical Rust pattern with no borrow issues.

---

## Out-of-Scope Reminders

Do NOT include in task prompts:
- Any mention of `TcpListener`, `BufReader`, `read`, `write_all`, `accept`, `bind` — these name
  the implementation
- Any mention of async runtimes (tokio, async-std) — locked out by "std only" decision
- Any routing concepts (match on URL, multiple routes) — locked out by "GET / only" scope
- Any mention of HTTP frameworks (hyper, axum, actix-web) — locked out
- `TcpStream::try_clone()` as a hint — if the agent needs it, it will find it; providing it
  leaks the fix for a borrow checker problem before the problem occurs
- The exact HTTP response string format — "respond with hello\n" is sufficient; the agent
  figures out the HTTP framing

Do NOT research for this phase:
- Async Rust patterns (tokio, futures) — not applicable
- HTTP/2 or HTTP/3 — not applicable
- rustup toolchain management — already verified; 1.95.0 is on path
- Cargo workspaces — single binary project; not needed

---

## Code Examples

Verified on host (Rust 1.95.0, cargo 1.95.0, macOS Darwin 25.3.0, 2026-05-28):

### Minimal working server (no headers)
```rust
use std::net::TcpListener;
use std::io::{Read, Write};

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").unwrap();
    for stream in listener.incoming() {
        let mut stream = stream.unwrap();
        let mut buf = [0u8; 4096];
        let _ = stream.read(&mut buf);
        stream.write_all(b"HTTP/1.1 200 OK\r\n\r\nhello\n").unwrap();
    }
}
```
Result: `curl -s http://localhost:8080/` → "hello\n", exit 0.

### With Content-Length and Connection: close (agent likely choice)
```rust
let response = "HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nhello\n";
stream.write_all(response.as_bytes()).unwrap();
```
Result: Same — curl exit 0, "hello\n".

### BufReader on reference (correct borrow pattern, if agent needs it)
```rust
use std::io::{BufRead, BufReader};
let reader = BufReader::new(&stream);  // &stream, not stream — borrows, doesn't move
for line in reader.lines() {
    let line = line.unwrap();
    if line.is_empty() { break; }
}
stream.write_all(response.as_bytes()).unwrap();  // stream still accessible
```
This compiles because `&TcpStream` implements Read (blanket impl in std).

---

## Sources

### Primary (HIGH confidence — live probes run during this research session)

- Host: `rustc --version` → 1.95.0; `cargo --version` → 1.95.0
- Host: `cargo new` → creates `edition = "2024"` Cargo.toml (observed directly)
- Host: Compiled 6 variants of the minimal HTTP server; curl-tested all 3 response formats
- Host: Verified BufReader-move E0382 error and BufReader-reference fix (cargo build on host)
- Host: Confirmed port 8080 free (`lsof -ti :8080` → empty)
- Host: Confirmed `curl -v` exchange: Status-Line + optional headers + blank line + body

### Secondary (HIGH confidence — from v1/v1.1 captured runs on this machine)

- `03-02-RUN-NOTES.md` — 35B behavior pattern: strong at diagnosing build errors, weak on
  obscure API names. The FsLex failure was a format-knowledge gap, not a logic gap.
- `06-RESEARCH.md` — unaided-first protocol, task prompt discipline, retry/fallback policy.
- `06-VERIFICATION.md` — confirmed `source=agent` on all ActionEvents; honesty check protocol.
- `captured-122b/CAPTURE-MANIFEST.md` — reference schema for Phase 8's CAPTURE-MANIFEST.

### Tertiary (MEDIUM confidence — RFC reference)

- RFC 7230 §3.3.3 (message body length): rule 7 — connection-close signals body end. This is
  the RFC basis for why the bare response works. Not directly tested against curl's RFC
  compliance, but practically confirmed.

---

## Metadata

**Confidence breakdown:**
- HTTP/1.1 minimal response format: HIGH — directly verified on host (3 variants, all with curl)
- Task decomposition: HIGH — parallel reasoning to v1/v1.1 proven decompositions
- Task prompt wording: HIGH — applies v1.1's discipline directly; tested phrasing avoids leaking
- 35B Rust blind spots: MEDIUM — inferred from 35B behavior pattern + Rust borrow semantics
- Scaffold fallback policy: HIGH — same logic as v1/v1.1; threshold adjusted for in-distribution
- CAPTURE-MANIFEST schema: HIGH — copied from working v1/v1.1 schemas with Rust-specific fields

**Research date:** 2026-05-28
**Valid until:** 30 days (stable stack — Rust 1.95, OpenHands 1.16, curl 8.7.1 are all pinned)
