---
milestone: v1
audited: 2026-05-28
status: passed
scores:
  requirements: 20/20
  phases: 5/5
  integration: 5/5 (3 gaps found during audit, all fixed)
  flows: live site E2E all 200
gaps_found_and_fixed:
  - id: GAP-1
    file: src/ch02-openhands/runtime.md
    issue: "DockerWorkspace row labeled '이 튜토리얼' but the tutorial actually used LocalWorkspace"
    fix: "Moved 'this tutorial' label to LocalWorkspace; added note that DockerWorkspace internals are OpenHands' default isolation model (used by openhands serve GUI)"
  - id: GAP-2
    file: src/ch02-openhands/llm-integration.md
    issue: "Said OpenHands runs in Docker with base URL host.docker.internal:8000; real setup is LocalWorkspace + litellm proxy at 127.0.0.1:4000"
    fix: "Base URL corrected to http://127.0.0.1:4000/v1 with LocalWorkspace framing; host.docker.internal kept as the documented Docker-mode alternative; model example → openai/qwen-local; 다음 단계 updated to env-var/headless (not GUI)"
  - id: GAP-3
    file: src/appendix-a-repro.md
    issue: "Minor: '약 6분' (active task sum) vs 4부 '약 10분' (wall-clock) unexplained"
    fix: "Added parenthetical clarifying active-time vs wall-clock"
tech_debt:
  - area: publishing
    items:
      - "macOS Keychain '-25308' warning on git push (cosmetic; `gh auth setup-git` would silence)"
      - ".planning/ history is public per author's explicit 'Publish everything' choice (reversing now = history rewrite)"
      - "deploy.yml uses Node-20 actions (checkout@v4 etc.) — GitHub deprecation notice; bump before Sept 2026"
  - area: scope (deferred to v2, already tracked)
    items:
      - "EXT-01 more examples; EXT-02 English translation; EXT-03 'build your own agent in F#'; EXT-04 local-vs-cloud comparison"
---

# Milestone v1 Audit — OpenHands Agentic AI 튜토리얼

**Status: PASSED** (3 integration gaps found during the audit were fixed in-place; book rebuilt clean and redeployed.)

## Definition of Done (from ROADMAP)
A Korean mdBook on GitHub Pages that teaches agentic AI through a real, verifiable OpenHands run building an F# FsLex/FsYacc calculator. → **Achieved.** Live: https://ohama.github.io/Openhands-Tutorial/

## Requirements coverage — 20/20 Complete
All v1 requirements (CONCEPT-01..03, SETUP-01..04, RUN-01..03, WALK-01..03, VERIFY-01/02, TROUBLE-01, REPRO-01, BOOK-01..03) verified Complete in REQUIREMENTS.md traceability; 0 Pending.

## Phase verifications — 5/5 passed
Every phase has a VERIFICATION.md with status: passed (1: scaffold/concepts; 2: env setup; 3: captured run; 4: worked-example; 5: troubleshooting/repro/publish).

## Cross-phase integration & E2E (gsd-integration-checker)
- Navigation: SUMMARY wires all 21 files; zero draft entries; `mdbook build` clean. ✓
- Forward-pointer payoff: all four 1부 concept forward-pointers paid off by 4부 callouts. ✓
- Evidence ↔ chapter fidelity: cited error strings (FSY000, FS0039 LexBuffer.FromText, FsLex '%', file_editor security_risk) and outputs (14/20/5) trace to Phase-3 captured artifacts. ✓
- Live site E2E: index + one page per part + fingerprinted CSS all return 200; lang="ko". ✓
- Consistency: **3 gaps found in 2부 (ch02), all fixed** (see frontmatter) — ch02 was written in Phase 1 before the Phase-2 LocalWorkspace/proxy reality was known, and described the DockerWorkspace path as "this tutorial." Now reconciled with 3부/4부/appendices.

## Conclusion
Milestone goal achieved and internally consistent. Remaining items are tracked tech debt (cosmetic/publishing) and already-deferred v2 extensions — none are blockers. Ready to complete/archive.
