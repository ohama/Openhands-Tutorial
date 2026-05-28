# 08-02 Run Notes — 35B Rust HTTP Server Capture

**Run date:** 2026-05-28
**Model:** openai/qwen-35b (Qwen2.5-35B via litellm @ http://127.0.0.1:4000/v1)
**OpenHands version:** CLI 1.16.0 / SDK 1.21.0
**Workspace:** oh-workdir-rust/ (LocalWorkspace, host PTY, gitignored)
**Rust version:** 1.95.0

---

## task1-scaffold

- invocation: `OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL="openai/qwen-35b" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-rust" openhands --headless --json --yolo --override-with-envs -t "$(cat task-prompts-rust/task1-scaffold.txt)" 2>oh-workdir-rust/task1-scaffold.stderr.log | tee oh-workdir-rust/task1-scaffold.jsonl`
- wall-clock: 2026-05-28T08:43:46Z → 2026-05-28T08:44:39Z (~53s)
- jsonl-counts: kinds={'MessageEvent': 2, 'ActionEvent': 4, 'ObservationEvent': 4} TerminalActions=4 FinishAction=false ConvError=false NonZeroExits=0
- agent-ran-cargo-new: YES  (source=agent on event #1: `cd /Users/ohama/projs/OpenHandsTests/oh-workdir-rust && cargo new rust-server`)
- disk-state: rust-server/Cargo.toml present (Y), src/main.rs default content (Y — `fn main() { println!("Hello, world!"); }`)
- outcome: PASS — agent ran cargo new rust-server (source=agent), listed files, confirmed Cargo.toml (edition=2024, empty [dependencies]) and src/main.rs (default Hello world). No FinishAction in JSONL — run ended with MessageEvent (agent completed without explicit finish signal). Scaffold landed correctly on disk.
- RUST-01 evidence (event #1): `source=agent command='cd /Users/ohama/projs/OpenHandsTests/oh-workdir-rust && cargo new rust-server'`

---

## task2-server

<!-- TO BE FILLED AFTER TASK2 -->

---

## task3-buildtest

<!-- TO BE FILLED AFTER TASK3 -->

---

## Final Summary

<!-- TO BE FILLED AFTER TASK3 -->
