---
phase: 01-scaffold-and-concept-chapters
verified: 2026-05-27T00:00:00Z
status: passed
score: 5/5 must-haves verified
---

# Phase 1: Scaffold & Concept Chapters — Verification Report

**Phase Goal:** The mdBook structure exists and the run-independent chapters (what agentic AI is; vocabulary; OpenHands V1 architecture) are written, in Korean, and `mdbook build` succeeds.
**Verified:** 2026-05-27
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `mdbook build` exits 0 with no missing-file or broken-link errors | VERIFIED | Build output: "HTML book written to /book", EXIT: 0, no errors |
| 2 | overview.md defines agentic AI and distinguishes it from a reactive chatbot | VERIFIED | 68 lines; "챗봇" appears 7×; explicit 반응형 chatbot vs 에이전틱 AI contrast in opening paragraph |
| 3 | concepts.md defines four terms each with a PROSE forward pointer to 4부 (no Markdown links to draft files) | VERIFIED | 104 lines; "4부" appears 10×; four term headings present; zero `]()` or `](../ch0[345]` links |
| 4 | ch02 files map step() loop, EventLog, DockerWorkspace to vocabulary terms; V1 only, no docker_sandbox | VERIFIED | All five files present and substantive; "step()" in agent-loop.md; 5 phases named; "ActionEvent" 5×; "DockerWorkspace" 5×; "LiteLLM" 5×; "host.docker.internal" 2×; zero "docker_sandbox" hits |
| 5 | All prose is Korean (Hangul present); English allowed for technical terms | VERIFIED | All 7 chapter files match Hangul grep pattern; about.md also contains Hangul |

**Score:** 5/5 truths verified

---

## Required Artifacts

| Artifact | Min Lines | Actual Lines | Status | Key Content Check |
|----------|-----------|--------------|--------|-------------------|
| `book.toml` | — | 19 | VERIFIED | `create-missing = false` ✓, `language = "ko"` ✓, `site-url = "/OpenHandsTests/"` ✓ |
| `src/SUMMARY.md` | — | 41 | VERIFIED | Phase 1 chapters have real paths; 12 draft `()` entries for parts 3/4/5/appendix; no Korean characters in any path |
| `src/about.md` | 10 | 35 | VERIFIED | Korean prose; covers 목적/독자/선행 지식/구성 |
| `.gitignore` | — | — | VERIFIED | Contains `book/` |
| `src/ch01-agentic-ai/overview.md` | 40 | 68 | VERIFIED | H1 `# 에이전틱 AI 개요`; explicit chatbot vs agentic AI contrast; Hangul present |
| `src/ch01-agentic-ai/concepts.md` | 60 | 104 | VERIFIED | H1 `# 핵심 개념과 용어`; all four terms present; "4부" appears 10×; zero dead/draft links |
| `src/ch02-openhands/overview.md` | 25 | 52 | VERIFIED | H1 `# OpenHands 개요`; four-package SDK described; Hangul present |
| `src/ch02-openhands/agent-loop.md` | 45 | 65 | VERIFIED | H1 `# 에이전트 루프 상세`; "step()" present; all five phases (DRAIN/USER BLOCK/PREPARE/CALL LLM/CLASSIFY & DISPATCH) named; EventLog + condensation explained; explicit mapping "이 step() 루프가 곧 1부에서 말한 agent loop입니다" |
| `src/ch02-openhands/actions-observations.md` | 40 | 67 | VERIFIED | H1 `# 액션과 관찰 타입`; "ActionEvent" 5×; self-correction explanation present; link to concepts.md ✓ |
| `src/ch02-openhands/runtime.md` | 30 | 55 | VERIFIED | H1 `# 런타임과 샌드박스`; "DockerWorkspace" 5×; "tmux" 2×; link to concepts.md ✓ |
| `src/ch02-openhands/llm-integration.md` | 25 | 48 | VERIFIED | H1 `# LLM 연동: LiteLLM`; "LiteLLM" 5×; "openai/" prefix documented; "host.docker.internal" 2× |

---

## Key Link Verification

