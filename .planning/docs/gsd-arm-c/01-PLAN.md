---
phase: 01-rust-std-http-server
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - Cargo.toml
  - src/main.rs
autonomous: true

must_haves:
  truths:
    - "curl -s http://localhost:8080/ prints `hello` + newline and curl exits 0"
    - "The server keeps accepting connections — a second curl request also returns `hello\\n` (does not exit after first request)"
    - "The project builds with zero external crates — Cargo.toml [dependencies] is empty"
    - "The server binds TCP port 8080 and responds to ANY HTTP request with the same body"
  artifacts:
    - path: "Cargo.toml"
      provides: "Binary crate manifest with an EMPTY [dependencies] section (std-only constraint)"
      contains: "[dependencies]"
    - path: "src/main.rs"
      provides: "TcpListener bind on 127.0.0.1:8080, infinite incoming() accept loop, handle_connection writing a framed HTTP/1.1 response with body `hello\\n`"
      min_lines: 20
      contains: "TcpListener::bind"
  key_links:
    - from: "src/main.rs main()"
      to: "TcpListener::bind(\"127.0.0.1:8080\")"
      via: "bind once before the loop, propagate error with ?"
      pattern: "TcpListener::bind\\(\"127\\.0\\.0\\.1:8080\"\\)\\?"
    - from: "src/main.rs main()"
      to: "listener.incoming()"
      via: "for stream in listener.incoming() — infinite iterator IS the accept loop (satisfies must-loop)"
      pattern: "for .* in listener\\.incoming\\(\\)"
    - from: "src/main.rs handle_connection()"
      to: "TcpStream write_all"
      via: "write_all of HTTP/1.1 status line + Content-Length + Connection: close + blank line + body"
      pattern: "write_all"
    - from: "src/main.rs handle_connection()"
      to: "request read"
      via: "read ONE line only (read_line), never read to EOF — avoids deadlock"
      pattern: "read_line"
---

<objective>
Build a Rust program (std library ONLY, no external crates) that binds TCP port 8080,
responds to ANY HTTP request with the literal body `hello\n`, and loops forever accepting
connections.

Purpose: This is the entire deliverable for the phase. The canonical acceptance test is
`curl -s http://localhost:8080/` printing `hello` + newline with curl exiting 0, and the
server continuing to serve subsequent requests.

Output:
- `Cargo.toml` — binary crate manifest, `[dependencies]` intentionally EMPTY.
- `src/main.rs` — ~25 lines: bind, infinite `incoming()` accept loop, `handle_connection`
  that writes a correctly framed HTTP/1.1 response.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/docs/gsd-arm-c/RESEARCH.md

This is a greenfield task: empty working directory, no existing codebase. The RESEARCH.md
above is prescriptive and HIGH confidence — it contains a verified, copy-ready reference
implementation. Follow it. The whole skill here is knowing what NOT to build (no request
parsing, no routing, no threading) and getting two things exactly right:
  1. HTTP response framing — valid HTTP/1.1 with `\r\n` line endings, Content-Length, and
     Connection: close.
  2. Not over-reading the request — read ONE line, never read to EOF (EOF never arrives
     because the client holds the socket open waiting for the response → deadlock).
</context>

<tasks>

