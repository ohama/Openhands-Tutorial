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
