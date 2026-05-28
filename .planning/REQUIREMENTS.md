# Requirements: OpenHands Agentic AI 튜토리얼 — v1.2 (Rust Example)

**Defined:** 2026-05-28
**Milestone:** v1.2 — Rust Example (second worked example)
**Core Value:** A reader watches the same local 35B model that built the F# calculator now build a minimal Rust HTTP server end-to-end — proving that the agentic pattern transfers across languages, with all model boundaries honestly documented.

> v1 + v1.1 requirements are archived complete at `.planning/milestones/v1-REQUIREMENTS.md` and `.planning/milestones/v1.1-REQUIREMENTS.md`. This file scopes ONLY the new v1.2 work.

## v1.2 Requirements

### Rust capture

- [ ] **RUST-01**: A real captured 35B OpenHands run of a minimal Rust HTTP server exists on disk (per-task JSONL), with the agent attempting the work **unaided first** — no provided source for any file, including `Cargo.toml` (the agent runs `cargo new` itself). Scaffold fallback may be prepared but should only be invoked if the agent demonstrably cannot proceed, and if invoked it must be disclosed in the capture manifest (parallel to v1.1's lexer protocol).
- [ ] **RUST-02**: The run honestly records whether 35B wrote the Rust source itself; if scaffolding was provided as a fallback for any task, that is disclosed (never hidden, never manually patched to fake success). The "any ActionEvent across all JSONLs must have `source=agent`" rule from v1/v1.1 applies — zero manual edits to agent-written files between tasks.
- [ ] **RUST-03**: The run's real outcome on the canonical test (`curl localhost:8080/` returns the body `hello\n` while the server runs from `cargo run`) is captured in a terminal observation in the JSONL — success or honest failure. Any genuine build error, runtime error, or borrow-checker/lifetime confusion the agent encountered and its self-correction sequence are captured in the JSONL (events traceable, no fabrication).

### 6부 chapter content

- [ ] **CHAP-01**: A new 6부 "다른 워킨 예제: Rust HTTP 서버" (or equivalent name approved during planning) chapter group is added to the book in `src/ch06-rust-server/` (or equivalent path) and is wired into `src/SUMMARY.md`. The chapter is structurally parallel to 4부 (intro / writing / build-test / final or a similar decomposition); it uses the **사용자 프롬프트 / 내부 프로세스 / 결과** callout pattern from v1.1 (without pictograph emojis, per the post-cleanup convention); concept↔action callouts pair what the agent did with the 1부/2부 concepts.
- [ ] **CHAP-02**: Every code quote, event number, timing figure, error message, and capability claim in 6부 traces verbatim to the captured JSONL / logs / transcript / `cargo` output. No fabricated or idealized numbers. The chapter's existence is permitted only if the underlying capture (RUST-01..03) supports the claim being made; if a section can't be backed by real evidence, it's omitted.

### Publish

- [ ] **PUB-01**: The updated book builds clean with `mdbook build` (no errors, no broken links). The new 6부 entries appear in `src/SUMMARY.md`; existing chapters (1부~5부 + 부록 A/B/C) are not regressed. The pre-existing cosmetic `<char>` warning from 부록 C is acceptable (tracked as v1.1 TD-4); no NEW warnings introduced.
- [ ] **PUB-02**: The updated book is re-deployed live to GitHub Pages via the existing Actions workflow on push to `main`. `.github/workflows/deploy.yml` is NOT modified by v1.2 (audit-style guard, parallel to v1.1 PUB-02). Live URL returns HTTP 200; the new 6부 chapters reachable from sidebar navigation.

## Future Requirements

Deferred to later milestones:

- **EXT-01 expansion** (carried forward): Go / Python / other-language worked examples following the Rust precedent — each could be its own future milestone (v1.3 Go Example, v1.4 Python Example, etc.)
- **EXT-02**: English translation of the tutorial (all parts including new 6부)
- **EXT-03**: "Build your own minimal agent in F#" appendix
- **EXT-04** (optional): Local-vs-cloud model comparison
- **EXT-05** (new from v1.2 setup): Rust HTTP server with a framework (`axum`/`actix`) — separate milestone if interesting; explicitly out of scope for v1.2
- **EXT-06** (new from v1.2 setup): 35B-vs-122B comparison on the Rust example (parallel to v1.1 doing this for F#) — if v1.2 35B-only run is interesting, a 122B follow-up could be a v1.3

## Out of Scope (v1.2)

| Feature | Reason |
|---------|--------|
| Rust HTTP framework (`hyper`, `axum`, `actix-web`) | v1.2 uses `std::net::TcpListener` deliberately to keep the agent's work visible at the byte level. Frameworks would hide most of what we want to show. Could be a later milestone. |
| Multiple endpoints / routing logic | Minimal scope = `GET / → "hello\n"` only. More routes = more interesting code but also more capture work; pushed to a possible v1.3. |
| HTTPS / TLS | Way beyond scope; not relevant to "agent writes minimal HTTP" demonstration. |
| Multi-threading / async runtime | std-only sync server is sufficient for the demo; concurrency is a different lesson. |
| Re-running v1 35B calc / v1.1 122B calc | Those are already captured and archived; this milestone only captures the new Rust run. |
| 35B vs 122B comparison on Rust | Out of v1.2 scope — single-model run this milestone. A future v1.3 could add 122B if v1.2 results warrant the comparison. |
| Fabricated / idealized capture transcripts | Honesty is the core value — all numbers and code quotes come from real captured run. |
| Modifying `.github/workflows/deploy.yml` | v1's deploy workflow handles all current and future content; v1.2 should not touch it. (Audit-style guard.) |
| Teaching Rust syntax/semantics in the chapter | The chapter explains what the agent did, not Rust. Readers expected to follow Rust at a basic level. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RUST-01 | TBD (Phase 8 expected) | Pending |
| RUST-02 | TBD (Phase 8 expected) | Pending |
| RUST-03 | TBD (Phase 8 expected) | Pending |
| CHAP-01 | TBD (Phase 9 expected) | Pending |
| CHAP-02 | TBD (Phase 9 expected) | Pending |
| PUB-01 | TBD (Phase 9 expected) | Pending |
| PUB-02 | TBD (Phase 9 expected) | Pending |

**Coverage:**
- v1.2 requirements: 7 total
- Mapped to phases: 0 (roadmapper will fill in)
- Unmapped: 7 (until roadmap is built)

---
*Requirements defined: 2026-05-28 (v1.2 milestone)*
*Traceability will be updated when roadmap is built.*
