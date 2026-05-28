---
phase: 04-worked-example-chapter
verified: 2026-05-28T00:00:00Z
status: passed
score: 8/8 must-haves verified
re_verification: false
---

# Phase 4: Worked-Example Chapter Verification Report

**Phase Goal:** The core chapter walks the reader through the real run step by step, with concept callouts, the error-and-fix narration, final source, and verification output.
**Verified:** 2026-05-28
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | WALK-01: intro.md explains tokenize→parse→evaluate without teaching F# | VERIFIED | intro.md lines 30–68: pipeline diagram, three-stage description, explicit "F#를 처음 보는 독자도 걱정할 필요가 없습니다" |
| 2 | WALK-02: walkthrough uses REAL captured output, no invented transcripts | VERIFIED | All error strings (FSY000, parse error at 16,7, FS0039 FromText) cross-checked verbatim against transcript.md and task3-parser.jsonl |
| 3 | ≥3 concept-to-action callouts, each linking to ch01 vocab | VERIFIED | 4 callouts found: Callout D (plan→write→test→run, planning.md:61), tool calling (writing.md:84), memory/context (writing.md:92), agent loop/self-correction (build-test.md:173) |
| 4 | Error-and-fix narrated as observed→decided→corrected using 4 REAL failures, no invented "precedence bug" | VERIFIED | All 4 failures correctly narrated; failure 3 explicitly notes no ThinkAction recorded; no precedence bug narrative anywhere |
| 5 | final.md ends with 2+3*4=14, (2+3)*4=20, HONEST performance note | VERIFIED | final.md lines 193–197 embed test-output.txt verbatim; perf note uses real task times (16s, 32s, 1m17s, 3m6s, ~10min total, ~150min attempt-1) |
| 6 | Scaffolding disclosure: Lexer.fsl and calc.fsproj disclosed as provided | VERIFIED | intro.md lines 87–104, planning.md lines 35–47, final.md lines 95–130 all explicitly state both files were provided in task prompts |
| 7 | NO "~240s/call" stale number | VERIFIED | grep -rn "240" src/ch04-calculator/ returns empty |
| 8 | WALK-03: final.md/writing.md embed real final Parser.fsy with %left PLUS MINUS / %left STAR SLASH | VERIFIED | writing.md lines 119–120 and final.md lines 30–31 contain these exact lines; matches captured/final-source/Parser.fsy verbatim |

