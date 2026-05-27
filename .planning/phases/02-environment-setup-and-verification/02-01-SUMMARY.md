---
phase: 02-environment-setup-and-verification
plan: "01"
subsystem: environment
tags: [openhands, uv, litellm, qwen-local, python, cli, preflight]

# Dependency graph
requires:
  - phase: 01-scaffold-and-concept-chapters
    provides: mdBook scaffold and Korean concept chapters — written foundation for the book
provides:
  - Verbatim preflight evidence: OpenHands CLI 1.16.0 on PATH, Python 3.12.13 via uv
  - Verbatim preflight evidence: litellm proxy at 127.0.0.1:4000 listing qwen-local with no auth
  - SETUP-01 install-side satisfied
  - SETUP-02 LLM-reachability-side satisfied
affects: [02-02, 02-03, 02-04, 02-05, 03-run-capture]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "OpenHands CLI invoked via uv tool install shim at ~/.local/bin/openhands"
    - "litellm proxy exposes model alias qwen-local at http://127.0.0.1:4000/v1 with no auth"
    - "PATH must include $HOME/.local/bin for openhands to resolve from shell"

key-files:
  created:
    - .planning/phases/02-environment-setup-and-verification/02-01-SUMMARY.md
  modified: []

key-decisions:
  - "Docker is NOT on the critical path — headless CLI uses LocalWorkspace (host process); Docker omitted from preflight"
  - "litellm proxy launchctl shows exit -9 (past SIGKILL) but PID 14555 is actively listening on *:4000 — proxy is up"
  - "Model id to use in env vars: qwen-local (as returned by /v1/models)"

patterns-established:
  - "Preflight order: CLI/Python first, then LLM gateway, then sandbox (02-02+)"
  - "Evidence captured verbatim in SUMMARY — no fabrication"

# Metrics
duration: 4min
completed: 2026-05-27
---

# Phase 2 Plan 01: Base-Stack Preflight Summary

**OpenHands CLI 1.16.0 confirmed on PATH via uv shim, Python 3.12.13 confirmed, litellm proxy serving qwen-local at 127.0.0.1:4000 with no auth — all prerequisites present for Phase 3 agent run**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-05-27T07:52:00Z
- **Completed:** 2026-05-27T07:56:32Z
- **Tasks:** 3
- **Files modified:** 1 (SUMMARY only)

## Accomplishments

- Verified OpenHands CLI 1.16.0 is installed and reachable on PATH at `~/.local/bin/openhands`
- Confirmed Python 3.12.13 backing the uv-managed openhands tool environment
- Verified litellm proxy (PID 14555, launchd `com.ohama.litellm`) is listening on *:4000 and returns `qwen-local` with no authentication
- Captured all evidence verbatim; confirmed Docker not needed for LocalWorkspace headless path

## Task Commits

Tasks 1-2 produced evidence only (no source files). Single commit covers SUMMARY + STATE update.

1. **Task 1: Verify OpenHands CLI + PATH + Python** — evidence captured (no file commit)
2. **Task 2: Preflight litellm proxy** — evidence captured (no file commit)
3. **Task 3: Write 02-01-SUMMARY.md** — committed in `docs(02-01)` commit

## Files Created/Modified

- `.planning/phases/02-environment-setup-and-verification/02-01-SUMMARY.md` — this file; verbatim preflight evidence

## Preflight Evidence

All outputs below are VERBATIM from the shell. No fabrication.

---

### Task 1: OpenHands CLI + PATH + Python

**Command:** `openhands --version`

