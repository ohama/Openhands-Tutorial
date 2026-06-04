//> using scala "3"

object Calc {

  sealed trait Token
  case class Num(value: Int)    extends Token
  case class Op(sym: String)    extends Token
  case object Eof               extends Token

  class Lexer(input: String) {
    private var pos = 0
    private val chars = input.toArray

    def skipWhitespace(): Unit = {
      while (pos < chars.length && chars(pos).isWhitespace) pos += 1
    }

    def nextToken: Token = {
      skipWhitespace()
      if (pos >= chars.length) return Eof
      val c = chars(pos)
      if (c.isDigit) {
        val start = pos
        while (pos < chars.length && chars(pos).isDigit) pos += 1
        val numStr = new String(chars, start, pos - start)
        Num(numStr.toInt)
      } else {
        pos += 1
        Op(c.toString)
      }
    }
  }

  class Parser(tokens: List[Token]) {
    private var pos = 0

    private def current: Token =
      if (pos < tokens.length) tokens(pos) else Eof

    private def consume: Token = {
      val t = current
      pos += 1
      t
    }

    def parse: Int = {
      val result = expr
      if (current != Eof)
        throw new RuntimeException(s"Unexpected token: $current")
      result
    }

    def expr: Int = {
      var left = term
      while (current == Op("+") || current == Op("-")) {
        val op = consume match { case Op(s) => s }
        val right = term
        left = if (op == "+") left + right else left - right
      }
      left
    }

    def term: Int = {
      var left = factor
      while (current == Op("*") || current == Op("/")) {
        val op = consume match { case Op(s) => s }
        val right = factor
        left = if (op == "*") left * right else left / right
      }
      left
    }

    def factor: Int = {
      current match {
        case Num(n) =>
          consume
          n
        case Op("(") =>
          consume
          val result = expr
          if (current != Op(")"))
            throw new RuntimeException("Expected ')'")
          consume
          result
        case Op("-") =>
          consume
          -factor
        case Op("+") =>
          consume
          factor
        case _ =>
          throw new RuntimeException(s"Unexpected token: $current")
      }
    }
  }

  def main(args: Array[String]): Unit = {
    if (args.length != 1) {
      System.err.println("Usage: scala-cli run Calc.scala -- \"<expression>\"")
      System.exit(1)
    }
    val input = args(0)
    val lexer = new Lexer(input)
    val tokens = Iterator.continually(lexer.nextToken).takeWhile(_ != Eof).toList
    val parser = new Parser(tokens)
    val result = parser.parse
    println(result)
  }
}
