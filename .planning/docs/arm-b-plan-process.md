# Arm B 플랜은 어떤 과정으로 세웠나

> 대상: v1.4 Planning Comparison 연구 / Phase 12 Rust pilot 의 **Arm B**
> (Arm B = "35B가 task tracker로 스스로 플랜하고 실행하는" 조건)
> 작성일: 2026-06-04 · 짝 문서: [`arm-a-plan-process.md`](./arm-a-plan-process.md)

---

## 0. 한 줄 요약 — Arm A와 결정적으로 다른 점

**Arm B의 플랜은 우리가 설계 시점에 작성하지 않았다.** 설계 시점에 만든 건 "35B가 스스로
플랜하도록 유도하는 프롬프트" 하나뿐이고, **실제 플랜은 35B가 런타임에 생성**했다(event #4).
우리는 그걸 JSONL에서 **verbatim 추출·캡처**했을 뿐이다.

| | Arm A | Arm B |
|---|---|---|
| 플랜 작성자 | Claude (설계 시점) | **35B (런타임)** |
| 우리가 만든 것 | 완성된 3-스텝 플랜 | 플랜을 *유도하는* 한 줄 |
| 산출물 성격 | authored input | **captured output** |

→ 그래서 Arm B의 "과정"은 **(A) 설계 시점 harness 작성**과 **(B) 런타임 self-plan 캡처**
두 단계로 나뉜다.

---

## 1. 같은 출발점: 연구 질문 (framing)

Arm A와 동일한 framing을 공유한다 — "전문가 플랜이 35B의 *실행*을 돕는가?"

- **Arm A:** 전문가(Claude) 플랜을 임베드 → 35B는 실행만.
- **Arm B:** 35B가 task tracker로 **스스로 플랜** → 실행. ← 대조군(baseline)
- 독립변수 = "전문가 플랜의 유무". Arm B는 "플랜이 없는(=self-plan) 쪽"을 담당.

*근거: `CAPTURE-MANIFEST.md` §Study Design*

---

## 2. (A) 설계 시점 — Arm B 프롬프트 작성

Arm B 프롬프트는 Arm A와 **byte-identical한 control block**을 공유하고, 가변 블록만 다르다.

```
Arm A = [control block] + "Complete the following numbered steps..." + Step 1/2/3   ← 우리가 쓴 플랜
Arm B = [control block] + "Plan your own implementation steps using the task tracker,
                           then execute each step. Do not ask for confirmation between steps."
                          └──────── 플랜을 '유도'만 함, 플랜 내용은 없음 ────────┘
```

control block = 동일한 목표(8080·hello\n·loop) + 제약(std-only) + canonical test(curl) +
bash-only 규칙. (`__WORKDIR__` 토큰으로 경로 차이 정규화 — Arm A 문서 §4와 동일)

### 이 한 줄 문구는 의도적으로 선택됐다

"Plan your own implementation steps **using the task tracker**" 라는 표현은 **TaskTrackerAction
emission을 유도(nudge)** 하려고 고른 phrasing이다. 이게 안 되면 Arm B는 self-plan 증거를 남기지
못해 실험이 약해진다 → 그래서 이건 **open unknown #1**("Arm B가 정말 TaskTrackerObservation을
내보내는가?")로 따로 추적됐다.

*근거: `12-01-PLAN.md` Task 2 STEP 3, `12-01-SUMMARY.md` key-decisions*

---

## 3. (B) 런타임 — 35B가 스스로 만든 플랜

라이브 실행(12-02) 시점에 35B가 직접 task tracker로 플랜을 생성했다. 캡처 결과:

- **event #2** (1-based): 첫 task-tracker 이벤트 (`view`)
- **event #4**: 초기 플랜 생성 (`plan`) — **4개 태스크**, 전부 status=todo

| # | 35B가 정한 태스크 | 비고 |
|---|---|---|
| 1 | Initialize Rust project with Cargo | Cargo.toml(빈 deps) + src/main.rs |
| 2 | Implement HTTP server in main.rs | `std::net::TcpListener`로 8080 bind, 'hello\n' 응답, loop |
| 3 | Build the project | `cargo build --release` |
| 4 | Run canonical test: `curl -s http://localhost:8080/` | output 'hello'+newline, exit 0 검증 |

### 진행(status) 추적도 verbatim 캡처됨

```
event:  #4    #6          #16   #22   #26   #38
T1:    todo  in_progress  done  done  done  done
T2:    todo  todo         todo  done  done  done
T3:    todo  todo         todo  todo  done  done
T4:    todo  todo         todo  todo  todo  done
```

