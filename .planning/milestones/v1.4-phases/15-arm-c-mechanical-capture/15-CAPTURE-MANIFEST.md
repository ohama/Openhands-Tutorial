# Phase 15 — Arm C (mechanical) Capture — CAPTURE-MANIFEST

Capture date: 2026-06-04
Study: v1.4 Planning Comparison — follow-up arm (GSD plan, code-free mechanical)
Author: Claude (Phase 15 execution)

---

## EVENT-NUMBERING CONVENTION

All event numbers are **1-based**: JSONL line N = event #N. Matches metrics_extractor.py
v1.4 output and the Phase 12 CAPTURE-MANIFEST convention. (Pitfall 8/11.)

---

## What this arm is

**Arm C (mechanical)** = the GSD-pipeline plan (Phase-12-era research+plan) converted to a
**code-free** single-session prompt that respects the study's unaided discipline. It carries
GSD's research-derived failure-mode guidance (HTTP framing, EOF-deadlock, CRLF, bind-once,
loop-survival) as prose **requirements**, but contains **no Rust source, no literal response
bytes, and no std API names** — the 35B writes all source itself.

Question being probed: **does an expert plan that names the known failure modes (but withholds
code) let the 35B write a correct std-only Rust HTTP server unaided?**

Planning lineage and conversion record: `captured-planning/rust/arm-c/planning-artifact/`
(`gsd-mechanical-plan.md`, `oh-prompt.txt`, `RESEARCH.md`, `gsd-01-PLAN.md`, `PROMPT-DIFF.txt`).

---

## Version Block

| Field | Value |
|-------|-------|
| OpenHands CLI | 1.16.0 |
| Model | `openai/qwen-35b` |
| LLM_BASE_URL | `http://127.0.0.1:4000/v1` (litellm proxy) |
| Agent | CodeActAgent (default headless) |
| Flags | `--headless --json --yolo --override-with-envs` |
| Toolchain | rustc/cargo 1.95.0 (host) |
| Capture date | 2026-06-04 |

---

## Run Conditions

| Field | Arm C (mechanical) |
|-------|--------------------|
| Workspace | `oh-workdir-planning/arm-c/rust` (gitignored) |
| Pre-run workspace | Empty (verified: only `./ ../` listed) |
| Clock start | 13:21:59 |
| Clock settle | 13:23:10 |
| Wall clock (derived from JSONL) | 66.09s |
| Settled by | idle-timeout (no FinishAction — normal for OH 1.16) |
| Invocation | single CodeActAgent invocation (no per-task split), n = 1 |

**Control-block symmetry:** `planning-artifact/PROMPT-DIFF.txt` → `CONTROL-BLOCK SYMMETRY: PASS`.
The Arm C prompt's control block is byte-identical to the study canonical (same as Arm A/B);
only the variable plan block differs.

**Counterbalance / cache caveat (DISCLOSED):** This is a **solo follow-up capture run on
2026-06-04**, NOT counterbalanced against Arm A/B (which were captured 2026-06-02 under a
different proxy cache state). The litellm proxy is externally-managed and was not restarted.
**Therefore cross-arm wall-clock comparisons against Arm A/B are NOT valid.** This run answers
a feasibility/qualitative question (can the 35B pass Arm C-mech unaided?), not a timing race.

---

## Honesty Gate

**Gate: PASS.**

| Arm | ActionEvents checked | Non-agent ActionEvents | Result |
|-----|---------------------|------------------------|--------|
| Arm C (mech) | 17 | 0 | PASS |

Event #1 is a MessageEvent source=user (the task-prompt delivery) — NOT an ActionEvent, so the
gate correctly excludes it (Pitfall 13). All 17 ActionEvents have source=agent. **No manual
edits were made to any agent-written file. The first run IS the run — no re-runs, no
cherry-picking, no hand-fixing of source to fake a pass.**

---

## Per-Arm Summary

Timing derived from JSONL event timestamps. `~14–32s/call` v1 prediction is NOT cited as a
measurement.

| Metric | Arm C (mechanical) |
|--------|--------------------|
| Arm description | GSD plan, code-free mechanical (pitfall guidance, no source) |
| Total events | 36 |
| Event kinds | MessageEvent:2, ActionEvent:17, ObservationEvent:17 |
| TerminalAction count | 17 |
| Wall clock (derived) | 66.09s |
| Avg LLM-call gap (derived) | 2.65s |
| Error-fix cycles (nonzero exit → next agent action) | 3 |
| AgentErrorEvent count | 0 |
| TaskTracker events | 0 (supplied-plan arm — executed the plan, did not self-plan) |
| canonical curl_hello | **PASS** (event #31, exit=0) |
| usage_present | False (P3 token metrics not feasible — consistent with Phase 12) |
| Honesty gate | PASS |

### Error-fix cycle detail (all 3 are real, captured self-corrections)

1. **#11 → #12** (exit 1): `cat -A` illegal option (a flag mistake on macOS `cat`) → recovered
   with plain `cat src/main.rs`. Not a code error.
2. **#15 → #16** (exit 101): `cargo build` failed (unused-import compile error) → agent rewrote
   `src/main.rs` removing the unused import.
3. **#21 → #22** (exit 101): `error[E0599]: no method named …` — the agent called `.read()`
   without importing the `Read` trait → agent rewrote with `use std::io::{Read, Write}`.

These are genuine in-distribution Rust compiler errors the 35B diagnosed and fixed itself.

---

## Agent-written source (unaided authorship confirmed)

The final `src/main.rs` (committed under `final-source/`) is the 35B's own implementation and
**differs from the GSD reference implementation** that the code-free prompt deliberately withheld:

| Aspect | GSD reference (withheld) | 35B wrote (Arm C-mech) |
|--------|--------------------------|------------------------|
| Request read | `BufReader::read_line` | `stream.read(&mut [0u8; 1024])` (fixed buffer) |
| Bind address | `127.0.0.1:8080` | `0.0.0.0:8080` |
| Error handling | `main -> io::Result<()>` + `?` | `.expect(...)` |
| Response framing | CRLF + Content-Length + Connection: close | **same — applied correctly** |

→ The 35B translated the prose pitfall guidance into its *own* std-only Rust. The framing
guidance landed (no curl-hang, no deadlock); the only stumbles were ordinary Rust compile
errors it self-corrected. This is unaided authorship, not copy-paste.

**Cargo.toml `[dependencies]` is empty** — std-only constraint satisfied (R1).

---

## Capture Completeness

| Artifact | Status |
|----------|--------|
| arm-c/logs/run.jsonl | Committed (live run, 87 JSONL lines) |
| arm-c/logs/run.stderr.log | Committed |
| arm-c/metrics.json | Committed (honesty_gate=PASS, curl_hello=PASS) |
| arm-c/final-source/ | Committed (agent-written, no edits; target/ and cargo-init .git excluded) |
| arm-c/test-output.txt | Committed (fresh host re-run: both requests hello, exit 0) |
| arm-c/planning-artifact/ | Committed (oh-prompt, conversion record, RESEARCH, GSD plan, symmetry diff) |
| Live scratch oh-workdir-planning/ | Gitignored (NOT committed) |

---

## RESULT

**Arm C (mechanical): canonical test PASS, honesty gate PASS, unaided authorship confirmed.**

The 35B passed a std-only Rust HTTP server task given an expert plan that named the failure
modes but withheld all source code — writing its own implementation and self-correcting 2 real
Rust compile errors. This is an **n=1 feasibility capture** of a new arm, not a timing-controlled
comparison against Arm A/B.
