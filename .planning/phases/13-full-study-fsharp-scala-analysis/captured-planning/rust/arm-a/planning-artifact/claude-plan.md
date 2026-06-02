# Claude's Task Decomposition — Rust HTTP Server (Arm A Input)

This is the mechanical conversion of Claude's v1.2 Rust task decomposition into a
single-session numbered plan. Three steps, meaning preserved verbatim from the
v1.2 task1-scaffold / task2-server / task3-buildtest prompts; phrasing adapted for
single-session state handoff only (no new planning detail added).

No scaffolded source code is included (unaided discipline: the 35B writes all
source code itself).

---

## Step 1 — Scaffold

Run `cargo new rust-server` in the working directory. Confirm the project was
created by listing the directory and showing Cargo.toml and src/main.rs. Do not
modify any files in this step.

Success criterion: `rust-server/` exists; `rust-server/Cargo.toml` and
`rust-server/src/main.rs` are present (cargo-generated defaults).

## Step 2 — Write server

After Step 1, the `rust-server/` directory and its default `src/main.rs` exist.
Rewrite `rust-server/src/main.rs` so that when the program runs, it:
- Binds TCP port 8080
- Responds to any HTTP request with the text `hello` followed by a newline
- Loops to accept the next connection (does not exit after the first request)

Use ONLY the Rust standard library — no external crates; Cargo.toml stays as-is.
After writing, show `cat rust-server/src/main.rs`. Do not build yet.

Success criterion: `rust-server/src/main.rs` is written (bash-only); its contents
implement the loop-accept-respond-hello pattern using std only.

## Step 3 — Build and test

After Step 2, `rust-server/src/main.rs` contains the server implementation.

Build:
  cd rust-server && cargo build 2>&1

If the build fails, read the compiler error, fix it (bash heredoc/printf/tee only —
NOT file_editor), and rebuild. Repeat until the build succeeds. Report each error
encountered and what was changed to fix it.

Run:
  cargo run &
  sleep 2
  curl -s http://localhost:8080/
  echo "exit_code: $?"
  kill %1
  wait %1 2>/dev/null

Report the EXACT curl output and exit code verbatim.

Success criterion: curl prints `hello` and a newline; curl exits 0. If the server
does not respond or the output is wrong, state that clearly — an honest failure is
more valuable than a fabricated success.
