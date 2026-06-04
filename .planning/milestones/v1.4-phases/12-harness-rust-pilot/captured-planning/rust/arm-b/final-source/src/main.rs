use std::io::{Read, Write};
use std::net::TcpListener;

fn handle_client(mut stream: impl Read + Write) {
    // Read the request (just need enough to consume the HTTP request headers)
    let mut buffer = [0u8; 4096];
    let _ = stream.read(&mut buffer);

    // Send a minimal HTTP/1.1 response
    let response = "HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nhello\n";
    let _ = stream.write_all(response.as_bytes());
    let _ = stream.flush();
}

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").expect("Failed to bind to port 8080");
    println!("Listening on http://0.0.0.0:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                handle_client(stream);
            }
            Err(e) => {
                eprintln!("Connection failed: {}", e);
            }
        }
    }
}
