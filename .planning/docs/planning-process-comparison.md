# 플래닝 프로세스 3-way 비교: Arm A vs Arm B vs GSD(Arm C)

> 같은 과제("std-only Rust HTTP 서버, 8080, `hello\n`, loop")를 세 가지 **플래닝 방식**으로
> 세운 뒤, 만들어진 *플랜 자체*를 구조 비교한다.
> 작성일: 2026-06-04 · 짝 문서: [`arm-a-plan-process.md`](./arm-a-plan-process.md) · [`arm-b-plan-process.md`](./arm-b-plan-process.md)

---

## 0. 정직성 라벨 (먼저 읽을 것)

- **Arm A / Arm B** 는 2026-06-02에 실제 35B에 캡처된 v1.4 pilot의 일부다(n=1).
- **Arm C (GSD)** 는 **2026-06-04에 이 비교를 위해 새로 만든 플랜**이다. GSD의 실제
  에이전트(gsd-phase-researcher → gsd-planner → gsd-plan-checker)를 돌려 생성했고,
  **35B에 실행하지 않았다.** 따라서 여기에는 실행/측정 지표가 없다 — **plan-vs-plan 구조 비교**일 뿐이다.
- 산출물: `.planning/docs/gsd-arm-c/RESEARCH.md`, `.planning/docs/gsd-arm-c/01-PLAN.md`.

---

## 1. 세 방식의 플래닝 *프로세스* 비교

| | **Arm A** (Claude 수동) | **Arm B** (35B self-plan) | **Arm C** (GSD 파이프라인) |
|---|---|---|---|
| 플랜 작성자 | Claude, 설계 시점 | **35B, 런타임** | Claude, 설계 시점 |
| 단계 수 | 1 (기계적 이식) | 1 유도 + 런타임 생성 | **3 에이전트** (research→plan→verify) |
| Research 단계 | 암묵적(검증된 v1.2 재사용) | 없음(35B 자체 지식) | **명시적 RESEARCH.md** (pitfall 카탈로그) |
| 검증 게이트 | symmetry diff (control-block byte-identical) | open-unknown #1 (task tracker emit 여부) | **gsd-plan-checker** goal-backward 검증 |
| 수정 루프 | 없음(첫 시도 clean) | 해당 없음 | 최대 3회 (이번엔 1회 PASS) |
| 출력 형식 | 번호 스텝 텍스트 | TaskTracker task list (JSON) | frontmatter + XML tasks + must_haves |

### 프로세스 도식 한 눈에

```
Arm A:  [v1.2 분해] ─기계적 이식→ [3 스텝] ─symmetry diff→ 확정
Arm B:  [control block + "스스로 플랜하라"] ─런타임→ [35B가 4 task 생성] ─캡처→ 확정
Arm C:  [goal] →gsd-researcher→ [RESEARCH.md] →gsd-planner→ [01-PLAN.md] →gsd-checker→ PASS
```

---

## 2. 만들어진 *플랜* 내용 비교

| 항목 | Arm A | Arm B (35B) | Arm C (GSD) |
|---|---|---|---|
| 스텝/태스크 수 | 3 (build+test 합침) | 4 (build·test 분리) | 3 (scaffold / impl / test) |
| **소스 코드 포함?** | **❌ 없음 (의도적)** | ❌ 없음 (notes만) | **✅ 완성 구현 전체 임베드** |
| 빌드 명령 | `cargo build` | `cargo build --release` | `cargo build` (+ `cargo init`) |
| 에러 대응 지시 | "컴파일 에러 읽고 고쳐라(bash-only)" | 없음 | pitfall 5개 사전 차단 명시 |
| 검증 방법 | curl + exit code 보고 | curl 검증(task 4) | grep 패턴 + scripted exit-0 assert |
| 메타데이터 | 없음 (프롬프트 텍스트) | TaskTracker status 추적 | frontmatter·must_haves·key_links |

### 결정적 차이 — Arm C는 **답을 적어준다**

