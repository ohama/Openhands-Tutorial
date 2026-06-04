# Phase: Rust std-only HTTP server - Research

**Researched:** 2026-06-04
**Domain:** Rust standard-library TCP/HTTP networking (`std::net`, `std::io`)
**Confidence:** HIGH

## Summary

This phase builds a minimal HTTP/1.1 server in Rust using the **standard library only** — no
external crates. The task: bind TCP port 8080, respond to ANY request with the literal body
`hello\n`, and loop forever accepting connections. The canonical acceptance test is
`curl -s http://localhost:8080/` returning `hello` + newline with exit code 0.

The standard, idiomatic approach is well-established and verified against both the official
`std::net::TcpListener` API docs and The Rust Programming Language Book (Ch. 21, "Building a
Multithreaded Web Server"). The pattern is: `TcpListener::bind("127.0.0.1:8080")` →
`for stream in listener.incoming()` → for each stream, read enough of the request to not block,
then `write_all` a hand-framed HTTP/1.1 response. Because `incoming()` is an infinite iterator
(never yields `None`), the `for` loop *is* the accept loop and satisfies the "must loop"
requirement automatically.

The two things that make-or-break this task are **HTTP response framing** (the response MUST be a
valid HTTP/1.1 message with `\r\n` line endings, a `Content-Length` header OR `Connection: close`,
and a blank line before the body) and **not over-reading the request** (reading to EOF deadlocks
because the client holds the connection open). Everything else (parsing the request, routing,
threading) is unnecessary for this task and should be deliberately skipped — the spec says respond
to ANY request identically.

**Primary recommendation:** Single-threaded blocking accept loop over `TcpListener::incoming()`;
for each connection read one buffered chunk/line of the request (do NOT read to EOF), then
`write_all` the exact bytes `HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nhello\n`.

## Standard Stack

This is a std-only task by hard constraint. "Stack" = which standard library modules to use.

### Core
| Module / Item | Version | Purpose | Why Standard |
|---------------|---------|---------|--------------|
| `std::net::TcpListener` | std (rustc 1.95.0) | Bind port, accept connections | The only std way to listen on TCP |
| `std::net::TcpStream` | std | Per-connection read/write socket | Yielded by `incoming()`/`accept()` |
| `std::io::Write` (`write_all`) | std | Write full response bytes | Guarantees all bytes written or errors |
| `std::io::{BufReader, BufRead}` | std | Buffered request reading | `read_line`/`lines()` avoid byte-fiddling |
| `std::io::Read` | std | Raw `read()` if not using BufReader | Read one chunk of request without EOF wait |

### Supporting
| Item | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `std::thread::spawn` | std | Handle connections concurrently | OPTIONAL — not needed; serial loop passes the test |
| `eprintln!` | std | Log accept errors to stderr | When a stream errors, log and `continue` |
| `std::process` / `main -> io::Result<()>` | std | Propagate bind error with `?` | Clean exit on EADDRINUSE |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `for stream in listener.incoming()` | `loop { listener.accept() }` | `accept()` also returns peer `SocketAddr`; functionally equivalent. `incoming()` is more idiomatic and slightly less code. |
| Single-threaded serial loop | `thread::spawn` per connection | Threading adds concurrency but is unnecessary; curl makes one request at a time. Keep it single-threaded for simplicity. |
| `BufReader::read_line` (read just request line) | raw `stream.read(&mut buf)` once | Both avoid EOF-blocking. `read_line` is cleaner; a single `read()` into a fixed buffer also works and is even simpler. |

**Cargo.toml requirement (verify this stays true):**
```toml
[dependencies]
# MUST remain empty — no external crates
```
No `cargo add` / no `npm install` equivalent. Build with `cargo build` / `cargo run`.

## Architecture Patterns

### Recommended Project Structure
```
project-root/
├── Cargo.toml          # [dependencies] empty — enforce this
└── src/
    └── main.rs         # entire program: bind, accept loop, handle_connection
```
Single binary crate. No modules, no lib.rs needed. ~25 lines of code total.

### Pattern 1: Infinite blocking accept loop
**What:** Bind once, then iterate `incoming()` forever. The iterator never returns `None`, so the
loop never terminates on its own — this is exactly the "keeps accepting; does not exit after first
request" requirement.
**When to use:** Always, for this task.
**Example:**
```rust
// Source: https://doc.rust-lang.org/std/net/struct.TcpListener.html
use std::net::{TcpListener, TcpStream};
use std::io::{BufReader, BufRead, Write};

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080")?;
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => handle_connection(stream),
            Err(e) => eprintln!("accept error: {e}"),
        }
    }
    Ok(())
}
```

### Pattern 2: Read-then-respond (drain just enough, don't wait for EOF)
**What:** Read only the part of the request you need (here: nothing semantically — but you must
consume at least the request line so the kernel/socket is in a sane state and you don't respond
before the client finishes sending its headers). Then write the fixed response.
**When to use:** Always. Reading the first line is sufficient and safe.
**Example:**
```rust
// Source: The Rust Book Ch.21 (single-threaded server), adapted to fixed "hello" body
fn handle_connection(mut stream: TcpStream) {
    // Read the request line only — do NOT read to EOF (would block forever).
    let mut reader = BufReader::new(&stream);
    let mut request_line = String::new();
    let _ = reader.read_line(&mut request_line); // ignore parse; we reply identically to ANY request

    let body = "hello\n";
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
        body.len(),
        body
    );
    let _ = stream.write_all(response.as_bytes());
    let _ = stream.flush();
}
```

### Anti-Patterns to Avoid
- **Reading the whole request to EOF** (`read_to_string`, `read_to_end`, consuming the full
  `lines()` iterator): the HTTP client keeps the socket open after sending headers, so EOF never
  arrives and the server blocks forever. Read just the first line (or a single `read()` chunk).
- **Writing the body with no HTTP framing** (e.g. `stream.write_all(b"hello\n")` alone): curl will
  report a protocol error or hang; the response is not a valid HTTP message. You MUST send a status
  line + headers + blank line.
- **Omitting `Content-Length` and `Connection: close`**: without a length and without close,
  HTTP/1.1 keep-alive means curl waits for more data → `curl -s` appears to hang. Include at least
  one of `Content-Length: 6` or `Connection: close`; sending BOTH is safest and cleanest.
- **Using `\n` instead of `\r\n` in the HTTP header section**: HTTP requires CRLF line endings.
  Note the BODY here is plain `hello\n` (a literal `\n` per spec), but the status line, headers,
  and the header-terminating blank line all use `\r\n`.
- **Calling `bind` inside the loop**: bind once before the loop; re-binding fails with
  "address already in use".

## Don't Hand-Roll

Given the no-crates constraint, much that a real server needs is intentionally OUT of scope here.
Do NOT build these — the spec replies identically to ANY request, so they add risk for zero value:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Request parsing (method, path, headers) | A request parser | Ignore the request entirely (read 1 line, discard) | Spec: respond to ANY request the same. Parsing is wasted effort + bug surface. |
| Routing / path matching | A router | Single hardcoded response | Only one response exists. |
| Concurrency / thread pool | Custom worker pool | Serial `incoming()` loop | curl tests serially; threads add complexity for no test benefit. |
| Buffered reading by hand | Manual byte loop | `std::io::BufReader` + `read_line` | std provides it; hand-rolling invites off-by-one and EOF bugs. |
| TCP socket plumbing | raw syscalls / `libc` | `std::net::TcpListener`/`TcpStream` | `libc` would be an external crate (banned) and is unnecessary. |

**What you MUST hand-roll (because no crates allowed):** the HTTP response string itself. There is
no `hyper`/`http` crate to format the response, so you construct the literal HTTP/1.1 byte sequence
yourself via `format!`. This is the one piece of "protocol" you own.

**Key insight:** This is a deliberately *minimal* server. The skill is knowing what NOT to
implement. The only genuinely tricky bits are (1) framing the response correctly and (2) not
blocking on request read. Everything else is omission.

## Common Pitfalls

### Pitfall 1: curl hangs (no Content-Length / no Connection: close)
**What goes wrong:** `curl -s http://localhost:8080/` prints `hello` but never exits; or hangs with
no output.
**Why it happens:** HTTP/1.1 defaults to persistent (keep-alive) connections. Without a
`Content-Length` header the client cannot know the body ended, and without `Connection: close` the
client keeps the socket open waiting for more.
**How to avoid:** Send `Content-Length: 6` (length of `hello\n`) AND `Connection: close`. Closing
the stream (drop at end of `handle_connection`) also signals EOF.
**Warning signs:** curl shows the body but the command prompt doesn't return; `curl -v` shows it
waiting on the connection.

### Pitfall 2: Server blocks forever on request read
**What goes wrong:** Server accepts the connection, then hangs; curl times out, no response sent.
**Why it happens:** Code reads the request to EOF (`read_to_string`, `read_to_end`, or fully
draining `lines()`). The client sent its request and is now waiting for the *response*, so it never
closes its write side → no EOF → server blocks.
**How to avoid:** Read only what you need — a single `read_line` for the request line, or a single
`stream.read(&mut buf)`. Then respond immediately.
**Warning signs:** Connection established (curl connects) but no bytes ever returned.

### Pitfall 3: "Address already in use" (EADDRINUSE) on restart
**What goes wrong:** `cargo run` fails immediately with `Os { code: 48, kind: AddrInUse, ... }`
(code 48 on macOS).
**Why it happens:** A previous instance is still running/bound to 8080, or the port is in
TIME_WAIT.
**How to avoid:** Ensure the prior process is killed before re-running (`pkill -f <binary>` or
Ctrl-C the foreground process). For the acceptance test, start the server, run curl, then stop it.
The `?` on `bind` surfaces this error cleanly rather than panicking opaquely.
**Warning signs:** Error fires at startup before any request; `lsof -i :8080` shows another PID.

### Pitfall 4: Wrong line endings in HTTP headers
**What goes wrong:** curl reports `curl: (1) Received HTTP/0.9 when not allowed` or a parse error.
**Why it happens:** Used `\n` instead of `\r\n` between the status line / headers, so curl doesn't
recognize a valid HTTP/1.1 response.
**How to avoid:** Use `\r\n` after the status line, after each header, and for the blank line that
terminates headers. The body content (`hello\n`) uses a plain `\n` because the spec literally wants
`hello` followed by a newline.
**Warning signs:** curl exits non-zero with a protocol/HTTP-version complaint.

### Pitfall 5: Broken pipe / WouldBlock crashes the loop
**What goes wrong:** A client disconnects early and `write_all().unwrap()` panics, or one bad
connection kills the whole server.
**Why it happens:** Per-connection I/O errors propagated as panics, ending the process — violating
"keeps accepting".
**How to avoid:** Don't `unwrap()` per-connection I/O in a way that aborts the loop. Either ignore
the `Result` (`let _ =`) or match and `eprintln!` + continue. The accept loop must survive a single
bad connection.
**Warning signs:** Server exits after one unusual request; second curl gets connection refused.

## Code Examples

Verified, copy-ready patterns from official sources.

### Complete minimal server (recommended reference implementation)
```rust
// Sources:
//   https://doc.rust-lang.org/std/net/struct.TcpListener.html  (bind/incoming pattern)
//   https://doc.rust-lang.org/book/ch21-01-single-threaded.html (response framing)
use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080")?;
    println!("listening on http://127.0.0.1:8080");
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => handle_connection(stream),
            Err(e) => eprintln!("accept error: {e}"),
        }
    }
    Ok(())
}

fn handle_connection(mut stream: TcpStream) {
    // Consume only the request line; never read to EOF (client keeps socket open).
    let mut reader = BufReader::new(&stream);
    let mut line = String::new();
    let _ = reader.read_line(&mut line);

    let body = "hello\n";
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
        body.len(),
        body
    );
    if let Err(e) = stream.write_all(response.as_bytes()) {
        eprintln!("write error: {e}");
    }
    let _ = stream.flush();
}
```

### The exact response bytes (what goes on the wire)
```
HTTP/1.1 200 OK\r\n
Content-Length: 6\r\n
Connection: close\r\n
\r\n
hello\n
```
(Shown line-per-line for clarity; written as one contiguous byte string. `Content-Length: 6`
because `hello\n` is 6 bytes: h-e-l-l-o-newline.)

### Cargo.toml (must stay dependency-free)
```toml
[package]
name = "hello-server"
version = "0.1.0"
edition = "2024"

[dependencies]
# intentionally empty — std only
```

### Acceptance test
```bash
cargo run &          # start server in background
sleep 0.5            # let it bind
curl -s http://localhost:8080/   # expect: hello\n , exit code 0
echo "exit: $?"      # expect: exit: 0
# also verify it loops:
curl -s http://localhost:8080/   # second request still works
kill %1              # stop server
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `try!` macro for error propagation | `?` operator | Rust 1.13 (2016) | Use `?` on `bind`; `main -> io::Result<()>` |
| edition 2015/2018/2021 | edition 2024 | Rust 1.85 (2025) | `cargo new` on 1.95 defaults to edition 2024; no code impact for this task |
| Manual byte buffer parsing | `BufReader` + `read_line`/`lines()` | Long stable | Cleaner, fewer bugs |

**Deprecated/outdated:** Nothing in this API surface is deprecated. `std::net::TcpListener`,
`incoming()`, `accept()`, `BufReader`, and `write_all` are stable and unchanged for years. This is
about as future-proof as Rust code gets.

**Note on async:** The modern "real" approach for production servers is async (`tokio` + `hyper` or
`axum`). That is explicitly **out of scope** — those are external crates, banned by the constraint.
For a std-only single-purpose server the blocking loop is correct and idiomatic.

## Open Questions

1. **127.0.0.1 vs 0.0.0.0 bind address**
   - What we know: Spec says either is fine. `curl http://localhost:8080` resolves to 127.0.0.1, so
     binding `127.0.0.1:8080` is sufficient for the acceptance test.
   - What's unclear: Nothing material. `0.0.0.0:8080` also passes and additionally accepts external
     interfaces.
   - Recommendation: Bind `127.0.0.1:8080` (matches `localhost` test, slightly safer default).

2. **Single-threaded vs threaded**
   - What we know: The test is serial (one curl at a time), so single-threaded passes fully.
   - What's unclear: Whether the grader probes for concurrent connections (no evidence it does).
   - Recommendation: Single-threaded. Add `thread::spawn(move || handle_connection(stream))` only
     if a concurrency requirement appears — it's a one-line change and still std-only.

3. **Whether to read the request line at all**
   - What we know: You can technically skip reading and just write the response. In practice reading
     one line is more robust (lets the client finish its send, avoids RST-on-unread-data edge cases
     on some platforms) and costs nothing.
   - Recommendation: Read one line with `read_line`, discard it. Low risk, more robust.

## Sources

### Primary (HIGH confidence)
- https://doc.rust-lang.org/std/net/struct.TcpListener.html — `bind` returns `Result<TcpListener>`;
  `incoming()` returns `Incoming` yielding `Result<TcpStream>` and **never returns `None`**;
  `accept()` returns `Result<(TcpStream, SocketAddr)>`. Canonical bind+incoming loop example.
- https://doc.rust-lang.org/book/ch21-01-single-threaded.html — Official single-threaded HTTP
  server: `BufReader` request read, response framed as
  `status_line\r\nContent-Length: N\r\n\r\nbody`, written via `stream.write_all(...)`.

### Secondary (MEDIUM confidence)
- Local toolchain check: `rustc 1.95.0 (2026-04-14)`, `cargo 1.95.0` confirmed on this macOS host
  (verified via `rustc --version`).

### Tertiary (LOW confidence)
- None. All claims trace to official Rust documentation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — std modules are the only option by constraint; APIs verified against
  official std docs.
- Architecture: HIGH — bind/incoming loop is the documented canonical pattern; response framing
  taken directly from the official Rust Book.
- Pitfalls: HIGH — EOF-blocking and HTTP-framing/keep-alive issues are well-known, deterministic,
  and explained by the protocol; EADDRINUSE code 48 is macOS-specific and confirmed by platform.

**Research date:** 2026-06-04
**Valid until:** 2026-12-04 (stable std APIs; ~6 months. No fast-moving dependencies — effectively
indefinite for this API surface.)
