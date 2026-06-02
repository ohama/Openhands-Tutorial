open System
open FSharp.Text.Lexing

[<EntryPoint>]
let main argv =
    if argv.Length <> 1 then
        eprintfn "Usage: calc <expression>"
        eprintfn "Example: calc \"2+3*4\""
        1
    else
        let expression = argv.[0]
        let lexbuf = LexBuffer<char>.FromString(expression)
        let result = Parser.start Lexer.tokenize lexbuf
        printfn "%d" result
        0