**Score:** 8/8 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/ch04-calculator/intro.md` | Pipeline explanation, scaffolding disclosure | VERIFIED | 113 lines; discloses Lexer.fsl and calc.fsproj as provided; explains tokenize→parse→evaluate |
| `src/ch04-calculator/planning.md` | Task decomposition, why lexer was provided | VERIFIED | 82 lines; 5-task breakdown with real timings; explains FsLex capability boundary |
| `src/ch04-calculator/writing.md` | Code writing walkthrough + 2 callouts + final Parser.fsy | VERIFIED | 150 lines; Parser.fsy first draft shown; tool calling callout; memory/context callout; WALK-03 section with final Parser.fsy |
| `src/ch04-calculator/build-test.md` | 4 failures narrated observed→decided→corrected + agent loop callout | VERIFIED | 188 lines; all 4 failures with verbatim error text; failure 3 ThinkAction honestly absent; agent loop callout |
| `src/ch04-calculator/final.md` | Full source, verified test output, honest perf note | VERIFIED | 226 lines; all 4 source files; test-output.txt verbatim; real timing data; no 240s reference |
| `captured/final-source/Parser.fsy` | Real final source with %left declarations | VERIFIED | Matches what chapter quotes exactly |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| build-test.md error quotes | transcript.md Task 3 Steps 5,8,10,12 | verbatim text | WIRED | FSY000 error: transcript Step 5 (event 9); "Parser.fsy(16,7): error parse error": Steps 8 and 10; FS0039 FromText: Step 12 (event 25) — all match exactly |
| build-test.md ThinkAction quotes | transcript.md Thought fields | verbatim text | WIRED | Failure 1 quote matches Step 6 Thought exactly; Failure 2 quote matches Step 9 Thought exactly; Failure 4 quote matches Step 13 Thought exactly |
| build-test.md (no ThinkAction for failure 3) | transcript.md Step 10→Step 11 jump | absence of Thought | WIRED | Transcript goes from Step 10 (event 19, build error) directly to Step 11 (event 23, rewrite) with no Thought field — chapter correctly reports this absence |
| final.md verification block | captured/test-output.txt | verbatim copy | WIRED | final.md lines 180–197 reproduce test-output.txt exactly, including Korean build output and 3 test cases |
| concept callouts | src/ch01-agentic-ai/concepts.md | direct citation | WIRED | "LLM이 일반 텍스트를 출력하는 대신, 구조화된 호출(이름 + 인자)을 출력해 환경에 행동을 지시합니다" is in concepts.md line 15; "자가 수정은 별도로 설계된 기능이 아니라, agent loop와 observation 메커니즘의 자연스러운 결과입니다" is in concepts.md line 58 |
| build-test.md test output (8 expressions) | transcript.md Task 3 Step 15 | verbatim | WIRED | "1+2*3 = 7 / 10-3-2 = 5 / (10-3)-2 = 5 / 10-(3-2) = 9 / 2*3+4 = 10 / (2+3)*4 = 20 / 100/10/2 = 5 / 1+2+3+4+5 = 15" matches transcript Step 15 exactly |

---

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| WALK-01: pipeline without F# tutorial | SATISFIED | intro.md clearly scoped to agent behavior |
| WALK-02: real captured output | SATISFIED | All quoted error strings verified against logs |
| WALK-03: real final source verbatim | SATISFIED | Parser.fsy matches captured/final-source/Parser.fsy |
| ≥3 concept callouts referencing ch01 vocab | SATISFIED | 4 callouts; all reference ch01 terms with direct quotes |
| Error-and-fix as observed→decided→corrected | SATISFIED | Structure used consistently for all 4 failures |
| No invented "precedence bug" narrative | SATISFIED | Chapter explicitly states precedence was correct from the start (build-test.md lines 7–8) |
| No ThinkAction invented for failure 3 | SATISFIED | Chapter explicitly acknowledges absence (build-test.md lines 90–92) |
| Scaffolding disclosed (Lexer.fsl + calc.fsproj) | SATISFIED | Disclosed in intro.md, planning.md, final.md — multiple places |
| No stale "240s/call" performance claim | SATISFIED | grep returns empty |
| Honest perf note with real numbers | SATISFIED | final.md lines 213–217 uses real task timings |
| mdBook builds to exit 0 | SATISFIED | Confirmed via mdbook build |
| SUMMARY.md wires all 5 ch04 files | SATISFIED | Lines 26–30 wire all five files |
| 5부/부록 remain () drafts | SATISFIED | Lines 34–40 of SUMMARY.md show () placeholders |

---

### Anti-Patterns Found

None. No TODO/FIXME/placeholder/stub patterns detected in any ch04 file.

---

### Criterion-by-Criterion Report

**WALK-01** (intro.md explains tokenize→parse→evaluate without teaching F#): PASS. intro.md opens with "F#을 처음 보는 독자도 걱정할 필요가 없습니다" and provides a pipeline ASCII diagram (lines 34–51) that explains the three stages without F# syntax. The three-stage description (lines 53–67) stays at a conceptual level. No F# language tutorial content.

**WALK-02** (real captured output, no invented transcripts): PASS. Every error string in build-test.md was traced to transcript.md:
- "FSYACC : error FSY000: at least one %start declaration is required" — transcript Task 3 Step 5 output, verbatim match including Korean surrounding text.
- "Parser.fsy(16,7): error parse error" — transcript Steps 8 and 10, verbatim match.
- "FS0039: 'LexBuffer<_>' 형식은 'FromText' 필드, 생성자 또는 멤버를 정의하지 않습니다. 다음 중 하나가 필요할 수 있습니다: FromTextReader FromBytes FromString" — transcript Step 12 (event 25), verbatim match.
- Build success: "calc net10.0 성공 (0.7초) → bin/Debug/net10.0/calc.dll / 성공 빌드(1.0초)" — transcript Step 14, verbatim match.
- The 8-expression self-test output — transcript Step 15, verbatim match.
ThinkAction quotes for failures 1, 2, and 4 match transcript Thought fields exactly.

**Callout criterion** (≥3 callouts linking to ch01 vocab): PASS. Four callouts present:
1. planning.md — plan→write→test→run (Callout D): cites ch01 탐색→분석→구현→검증 mapping; references ch01 text "자가 수정은 별도로 설계된 기능이 아니라, agent loop와 observation 메커니즘의 자연스러운 결과"
2. writing.md — tool calling callout: cites ch01 concepts.md wording "LLM이 일반 텍스트를 출력하는 대신, 구조화된 호출(이름 + 인자)을 출력해 환경에 행동을 지시합니다" (verified present in concepts.md line 15)
3. writing.md — memory/context callout: explains EventLog vs filesystem distinction; references ch01 memory definition
4. build-test.md — agent loop/self-correction callout: cites ch01 "빌드가 실패하면 오류 메시지를 읽고 수정 코드를 작성하고" (verified in concepts.md line 39) and "자가 수정은 별도로 설계된 기능이 아니라..." (concepts.md line 58)

**Error-and-fix criterion** (4 REAL failures, no invented precedence bug): PASS. build-test.md:
- Opens with explicit statement (lines 7–8): "이 네 번의 실패는 연산자 우선순위 버그가 아닙니다. 에이전트는 %left PLUS MINUS와 %left STAR SLASH를 처음 작성할 때부터 올바르게 선언했습니다."
- Failure 1 (%start missing): correctly narrated, error matches transcript.
- Failure 2 (%start <int> start invalid syntax): correctly narrated, error matches transcript.
- Failure 3 (same parse error, no ThinkAction): chapter explicitly states "이 단계에서는 ThinkAction이 기록되지 않았습니다" — honest, confirmed by transcript gap from Step 10 to Step 11.
- Failure 4 (FS0039 LexBuffer.FromText): correctly narrated, error matches transcript.

**final.md verification block**: PASS. Lines 180–197 of final.md reproduce captured/test-output.txt exactly, including "=== Calculator Correctness Test ===" header, Korean dotnet build output, "경고 0개 / 오류 0개", and "2+3*4 = 14 / (2+3)*4 = 20 / 10-3-2 = 5".

**Scaffolding disclosure**: PASS. intro.md lines 94–104 has a dedicated section "솔직한 공개: 스캐폴딩에 대하여" stating "Lexer.fsl과 calc.fsproj는 에이전트가 만든 것이 아닙니다. 두 파일은 태스크 프롬프트에 텍스트 그대로 포함되어 에이전트에게 전달됐습니다." The intro.md file table (lines 85–90) labels both files "제공됨 — 에이전트가 작성하지 않음". No part of the chapter implies the agent wrote the lexer.

**No stale "240" claim**: PASS. `grep -rn "240" src/ch04-calculator/` returns empty.

**WALK-03** (final source verbatim): PASS. writing.md lines 107–145 and final.md lines 17–56 both show the full Parser.fsy. Both include `%left PLUS MINUS` and `%left STAR SLASH`. Both match captured/final-source/Parser.fsy exactly (39 lines, same content).

**mdBook build**: PASS. `mdbook build` exits 0. HTML written to book/. SUMMARY.md wires all 5 ch04 files at lines 26–30. 5부/부록 entries remain `()` placeholders at lines 34–40.

---

_Verified: 2026-05-28_
_Verifier: Claude (gsd-verifier)_
