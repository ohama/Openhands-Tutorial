# Requirements: OpenHands Agentic AI 튜토리얼

**Defined:** 2026-05-27
**Core Value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator.

## v1 Requirements

Requirements for the initial published tutorial. Each maps to a roadmap phase.
("Reader can…" = the tutorial enables it; "Tutorial…" = a property of the content/artifact.)

### Concepts

- [x] **CONCEPT-01**: Reader can explain what agentic AI is and how it differs from a reactive chatbot
- [x] **CONCEPT-02**: Tutorial defines the core vocabulary — tool/function calling, agent loop, plan→write→test→run, memory/context — each pointing forward to where it appears in the run
- [x] **CONCEPT-03**: Tutorial explains OpenHands V1 architecture (agent loop, EventLog action/observation, Docker sandbox, LiteLLM) and maps each component to an agentic concept

### Setup

- [x] **SETUP-01**: Reader can install and run OpenHands on macOS (uv + headless CLI) by following the tutorial
- [x] **SETUP-02**: Reader can configure OpenHands to use the local Qwen endpoint via env vars (`LLM_MODEL=openai/qwen-local`, `LLM_BASE_URL=http://127.0.0.1:4000/v1`, dummy api_key, `--override-with-envs`)
- [x] **SETUP-03**: The .NET SDK is available to the agent's workspace (host toolchain via LocalWorkspace; `dotnet --version` works inside an OpenHands session)
- [x] **SETUP-04**: Tutorial provides a pre-run verification checklist (litellm proxy + tool calling, headless tool-call ping, `dotnet --version` via the agent) the reader runs before the live run

### Run capture

- [x] **RUN-01**: Tutorial is built from a real captured OpenHands run (commands + output logged), not fabricated output
- [x] **RUN-02**: The captured run shows OpenHands building the calculator across scoped tasks (scaffold → lexer → parser → evaluator → integration), not one mega-prompt
- [x] **RUN-03**: The captured run includes at least one real error-and-fix cycle, narrated explicitly (the strongest agentic demonstration)

### Worked example

- [ ] **WALK-01**: Tutorial introduces what the calculator does without teaching F# from scratch
- [ ] **WALK-02**: Worked-example chapter walks the reader through the real run step by step, with concept↔action callouts linking each step to a concept from CONCEPT-02
- [ ] **WALK-03**: Tutorial includes the final F# source — lexer (`.fsl`), parser (`.fsy`) with correct `%left` operator precedence, and evaluator

### Verification

- [ ] **VERIFY-01**: Tutorial shows the finished calculator correctly evaluating `2+3*4 → 14` plus a couple more cases (precedence, parentheses)
- [ ] **VERIFY-02**: Tutorial honestly reports local-LLM performance (~240s/call) and what to expect when running it yourself

### Troubleshooting

- [ ] **TROUBLE-01**: Troubleshooting chapter covers the top failure modes — `host.docker.internal` vs `127.0.0.1`, model name/`openai/` prefix, timeout/retry storm, missing .NET in sandbox, FsYacc precedence

### Reproducibility

- [ ] **REPRO-01**: Reproducibility appendix lists exact task strings, Docker/run commands, config values, and expected outputs so a reader can reproduce the run

### Tutorial artifact (mdBook)

- [x] **BOOK-01**: Tutorial is structured as an mdBook (SUMMARY.md, book.toml with `site-url` for project pages) and builds cleanly with `mdbook build`
- [x] **BOOK-02**: Tutorial is written in Korean (English for technical terms)
- [ ] **BOOK-03**: Tutorial is deployed to GitHub Pages via a GitHub Actions workflow (live published site)

## v2 Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Extensions

- **EXT-01**: Additional worked examples beyond the calculator (e.g., a second language target)
- **EXT-02**: English translation of the tutorial
- **EXT-03**: A "build your own minimal agent" appendix in F# (the original learning idea, now optional)
- **EXT-04**: Comparison of the local 35B run vs a larger/cloud model run

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Teaching F# language fundamentals | Readers are programming-literate; F# appears only as the example OpenHands builds |
| Exhaustive OpenHands feature reference | The tutorial teaches through ONE worked example, not the whole product |
| Fabricated / idealized transcripts | Dishonest and non-reproducible; the value is real captured output |
| Cloud / hosted LLM APIs | The tutorial uses the existing local Qwen server only |
| Re-implementing an agent from scratch | OpenHands is used as-is; building one is a different (v2) tutorial |
| Modifying OpenHands source | We use it as released |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONCEPT-01 | Phase 1 | Complete |
| CONCEPT-02 | Phase 1 | Complete |
| CONCEPT-03 | Phase 1 | Complete |
| SETUP-01 | Phase 2 | Complete |
| SETUP-02 | Phase 2 | Complete |
| SETUP-03 | Phase 2 | Complete |
| SETUP-04 | Phase 2 | Complete |
| RUN-01 | Phase 3 | Complete |
| RUN-02 | Phase 3 | Complete |
| RUN-03 | Phase 3 | Complete |
| WALK-01 | Phase 4 | Pending |
| WALK-02 | Phase 4 | Pending |
| WALK-03 | Phase 4 | Pending |
| VERIFY-01 | Phase 4 | Pending |
| VERIFY-02 | Phase 4 | Pending |
| TROUBLE-01 | Phase 5 | Pending |
| REPRO-01 | Phase 5 | Pending |
| BOOK-01 | Phase 1 | Complete |
| BOOK-02 | Phase 1 | Complete |
| BOOK-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20 (complete)
- Unmapped: 0

---
*Requirements defined: 2026-05-27*
*Last updated: 2026-05-27 — traceability populated after roadmap creation*
