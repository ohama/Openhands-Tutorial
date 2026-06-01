# 완성된 Scala 계산기

이 장은 7부의 마무리입니다. 에이전트가 작성한 Scala 3 계산기의 최종 소스를 모두 보여주고, 실제 캡처된 실행 증거로 동작을 확인하며, 솔직한 성능 기록과 계산기 삼부작 완성으로 끝맺습니다.

---

## 완성된 소스

### Calc.scala (에이전트 작성, 70줄)

task2에서 비보조 상태로 작성하고, task3에서 하나의 자가 수정(`private var pos` → `var pos`)을 거쳐 최종 확정된 계산기 코드입니다. `final-source/Calc.scala`에서 그대로 인용합니다(70줄, line 10: `var pos = 0`).

```scala
@main def calc(args: String*) =
  val expr = args.headOption.getOrElse(throw new IllegalArgumentException("Usage: calc <expression>"))
  val parser = new ExprParser(expr)
  val result = parser.parseExpression()
  if parser.pos < expr.length then
    throw new IllegalArgumentException("Unexpected character: " + expr(parser.pos))
  println(result)

class ExprParser(input: String):
  var pos = 0
  private def peek(): Option[Char] = if pos < input.length then Some(input(pos)) else None
  private def consume(): Char =
    val c = input(pos)
    pos += 1
    c
  private def skipWhitespace(): Unit =
    while pos < input.length && input(pos).isWhitespace do pos += 1

  def parseExpression(): Int =
    var left = parseTerm()
    while true do
      skipWhitespace()
      peek() match
        case Some('+') =>
          consume()
          skipWhitespace()
          val right = parseTerm()
          left = left + right
        case Some('-') =>
          consume()
          skipWhitespace()
          val right = parseTerm()
          left = left - right
        case _ => return left
    left

  def parseTerm(): Int =
    var left = parseFactor()
    while true do
      skipWhitespace()
      peek() match
        case Some('*') =>
          consume()
          skipWhitespace()
          val right = parseFactor()
          left = left * right
        case Some('/') =>
          consume()
          skipWhitespace()
          val right = parseFactor()
          left = left / right
        case _ => return left
    left

  def parseFactor(): Int =
    skipWhitespace()
    peek() match
      case Some('(') =>
        consume()
        skipWhitespace()
        val result = parseExpression()
        skipWhitespace()
        if peek() == Some(')') then consume()
        else throw new IllegalArgumentException("Expected )")
        result
      case Some(c) if c.isDigit =>
        val start = pos
        while pos < input.length && input(pos).isDigit do pos += 1
        input.substring(start, pos).toInt
      case _ => throw new IllegalArgumentException(s"Unexpected character: ${peek()}")
```

출처: final-source/Calc.scala

### Hello.scala (task1 스캐폴드 검증용)

```scala
@main def hello() = println("SCALA_OK")
```

출처: final-source/Hello.scala

---

## 실행 결과 요약

| 항목 | 결과 |
|------|------|
| 컴파일 상태 | PASS (자가 수정 1회 후) |
| `2+3*4` | `14` (exit 0) |
| `(2+3)*4` | `20` (exit 0) |
| `10-3-2` | `5` (exit 0, 왼쪽 결합) |
| 호스트 재실행 (2026-06-01) | 일치 (14 / 20 / 5) |
| 외부 의존성 | 없음 (std-only) |
| sealed trait Expr ADT | 없음 (직접 Int 반환 재귀 하강) |

---

## 타이밍 — 실제 측정값

아래 수치는 JSONL 타임스탬프에서 계산된 실제 측정값입니다. 추정치가 아닙니다.

| 태스크 | 첫 이벤트 | 마지막 이벤트 | 소요 시간 | TerminalActions | 평균 LLM 호출 간격 | 최소 | 최대 |
|--------|-----------|---------------|-----------|----------------|-------------------|------|------|
| task1-scaffold | 14:40:30.693 | 14:41:01.220 | **30.5초** | 4 | 2.1초 | 1.1초 | 2.9초 |
| task2-write-calc | 14:42:16.270 | 14:45:11.031 | **174.8초 (~2분 55초)** | 20 | 6.5초 | 1.4초 | 14.7초 |
| task3-buildtest | 14:52:18.696 | 14:52:48.221 | **29.5초** | 6 | 2.3초 | 1.9초 | 2.8초 |
| **합계 (active)** | — | — | **234.8초 (~3분 55초)** | **30** | **~5.0초 평균** | — | — |

- **태스크 간 대기 시간:** task1→task2 약 1.25분, task2→task3 약 7.1분 (운영자 검토 및 재실행). 위 표의 소요 시간은 에이전트 active 시간만입니다.

출처: CAPTURE-MANIFEST.md, Timing Summary 절

---

## 타이밍 표기에 대한 솔직한 주의

