# 02-VERIFICATION-EVIDENCE.md

**Date:** 2026-05-27
**Purpose:** Authoritative real-output record for the end-to-end headless OpenHands verification.
All outputs below are VERBATIM from captured JSONL and shell sessions. No fabrication.

---

## Exact Invocation Shape

The following env-var form (Mode A — pure env-var, no `~/.openhands/config.toml`) was used for
both headless runs:

```sh
OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" \
LLM_BASE_URL="http://127.0.0.1:4000/v1" \
LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir" \
openhands --headless --json --yolo --override-with-envs \
  -t '<task>' \
  2>/Users/ohama/projs/OpenHandsTests/oh-workdir/<run>.stderr.log \
  | tee /Users/ohama/projs/OpenHandsTests/oh-workdir/<run>.jsonl
```

Key flags:
- `--override-with-envs` — REQUIRED; without it env vars are silently ignored
- `--json` — JSONL output on stdout (only active with `--headless`)
- `--yolo` / `--always-approve` — auto-approves all agent tool calls (user-authorized)
- `OPENHANDS_SUPPRESS_BANNER=1` — suppresses the SDK banner from stderr

---

## Pre-Run Checklist

### Item 1: OpenHands CLI version — PASS

Source: 02-01-SUMMARY.md (verbatim from 2026-05-27 preflight).

**Command:**
```
openhands --version
```

**Output (relevant lines):**
```
OpenHands CLI 1.16.0
```

Full banner output:
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

**Result:** PASS — CLI 1.16.0 confirmed. (SDK package is v1.21.0; CLI version is 1.16.0.)

---

### Item 2: litellm proxy / qwen-local model listing — PASS

Source: 02-01-SUMMARY.md (verbatim from 2026-05-27 preflight).

**Command:**
```
curl -s http://127.0.0.1:4000/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); ids=[m['id'] for m in d['data']]; print('MODELS:', ids); assert 'qwen-local' in ids, 'qwen-local MISSING'; print('PASS')"
```

**Output:**
```
MODELS: ['qwen-local']
PASS
```

**Result:** PASS — litellm proxy at 127.0.0.1:4000, no auth, model `qwen-local` present.

---

### Item 3: Headless echo ping — ActionEvent + ObservationEvent — PASS

**Run:** 2026-05-27T17:00:13Z → 17:00:28Z (wall-clock: 15 seconds)
**Task string:** `Run the bash command: echo OPENHANDS_PING_OK`
**JSONL saved to:** `oh-workdir/ping.jsonl`
**Conversation ID:** `11dce91445414a7eb44a3ec4590c7424`

**ActionEvent (agent tool call — TerminalAction, verbatim from ping.jsonl line 7):**
```json
{"id": "057048a3-c3a3-4d0c-b577-9e634e5ae6b4", "timestamp": "2026-05-27T17:00:26.152430", "source": "agent", "thought": [], "reasoning_content": null, "thinking_blocks": [], "responses_reasoning_item": null, "action": {"command": "echo OPENHANDS_PING_OK", "is_input": false, "timeout": null, "reset": false, "kind": "TerminalAction"}, "tool_name": "terminal", "tool_call_id": "eaadcec5-fce9-423d-acb9-bca7f5b668c8", "tool_call": {"id": "eaadcec5-fce9-423d-acb9-bca7f5b668c8", "responses_item_id": null, "name": "terminal", "arguments": "{\"command\": \"echo OPENHANDS_PING_OK\", \"summary\": \"Echo a ping test string\", \"security_risk\": \"LOW\"}", "origin": "completion"}, "llm_response_id": "chatcmpl-25a0fa6c-cc05-4f64-9f31-f9e257a52d9a", "security_risk": "LOW", "critic_result": null, "summary": "Echo a ping test string", "kind": "ActionEvent"}
```

**ObservationEvent (tool output — TerminalObservation, verbatim from ping.jsonl line 8):**
```json
{"id": "e1f7e9b3-3b5d-4997-ac94-2d467a2ad127", "timestamp": "2026-05-27T17:00:26.637800", "source": "environment", "tool_name": "terminal", "tool_call_id": "eaadcec5-fce9-423d-acb9-bca7f5b668c8", "observation": {"content": [{"cache_prompt": false, "type": "text", "text": "OPENHANDS_PING_OK"}], "is_error": false, "command": "echo OPENHANDS_PING_OK", "exit_code": 0, "timeout": false, "metadata": {"exit_code": 0, "pid": -1, "username": "ohama", "hostname": "ohama", "working_dir": "/Users/ohama/projs/OpenHandsTests/oh-workdir", "py_interpreter_path": "", "prefix": "", "suffix": "\n[The command completed with exit code 0.]"}, "full_output_save_dir": "/Users/ohama/.openhands/conversations/11dce91445414a7eb44a3ec4590c7424/observations", "kind": "TerminalObservation"}, "action_id": "057048a3-c3a3-4d0c-b577-9e634e5ae6b4", "kind": "ObservationEvent"}
```

**Parse result:**
```
actions= 2 observations= 2 echo_command_action= True sentinel_in_observation= True
PING PASS
```

Key observation field: `"content": [{"type": "text", "text": "OPENHANDS_PING_OK"}]`, `"exit_code": 0`.