<task type="auto">
  <name>Task 1: Scaffold the dependency-free Rust binary crate</name>
  <files>Cargo.toml, src/main.rs</files>
  <action>
    Create a new Rust binary crate in the current working directory.

    Run: `cargo init --name hello-server` (NOT `cargo new`, since the directory already
    exists). This creates `Cargo.toml` and `src/main.rs` with a default `fn main()`.

    Then verify/enforce the std-only constraint: open `Cargo.toml` and confirm the
    `[dependencies]` section exists and is EMPTY. The manifest should look like:

    ```toml
    [package]
    name = "hello-server"
    version = "0.1.0"
    edition = "2024"

    [dependencies]
    # intentionally empty — std only
    ```

    Do NOT run `cargo add` or add any crate. The `[dependencies]` table must stay empty for
    the entire phase (hard requirement R1). edition 2024 is the default on rustc 1.95.0 and
    is fine — no code impact.

    If `cargo init` complains that a VCS/files already exist, pass `--vcs none` or proceed
    with whatever it scaffolds, as long as `Cargo.toml` and `src/main.rs` end up present.
  </action>
  <verify>
    `test -f Cargo.toml && test -f src/main.rs` succeeds.
    Confirm dependencies are empty — this command should print nothing:
    `awk '/^\[dependencies\]/{f=1;next} /^\[/{f=0} f && NF && $1 !~ /^#/' Cargo.toml`
  </verify>
  <done>
    Cargo.toml and src/main.rs exist. Cargo.toml has a `[dependencies]` section containing
    no actual dependency entries (comments/blank lines only).
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement the std-only HTTP server in src/main.rs</name>
  <files>src/main.rs</files>
  <action>
    Replace the entire contents of `src/main.rs` with the verified reference implementation
    from RESEARCH.md. Write exactly this (it is copy-ready and known-correct):

    ```rust
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

    Critical correctness points (do NOT deviate — these are the make-or-break items from
    research):
    - `bind` is called ONCE before the loop, with `?` to surface EADDRINUSE cleanly. Never
      bind inside the loop.
    - `listener.incoming()` is an infinite iterator (never yields `None`) — the `for` loop
      IS the accept loop. This is what satisfies "must loop / does not exit after first
      request" (R3). Do not add a break.
    - In `handle_connection`, read ONLY one line via `read_line`. Do NOT use
      `read_to_string`, `read_to_end`, or fully drain `lines()` — those wait for EOF that
      never comes and deadlock the server (Pitfall 2).
    - The response header section uses `\r\n` (CRLF) after the status line, after each
      header, and for the blank line that ends the headers. Using `\n` there causes curl to
      reject the response (Pitfall 4). The BODY is plain `hello\n` (literal newline per spec).
    - Include BOTH `Content-Length: 6` (computed via `body.len()`) AND `Connection: close`,
      so `curl -s` does not hang on keep-alive (Pitfall 1).
    - Per-connection I/O errors are logged + ignored (`let _ =` / `if let Err`), never
      `unwrap()` in a way that aborts the loop — one bad connection must not kill the server
      (Pitfall 5).

    Do NOT add: request parsing, routing, threading, or any external crate. The spec replies
    identically to ANY request; everything beyond the above is out of scope and adds risk.
  </action>
  <verify>
    `cargo build` completes with no errors and no dependency downloads.
    Sanity-check the framing and loop are present:
    `grep -q 'TcpListener::bind("127.0.0.1:8080")?' src/main.rs && grep -q 'listener.incoming()' src/main.rs && grep -q 'Content-Length' src/main.rs && grep -q 'Connection: close' src/main.rs && grep -q 'read_line' src/main.rs`
  </verify>
  <done>
    `cargo build` succeeds with zero external crates compiled. src/main.rs binds 127.0.0.1:8080,
    loops over `incoming()`, reads one request line, and writes a CRLF-framed HTTP/1.1 200
    response with body `hello\n`, Content-Length, and Connection: close.
  </done>
</task>

<task type="auto">
  <name>Task 3: Run the canonical acceptance test (curl, loop, exit code)</name>
  <files></files>
  <action>
    Verify the running server against the phase acceptance criterion. Run the server in the
    background, hit it twice with curl (to prove it loops), check output and exit codes, then
    stop it.

    Use a single scripted sequence so the background process is always cleaned up:

    ```bash
    # Make sure nothing is already on 8080 (avoid EADDRINUSE / Pitfall 3)
    pkill -f 'target/debug/hello-server' 2>/dev/null; sleep 0.3

    cargo run &        # start server in background
    SRV=$!
    sleep 1            # let it bind

    echo "--- request 1 ---"
    OUT1=$(curl -s http://localhost:8080/); C1=$?
    printf 'body=[%s] exit=%s\n' "$OUT1" "$C1"

    echo "--- request 2 (proves it loops) ---"
    OUT2=$(curl -s http://localhost:8080/); C2=$?
    printf 'body=[%s] exit=%s\n' "$OUT2" "$C2"

    kill "$SRV" 2>/dev/null
    pkill -f 'target/debug/hello-server' 2>/dev/null
    ```

    Expected, all of which MUST hold:
    - OUT1 is exactly `hello` followed by a newline; C1 is 0.
    - OUT2 is exactly `hello` + newline; C2 is 0 (server did NOT exit after request 1 → R3).
    - curl returns promptly (does not hang) — if it hangs, framing/keep-alive is wrong
      (revisit Content-Length / Connection: close).

    If EADDRINUSE appears at startup, an old instance is still bound — run
    `pkill -f hello-server`, wait, and retry. If curl hangs, re-check Task 2's framing
    (CRLF endings, Content-Length, Connection: close) and that the request is not read to EOF.
  </action>
  <verify>
    Both curl invocations print `hello\n` and exit 0. Concretely, this scripted check exits 0:
    `cargo build >/dev/null 2>&1; pkill -f 'target/debug/hello-server' 2>/dev/null; sleep 0.3; (cargo run >/dev/null 2>&1 &) ; sleep 1; O1=$(curl -s http://localhost:8080/); C1=$?; O2=$(curl -s http://localhost:8080/); C2=$?; pkill -f 'target/debug/hello-server' 2>/dev/null; [ "$O1" = "$(printf 'hello\n')" ] && [ "$C1" = 0 ] && [ "$O2" = "$(printf 'hello\n')" ] && [ "$C2" = 0 ]`
  </verify>
  <done>
    Canonical test passes: `curl -s http://localhost:8080/` prints `hello` + newline with exit
    code 0, and a second request also succeeds (server loops, does not exit after the first).
  </done>
</task>

</tasks>

<verification>
- R1 (std-only): `cargo build` compiles with no external crates; `Cargo.toml` `[dependencies]`
  is empty.
- R2 (bind 8080, respond hello): server binds 127.0.0.1:8080 and any request returns body
  `hello\n`.
- R3 (loop): two sequential curl requests both succeed; server does not exit after the first.
- R4 (canonical test): `curl -s http://localhost:8080/` → `hello\n`, curl exit code 0.
</verification>

<success_criteria>
- Cargo.toml exists with an empty `[dependencies]` section.
- src/main.rs binds 127.0.0.1:8080, loops over `incoming()`, and writes a CRLF-framed
  HTTP/1.1 200 response with body `hello\n` (Content-Length: 6, Connection: close).
- `cargo build` succeeds, zero external crates.
- `curl -s http://localhost:8080/` prints `hello` + newline and exits 0.
- A second curl request also returns `hello\n` (loop requirement satisfied).
</success_criteria>

<output>
After completion, create `.planning/docs/gsd-arm-c/01-01-SUMMARY.md` recording: files created
(Cargo.toml, src/main.rs), confirmation that [dependencies] is empty, and the acceptance-test
result (both curl outputs + exit codes).
</output>
