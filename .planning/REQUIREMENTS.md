# Requirements: OpenHands Agentic AI 튜토리얼 — v1.4 (Planning Comparison)

**Defined:** 2026-06-01
**Milestone:** v1.4 — Planning Comparison (Claude-led vs OpenHands-native task planning)
**Core Value:** An honest, captured A/B that asks — for the same local 35B and the same goals (F#/Rust/Scala) — whether *who plans the task decomposition* (an expert/Claude-authored plan vs the agent planning itself) changes execution efficiency. Whatever the data shows (including "mixed/inconclusive") is reported faithfully from real captured runs.

> v1 / v1.1 / v1.2 / v1.3 requirements are archived complete under `.planning/milestones/`. This file scopes ONLY the new v1.4 work. Research: `.planning/research/SUMMARY.md`.

## v1.4 Requirements

### Comparison method & harness (METH)

- [ ] **METH-01**: Two prompt templates per example share an **identical control block** (the canonical goal, constraints, and canonical tests) and differ ONLY in the planning input: **Arm A** embeds Claude's numbered task plan in the prompt; **Arm B** gives the bare goal plus an instruction to plan its own steps (via the task tracker) then execute. Before any run, the two prompts are diffed and any non-plan asymmetry stripped (fairness control).
- [ ] **METH-02**: Each (example × arm) is captured with the established headless invocation (default `CodeActAgent`, `--headless --json --yolo --override-with-envs`) as ONE invocation per arm (not split into per-task runs), in an arm-isolated **gitignored** workspace, with identical model/version/timeout/flags for both arms; run-order is counterbalanced across examples and the proxy state is controlled between arms, with conditions disclosed in the manifest (timing-fairness).
- [ ] **METH-03**: A `metrics_extractor.py` emits a per-run `metrics.json` from the JSONL — TerminalAction count, total event count, wall-clock active time, LLM-call-gap stats (ObservationEvent→next ActionEvent), error-fix cycles (non-zero-exit → next corrective action), AgentErrorEvent count, and canonical-test pass/fail — plus a per-example `comparison.json` (Arm A vs Arm B). The mechanical `source=agent` honesty gate is run over every arm's JSONL. The harness is validated on a **pilot example (Rust)** before the full study.

### Planning capture (PCAP)

- [ ] **PCAP-01**: Both arms (A and B) are captured on the **35B** for **all three examples** (F# FsLex/FsYacc calculator, Rust HTTP server, Scala calculator), with real per-run JSONL on disk, `source=agent` on every ActionEvent, and zero manual edits to agent files. Each (example × arm) is run **n=3 where feasible** (report median + range); **n=1 is permitted only as an explicitly-hedged "single-run observation"** — never presented as representative.
- [ ] **PCAP-02**: Both planning artifacts are saved per example for qualitative comparison: Claude's authored task plan (the Arm A input) and OpenHands' self-generated plan (Arm B — extracted from the `TaskTrackerObservation` events, or the agent's stated steps if the tracker isn't emitted).
- [ ] **PCAP-03**: A committed `CAPTURE-MANIFEST.md` (under `captured-planning/`) summarizes each (example × arm) outcome, the run conditions/order, and the honesty-gate result — closing the capture gate. The chapter (Phase 14) cannot be written until this is committed.

### Analysis (ANAL)

- [ ] **ANAL-01**: Per-example comparison tables (Arm A vs Arm B) on the chosen metrics — retries/error-fix cycles, wall-clock + per-call time, LLM-call & TerminalAction counts, and canonical-test pass/fail — with **median + range for n≥2** and explicit "single-run" labels for n=1. No metric is presented without its fairness caveat where one applies.
- [ ] **ANAL-02**: A qualitative comparison of the two **plans** per example: task count, granularity, ordering, and whether each decomposition matches the canonical scaffold→write→build→test shape (Claude's plan vs OpenHands' self-plan).

### 부록 D chapter content (DCHAP)

- [ ] **DCHAP-01**: A new 부록 D "계획 방식 비교: Claude 계획 vs OpenHands 자체 계획" chapter, written verbatim from the committed `captured-planning/` data, wired into `src/SUMMARY.md` after 부록 C, in the book's style (no pictograph emoji). Every number, plan excerpt, and metric is traceable to the captured artifacts; manifest 1-based event numbers are cited.
- [ ] **DCHAP-02**: The chapter enforces the honest **framing rule**: Arm A is presented as *"does an expert-authored plan help the 35B execute?"* — NOT "Claude plans better than the 35B." Mixed/per-metric/inconclusive outcomes are reported as valid results; n=1 figures are hedged; the legacy `~14–32s/call` figure is never cited as a measurement.

### Publish (DPUB)

- [ ] **DPUB-01**: `mdbook build` clean (no errors; only the pre-existing 부록 C `<char>` warning, TD-4); existing 1부~7부 + 부록 A/B/C not regressed.
- [ ] **DPUB-02**: Re-deployed live to GitHub Pages via the existing Actions workflow on push to `main`; `.github/workflows/deploy.yml` NOT modified; live URL 200; 부록 D reachable from sidebar.

## Future Requirements

Deferred to later milestones: EXT-07 (cross-language "calculator in 3 languages" appendix), EXT-01 (Go/Python examples), EXT-06 (35B-vs-122B on Rust/Scala), EXT-02 (English translation), EXT-08 (new — extend the planning comparison to 122B, or to the SDK `PlanningAgent` arm).

## Out of Scope (v1.4)

| Feature | Reason |
|---------|--------|
| The SDK-only `PlanningAgent` (PLAN.md) as a third arm | The headless CLI uses CodeActAgent; wiring the Python SDK PlanningAgent is a separate effort. Arm B uses the CLI agent's own TaskTracker self-planning. Could be EXT-08. |
| 122B planning comparison | Single-model (35B) study this milestone, parallel to v1.2/v1.3. |
| Large-n statistical study (n≥10) | Prohibitive on slow local 35B; n=3 (hedged) is the honest micro-study floor. Bigger n is a future effort. |
| New worked examples / new languages | v1.4 reuses the existing three examples; it studies *planning*, not new captures of new programs. |
| Fabricated / idealized comparison numbers, cherry-picked runs | Honesty is the core value — all metrics come from real captured runs; failed/!pass runs are included, not hidden. |
| Modifying `.github/workflows/deploy.yml` | The existing deploy workflow handles all content. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| METH-01 | Phase 12 | Pending |
| METH-02 | Phase 12 | Pending |
| METH-03 | Phase 12 | Pending |
| PCAP-01 | Phase 13 | Pending |
| PCAP-02 | Phase 13 | Pending |
| PCAP-03 | Phase 13 | Pending |
| ANAL-01 | Phase 13 | Pending |
| ANAL-02 | Phase 13 | Pending |
| DCHAP-01 | Phase 14 | Pending |
| DCHAP-02 | Phase 14 | Pending |
| DPUB-01 | Phase 14 | Pending |
| DPUB-02 | Phase 14 | Pending |

**Coverage:**
- v1.4 requirements: 12 total
- Mapped to phases: 12 (Phase 12: 3, Phase 13: 5, Phase 14: 4)
- Unmapped: 0

---
*Requirements defined: 2026-06-01 (v1.4 milestone)*