**Result:** PING PASS — agent called TerminalAction with `echo OPENHANDS_PING_OK`; environment returned `OPENHANDS_PING_OK` in observation content.

---

### Item 4: Headless dotnet --version — 10.0.x in observation — PASS

**Run:** 2026-05-27T17:00:45Z → 17:00:59Z (wall-clock: 14 seconds)
**Task string:** `Run the bash command: dotnet --version`
**JSONL saved to:** `oh-workdir/dotnet.jsonl`
**Conversation ID:** `23ebc1b62b6e4cb0bea6a0320d0dac0d`

**ActionEvent (agent tool call — TerminalAction, verbatim from dotnet.jsonl line 7):**
```json
{"id": "500fac32-b8fc-4030-a656-7529d269bcfd", "timestamp": "2026-05-27T17:00:57.745375", "source": "agent", "thought": [], "reasoning_content": null, "thinking_blocks": [], "responses_reasoning_item": null, "action": {"command": "dotnet --version", "is_input": false, "timeout": null, "reset": false, "kind": "TerminalAction"}, "tool_name": "terminal", "tool_call_id": "cf8bf532-ce6f-4d72-8e03-15ec51f28b05", "tool_call": {"id": "cf8bf532-ce6f-4d72-8e03-15ec51f28b05", "responses_item_id": null, "name": "terminal", "arguments": "{\"command\": \"dotnet --version\", \"security_risk\": \"LOW\", \"summary\": \"Check installed .NET SDK version\"}", "origin": "completion"}, "llm_response_id": "chatcmpl-bfb2cc3e-1178-4a71-ad93-9ea0c3252bda", "security_risk": "LOW", "critic_result": null, "summary": "Check installed .NET SDK version", "kind": "ActionEvent"}
```

**ObservationEvent (tool output — TerminalObservation, verbatim from dotnet.jsonl line 8):**
```json
{"id": "673e5f39-e09e-49d2-a5b8-b9afc43284a2", "timestamp": "2026-05-27T17:00:58.804378", "source": "environment", "tool_name": "terminal", "tool_call_id": "cf8bf532-ce6f-4d72-8e03-15ec51f28b05", "observation": {"content": [{"cache_prompt": false, "type": "text", "text": "10.0.203"}], "is_error": false, "command": "dotnet --version", "exit_code": 0, "timeout": false, "metadata": {"exit_code": 0, "pid": -1, "username": "ohama", "hostname": "ohama", "working_dir": "/Users/ohama/projs/OpenHandsTests/oh-workdir", "py_interpreter_path": "", "prefix": "", "suffix": "\n[The command completed with exit code 0.]"}, "full_output_save_dir": "/Users/ohama/.openhands/conversations/23ebc1b62b6e4cb0bea6a0320d0dac0d/observations", "kind": "TerminalObservation"}, "action_id": "500fac32-b8fc-4030-a656-7529d269bcfd", "kind": "ObservationEvent"}
```

**Parse result:**
```
dotnet_version_in_observation= 10.0.203
DOTNET PASS
```

Key observation field: `"content": [{"type": "text", "text": "10.0.203"}]`, `"exit_code": 0`.

**Result:** DOTNET PASS — agent ran `dotnet --version`; host .NET SDK 10.0.203 confirmed in observation.

---

## Timing Summary

| Run | Task | Wall-clock | Notes |
|-----|------|-----------|-------|
| ping | echo OPENHANDS_PING_OK | 15 seconds | LLM inference fast; qwen-local responded in ~9s |
| dotnet | dotnet --version | 14 seconds | LLM inference fast; second call slightly faster |

Note: The plan warned ~240s+ per run on the 35B MLX model. Actual times were 14-15 seconds, significantly faster. The litellm proxy with qwen-local (Qwen 36B-35B) was responding in under 10 seconds per tool-call cycle during this session.

---

## Fallback Notes

**dotnet PATH:** No PATH fallback was needed. Bare `dotnet --version` succeeded on the first attempt. The agent's LocalWorkspace PTY inherits the host user's PATH which includes `/opt/homebrew/bin`. Phase 3/4 tasks can use bare `dotnet` commands.

**No other fallbacks were required.** All four checklist items passed on first attempt without any modification to the invocation.

---

## Environment Summary (for reference)

- **OpenHands CLI:** 1.16.0 (SDK v1.21.0), installed via `uv tool install openhands`
- **Python backing openhands:** 3.12.13 (uv-managed)
- **LLM endpoint:** `http://127.0.0.1:4000/v1`, model alias `qwen-local`
- **LLM routing:** litellm proxy (launchd `com.ohama.litellm`, PID 14555) → MLX server (launchd `com.ohama.qwen36-35b`, PID 73832) on 127.0.0.1:8000
- **Workspace:** LocalWorkspace (host PTY, no Docker required)
- **OPENHANDS_WORK_DIR:** `/Users/ohama/projs/OpenHandsTests/oh-workdir`
- **dotnet SDK:** 10.0.203 at `/opt/homebrew/bin/dotnet` (on host PATH)
- **Platform:** macOS Apple Silicon (ARM64), headless SSH

---

*Generated: 2026-05-27*
*Captured by: Claude Sonnet 4.6 executing plan 02-02*