이 전체 task list와 todo→in_progress→done 진행은 JSONL에서 **무편집 verbatim 추출**해
`oh-self-plan.md`에 기록했다 (Raw JSON까지 보존).

*근거: `oh-self-plan.md`, `CAPTURE-MANIFEST.md` §RESOLVED OPEN UNKNOWN #1*

---

## 4. open unknown #1 검증: "35B가 진짜 task tracker를 쓰나?" → YES

이 부분이 Arm B 플랜 과정의 **리스크 게이트**였다. 35B가 task tracker 지시를 무시하면
프롬프트를 다시 손봐야(re-pilot) 했다.

- 결과: **RESOLVED YES** — Arm B는 TaskTrackerAction 7개 + TaskTrackerObservation 7개(총 14개)를
  emit. Arm A는 0개(설계대로 제공된 플랜만 실행).
- 함의: **프롬프트 re-pilot 불필요.** Arm B 프롬프트는 Phase 13(F#/Scala)에서 그대로 재사용 가능.
- metrics_extractor.py에 `task_tracker_observation_count` 검출기를 미리 심어둬서(12-01),
  라이브 후 이 필드만 읽으면 self-plan emission 여부가 확정되도록 해뒀다.

*근거: `CAPTURE-MANIFEST.md` §RESOLVED OPEN UNKNOWN #1, Per-Arm Summary Table*

---

## 5. 두 arm의 플랜이 실제로 달랐던 지점 (실험이 작동했다는 증거)

35B의 self-plan은 Arm A의 전문가 플랜과 **organic하게 달랐다** — 이게 대조가 성립한 증거다:

| | Arm A (Claude 플랜) | Arm B (35B self-plan) |
|---|---|---|
| 스텝 수 | 3 (build+test 합침) | **4** (build와 test 분리) |
| 빌드 명령 | `cargo build` | `cargo build --release` |
| 출처 | v1.2 검증 분해 이식 | 35B 자체 판단 |

두 arm 모두 canonical test는 **PASS**(Arm A event #25, Arm B event #31, 둘 다 exit 0).

*근거: `CAPTURE-MANIFEST.md` Per-Arm Summary Table*

---

## 6. 전체 파이프라인 (요약 도식)

```
[연구 질문 고정]                         §1   (Arm A와 공유)
        │
        ▼
─── 설계 시점 (A) ──────────────────────  §2
[Arm B 프롬프트 작성]
   공유 control block (= Arm A와 byte-identical)
   + "task tracker로 스스로 플랜하라" 한 줄  ← 플랜 '유도'만, 내용 없음
        │
        ▼
[symmetry diff 게이트]                          (Arm A §5와 동일 — control block PASS)
        │
        ▼
─── 런타임 (B) ─────────────────────────  §3
[35B가 self-plan 생성]
   event #2 view → event #4 plan (4 tasks, todo)
   → todo→in_progress→done 진행 (#6/#16/#22/#26/#38)
        │
        ▼
[JSONL verbatim 추출]
   oh-self-plan.md  ← 무편집 캡처 (Raw JSON 포함)
        │
        ▼
[open unknown #1 검증]                    §4
   task_tracker_observation_count > 0  → RESOLVED YES → re-pilot 불필요
```

---

## 7. 결과물 위치 (traceability)

| 산출물 | 경로 |
|---|---|
| Arm B 최종 OH 프롬프트 (우리가 작성) | `captured-planning/rust/arm-b/planning-artifact/oh-goal-prompt.txt` |
| Arm B self-plan (35B가 작성, verbatim 캡처) | `captured-planning/rust/arm-b/planning-artifact/oh-self-plan.md` |
| 공유 control block | `task-prompts/CONTROL-BLOCK-rust.txt` |
| 대칭 증거 diff | `task-prompts/PROMPT-DIFF-rust.txt` |
| self-plan emission 검출기 | `metrics_extractor.py` (`task_tracker_observation_count`) |
| 이 과정을 지시한 플랜 / 실행 요약 | `12-01-PLAN.md`(Task 2) / `12-02-SUMMARY.md` |

(경로는 모두 `.planning/milestones/v1.4-phases/12-harness-rust-pilot/` 기준)

---

## 8. 한 문장 핵심

> Arm B 플랜은 **우리가 만든 게 아니라 35B가 런타임에 만든 것**이다 — 설계 시점엔 같은 control
> block에 "task tracker로 스스로 플랜하라"는 한 줄만 붙여(§2) self-plan을 *유도*했고, 실제 4-태스크
> 플랜과 그 진행은 JSONL에서 verbatim으로 **캡처**했다(§3). 그래야 "전문가 플랜의 유무"만이 두
> arm의 유일한 차이로 남는다.