GSD 플랜의 Task 2는 RESEARCH에서 검증한 **~25줄 Rust 구현 전체를 그대로 붙여넣으라**고 지시한다
(`01-PLAN.md` 127–160행). CRLF 프레이밍, `Content-Length`, `Connection: close`, `read_line`
한 줄만 읽기까지 — make-or-break 지점을 전부 코드로 박아둔다.

대조적으로:
- **Arm A**는 머리말에 *"No scaffolded source code … the 35B writes all source code itself"* 라고
  명시하며 코드를 의도적으로 뺐다.
- **Arm B**는 35B 자신이 만든 것이라 당연히 코드가 없고 `notes`에 "use std::net::TcpListener…"
  수준의 방향만 있다.

---

## 3. 왜 이 차이가 핵심인가 — "실행 최적화" vs "측정 보존"

GSD와 study-arm은 **최적화 목표가 정반대**다.

| | 목표 | 그래서 플랜은… |
|---|---|---|
| **GSD (Arm C)** | executor가 **성공**하게 | 리서치로 pitfall을 미리 캐고, **정답 코드를 떠먹여 준다** |
| **Arm A/B (study)** | executor 능력을 **측정** | 일부러 코드를 **빼서**, 35B가 스스로 쓰고 self-correct 하는지 본다 |

