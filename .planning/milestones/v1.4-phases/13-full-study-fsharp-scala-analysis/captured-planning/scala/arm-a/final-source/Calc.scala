import scala.annotation.tailrec

object Calc:
  enum Token:
    case Num(value: Int)
    case Plus
    case Minus
    case Star
    case Slash
    case LParen
    case RParen
    case Eof

  def tokenize(input: String): List[Token] =
    @tailrec
    def loop(chars: List[Char], acc: List[Token]): List[Token] = chars match
      case Nil => acc :+ Token.Eof
      case c :: rest if c.isWhitespace => loop(rest, acc)
      case '+' :: rest => loop(rest, acc :+ Token.Plus)
      case '-' :: rest => loop(rest, acc :+ Token.Minus)
      case '*' :: rest => loop(rest, acc :+ Token.Star)
      case '/' :: rest => loop(rest, acc :+ Token.Slash)
      case '(' :: rest => loop(rest, acc :+ Token.LParen)
      case ')' :: rest => loop(rest, acc :+ Token.RParen)
      case c :: rest if c.isDigit =>
        val (digits, remaining) = chars.span(_.isDigit)
        loop(remaining, acc :+ Token.Num(digits.mkString.toInt))
      case c :: _ =>
        throw new IllegalArgumentException(s"Unexpected character: '$c'")
    loop(input.toList, Nil)

  class Parser:
    private var pos = 0
    private var toks: List[Token] = List.empty

    def parseAll(input: List[Token]): Int =
      toks = input
      pos = 0
      val result = expr()
      if current != Token.Eof then
        throw new IllegalArgumentException(s"Unexpected token: $current after position $pos")
      result

    def current: Token =
      if pos < toks.length then toks(pos) else Token.Eof

    def consume(expected: Token): Token =
      val t = current
      if t != expected then
        throw new IllegalArgumentException(s"Expected $expected but got $t at position $pos")
      pos += 1
      t

    def expr(): Int =
      var result = term()
      while current == Token.Plus || current == Token.Minus do
        val op = current
        pos += 1
        val right = term()
        if op == Token.Plus then result = result + right
        else result = result - right
      result

    def term(): Int =
      var result = factor()
      while current == Token.Star || current == Token.Slash do
        val op = current
        pos += 1
        val right = factor()
        if op == Token.Star then result = result * right
        else result = result / right
      result

    def factor(): Int =
      current match
        case Token.Num(n) =>
          pos += 1
          n
        case Token.LParen =>
          pos += 1
          val result = expr()
          consume(Token.RParen)
          result
        case Token.Eof =>
          throw new IllegalArgumentException("Unexpected end of input")
        case other =>
          throw new IllegalArgumentException(s"Unexpected token: $other")

  def evaluate(expression: String): Int =
    val tokens = tokenize(expression)
    val parser = new Parser()
    parser.parseAll(tokens)

@main def runCalc(expression: String): Unit =
  try
    val result = Calc.evaluate(expression)
    println(result)
  catch
    case e: IllegalArgumentException =>
      println(s"Error: ${e.getMessage}")
      sys.exit(2)
