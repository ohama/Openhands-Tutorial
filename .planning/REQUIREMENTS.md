# Requirements: OpenHands Agentic AI 튜토리얼 — v1.3 (Scala Example)

**Defined:** 2026-06-01
**Milestone:** v1.3 — Scala Example (third worked example)
**Core Value:** A reader watches the same local 35B model that needed a scaffolded lexer for the F# calculator now build the *same calculator* in Scala — where ADTs + pattern matching are the idiom — testing, honestly, whether the model can express unaided what defeated it in F#.

> v1 / v1.1 / v1.2 requirements are archived complete under `.planning/milestones/`. This file scopes ONLY the new v1.3 work.

## v1.3 Requirements

### Scala capture

- [x] **SCAL-01**: A real captured 35B OpenHands run of a minimal Scala 3 arithmetic calculator exists on disk (per-task JSONL), with the agent attempting the work **unaided first** — no provided source for any file (the agent runs the `scala-cli` project setup itself). The run is preceded by a host **preflight** that verifies the Scala toolchain (`scala-cli` / JDK) is present and a trivial `scala-cli run` works. Scaffold fallback may be prepared but only invoked if the agent demonstrably cannot proceed, and if invoked it must be disclosed in the capture manifest (parallel to v1's lexer protocol). The parser must be the model's own work — **no parser-combinator library, no parser generator** (std-only discipline, parallel to v1.2).
- [x] **SCAL-02**: The run honestly records whether 35B wrote the Scala source itself; if scaffolding was provided as a fallback for any task, that is disclosed (never hidden, never manually patched to fake success). The "every ActionEvent across all JSONLs must have `source=agent`" rule applies — zero manual edits to agent-written files between tasks.
- [x] **SCAL-03**: The run's real outcome on the canonical test (`2+3*4 → 14`, plus `(2+3)*4 → 20` and `10-3-2 → 5`) is captured in a terminal `ObservationEvent` in the JSONL — success or honest failure, whichever actually occurred. Any genuine error the agent encountered (operator-precedence bug, Scala 3-vs-2 syntax slip, type/compile error, `scala-cli` usage confusion) and its self-correction sequence are captured in the JSONL (events traceable, no fabrication).

### 7부 chapter content

- [ ] **CHAP-01**: A new 7부 "다른 워킹 예제: Scala 계산기" chapter group is added to the book in `src/ch07-scala-calc/` (or equivalent path) and wired into `src/SUMMARY.md`. The chapter is structurally parallel to 4부/6부 (intro / planning / writing / build-test / final or a similar decomposition); it uses the **사용자 프롬프트 / 내부 프로세스 / 결과** callout pattern (without pictograph emojis); concept↔action callouts pair what the agent did with 1부/2부 concepts. It includes a short calculator-to-calculator note contrasting the Scala approach (ADT + pattern matching) with 4부's F# (FsLex/FsYacc DSL).
- [ ] **CHAP-02**: Every code quote, event number, timing figure, error message, and capability claim in 7부 traces verbatim to the captured JSONL / logs / `scala-cli` output. No fabricated or idealized numbers; the legacy v1 `~14–32s/call` figure is never cited as a measurement. If a section can't be backed by real evidence, it's omitted rather than invented.

### Publish

- [ ] **PUB-01**: The updated book builds clean with `mdbook build` (no errors, no broken links). The new 7부 entries appear in `src/SUMMARY.md`; existing chapters (1부~6부 + 부록 A/B/C) are not regressed. The pre-existing cosmetic `<char>` warning from 부록 C is acceptable (TD-4); no NEW warnings introduced.
- [ ] **PUB-02**: The updated book is re-deployed live to GitHub Pages via the existing Actions workflow on push to `main`. `.github/workflows/deploy.yml` is NOT modified (audit-style guard). Live URL returns HTTP 200; the new 7부 chapters are reachable from sidebar navigation.

## Future Requirements

Deferred to later milestones:

- **EXT-01 expansion**: more-language worked examples (Go / Python) following the precedent.
- **EXT-06**: 35B-vs-122B comparison on the Rust (or Scala) example.
- **EXT-07** (new): a cross-language "calculator in 3 languages" comparison appendix (F# / Scala, + any future) — parallel to 부록 C's model comparison, but language-axis.
- **EXT-02**: English translation. **EXT-03**: "build your own minimal agent" appendix. **EXT-04**: local-vs-cloud comparison. **EXT-05**: Rust/Scala with a framework.

## Out of Scope (v1.3)

| Feature | Reason |
|---------|--------|
| Parser-combinator library (`scala-parser-combinators`, `fastparse`, `cats-parse`) | v1.3 has the model write a hand-rolled recursive-descent parser to keep the work visible and test in-distribution capability. A library would hide the parsing logic. |
| `sbt` / heavyweight build setup | `scala-cli` keeps the example single-file and minimal (parallel to `cargo`/`dotnet` simplicity). sbt project boilerplate is out of scope. |
| Full expression language (variables, functions, floats) | Minimal scope = integer `+ - * /` with precedence and parentheses, matching v1's calculator. More features = more capture work; defer. |
| Teaching Scala syntax/semantics in the chapter | The chapter explains what the agent did, not Scala. Readers follow Scala at a basic level. |
| 35B-vs-122B comparison on Scala | Out of v1.3 scope — single-model run this milestone (parallel to v1.2). |
| Fabricated / idealized capture transcripts | Honesty is the core value — all numbers and code quotes come from the real captured run. |
| Modifying `.github/workflows/deploy.yml` | The existing deploy workflow handles all content; v1.3 must not touch it. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCAL-01 | Phase 10 | Complete |
| SCAL-02 | Phase 10 | Complete |
| SCAL-03 | Phase 10 | Complete |
| CHAP-01 | Phase 11 | Pending |
| CHAP-02 | Phase 11 | Pending |
| PUB-01 | Phase 11 | Pending |
| PUB-02 | Phase 11 | Pending |

**Coverage:**
- v1.3 requirements: 7 total
- Mapped to phases: 7 (Phase 10: 3, Phase 11: 4)
- Unmapped: 0

---
*Requirements defined: 2026-06-01 (v1.3 milestone)*
