---
phase: 02-environment-setup-and-verification
verified: 2026-05-27T00:00:00Z
status: passed
score: 5/5 must-haves verified
---

# Phase 2: Environment Setup & Verification — Verification Report

**Phase Goal:** The stack is set up and smoke-tested so the OpenHands run (Phase 3) can begin without surprises, and the 3부 setup chapter documents the verified steps.

**Verified:** 2026-05-27
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | openhands --version returns 1.16.0 (CLI installed via uv) | VERIFIED | Live: `openhands --version` → "OpenHands CLI 1.16.0"; 02-01-SUMMARY.md verbatim output confirmed |
| 2 | Configured to local Qwen via env vars; headless ping produces action+observation with OPENHANDS_PING_OK | VERIFIED | oh-workdir/ping.jsonl exists; grep confirms 7 occurrences of OPENHANDS_PING_OK; 02-VERIFICATION-EVIDENCE.md quotes verbatim ActionEvent + ObservationEvent JSONL lines; proxy live: MODELS: ['qwen-local'] |
| 3 | dotnet --version (10.0.x) runs in agent's LocalWorkspace | VERIFIED | oh-workdir/dotnet.jsonl exists; grep confirms "10.0." present; 02-VERIFICATION-EVIDENCE.md quotes ObservationEvent with "10.0.203"; host: dotnet --version → 10.0.203 |
| 4 | Pre-run verification checklist passes with REAL captured outputs in evidence file | VERIFIED | 02-VERIFICATION-EVIDENCE.md contains all 4 checklist items with verbatim JSONL, not fabricated: JSONL files on disk match quoted content; conversation IDs and timestamps in evidence are consistent with real runs |
| 5 | 3부 setup chapter documents every reader step matching verified config; mdbook build exits 0 | VERIFIED | src/ch03-setup/{installation,qwen-connection,first-run}.md exist (103/103/168 lines); SUMMARY.md links 3 real files; 4부/5부 remain () drafts (9 total); `/opt/homebrew/bin/mdbook build` exit 0 |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `oh-workdir/ping.jsonl` | VERIFIED | 5549 bytes, May 27 17:00; contains "OPENHANDS_PING_OK" 7 times |
| `oh-workdir/dotnet.jsonl` | VERIFIED | 4316 bytes, May 27 17:00; contains "10.0." 3 times |
| `.planning/phases/02-environment-setup-and-verification/02-VERIFICATION-EVIDENCE.md` | VERIFIED | Contains "OPENHANDS_PING_OK" and "10.0.203"; 4 checklist items with verbatim JSONL; not fabricated (cross-checked against raw JSONL files on disk) |
| `.planning/phases/02-environment-setup-and-verification/02-01-SUMMARY.md` | VERIFIED | 188 lines; contains "qwen-local", "1.16.0", "Python 3.12.13", verbatim shell outputs |
| `.planning/phases/02-environment-setup-and-verification/02-02-SUMMARY.md` | VERIFIED | Exists; references evidence file; maps SETUP-01/02/03/04 |
| `src/ch03-setup/installation.md` | VERIFIED | 103 lines; Korean; "uv tool install openhands", "1.16.0", PATH instructions present; Docker framed as GUI-only alternative |
| `src/ch03-setup/qwen-connection.md` | VERIFIED | 103 lines; Korean; "openai/qwen-local", "127.0.0.1:4000", "--override-with-envs", real timing (~15s), 127.0.0.1 loopback explanation present |
| `src/ch03-setup/first-run.md` | VERIFIED | 168 lines; Korean; "OPENHANDS_PING_OK", "dotnet --version", "10.0.203", 4-item checklist, actual timestamps (17:00:13 → 17:00:28), ~15s timing |
| `src/SUMMARY.md` (3부 entries) | VERIFIED | Exactly 3 occurrences of "ch03-setup/"; all 4부/5부/appendix entries remain () (9 draft entries total) |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| openhands CLI | ~/.local/bin on PATH | uv tool shim | WIRED | Live: `command -v openhands` → /Users/ohama/.local/bin/openhands; 02-01-SUMMARY.md confirms |
| litellm proxy | qwen-local model alias | GET /v1/models | WIRED | Live: curl 127.0.0.1:4000/v1/models → MODELS: ['qwen-local'], PASS |
| headless openhands invocation | openai/qwen-local @ 127.0.0.1:4000/v1 | LLM_MODEL/LLM_BASE_URL/LLM_API_KEY + --override-with-envs | WIRED | ping.jsonl on disk; ObservationEvent contains OPENHANDS_PING_OK at exit_code 0 |
| agent TerminalTool (LocalWorkspace) | host dotnet 10.0.x | dotnet --version executed by agent | WIRED | dotnet.jsonl on disk; ObservationEvent content: "10.0.203" at exit_code 0 |
| src/SUMMARY.md 3부 entries | src/ch03-setup/*.md | Markdown links to existing files | WIRED | grep confirms 3 ch03-setup/ links; mdbook build exits 0 with create-missing=false |
| first-run.md checklist | 02-VERIFICATION-EVIDENCE.md real outputs | documented commands match captured invocation exactly | WIRED | Commands in first-run.md (echo OPENHANDS_PING_OK, --override-with-envs, LLM_MODEL=openai/qwen-local) match evidence file invocation verbatim |

---

### Anti-Patterns Found

None. No TODO/FIXME, no placeholder text, no stub patterns in any delivered files. Chapter commands are copy-pasteable and match verified invocations exactly. The fabrication risk was cross-checked: raw JSONL files exist on disk with consistent timestamps (May 27 17:00) and content matching what the evidence document quotes.

---

### Additional Criterion Checks

**Criterion 1 — openhands --version (live):**
Live run confirmed: "OpenHands CLI 1.16.0". Binary at /Users/ohama/.local/bin/openhands.

**Criterion 2 — Proxy live now:**
Live curl confirms `MODELS: ['qwen-local']`, PASS. Evidence file records real ActionEvent+ObservationEvent JSONL (not fabricated — raw ping.jsonl on disk matches).

**Criterion 3 — dotnet 10.0.x in agent observation:**
Evidence records `"text": "10.0.203"` in ObservationEvent. Host also returns 10.0.203. No PATH fallback was needed.

**Criterion 4 — Evidence file not fabricated:**
Cross-check: oh-workdir/ping.jsonl (5549 bytes) and oh-workdir/dotnet.jsonl (4316 bytes) exist on disk with matching timestamps. grep confirms OPENHANDS_PING_OK appears 7 times in ping.jsonl. The conversation IDs and precise timestamps in the evidence document (17:00:13Z-17:00:28Z for ping; 17:00:45Z-17:00:59Z for dotnet) are internally consistent with ~15s runs. Content matches what was quoted.

**Criterion 5 — Timing honest (~15s, not fictional 240s):**
Chapters document "약 15초" and "약 14초" in tables, referencing actual measured runs. The 240s figure appears only in 02-02-PLAN.md as a warning (which proved to be overly conservative). Chapters correctly note that complex multi-tool-call tasks may take longer than single-call tests.

**Criterion 5 — Docker framed as alternative only:**
installation.md: "이 경로에서는 Docker가 필요하지 않습니다" and GUI aside. qwen-connection.md: "Docker 컨테이너를 경유하지 않기 때문에 host.docker.internal이 필요하지 않습니다". Docker is mentioned only to clarify what the reader does NOT need.

**Criterion 5 — 4부/5부 remain () drafts:**
SUMMARY.md has 9 remaining `()` draft entries (예제 프로젝트 소개, 태스크 계획 단계, 코드 작성 단계, 빌드와 테스트 단계, 완성된 계산기, 개념 되짚기, 다음 단계, 부록 A, 부록 B). None converted to real links. mdbook build exits 0.

---

## Summary

Phase 2 fully achieved its goal. The entire headless OpenHands path — uv install, env-var LLM config to openai/qwen-local@127.0.0.1:4000 via --override-with-envs, real tool-call ping, and host dotnet verification — is captured in genuine JSONL evidence files, documented in the evidence markdown, and faithfully reproduced in Korean reader-facing chapters. mdbook builds green. All 5 success criteria pass.

---

_Verified: 2026-05-27_
_Verifier: Claude Sonnet 4.6 (gsd-verifier)_