→ **GSD의 자연스러운 산출물은 이 연구에 그대로 쓰면 실험을 무효화한다.** 완성 구현을 프롬프트에
넣으면 35B는 복붙만 하게 되고, "전문가 플랜이 35B의 *실행/작성*을 돕는가"라는 독립변수가 무너진다.
이건 메모리 노트 [[qwen35b-agentic-limits]]("scaffold OOD bits, never manually fix to fake
success")와 같은 결의 위험이다 — **떠먹여 주면 측정이 아니라 연출이 된다.**

거꾸로, **Arm A를 GSD식으로 만들면 더 견고하다.** GSD 리서치는 35B가 Arm A를 실행하다 부딪힐
법한 함정(curl keep-alive 행, EOF 데드락, CRLF 누락)을 미리 차단한다. 실제 Arm A pilot에서
35B는 multi-command 거부 같은 self-correction을 보였는데(CAPTURE-MANIFEST #17/#19), GSD 플랜은
그런 마찰을 사전에 제거하는 쪽이다 — **관찰하고 싶은 바로 그 행동을 없앤다.**

---

## 4. 검증 게이트 비교 (세 방식 모두 "검증"은 한다)

| | 무엇을 보장하나 | 한계 |
|---|---|---|
| Arm A: symmetry diff | 두 arm의 control block이 byte-identical → 변수 오염 방지 | 플랜 *품질*은 안 봄 |
| Arm B: open-unknown #1 | 35B가 task tracker를 실제로 emit하는지 | 플랜 *내용*은 35B에 위임 |
| Arm C: gsd-plan-checker | goal-backward로 "이 플랜 실행 시 목표 달성?" | checker가 비-blocking 약점 2건 발견(아래) |

GSD checker가 잡은 비-blocking 관찰(실제로 유용했던 지점):
1. Task 3의 `O1=$(curl …)`가 trailing `\n`을 strip → 양변 모두 `"hello"`라 통과는 하지만
   **body의 newline을 엄격 검증하진 못함**. (canonical은 `hello\n` 요구)
2. `127.0.0.1` bind + `localhost` 테스트 → IPv6-first 호스트면 깨질 수 있음(이 macOS에선 안전).

→ 세 게이트는 **검증 대상이 다르다**: Arm A=대칭성, Arm B=프로세스 발현, Arm C=플랜→목표 정합성.

---

## 5. 종합 — 어떤 방식이 "더 나은가"는 목적에 달렸다

| 쓰임새 | 최적 방식 | 이유 |
|---|---|---|
| 실제로 서버를 **완성**시키기 | **GSD (Arm C)** | 리서치+정답코드+검증으로 실패율 최저 |
| 모델의 **작성 능력 측정** | **Arm A/B** | 코드를 빼야 측정이 성립 |
| A/B 실험의 **대조군** | **Arm B** | "플랜 없음(self-plan)" baseline |
| A/B 실험의 **처치군** | **Arm A** | "전문가 플랜 있음", 단 코드 없는 mechanical 버전 |

**한 문장:** GSD 파이프라인은 *실행을 성공시키도록* 설계된 플래너라서 정답 코드까지 떠먹여 주는
반면, study의 Arm A/B는 *능력을 측정하도록* 일부러 코드를 빼고 35B의 self-correction 여지를
남긴다 — 그래서 GSD 플랜은 "더 좋은 플랜"이지만 이 연구의 **측정 도구로는 부적합**하고,
역으로 GSD의 pitfall 리서치는 Arm A를 더 견고하게 만드는 데 차용할 수 있다.

---

## 5.5 후속 — Arm C (mechanical): study-usable 버전 생성됨 (2026-06-04)

§3의 결론("GSD 원본은 정답 코드를 떠먹여 줘 측정 도구로 부적합")을 받아, GSD 플랜을 **코드 없는
mechanical 버전**으로 변환해 실제 투입 가능한 후보 arm을 만들었다.

- 변환: Rust 소스·정답 byte-string·API 토큰 전부 제거, GSD의 pitfall 5종은 **HTTP 요구사항/실패
  모드 prose로 보존**.
- control block은 study 캐노니컬과 **byte-identical** 확인 (`PROMPT-DIFF.txt` → `SYMMETRY: PASS`).
- 산출물: `.planning/docs/gsd-arm-c/arm-c-mechanical/{oh-prompt.txt, PROMPT-DIFF.txt, gsd-mechanical-plan.md}`.

이로써 "전문가 플랜 정보량" 그라디언트가 정렬된다:

```
Arm B (self-plan, 플랜 없음)
  < Arm A (구조만, pitfall 無)
    < Arm C-mech (구조 + pitfall 가이드, 코드 無)   ← study-usable
      < Arm C-orig (구조 + pitfall + 정답 코드)        ← study-invalid (복붙)
```

Arm A vs Arm C-mech은 "코드 없음"을 고정한 채 **실패 모드 사전 경고의 가치**만 분리해 측정할 수
있는 깔끔한 대조다.

**캡처 완료 (2026-06-04, Phase 15):** Arm C-mech를 정식 phase로 승격해 실제 35B로 캡처했다 →
**canonical curl PASS (event #31), honesty gate PASS (17/17 source=agent), unaided 작성 확인.**
35B는 withheld된 GSD 레퍼런스와 *다른* 구현(`stream.read(&buf)` / `0.0.0.0` bind / `.expect`)을
직접 작성하되, prose 프레이밍 가이드(Content-Length·Connection: close·CRLF)는 정확히 적용 —
curl-hang/데드락 없이 통과했고, 막힌 건 일반 Rust 컴파일 에러 2건(미사용 import, `Read` trait
미import)으로 스스로 self-correct 했다. 즉 **"정답을 주지 않고 실패모드만 알려줘도 35B가 통과"** 가
이 arm에서 관측됐다. (n=1 단독 캡처 — Arm A/B와 cache 상태가 달라 **timing 비교는 무효**.)
상세: `.planning/milestones/v1.4-phases/15-arm-c-mechanical-capture/15-CAPTURE-MANIFEST.md`.

---

## 6. 산출물 / traceability

| 산출물 | 경로 |
|---|---|
| GSD Research | `.planning/docs/gsd-arm-c/RESEARCH.md` |
| GSD Plan (Arm C) | `.planning/docs/gsd-arm-c/01-PLAN.md` |
| Arm A 플랜 | `…/12-harness-rust-pilot/…/arm-a/planning-artifact/claude-plan.md` |
| Arm B self-plan | `…/12-harness-rust-pilot/…/arm-b/planning-artifact/oh-self-plan.md` |
| 프로세스 문서 | `arm-a-plan-process.md`, `arm-b-plan-process.md` (this dir) |

**GSD 파이프라인 실행 기록 (2026-06-04):**
gsd-phase-researcher (RESEARCH.md, confidence HIGH) → gsd-planner (1 plan, 3 tasks) →
gsd-plan-checker (**VERIFICATION PASSED**, 1회 통과, 비-blocking 관찰 2건).