```
[LiteLLM:WARNING]: common_utils.py:979 - litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream decoding will be unavailable. Error: No module named 'botocore'
[LiteLLM:WARNING]: common_utils.py:24 - litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream decoding will be unavailable. Error: No module named 'botocore'
/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/sdk/llm/auth/openai.py:25: AuthlibDeprecationWarning: authlib.jose module is deprecated, please use joserfc instead.
It will be compatible before version 2.0.0.
  from authlib.jose import JsonWebKey, jwt
+----------------------------------------------------------------------+
|  OpenHands SDK v1.21.0                                               |
|                                                                      |
|  Report a bug: github.com/OpenHands/software-agent-sdk/issues        |
|  Get help: openhands.dev/joinslack                                   |
|  Scale up: openhands.dev/product/sdk                                 |
|                                                                      |
|  Set OPENHANDS_SUPPRESS_BANNER=1 to hide this message                |
+----------------------------------------------------------------------+

OpenHands CLI 1.16.0
```

**Command:** `command -v openhands`

```
/Users/ohama/.local/bin/openhands
```

**Command:** `uv tool list | grep -i openhands`

```
openhands v1.16.0
- openhands
- openhands-acp
```

**Command:** `~/.local/share/uv/tools/openhands/bin/python --version`

```
Python 3.12.13
```

**Result:** PASS — CLI 1.16.0 on PATH at `~/.local/bin/openhands`, Python 3.12.13, two binaries (`openhands`, `openhands-acp`).

Note on banner: The SDK version in the banner is v1.21.0 (the underlying SDK package version); the CLI version reported on the last line is 1.16.0. The plan must_have targets CLI 1.16.0 — confirmed.

---

### Task 2: litellm Proxy Preflight

**Command:** `launchctl list | grep com.ohama.litellm`

```
14555	-9	com.ohama.litellm
```

Note: exit column shows `-9` (the SIGKILL exit status from a prior restart). The first column (PID) is `14555` — a numeric PID, meaning the process is currently running. Confirmed with `lsof -nP -iTCP:4000 -sTCP:LISTEN`:

```
COMMAND     PID  USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
python3.1 14555 ohama   13u  IPv4 0xca92faa3fd200108      0t0  TCP *:4000 (LISTEN)
```

**Command:** `curl -s http://127.0.0.1:4000/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); ids=[m['id'] for m in d['data']]; print('MODELS:', ids); assert 'qwen-local' in ids, 'qwen-local MISSING'; print('PASS')"`

```
MODELS: ['qwen-local']
PASS
```

**Result:** PASS — litellm proxy is alive at 127.0.0.1:4000, returns model `qwen-local`, no auth required.

---

## Decisions Made

- Docker is NOT on the critical path for this plan or the Phase 3 agent run. The headless CLI uses `LocalWorkspace` (agent runs directly on the host process). No Docker commands were run. This eliminates the `DOCKER_HOST` and Colima socket complexity for the primary execution path.
- The launchctl `-9` exit code for `com.ohama.litellm` is the prior process exit status, not the current state. PID presence + lsof confirmation is the correct health check.
- Model identifier to use in LLM env vars: `qwen-local` (exactly as returned by `/v1/models`). Combined with `LLM_BASE_URL=http://127.0.0.1:4000/v1` and `LLM_MODEL=openai/qwen-local`.

## Deviations from Plan

None — plan executed exactly as written. The plan correctly anticipated the proxy being up and the CLI at 1.16.0. The launchctl `-9` exit field was noted but is normal (plan warned to check the PID column specifically).

## Issues Encountered

None. All checks passed on first attempt.

## User Setup Required

None — no external service configuration required. All components were pre-installed.

## Next Phase Readiness

Ready for 02-02: The end-to-end headless agent invocation (proves `LLM_MODEL`/`LLM_BASE_URL`/`LLM_API_KEY` env vars flow through `--override-with-envs` and that a real tool call returns successfully). Prerequisites confirmed:

- `openhands` binary: `/Users/ohama/.local/bin/openhands` (1.16.0)
- LLM gateway: `http://127.0.0.1:4000/v1`, model `qwen-local`, no auth header needed
- Python: 3.12.13 via uv

No blockers.

---
*Phase: 02-environment-setup-and-verification*
*Completed: 2026-05-27*
