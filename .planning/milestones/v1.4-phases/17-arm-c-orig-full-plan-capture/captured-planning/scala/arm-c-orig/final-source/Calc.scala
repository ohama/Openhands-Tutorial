// Scala 3 integer calculator — stdlib only, single file, run with scala-cli.
// 2+3*4 -> 14   (2+3)*4 -> 20   10-3-2 -> 5
@main def run(arg: String): Unit =
  println(eval(arg))

def eval(input: String): Int =
  val parser = Parser(tokenize(input))
  parser.parseExpr()

def tokenize(s: String): List[String] =
  val buf = scala.collection.mutable.ListBuffer[String]()
  var i = 0
  while i < s.length do
    val c = s(i)
    if c.isWhitespace then i += 1
    else if c.isDigit then
      val start = i
      while i < s.length && s(i).isDigit do i += 1
      buf += s.substring(start, i)
    else
      buf += c.toString
      i += 1
  buf.toList

class Parser(tokens: List[String]):
  private var pos = 0
  private def peek: Option[String] = tokens.lift(pos)
  private def next(): String = { val t = tokens(pos); pos += 1; t }

  def parseExpr(): Int =
    var acc = parseTerm()
    while peek.contains("+") || peek.contains("-") do
      val op = next()
      val rhs = parseTerm()
      acc = if op == "+" then acc + rhs else acc - rhs
    acc

  private def parseTerm(): Int =
    var acc = parseFactor()
    while peek.contains("*") || peek.contains("/") do
      val op = next()
      val rhs = parseFactor()
      acc = if op == "*" then acc * rhs else acc / rhs
    acc

  private def parseFactor(): Int =
    peek match
      case Some("(") =>
        next()
        val e = parseExpr()
        next()
        e
      case _ =>
        next().toInt
