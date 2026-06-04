# Arm A 플랜은 어떤 과정으로 세웠나

> 대상: v1.4 Planning Comparison 연구 / Phase 12 Rust pilot 의 **Arm A**
> (Arm A = "전문가가 작성한 플랜을 프롬프트에 박아 넣은" 조건)
> 작성일: 2026-06-04 · 근거 파일은 각 절 끝에 명시

---

## 0. 한 줄 요약

Arm A 플랜은 **새로 발명한 것이 아니라**, 이미 검증된 v1.2 Rust 과제 분해(phase 08의
task1/task2/task3)를 **단일 세션용 3-스텝 번호 플랜으로 기계적(mechanical)으로 변환**한 것이다.
변환에는 새로운 기획 내용을 일절 추가하지 않았고, 변환 결과는 **Arm B와 byte-identical한
control block을 공유하는지 literal diff로 검증**한 뒤에야 확정되었다.

---

## 1. 먼저: Arm A 플랜이 답하려는 질문 (framing)

플랜을 만들기 전에 **무엇을 측정하는가**부터 고정했다. 이게 플랜의 성격을 결정한다.

- **연구 질문(framing rule):** "전문가가 작성한 플랜이 35B의 *실행*을 돕는가?"
  - ❌ "Claude가 35B보다 플랜을 잘 짠다" 가 아니다.
- **Arm A:** 완성된 Claude 작성 단계별 플랜을 프롬프트에 임베드 → 35B는 그걸 실행만.
- **Arm B:** 35B가 task tracker로 스스로 플랜 → 실행.
- 독립변수 = "전문가 플랜의 유무". 플랜의 *출처*(Claude vs 35B)는 변수일 뿐, 품질 비교가 목적이 아님.

→ 그래서 Arm A 플랜은 "Claude가 똑똑하게 다시 기획한 것"이 아니라 "이미 통하는 분해를 그대로
옮긴 것"이어야 했다. 이게 아래 모든 제약의 근거다.

*근거: `captured-planning/CAPTURE-MANIFEST.md` §Study Design, §Arm A Framing Reminder*

---

## 2. 플랜의 출처: v1.2 분해 재사용 (발명 아님)

Arm A의 3개 스텝은 v1.2(phase 08)의 Rust 과제 프롬프트 3개에서 그대로 가져왔다.

| Arm A 스텝 | 출처 (v1.2 / phase 08) |
|---|---|
| Step 1 — Scaffold (`cargo new`) | `task-prompts-rust/task1-scaffold.txt` |
| Step 2 — Write server (std-only, 8080, hello\n, loop) | `task-prompts-rust/task2-server.txt` |
| Step 3 — Build & test (`cargo build`/`run`, curl 검증) | `task-prompts-rust/task3-buildtest.txt` |

이 v1.2 분해는 이미 실제 35B 캡처에서 작동이 확인된 것이라 "검증된 입력"으로 재사용 가능했다.

*근거: `12-01-PLAN.md` <context> 블록의 `@.../v1.2-phases/08-.../task1·2·3.txt` 참조,
`12-01-SUMMARY.md` requires: phase 08 "provides v1.2 Rust task decomposition (Arm A source)"*

---

## 3. 변환 규칙: "mechanical conversion" (핵심)

세 v1.2 서브태스크 → 단일 세션용 번호 스텝 3개로 옮기되, **다음만 허용**했다:

- ✅ 포맷 정규화 (번호 매기기, 단일 세션 문장으로 정리)
- ✅ 단일 세션 state-handoff 문구만 추가
  (예: "After Step 1, the `rust-server/` directory exists; in Step 2 rewrite its src/main.rs")

그리고 **다음은 금지**했다 (honesty / unaided 규율):

- ❌ 새로운 기획 디테일·재구조화·추가 설명 (Pitfall 7)
- ❌ 스캐폴드된 Rust 소스 코드를 프롬프트에 붙여넣기
  → 35B가 *모든* 소스를 직접 작성해야 하는 "unaided discipline" 위반이 되므로
- ❌ v1 시절의 `~14–32s/call` 같은 예측치를 측정값처럼 인용

즉 Arm A 플랜 파일(`claude-plan.md`) 자체가 "이건 v1.2 분해를 의미 보존하며 단일 세션 번호
플랜으로 옮긴 것일 뿐, 새 기획 없음"이라고 머리말에 명시하고 있다.

*근거: `claude-plan.md` 머리말, `12-01-PLAN.md` <honesty_constraints> + Task 2 STEP 2,
`12-01-SUMMARY.md` key-decisions*

---

## 4. control block 대칭 구성 (Arm B와 짝 맞추기)

