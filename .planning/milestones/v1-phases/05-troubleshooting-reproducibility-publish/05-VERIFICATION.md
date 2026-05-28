---
phase: 05-troubleshooting-reproducibility-publish
verified: 2026-05-28T01:21:44Z
status: passed
score: 4/4 must-haves verified
---

# Phase 5: Troubleshooting, Reproducibility & Publish — Verification Report

**Phase Goal:** The book is complete with troubleshooting + reproducibility chapters, builds cleanly, and is live on GitHub Pages.
**Verified:** 2026-05-28T01:21:44Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | TROUBLE-01: Appendix B covers 6 real failure modes with diagnosis+fix and honest reconciliation of anticipated-but-didn't-occur items | VERIFIED | 274 lines; all 6 REAL items present; §4 reconciliation names host.docker.internal, timeout/240s, .NET sandbox, %left — each explicitly marked did-not-occur |
| 2 | REPRO-01: Appendix A gives exact prereqs, env-var headless invocation, task-prompt pointers, verbatim expected outputs | VERIFIED | 193 lines; test-output.txt values (2+3*4=14, (2+3)*4=20, 10-3-2=5) match captured/test-output.txt verbatim; model cited as "Qwen 35B(qwen36-35b)" — no "Qwen2.5" |
| 3 | SC#3: mdbook build exits 0; SUMMARY.md has no draft () entries; all parts wired including ch05-wrap-up, 부록 A, 부록 B | VERIFIED | `mdbook build` → EXIT 0; zero empty `[]()` links in SUMMARY.md; all five parts + two appendices wired |
| 4 | BOOK-03 / live deploy: deploy.yml valid; live site returns 200 for index, chapter pages, appendices, and hashed CSS; lang="ko" present | VERIFIED | All curl checks return 200; css/general-0392ca55.css → 200; lang="ko" confirmed in live index.html |

**Score:** 4/4 truths verified

---

## Required Artifacts

| Artifact | Min Lines | Actual Lines | Status | Notes |
|----------|-----------|--------------|--------|-------|
| `src/appendix-b-troubleshooting.md` | 90 | 274 | VERIFIED | 6 real failure modes + §4 reconciliation |
| `src/appendix-a-repro.md` | — | 193 | VERIFIED | Prereqs, invocation, prompts, verbatim outputs |
| `src/ch05-wrap-up/review.md` | 20 | 67 | VERIFIED | 4 agentic concepts recap in Korean prose |
| `src/ch05-wrap-up/next-steps.md` | 20 | 55 | VERIFIED | Next-steps suggestions, prose refs to 부록 A |
| `.github/workflows/deploy.yml` | — | exists | VERIFIED | deploy-pages@v4, pages:write + id-token:write |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| appendix-b-troubleshooting.md | captured run evidence | verbatim error strings | VERIFIED | security_risk (5 hits), FSY000, FS0039, LexBuffer FromText, Unexpected character '%' all present and match 03-02-RUN-NOTES files |
| appendix-a-repro.md | captured/test-output.txt | verbatim expected output | VERIFIED | "2+3*4 = 14", "(2+3)*4 = 20", "10-3-2 = 5" match test-output.txt exactly |
| SUMMARY.md | all src/*.md files | mdBook wiring | VERIFIED | Build exits 0; zero draft () links |
| deploy.yml | GitHub Pages | actions/deploy-pages@v4 | VERIFIED | Correct permissions (pages:write, id-token:write) |
| live site | all chapter pages | GitHub Pages CDN | VERIFIED | index, ch01/overview.html, ch04/final.html, appendix-a-repro.html, appendix-b-troubleshooting.html all 200 |

---

## Honesty / Content Accuracy Checks

### TROUBLE-01 specifics

- "240s" appears exactly twice in appendix-b, both times framed as an unmeasured estimate that did not hold — never as a real measured figure. Pass.
- Reconciliation section (§4) explicitly covers all four anticipated-but-didn't-occur items: host.docker.internal, timeout storm, .NET sandbox, %left precedence bug. Each labeled did-not-occur. Pass.
- No fabricated failure presented as real. Pass.

### REPRO-01 specifics

- Model cited as "Qwen 35B(qwen36-35b)" — matches PROJECT.md and STATE.md identifiers. No "Qwen2.5" or "Qwen2" appears in either appendix. Pass.
- Verbatim expected outputs (2+3*4 = 14, (2+3)*4 = 20, 10-3-2 = 5) match captured/test-output.txt byte-for-byte. Pass.
- env-var headless invocation with --override-with-envs, LLM_MODEL="openai/qwen-local", --yolo, --headless --json present and correct. Pass.
- Task-prompt pointers give canonical paths under .planning/phases/03-capture-the-openhands-run/task-prompts/. Pass.

### SC#3: SUMMARY.md wiring

- `grep -c '()' src/SUMMARY.md` returns 0 (the success criterion literal). Python regex scan for `\[.*?\]\(\)` also returns 0 empty destination links. All 13 entries in SUMMARY.md have real file paths. Pass.
- 5부 includes both ch05-wrap-up/review.md and ch05-wrap-up/next-steps.md. Pass.
- 부록 A and 부록 B both linked. Pass.

### BOOK-03: Live deploy

- https://ohama.github.io/Openhands-Tutorial/ → 200
- ch01-agentic-ai/overview.html → 200
- ch04-calculator/final.html → 200
- appendix-a-repro.html → 200
- appendix-b-troubleshooting.html → 200
- css/general-0392ca55.css (actual fingerprinted asset from live index.html) → 200
- lang="ko" present in live index.html. Pass.

---

## Anti-Patterns Found

None blocking. No TODO/FIXME/placeholder in appendix-b or appendix-a. No empty handlers or stub returns — these are documentation files (Korean prose + code blocks).

---

## Human Verification Required

None. All four success criteria are verifiable programmatically for this phase (documentation content + build + live site curl checks).

---

## Summary

All four must-haves verified. Phase 5 goal achieved:

- Appendix B is honest and complete: 6 real failure modes with diagnosis and fix, verbatim error strings matching captured evidence, and an explicit §4 reconciliation naming all four anticipated-but-didn't-occur items. The 240s figure appears only as a disclaimed unmeasured estimate.
- Appendix A is accurate: exact invocation, verbatim expected outputs from captured/test-output.txt, model cited correctly as qwen36-35b / Qwen 35B without unverified Qwen2.5 attribution.
- The book builds cleanly (mdbook exit 0) with a fully wired SUMMARY.md and no draft entries.
- The live GitHub Pages site serves all pages and hashed assets at 200, with lang="ko".

---

_Verified: 2026-05-28T01:21:44Z_
_Verifier: Claude (gsd-verifier)_
