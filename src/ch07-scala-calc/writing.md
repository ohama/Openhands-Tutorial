# 코드 작성 단계

이 장에서는 OpenHands 에이전트가 Scala 3 재귀 하강 계산기의 소스 파일 — `Calc.scala` — 을 실제로 작성하는 과정을 따라갑니다. 에이전트가 어떤 명령을 실행했는지, 어떤 코드를 작성했는지를 캡처된 증거에서 직접 인용합니다.

---

## 스캐폴딩 공개

task2를 시작하기 전에 중요한 사실을 밝힙니다.

- **scaffold-invoked: NO** — 스캐폴드는 발동되지 않았습니다.
- **did-write-calc-unaided: YES** — 에이전트는 계산기 코드를 비보조 상태로 직접 작성했습니다.
- **unaided-attempts: 1** — 첫 번째 시도에서 작성했습니다.

4부에서 FsLex 렉서 파일을 프롬프트에 제공해야 했던 것과 달리, 이번에는 에이전트가 목표 설명("정수 덧셈, 뺄셈, 곱셈, 나눗셈을 지원하는 Scala 3 계산기, 연산자 우선순위와 괄호를 올바르게 처리하라")만으로 코드를 작성했습니다.

폴백 스캐폴드(task2-calc-scaffold.txt)는 만일을 위해 준비됐으나, 에이전트가 task2에서 계산기를 직접 완성했기 때문에 한 번도 사용되지 않았습니다.

출처: CAPTURE-MANIFEST.md, Calculator Outcome 절

---

## task2 — 에이전트가 계산기를 작성하다

> **사용자 프롬프트**
>
> `task2-write-calc.txt` 요약: "`calc/` 폴더 안에 Scala 3 명령줄 계산기 `Calc.scala`를 작성하라. `scala-cli run Calc.scala -- "2+3*4"`가 `14`를 출력해야 하며, `(2+3)*4`는 `20`, `10-3-2`는 `5`를 출력해야 한다. 연산자 우선순위와 왼쪽 결합을 올바르게 구현하라. 표준 라이브러리만 사용하라. 빌드와 테스트는 다음 태스크에서 수행한다."

> **내부 프로세스**
>
> - 이벤트 #6 (TerminalAction): 첫 Calc.scala 작성 시도 (heredoc)
> - 이벤트 #30, #32, #34, #36, #38 (TerminalAction): `printf '%s\n'` 명령으로 파일 섹션을 순서대로 작성해 최종 Calc.scala 완성
> - 이벤트 #40 (TerminalAction): `cat Calc.scala`로 파일 내용 검증
> - 이벤트 #41 (ObservationEvent, exit=0): 70줄 Scala 3 계산기 내용 확인

> **결과**
>
> 20회의 TerminalAction, 174.8초(약 2분 55초). 에이전트가 `@main def calc(args: String*)` 진입점과 `class ExprParser(input: String):` 재귀 하강 파서를 사용해 70줄의 Scala 3 계산기를 비보조 상태로 작성했습니다. 출처: task2-write-calc.jsonl, CAPTURE-MANIFEST.md § SCAL-02

---

## 에이전트가 작성한 계산기 코드

아래는 task2에서 에이전트가 작성한 `Calc.scala`입니다(이벤트 #40/#41에서 `cat`으로 검증, task3의 `sed` 수정을 거쳐 최종 확정). `final-source/Calc.scala`(70줄, post-fix 상태)에서 그대로 인용합니다.

> **주의:** task2 완료 시점의 온디스크 버전은 `private var pos = 0`으로 기록됐습니다. task3에서 에이전트 자신의 `sed` 명령이 `private`를 제거해 `var pos = 0`으로 수정했습니다. 아래 코드는 수정 후 최종 상태입니다(line 10: `var pos = 0`).

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

출처: final-source/Calc.scala (70줄)

---

## 코드 해설

에이전트가 선택한 설계를 코드에서 직접 읽을 수 있습니다.

**Scala 3 진입점**

`@main def calc(args: String*)` — Scala 3의 `@main` 어노테이션을 사용하는 진입점입니다. Scala 2의 `object extends App` 또는 `def main(args: Array[String])`이 아닙니다. 에이전트가 프롬프트에서 별도 지시 없이 Scala 3 관용어를 선택했습니다. 슬립이 전혀 없습니다.

**클래스 선언과 유의미한 들여쓰기**

`class ExprParser(input: String):` — Scala 3의 `:` 블록 구문(significant-indentation)을 사용합니다. 중괄호 없이 들여쓰기로 블록을 표현하는 Scala 3 전용 방식입니다.

**`sealed trait Expr` ADT 없음**

CAPTURE-MANIFEST.md의 Scala 3 Idiom Notes가 명시하듯: `adt-style: None`. 에이전트는 `sealed trait Expr`와 case class 트리를 사용하지 않았습니다. 대신 `parseExpression`, `parseTerm`, `parseFactor` 각 메서드가 직접 `Int`를 반환하는 단순하고 유효한 방식을 선택했습니다.

**재귀 하강 파서 구조**

세 메서드가 계층을 이루어 연산자 우선순위를 구현합니다.

```
parseExpression  →  + / - 처리 (가장 낮은 우선순위)
  parseTerm      →  * / / 처리
    parseFactor  →  숫자 리터럴, 괄호 처리 (가장 높은 우선순위)
```

**`while ... do` 루프와 왼쪽 결합**

`parseExpression`과 `parseTerm`은 `while true do { ... case _ => return left }` 루프로 같은 우선순위 연산자를 왼쪽에서 오른쪽으로 처리합니다. `10-3-2`가 `(10-3)-2 = 5`로 평가되는 것은 이 루프 구조의 결과입니다(`10-(3-2) = 9`가 아닙니다).

**`peek() match`와 패턴 매칭**

`peek() match { case Some('+') => ... case Some('-') => ... case _ => return left }` — `Option[Char]`에 대한 패턴 매칭으로 다음 문자를 확인합니다. 다른 문자나 입력 끝이 나오면 현재 결과를 반환합니다.

**표준 라이브러리만**

임포트 선언이 없습니다. `String`, `Int`, `Option`, `Some`, `None`, `IllegalArgumentException` 모두 `scala.*` / `java.lang.*`에서 기본 제공됩니다. 외부 의존성이 전혀 없습니다.

---

> **개념 ↔ 행동: 도구 사용(tool calling)과 액션-관찰 사이클**
>
> 에이전트가 `Calc.scala`를 작성할 때 "이런 파일을 만들겠습니다"라고 텍스트를 출력하는 것이 아닙니다. 이벤트 #6, #30, #32, #34, #36, #38에서 각각 `TerminalAction`을 emit해 실제 파일 쓰기 명령을 실행합니다. 이것이 1부에서 설명한 **tool calling(툴 호출)**의 실제 모습입니다 — LLM이 구조화된 호출(이름 + 인자)을 출력해 환경에 행동을 지시합니다(1부 concepts.md). 이벤트 #40의 `cat Calc.scala`(TerminalAction)는 직후 이벤트 #41 ObservationEvent로 파일 내용이 돌아오는 **액션-관찰 사이클(action-observation cycle)**의 완전한 한 번입니다. 에이전트는 이 관찰로 파일이 올바르게 작성됐음을 확인했습니다.
