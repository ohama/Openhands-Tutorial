open System
open System.IO
open Lexer
open Parser

let main argv =
    if argv.Length <> 1 then
        eprintfn "Usage: Calculator <expression>"
        exit 1

    let input = argv.[0]
    let lexbuf = LexBuffer<char>.FromTextReader(new StringReader(input))
    let result = expr lexbuf
    printfn "%d" result
    0

[<EntryPoint>]
let entry argv =
    main argv
