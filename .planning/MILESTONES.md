# Project Milestones: OpenHands Agentic AI 튜토리얼

## v1.4 Planning Comparison (Shipped: 2026-06-04)

**Delivered:** An honest, captured **A/B study of task planning** on the local Qwen **35B** — **Arm A** (Claude-authored plan → 35B executes) vs **Arm B** (35B self-plans via its task tracker + executes) — across all three existing worked examples (F# FsLex/FsYacc calculator, Rust HTTP server, Scala 3 calculator), published as **부록 D "계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획"**. The research question was framed honestly as *"does an expert-authored plan help the 35B execute?"* — not "Claude plans better."

🌐 **Live:** https://ohama.github.io/Openhands-Tutorial/appendix-d-planning-comparison.html

**Phases completed:** 12–14 (10 plans total)

**Key accomplishments:**

- **Phase 12 — harness proven on a Rust pilot:** two prompt templates sharing an identical control block (only the planning input differs), enforced by a literal `CONTROL-BLOCK SYMMETRY: PASS` diff; `metrics_extractor.py` (1-based, self-validated) + a mechanical `source=agent` honesty gate; arm-isolated gitignored workspaces; one CodeActAgent invocation per arm. Both arms passed curl→hello. **Resolved both open unknowns:** the 35B self-plans via TaskTracker at the Arm B phrasing (no prompt change needed), and there is **no token `usage` in the JSONL** → P3 token metrics dropped.
- **Phase 13 — the full study, captured honestly at n=3:** F# + Scala both arms n=3, Rust topped to n=3 — **18 real JSONL captures**, counterbalanced run order, one invocation per run, judged from the JSONL (never the CLI exit code). 18/18 `source=agent` honesty gates PASS. Honest outcomes preserved including F# OOD failures; both planning artifacts saved per example (`claude-plan.md` + verbatim `oh-self-plan.md` from the TaskTracker), plus the ANAL-02 qualitative plan comparison and a CAPTURE-MANIFEST gate.
- **Phase 13 — caught and fixed a measurement-tool bug (honesty save):** the reused Phase-12 canonical detector mis-scored — heredoc first-match produced false-negative Scala FAILs and **null** F# cells that would have blocked the capture gate. The detector was fixed deterministically (genuine run-command match + "any successful run" semantics + build-never-ran ⇒ FAIL-not-null) and **all 18 runs re-extracted** (user-approved, `b7a74b9`), reproducing the JSONL-event-cited RUN-NOTES outcomes exactly with zero nulls.
- **Phase 14 — 부록 D written verbatim + published:** a 287-line Korean appendix built entirely from the committed `captured-planning/` artifacts (every number traces to `comparison.json`/CAPTURE-MANIFEST; 1-based event numbers; `~14–32s/call` never cited as a measurement; mixed/inconclusive results reported, not softened). Wired after 부록 C, clean `mdbook build`, deployed live (Actions run 26924773565); existing 1부–7부 + 부록 A/B/C byte-unchanged; `deploy.yml` untouched.
- **The finding (mixed/inconclusive — itself the result):** an expert-authored plan helps the 35B mainly when the task is **out-of-distribution** — F# Arm A 1/3 reps PASS vs Arm B 0/3 (the lone F# success came from the Claude plan navigating FsLex/FsYacc wiring). For **in-distribution** work the 35B self-plans just as well — Scala Arm A 3/3 vs Arm B 2/3 + 1 PARTIAL; Rust both arms 3/3 with zero error-fix cycles. This extends the standing **"capability is domain-distribution, not model size"** thesis onto the *planning* axis. Timing carried a cache/run-order confound and was explicitly not read as a planning-quality signal.
- **Milestone audit — PASSED (12/12 requirements, integration 6/6):** the recurring 1-based event-numbering tech debt did **not** recur this time. Six non-blocking cosmetic TDs carried forward (TD-11 vacuous gate assertion; TD-12 `__pycache__` gitignore; TD-13 batch-vs-individual event citation; plus 부록 C TD-2/TD-3/TD-5).

**Stats:**

- 부록 D: 1 new chapter (`src/appendix-d-planning-comparison.md`, 287 lines) + 1-line SUMMARY.md wiring; `captured-planning/` under the Phase-13 archive: 18 run JSONLs + 18 per-run metrics + 6 per-arm metrics.json + 3 comparison.json + 6 planning artifacts + PLAN-COMPARISON-QUALITATIVE.md + CAPTURE-MANIFEST.md + metrics_extractor.py (patched) + aggregate_metrics.py
- 3 phases, 10 plans, ~14 task commits (30 commits total incl. docs) over 2026-06-02 → 2026-06-04
- Study scale: 18 captured runs (6 example×arm cells × n=3). Single-model (35B). No token metrics (no `usage` in JSONL).

**Git range:** `milestone-v1.3` tag → `milestone-v1.4` tag

**Process note:** This was the first milestone whose object of study was the **planning step itself**, not a new program — every prior milestone used Claude-authored task decomposition without testing whether it helped. The one genuine wrinkle (a buggy reused measurement tool) was caught before the gate and fixed by patching the tool + re-running all captures, never by hand-editing outputs.

**What's next:** Open candidates (no commitment): **EXT-08** extend the planning comparison to the 122B or add the SDK `PlanningAgent` as a third arm; **EXT-07** cross-language "calculator in 3 languages" appendix; **EXT-01** more-language examples (Go/Python); **EXT-06** 35B-vs-122B on Rust/Scala; **EXT-02** English translation; or sweep the carried 부록 C debt (TD-2/TD-3/TD-5) + v1.4 cosmetics (TD-11/TD-12/TD-13).

---

## v1.3 Scala Example (Shipped: 2026-06-01)

**Delivered:** A third worked example — the same local Qwen **35B** built a minimal **Scala 3 arithmetic calculator** (`scala-cli`, hand-rolled recursive-descent parser, std-only), captured honestly and published as **7부 "다른 워킹 예제 - Scala 계산기"**. This **completes the "calculator trilogy"**: the model that needed a scaffolded FsLex lexer for the *F# calculator* in v1 wrote the *same calculator* in Scala **unaided on attempt 1**.

🌐 **Live:** https://ohama.github.io/Openhands-Tutorial/ch07-scala-calc/intro.html

**Phases completed:** 10–11 (6 plans total)

**Key accomplishments:**

- **Phase 10 — 35B Scala capture (unaided):** preflight installed/verified `scala-cli` 1.14.0 (Scala 3.8.3) + pre-warmed the artifact cache, then captured a 3-task run. The 35B verified scala-cli itself (task1, Scala 3 `@main def`), then wrote a **70-line idiomatic Scala 3 recursive-descent calculator unaided** (task2) — `@main def calc`, significant-indentation `class ExprParser:`, `if/then`, `while/do`, `match` on `Option[Char]`; **correct operator precedence AND left-associativity** (avoided the naive right-recursive `10-3-2→9` bug). Scaffold staged but **never invoked**; 36/36 ActionEvents `source=agent`.
- **Phase 10 — one genuine, teachable error-and-fix:** task3 hit a single compile error — `variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level` (the unaided source declared `private var pos`, accessed from `@main`). The agent **self-corrected with its own `sed`** (drop `private`), recompiled, and **all three canonical tests passed: `2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5`**. Host re-run reproduced 14/20/5.
- **Phase 11 — 7부 chapter (verbatim, honest):** 5-file chapter group (~664 lines) written from `captured-scala/` — Scala code **byte-identical** to `final-source/Calc.scala`, compile error verbatim, manifest 1-based event numbers, `사용자 프롬프트/내부 프로세스/결과` callouts (no emoji). It honestly notes the agent used **no `sealed trait` ADT** (the roadmap's pre-run assumption) and frames the contrast as "hand-rolled recursive descent (unaided)" vs 4부's "FsLex/FsYacc DSL (scaffolded, 94+27+16 failed TerminalActions)". Live on Pages.
- **Thesis confirmed — capability is distribution, not size:** the 35B failed FsLex (out-of-distribution DSL) but succeeded at both Rust (v1.2) and Scala (v1.3) unaided. The errors it *does* make are teachable, in-distribution mistakes (borrow-checker; access modifiers), not deep capability failures. The book now ends on a direct calculator-to-calculator comparison across three languages.
- **Milestone audit — caught + closed a cross-chapter contradiction:** the integration check found 7부 `final.md` dated the v1.2 Rust run `2026-06-01` (should be `2026-05-28`, per 6부 + the Rust manifest) — TD-9 — plus a cosmetic wrong arithmetic for the ~5.0s/call figure (TD-10). Both fixed, rebuilt, redeployed (run 26741929202), verified live. Notably, the two honesty items that were *prior* tech debt — event-numbering drift (v1.2 TD-7/TD-8) and the `~14–32s/call` prediction-as-measurement (v1.2 TD-6) — were both **correct this time** without needing audit fixes.

**Stats:**

- 7부 chapter: 5 new files (`src/ch07-scala-calc/*.md`, ~664 lines) + SUMMARY.md entry; `captured-scala/`: 11 tracked artifacts (3 JSONL + stderr + final-source Calc.scala/Hello.scala + manifest + transcript + host test-output)
- 2 phases, 6 plans; 24 commits over ~3 hours on 2026-06-01
- 35B Scala run: 30 TerminalActions / 234.8s active agent time; ~5.0s/call (weighted LLM-call-gap avg). Single-model run (35B only).

**Git range:** `milestone-v1.2` tag → `milestone-v1.3` tag

**Process note:** Phase 10 was a live local-35B capture driven directly via the OpenHands headless CLI (backgrounded per task, JSONL-polled). It went cleanly on the first attempt — unaided success with one self-corrected error — so no honesty escalations (no scaffold, no rejected attempt) were needed, unlike v1's F# capture. The single defect that reached publish (a copy-paste date error in the trilogy table) was caught by the milestone audit and fixed same-day.

**What's next:** Open candidates (no commitment): **EXT-07** a cross-language "calculator in 3 languages" comparison appendix (F# / Scala / + future) — now natural since the trilogy is complete; **EXT-01** more-language examples (Go / Python); **EXT-06** a 35B-vs-122B comparison on Rust or Scala; **EXT-02** English translation; or polish the carried v1.1 appendix-C debt (TD-2…TD-5).

---

## v1.2 Rust Example (Shipped: 2026-06-01)

**Delivered:** A second worked example for the tutorial — the same local Qwen **35B** that built the F# calculator now autonomously builds a minimal **std-only Rust HTTP server** (`GET / → "hello\n"`), captured honestly and published as a new **6부 "다른 워킹 예제 - Rust HTTP 서버"**. The milestone's thesis held: the model that **could not** write FsLex unaided in v1 wrote a working Rust server **unaided on attempt 1** — Rust is more in-distribution than FsLex.

🌐 **Live:** https://ohama.github.io/Openhands-Tutorial/ch06-rust-server/intro.html

**Phases completed:** 8–9 (6 plans total)

**Key accomplishments:**

- **Phase 8 — 35B Rust capture (unaided-first):** OpenHands on the local Qwen 35B ran `cargo new` → wrote `src/main.rs` → built/tested, captured as 3 per-task JSONL (`task1-scaffold`, `task2-server`, `task3-buildtest`). The agent wrote a 43-line server using `std::net::TcpListener` + `BufReader` on **unaided attempt 1** (task2 event #13); the scaffold fallback was prepared but **never invoked**. Honesty gate PASSED — all 28 ActionEvents `source=agent`, zero manual edits.
- **Phase 8 — genuine error-and-fix cycle:** two real build failures self-corrected with no human help — (1) a `format!` heredoc syntax artifact (`unexpected closing delimiter`, event #16): two `sed` patches failed silently, the agent detected the unchanged file and escalated to a full heredoc rewrite; (2) a genuine borrow-checker error (`E0382: use of moved value: reader`, event #28: `reader.lines()` consumed twice) fixed with a single `Lines` iterator. Build PASS (event #32); `curl` → `hello\nEXIT_CODE=0` exit 0 (#37/#38); independent host re-run confirmed `HTTP/1.1 200 OK`, `Content-Length: 6`.
- **Phase 9 — 6부 chapter (verbatim, honest):** new "다른 워킹 예제 - Rust HTTP 서버" chapter group (5 sections, ~605 lines Korean Markdown) written verbatim from the captured evidence — server code **byte-identical** to `final-source/src/main.rs`, both compiler errors quoted verbatim, `사용자 프롬프트 / 내부 프로세스 / 결과` callouts (no pictograph emoji), concept↔action pairing to 1부/2부. Wired into SUMMARY.md, `mdbook build` clean, live on GitHub Pages.
- **Thesis confirmed (same model, different language):** the 35B that failed FsLex (deeply out-of-distribution) succeeded at std Rust (in-distribution). Per-call latency is comparable (~3.8s/call Rust vs ~5.3s/call v1 F#); the run-total difference comes from **call count**, not per-call speed — the Rust task needed far fewer iterations.
- **Milestone audit — caught + closed a cross-chapter honesty regression:** the audit found 6부 had re-introduced v1's deprecated `~14–32s/call` **pre-run prediction** as if it were a v1 *measurement* (the exact number v1.1 had already corrected), contradicting 부록 C. Fixed to the derived `~5.3s/call` baseline with a disclosure note, reconciling 6부 / 부록 C / the Phase 8 manifest. Two cosmetic items also closed (TD-7 task3 event count 41→36 JSON objects + numbering footnote; TD-8 unverifiable per-action event indices removed). Rebuilt clean, redeployed, verified live (7/7 requirements, 2/2 phases, 5/5 integration after fix).

**Stats:**

- 6부 chapter: 5 new files (`src/ch06-rust-server/*.md`, ~605 lines) + SUMMARY.md entry; `captured-rust/`: 12 tracked artifacts (3 JSONL + stderr + final-source + manifest + transcript + host test-output)
- 2 phases, 6 plans; 26 commits over 4 days (2026-05-28 → 2026-06-01)
- 35B Rust run: 62 JSON events / 26 TerminalActions / 113.4s active agent time; per-call ~3.8s avg (range 1.2–7.7s)
- Single-model run (35B only) — a 122B Rust comparison was deliberately deferred (EXT-06)

**Git range:** `milestone-v1.1` tag → `milestone-v1.2` tag

**Process note:** a flaky tool-output channel during `/gsd:plan-phase 9` caused an early verify loop to race against an as-yet-empty phase directory and let a first draft of plan 09-01 bake in wrong evidence paths/event-counts. This was caught, re-grounded against `CAPTURE-MANIFEST.md` before execution, and the phase verifier (5/5) + integration checker independently re-confirmed every citation against the real artifacts. Honesty discipline held end-to-end; the one regression that slipped to publish (the timing figure) was caught by the milestone audit and fixed same-day.

**What's next:** Open candidates (no commitment): **EXT-01** more worked examples (Go / Python, following the Rust precedent); **EXT-06** a 35B-vs-122B comparison on the Rust example (parallel to v1.1 for F#); **EXT-02** English translation; or polish the carried-over v1.1 appendix-C tech debt (TD-2…TD-5).

---

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
