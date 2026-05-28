open FSharp.Text.Lexing

[<EntryPoint>]
let main args =
    if args.Length <> 1 then
        eprintf "Usage: dotnet run -- \"<expression>\"\n"
        1
    else
        let lexbuf = LexBuffer<char>.FromString args.[0]
        let result = Parser.start Lexer.tokenize lexbuf
        printfn "%d" result
        0
