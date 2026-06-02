use std::io::{Read, Write};
use std::net::TcpListener;

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").expect("Failed to bind to port 8080");
    println!("Server listening on 0.0.0.0:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(mut stream) => {
                // Read the request (we only need a small buffer for the headers)
                let mut buffer = [0u8; 1024];
                if let Ok(_n) = stream.read(&mut buffer) {
                    // Build a minimal HTTP/1.1 200 OK response
                    let response = "HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nhello\n";
                    let _ = stream.write_all(response.as_bytes());
                    let _ = stream.flush();
                }
            }
            Err(e) => {
                eprintln!("Connection error: {}", e);
            }
        }
    }
}
