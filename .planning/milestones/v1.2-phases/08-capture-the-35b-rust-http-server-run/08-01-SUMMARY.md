---
phase: 08-capture-the-35b-rust-http-server-run
plan: 01
subsystem: infra
tags: [rust, cargo, openhands, litellm, qwen-35b, preflight, task-prompts]

# Dependency graph
requires: []
provides:
  - 4 task prompt files for 35B Rust HTTP server capture (task1-scaffold, task2-server unaided, task2-server-scaffold fallback, task3-buildtest)
  - 00-INVOCATION.md: qwen-35b headless invocation reference + JSONL filename table + scaffold-fallback policy
  - oh-workdir-rust/ scratch dir (empty, gitignored)
  - 08-01-PREFLIGHT.md: live evidence of PREFLIGHT GREEN (rustc 1.95.0, port 8080 free, proxy confirmed)
affects: [08-02-execute-capture, 08-03-capture-manifest]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Unaided-first prompt discipline: task2-server.txt names goal only (port 8080, hello\\n, std-only) — zero implementation leaks verified by grep"
    - "Scaffold-fallback policy: task2-server-scaffold.txt staged but unused unless 3+ identical build failures with no progress"
    - "Background-process testing pattern: cargo run & + sleep 2 + curl in task3-buildtest.txt"

key-files:
  created:
    - .planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task1-scaffold.txt
    - .planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task2-server.txt
    - .planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task2-server-scaffold.txt
    - .planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task3-buildtest.txt
    - .planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/00-INVOCATION.md
    - .planning/phases/08-capture-the-35b-rust-http-server-run/08-01-PREFLIGHT.md
    - oh-workdir-rust/ (empty directory)
  modified:
    - .gitignore (appended oh-workdir-rust/)

key-decisions:
  - "task2-server.txt uses 'HTTP request it receives' not 'incoming HTTP request' — avoids grep -iE incoming match (TcpListener::incoming() leak)"
  - "Scaffold fallback is staged (task2-server-scaffold.txt) but only invoked if agent cycles on same build error 3+ times with no variation"
  - "PREFLIGHT GREEN: rustc 1.95.0, cargo 1.95.0, port 8080 free, litellm proxy lists qwen-35b — 08-02 can launch"

patterns-established:
  - "Zero-leak discipline: grep checks block prompt authoring if any Rust API name leaks into unaided prompt"
  - "Preflight gate: 08-02 cannot launch without PREFLIGHT GREEN evidence file"

# Metrics
duration: 3min
completed: 2026-05-28
---

# Phase 8 Plan 01: Preflight — Rust Task Prompts + Green Launchpad Summary

**5 task-prompt/invocation files authored for unaided 35B Rust HTTP server capture; scratch dir gitignored; rustc 1.95.0 + port 8080 free + qwen-35b proxy confirmed — PREFLIGHT GREEN**

## Performance

- **Duration:** 3 min
- **Started:** 2026-05-28T08:33:42Z
- **Completed:** 2026-05-28T08:37:28Z
- **Tasks:** 3
- **Files modified:** 8 (6 created + 1 modified .gitignore + 1 created oh-workdir-rust/)

## Accomplishments
- Authored all 4 task prompt files with correct unaided-first discipline: task2-server.txt passes all zero-leak grep checks (TcpListener/BufReader/read_to_string/Content-Length/hyper/borrow-checker greps all return 0)
- Wrote 00-INVOCATION.md with qwen-35b headless command pattern, JSONL filename table, polling guidance, exit-code warning, and scaffold-fallback policy
- Confirmed PREFLIGHT GREEN: rustc 1.95.0 + cargo 1.95.0 on host, port 8080 free, litellm proxy at 127.0.0.1:4000 lists qwen-35b; oh-workdir-rust/ exists empty and gitignored (v1/v1.1 scratch dirs untouched)

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the 4 task prompts** - `fcb5789` (feat)
2. **Task 2: Write 00-INVOCATION.md** - `1574b95` (feat)
3. **Task 3: Preflight checks + write 08-01-PREFLIGHT.md** - `094db33` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `.planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task1-scaffold.txt` — agent runs `cargo new rust-server` itself
- `.planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task2-server.txt` — unaided server prompt (goal only, zero implementation leaks)
- `.planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task2-server-scaffold.txt` — fallback with verbatim working src/main.rs (TcpListener::bind)
- `.planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/task3-buildtest.txt` — build + background run + curl + honest reporting
- `.planning/phases/08-capture-the-35b-rust-http-server-run/task-prompts-rust/00-INVOCATION.md` — qwen-35b invocation reference + JSONL table + scaffold-fallback policy
- `.planning/phases/08-capture-the-35b-rust-http-server-run/08-01-PREFLIGHT.md` — live preflight evidence, verdict PREFLIGHT GREEN
- `.gitignore` — appended `oh-workdir-rust/` (book/, oh-workdir/, oh-workdir-122b/ untouched)
- `oh-workdir-rust/` — empty scratch dir (gitignored)

## Decisions Made
- **"incoming" word substitution:** The plan's verbatim body for task2-server.txt used "any incoming HTTP request" — the word "incoming" triggers `grep -iE incoming` (same as Rust's `TcpListener::incoming()` method). Changed to "any HTTP request it receives" to pass the zero-leak check without altering the prompt's meaning.
- **Fallback staged but unused:** task2-server-scaffold.txt is committed and ready but the scaffold-fallback policy in 00-INVOCATION.md makes clear it is only used on disclosed deviation (3+ identical build failures).
- **PREFLIGHT GREEN confirmed on first check:** All 5 checks (rustc, cargo, port 8080, gitignore, proxy) passed in a single pass. No retries needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Replaced "incoming HTTP request" with "HTTP request it receives" in task2-server.txt**
- **Found during:** Task 1 verification (grep -iE "incoming" check)
- **Issue:** Plan's verbatim prompt body contained "any incoming HTTP request". The word "incoming" matches `grep -iE "TcpListener|...|incoming|..."` because `TcpListener::incoming()` is the Rust API. The grep returned 1 instead of 0.
- **Fix:** Changed the English phrase to "any HTTP request it receives" — semantically equivalent, passes the zero-leak grep.
- **Files modified:** task-prompts-rust/task2-server.txt
- **Verification:** All four zero-leak greps now return 0.
- **Committed in:** fcb5789 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — natural English word "incoming" triggered API-name leak grep)
**Impact on plan:** The fix preserves the prompt's meaning and tightens honesty discipline. No scope creep.

## Issues Encountered
None — all 3 tasks completed first-pass. Port 8080 was free, proxy was live, toolchain was present.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- PREFLIGHT GREEN: 08-02 can launch. All prerequisites met.
- oh-workdir-rust/ is empty and gitignored, ready for the 35B capture run.
- The unaided-first protocol is encoded: task2-server.txt names the goal without leaking any implementation detail (RUST-01 achievable).
- Scaffold fallback is staged and policy is documented.

---
*Phase: 08-capture-the-35b-rust-http-server-run*
*Completed: 2026-05-28*
