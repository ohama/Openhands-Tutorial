object Calc:
  @main def main(expr: String): Unit =
    val result = evaluate(expr)
    println(result)

  def evaluate(expr: String): Int =
    val tokens = tokenize(expr)
    val parser = new Parser(tokens)
    val result = parser.expression()
    if parser.hasMore then
      throw new RuntimeException(s"Unexpected token: ${parser.current}")
    result

  sealed trait Token
  case class Num(value: Int) extends Token
  case class Op(ch: Char) extends Token
  case object Eof extends Token

  def tokenize(input: String): List[Token] =
    val chars = input.toList.filterNot(_.isWhitespace)
    val builder = List.newBuilder[Token]
    var i = 0
    while i < chars.length do
      val c = chars(i)
      if c.isDigit then
        val start = i
        while i < chars.length && chars(i).isDigit do i = i + 1
        val num = chars.slice(start, i).mkString.toInt
        builder += Num(num)
      else
        builder += Op(c)
        i = i + 1
    builder.result()

  class Parser(tokens: List[Token]):
    private var remaining: List[Token] = tokens

    def hasMore: Boolean = remaining.nonEmpty
    def current: Token = remaining.headOption.getOrElse(Eof)
    def consume(): Token =
      val t = remaining.head
      remaining = remaining.tail
      t

    def expression(): Int =
      var acc = term()
      while hasMore do
        current match
          case Op('+') =>
            consume()
            acc = acc + term()
          case Op('-') =>
            consume()
            acc = acc - term()
          case _ => return acc
      acc

    def term(): Int =
      var acc = factor()
      while hasMore do
        current match
          case Op('*') =>
            consume()
            acc = acc * factor()
          case Op('/') =>
            consume()
            acc = acc / factor()
          case _ => return acc
      acc

    def factor(): Int =
      current match
        case Op('(') =>
          consume()
          val result = expression()
          if current != Op(')') then
            throw new RuntimeException("Expected ')'")
          consume()
          result
        case Num(n) =>
          consume()
          n
        case _ =>
          throw new RuntimeException(s"Unexpected token: ${current}")
