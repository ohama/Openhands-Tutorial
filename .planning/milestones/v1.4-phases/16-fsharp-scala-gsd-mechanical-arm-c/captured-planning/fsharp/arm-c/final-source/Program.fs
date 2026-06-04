open System

[<EntryPoint>]
let main argv =
    if Array.isEmpty argv then
        printfn "Usage: Calculator <expression>"
        1
    else
        let expr = argv.[0]
        let lexbuf = LexBuffer<char>.FromTextReader(new StringReader(expr))
        let result = Parser.main Lexer.tokenize lexbuf
        printfn "%d" result
        0