> **솔직한 표기 주의:** v1 35B에 대해 한때 인용되던 "~14–32초/call" 수치는 2026-05-28 pre-run 예측값(v1 ROADMAP의 사전 예측)이며 실측이 아닙니다. 부록 C가 이를 바로잡았고, 본 장도 부록 C와 동일하게 파생 측정값 약 5.3초/call을 v1 35B 기준으로 사용합니다. 이 v1.3 Scala 실행의 실측 평균은 약 5.0초/call(전체 active time 234.8초 ÷ 30 TerminalAction)입니다.

---

## 4부 F# 계산기와의 대조 — 재귀 하강 vs FsLex/FsYacc

CHAP-01이 요구하는 대조 주석입니다.

**4부 (F# 계산기, v1, 2026-05-28):**

35B 모델은 FsLex `.fsl` 렉서 파일을 비보조 상태로 올바르게 생성하지 못했습니다. 세 번의 별도 에이전트 실행(94 + 27 + 16 TerminalAction)이 모두 실패했습니다 — 잘못된 문법 형식, `%%` 혼동 등. 결국 FsLex 렉서 파일은 태스크 프롬프트에 텍스트 그대로 포함(스캐폴드)됐고, 에이전트는 그 내용을 파일로 복사했습니다.

출처: CAPTURE-MANIFEST.md, Comparison Hook 절 / src/ch04-calculator/intro.md

**7부 (Scala 3 계산기, v1.3, 2026-06-01):**

같은 35B 모델이 손으로 작성하는 재귀 하강 파서를 비보조 상태로 1회 시도에 완성했습니다. 스캐폴드가 없었고 에이전트 자신의 오류 수정 1회로 통과했습니다.

**정직한 대조 프레임:**

"**손 작성 재귀 하강 + 패턴 매칭 (비보조)**" vs "**FsLex/FsYacc DSL (스캐폴드 제공됨)**"

참고: 7부의 Scala 계산기에는 `sealed trait Expr` ADT가 없습니다(CAPTURE-MANIFEST.md, Scala 3 Idiom Notes: `adt-style: None`). 에이전트는 sealed trait / case class 트리 없이 `Int`를 직접 반환하는 재귀 하강 파서를 선택했습니다. 대조는 "ADT 방식 vs FsLex 방식"이 아니라 "손 작성 재귀 하강(비보조) vs 파서 생성기 DSL(스캐폴드)"입니다.

**핵심 관찰:** 어려운 부분은 계산기 자체가 아닙니다. FsLex/FsYacc는 이 모델의 훈련 데이터에서 드문 DSL 형식이었고, 손으로 작성하는 재귀 하강 파서는 일반적인 패턴입니다. 같은 모델이 같은 목표(산술 계산기)를 도메인에 따라 다른 결과로 처리했습니다.

---

## 계산기 삼부작 완성

| 버전 | 예제 | 언어 | 파서 방식 | 비보조 여부 |
|------|------|------|-----------|-------------|
| v1 (4부, 2026-05-28) | F# 계산기 | F# | FsLex/FsYacc DSL | **스캐폴드 필요** |
| v1.2 (6부, 2026-06-01) | Rust HTTP 서버 | Rust | 해당 없음 | unaided (1회) |
| v1.3 (7부, 2026-06-01) | Scala 3 계산기 | Scala 3 | 손 작성 재귀 하강 | **unaided (1회)** |

FsLex 스캐폴드가 필요했던 같은 35B 모델이, 동일한 산술 계산기 목표를 Scala 3 재귀 하강 파서로 비보조 상태로 완성했습니다. 이것이 7부가 기록하는 핵심 사실입니다.

출처: CAPTURE-MANIFEST.md, Comparison Hook 및 Calculator-trilogy completion 절

---

## Sources / 출처

이 7부에서 인용한 증거 파일 목록입니다.

- `.planning/phases/10-capture-the-35b-scala-calculator-run/captured-scala/CAPTURE-MANIFEST.md` — 실행 메타데이터, 요구사항 매핑, 타이밍, 오류·수정 기록, Comparison Hook
- `.planning/phases/10-capture-the-35b-scala-calculator-run/captured-scala/logs/task1-scaffold.jsonl` — task1 원시 JSONL (4 TerminalAction)
- `.planning/phases/10-capture-the-35b-scala-calculator-run/captured-scala/logs/task2-write-calc.jsonl` — task2 원시 JSONL (20 TerminalAction; 이벤트 #6/#30/#32/#34/#36/#38/#40/#41)
- `.planning/phases/10-capture-the-35b-scala-calculator-run/captured-scala/logs/task3-buildtest.jsonl` — task3 원시 JSONL (6 TerminalAction; 이벤트 #6–#15)
- `.planning/phases/10-capture-the-35b-scala-calculator-run/captured-scala/final-source/Calc.scala` — 최종 70줄 Scala 3 계산기 소스 (post-sed, `var pos = 0`)
- `.planning/phases/10-capture-the-35b-scala-calculator-run/captured-scala/final-source/Hello.scala` — task1 스캐폴드 검증 파일
- `.planning/phases/10-capture-the-35b-scala-calculator-run/captured-scala/test-output.txt` — 호스트 독립 재실행 결과 (2026-06-01T06:03:25Z)