Arm A 플랜은 단독으로 존재하지 않는다. Arm B와 **byte-identical한 control block**을 공유하고,
오직 "플랜 블록"만 달라야 실험이 성립한다.

```
Arm A 프롬프트 = [control block] + "Complete the following numbered steps..." + Step 1/2/3
Arm B 프롬프트 = [control block] + "Plan your own implementation steps using the task tracker..."
                  └────────────── 동일 ──────────────┘   └──── 여기만 다름 ────┘
```

control block = 목표(8080에서 hello\n 응답·loop) + 제약(std-only, no crates) +
canonical test(`curl -s http://localhost:8080/` → `hello`, exit 0) + bash-only 파일 작성 규칙.

워크스페이스 경로 차이가 diff에 잡히지 않도록 control block은 `__WORKDIR__` 토큰으로 쓰고,
각 arm이 자기 경로로 치환하는 방식을 썼다.

*근거: `12-01-PLAN.md` Task 2 STEP 1·3, `CONTROL-BLOCK-rust.txt`, `oh-prompt.txt`(Arm A 최종)*

---

## 5. 확정 게이트: 강제 symmetry diff (METH-01 / Pitfall 1)

플랜은 "썼다"로 끝나지 않고, **literal diff로 대칭을 증명한 뒤에야 확정**됐다. 이게 연구 전체가
얹혀 있는 토대라서 모델을 한 번이라도 호출하기 *전에* 깬다.

절차:
1. 두 프롬프트의 `__WORKDIR__`를 토큰으로 되돌리고(경로 차이 제거),
2. 각자의 가변 블록(Arm A=번호 스텝 전체, Arm B=self-plan 한 줄)을 제거,
3. 남은 control block끼리 `diff` → **차이 0이어야 함**.
4. 결과를 `task-prompts/PROMPT-DIFF-rust.txt`에 명령어·마스킹 설명과 함께 저장,
   깨끗하면 마지막 줄에 `CONTROL-BLOCK SYMMETRY: PASS`.

차이가 하나라도 나오면 control block이 clean하게 diff될 때까지 프롬프트를 고친다.
(실제로는 첫 시도에 exit 0으로 깨끗하게 통과했다.)

*근거: `12-01-PLAN.md` Task 2 STEP 4 + <verification>, `12-01-SUMMARY.md` Issues Encountered,
`PROMPT-DIFF-rust.txt`*

---

## 6. 전체 파이프라인 (요약 도식)

```
[연구 질문 고정]                        §1
   "전문가 플랜이 35B 실행을 돕나?"  → Arm A는 '재기획'이 아니라 '검증된 분해 재사용'이어야 함
        │
        ▼
[v1.2 분해 가져오기]                     §2
   phase 08 task1/2/3.txt  ──┐
        │                    │
        ▼                    │
[mechanical conversion]      │           §3
   3 서브태스크 → 3 번호 스텝 │
   포맷·state-handoff만 추가  │
   새 기획·소스 금지          │
        │                    │
        ▼                    ▼
[claude-plan.md]   +   [공유 control block]   §4
        │                    │
        └──────┬─────────────┘
               ▼
[Arm A oh-prompt.txt 조립]               §4
        │
        ▼
[강제 symmetry diff]                     §5  ← 모델 호출 前 게이트
   PROMPT-DIFF-rust.txt → "SYMMETRY: PASS"
        │
        ▼
   Arm A 플랜 확정 → 12-02에서 라이브 실행
```

---

## 7. 결과물 위치 (traceability)

| 산출물 | 경로 |
|---|---|
| Arm A 플랜 입력(분해 기록) | `captured-planning/rust/arm-a/planning-artifact/claude-plan.md` |
| Arm A 최종 OH 프롬프트 | `captured-planning/rust/arm-a/planning-artifact/oh-prompt.txt` |
| 공유 control block | `task-prompts/CONTROL-BLOCK-rust.txt` |
| 대칭 증거 diff | `task-prompts/PROMPT-DIFF-rust.txt` (`CONTROL-BLOCK SYMMETRY: PASS`) |
| 이 과정을 지시한 플랜 | `12-01-PLAN.md` (Task 2) |
| 실행 요약 | `12-01-SUMMARY.md` |

(경로는 모두 `.planning/milestones/v1.4-phases/12-harness-rust-pilot/` 기준)

---

## 8. 한 문장 핵심

> Arm A 플랜은 **Claude가 새로 머리 써서 짠 플랜이 아니라**, 검증된 v1.2 분해를 의미 보존하며
> 단일 세션 3-스텝으로 옮긴 뒤(§3), Arm B와 control block이 byte-identical함을 diff로 증명(§5)해
> 확정한 것이다 — 그래야 "전문가 플랜의 유무"만이 두 arm의 유일한 차이가 되기 때문이다.