| From | To | Via | Status |
|------|----|-----|--------|
| `book.toml` | GitHub Pages project URL | `site-url = "/OpenHandsTests/"` | VERIFIED — 404.html has `<base href="/OpenHandsTests/">` confirming site-url is applied |
| `src/SUMMARY.md` | Phase 2-5 chapters | Draft `()` hrefs | VERIFIED — 12 draft entries; build succeeds with create-missing=false |
| `src/ch01-agentic-ai/concepts.md` | 4부 walkthrough | PROSE forward pointers per term (word "4부") | VERIFIED — "4부" appears 10×; zero Markdown links to draft files |
| `src/ch02-openhands/agent-loop.md` | `src/ch01-agentic-ai/concepts.md` | Relative Markdown link + explicit mapping statement | VERIFIED — `[핵심 개념과 용어](../ch01-agentic-ai/concepts.md)` present; "이 step() 루프가 곧 1부에서 말한 agent loop입니다" |
| `src/ch02-openhands/llm-integration.md` | Local Qwen endpoint | `openai/` prefix + `host.docker.internal:8000/v1` | VERIFIED |
| All `src/` files | Phase 2-5 draft chapters | NO Markdown links to draft files | VERIFIED — zero `](../ch0[345]` or `]()` links in any src/ chapter file |

---

## Anti-Patterns Found

| File | Pattern | Severity | Status |
|------|---------|----------|--------|
| All chapter files | TODO / FIXME / placeholder | — | None found |
| All chapter files | `return null` / empty implementations | — | N/A (Markdown prose, not code) |
| `src/SUMMARY.md` | Korean chars in file paths | — | None found (all paths are ASCII kebab-case) |
| `src/ch02-openhands/*.md` | V0 term "docker_sandbox" | — | None found |

No blockers. No warnings.

---

## Criterion-by-Criterion Report

### Criterion 1: `mdbook build` exits 0

PASSED. Build output: `INFO HTML book written to /Users/ohama/projs/OpenHandsTests/book`, exit code 0. No "Summary parsing failed", "file not found", or broken-link warnings.

### Criterion 2: concept chapter (overview.md) defines agentic AI, distinguishes from reactive chatbot

PASSED. `src/ch01-agentic-ai/overview.md` (68 lines) opens with an explicit chatbot-vs-agentic-AI framing in the first sentence. "챗봇" appears 7 times; "루프" appears 3 times. The contrast covers: single response vs loop, text only vs environment actions, human-directed vs self-directed, stateless vs memory-holding.

### Criterion 3: vocabulary chapter (concepts.md) defines four terms with PROSE forward pointers

PASSED. `src/ch01-agentic-ai/concepts.md` (104 lines) defines all four required terms under H2 headings. "4부" appears 10 times (well above the required ≥4). Zero Markdown links to draft files (`]()` or `](../ch0[345]`).

### Criterion 4: ch02 architecture chapter maps step(), EventLog, DockerWorkspace to vocabulary; V1 only

PASSED.
- `agent-loop.md`: Contains "step()", all five loop phases named, EventLog + condensation explained, explicit "이 step() 루프가 곧 1부에서 말한 agent loop입니다" mapping.
- `actions-observations.md`: "ActionEvent" present (5×), self-correction via observation loop explained.
- `runtime.md`: "DockerWorkspace" present (5×).
- `llm-integration.md`: "LiteLLM" (5×), "host.docker.internal" (2×).
- V0 check: zero "docker_sandbox" occurrences across all ch02 files.

### Criterion 5: All prose is Korean (Hangul present)

PASSED. Hangul pattern match confirmed in all 7 chapter files and about.md. Technical terms (step(), EventLog, ActionEvent, DockerWorkspace, LiteLLM, etc.) remain in English as required.

---

## Notes

- The PLAN.md (01-01) predicts 13 draft entries in SUMMARY.md; actual count is 12. The discrepancy is in the PLAN estimate, not the implementation — the spec template in the same PLAN shows exactly the 12 entries that were written (3부: 3, 4부: 5, 5부: 2, appendix: 2). The build succeeds, all required entries are present, and create-missing=false is satisfied.
- `book/index.html` does not show `/OpenHandsTests/` asset prefixes when built locally (assets use relative paths for local serving); the project site-url is correctly reflected in `book/404.html` with `<base href="/OpenHandsTests/">`, which is the correct mdBook 0.5.x behavior for project Pages URLs.

---

## Human Verification Required

None. All success criteria are verifiable programmatically and all passed.

---

_Verified: 2026-05-27_
_Verifier: Claude (gsd-verifier)_
