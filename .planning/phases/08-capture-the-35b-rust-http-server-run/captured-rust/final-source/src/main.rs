use std::io::{BufRead, BufReader, Write};
use std::net::TcpListener;

fn handle_client(mut stream: std::net::TcpStream) -> std::io::Result<()> {
    let reader = BufReader::new(&stream);
    let mut lines = reader.lines();
    // Read the request line (first line of the HTTP request)
    let _request_line = lines.next();
    // Consume remaining header lines until empty line
    for line in lines {
        match line {
            Ok(l) if l.is_empty() => break,
            Ok(_) => continue,
            Err(_) => break,
        }
    }

    let body = "hello\n";
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
        body.len(),
        body
    );
    stream.write_all(response.as_bytes())?;
    stream.flush()?;
    Ok(())
}

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").expect("Failed to bind to port 8080");
    println!("Listening on http://0.0.0.0:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if let Err(e) = handle_client(stream) {
                    eprintln!("Error handling client: {}", e);
                }
            }
            Err(e) => eprintln!("Connection failed: {}", e),
        }
    }
}
