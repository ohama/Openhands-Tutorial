# Project Milestones: OpenHands Agentic AI 튜토리얼

## v1 MVP (Shipped: 2026-05-28)

**Delivered:** A Korean mdBook tutorial that teaches agentic AI by walking through a *real, captured* OpenHands run (on a local Qwen 35B) that autonomously builds an F# FsLex/FsYacc calculator — published live on GitHub Pages.

🌐 **Live:** https://ohama.github.io/Openhands-Tutorial/

**Phases completed:** 1–5 (17 plans total)

**Key accomplishments:**

- **1부/2부 — Concepts & architecture:** explained agentic AI (tool calling, agent loop, plan→write→test→run, memory/context) and mapped OpenHands V1 (step() loop, EventLog, ActionEvent/ObservationEvent, workspaces, LiteLLM) to each concept — in Korean.
- **2부 capture-gate environment:** discovered and verified the real stack on a headless SSH Mac — Colima (not Docker Desktop), the existing litellm proxy alias `qwen-local` @ `127.0.0.1:4000`, OpenHands 1.16 headless CLI on **LocalWorkspace** + env-var config — and documented it as the 3부 setup chapter.
- **3부 — Real captured run:** OpenHands autonomously built the calculator across 5 scoped tasks and **self-corrected 4 genuine FsYacc/F# build errors** (RUN-03), ending with `2+3*4=14`, `(2+3)*4=20`, `10-3-2=5`. Honesty held: attempt 1 (the 35B couldn't write FsLex; a manual fix was caught and rejected) is preserved, and attempt 2 was a real agent self-correction.
- **4부 — Worked-example chapter:** the core walkthrough written verbatim from the captured JSONL, with concept↔action callouts, the error-and-fix narration (observed→decided→corrected), the final source, and honest performance numbers.
- **5부 — Troubleshooting, reproducibility & publish:** an honest troubleshooting appendix (6 real failure modes + reconciliation of anticipated-but-didn't-occur), a reproducibility guide, and a GitHub Actions workflow that deploys the book live to GitHub Pages.

**Stats:**

- 21 chapter files, ~2,255 lines of Korean Markdown (mdBook 0.5.3)
- 5 phases, 17 plans, ~40+ tasks
- 72 commits over 2 days (2026-05-27 → 2026-05-28)
- Phase 2 was re-planned once (Docker-Desktop → verified LocalWorkspace path); Phase 3 ran twice (attempt 1 rejected for honesty, attempt 2 a genuine agent self-correction)

**Git range:** `7b213ad` (docs: initialize project) → `milestone-v1` tag

**Process note (the honesty thread):** the project's core value was an honest, real capture, and the workflow held to it — a manual fix that would have faked RUN-03 was rejected and re-run properly, and the milestone audit caught a cross-part contradiction (2부 still described the pre-pivot Docker path) and fixed it before shipping.

**What's next:** v2 candidates (deferred): EXT-01 more worked examples, EXT-02 English translation, EXT-03 a "build your own minimal agent in F#" appendix, EXT-04 local-vs-cloud model comparison.

---
