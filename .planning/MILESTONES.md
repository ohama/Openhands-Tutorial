# Project Milestones: OpenHands Agentic AI 튜토리얼

## v1.1 Model Comparison (Shipped: 2026-05-28)

**Delivered:** A real captured **122B** OpenHands run of the same FsLex/FsYacc calculator — with the `.fsl` lexer attempted **unaided first** (122B succeeded where the 35B could not) — and a **35B-vs-122B comparison chapter (부록 C)** added to the published tutorial, backed by verbatim citations from both runs. Beginner-friendly 📨/⚙️/✅ callouts also added across the run-walkthrough chapters.

🌐 **Live:** https://ohama.github.io/Openhands-Tutorial/appendix-c-comparison.html

**Phases completed:** 6–7 (6 plans total)

**Key accomplishments:**

- **Phase 6 — 122B capture (unaided-first protocol):** OpenHands on the local Qwen 122B ran through the same 5-task pipeline as the 35B baseline, but with `task2-lexer-unaided.txt` — no provided lexer body, no FsLex API hints. The agent wrote structurally valid FsLex on its first attempt (`rule tokenize = parse`, no `%%`). The scaffold-fallback path was prepared but **never triggered**.
- **Phase 6 — genuine error-fix cycle:** task5 hit FsLex `lexbuf.Lexeme` API confusion and self-corrected through **9 iterations** (events 12–74 in `task5-buildtest.jsonl`): `int s` → `Lexing.matched` → `matchedText` → `lexbuf.ToString()` → `lexbuf.Lexeme` → `new string(lexbuf.Lexeme)` (final working). Outcome: 14/20/5 PASS, confirmed in JSONL events 76/78/80 and an independent host re-run. Zero manual edits to any agent-written file.
- **Phase 7 — 부록 C comparison chapter (honest):** Korean comparison chapter (`src/appendix-c-comparison.md`) contrasts 35B vs 122B on capability (did the model write the lexer unaided?), error-fix cycle shape, and **real measured per-call timing** — derived from both runs' JSONL timestamps (35B ≈ 5.3s/call, 122B ≈ 6.3s/call). Every numeric claim verbatim-traced; setup asymmetry (35B was scaffolded, 122B was not) explicitly disclosed at the top before any capability claim. The legacy "~14–32s/cycle" pre-run estimate from v1 is corrected here (and in the README) with a clear pre-run-prediction-vs-measured-data disclaimer.
- **Out-of-band — beginner UX callouts:** added `📨 사용자 프롬프트 / ⚙️ 내부 프로세스 / ✅ 결과` blockquote pattern to 4 chapters (writing.md, build-test.md, final.md, appendix-c-comparison.md) so a beginner can see the agentic loop structure at a glance. 7 callout groups, all grounded in real captured task prompts and JSONL events.
- **Milestone audit — PASSED:** 7/7 requirements satisfied, 12/12 cross-phase wiring connections verified (every cited source file matches verbatim), 5/5 E2E reader flows complete, all 6 honesty checks green, v1↔v1.1 narrative consistency confirmed. 5 deferrable tech-debt items logged (none reader-facing, none affecting honesty); TD-1 was closed during milestone completion.

**Stats:**

- 1 new chapter file (`src/appendix-c-comparison.md`, ~380 lines Korean Markdown after UX callouts) + 3 chapters modified for UX callouts + 1 SUMMARY.md entry + README.md refresh
- 2 phases, 6 plans, agent-driven captured run (150 TerminalActions / 1229s for 122B)
- 26 commits over ~5 hours on 2026-05-28 (same day v1 shipped)
- 122B per-call avg ≈ 6.3s; 35B per-call avg ≈ 5.3s (per-call timing comparable; run-total difference came from iteration count, not speed — a more nuanced result than the milestone's starting hypothesis)

**Git range:** `1a6ee20` (chore: complete v1 milestone) → `milestone-v1.1` tag (this milestone)

**Process note:** the milestone's honesty discipline held end-to-end — the manual-fix prohibition, source-verbatim-citation requirement, and explicit asymmetry disclosure were all enforced by per-plan verification guards and re-checked by the final milestone audit. One audit tech-debt item (TD-1: missing 06-02-SUMMARY.md) was closed before archive by writing the artifact retroactively with a clear `retro_written: true` marker — no fabrication of contemporaneous notes.

**What's next:** Open milestone candidates (no commitment): EXT-01 more worked examples, EXT-02 English translation, EXT-03 "build your own minimal agent in F#" appendix, EXT-04 local-vs-cloud model comparison. Or polish: address the 4 remaining deferrable tech-debt items from v1.1-MILESTONE-AUDIT.md (TD-2 through TD-5).

---

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
