module Program

open FSharp.Text.Lexing

[<EntryPoint>]
let main argv =
    let input = argv.[0]
    let lexbuf = LexBuffer<char>.FromString input
    let result = Parser.start Lexer.tokenize lexbuf
    printfn "%d" result
    0
