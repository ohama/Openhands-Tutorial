open System
open FSharp.Text.Lexing

[<EntryPoint>]
let main argv =
    if Array.length argv <> 1 then
        eprintfn "Usage: calc <expression>"
        1
    else
        let input = argv.[0]
        let lexbuf = LexBuffer<char>.FromString input
        let result = Parser.start Lexer.tokenize lexbuf
        printfn "%d" result
        0
