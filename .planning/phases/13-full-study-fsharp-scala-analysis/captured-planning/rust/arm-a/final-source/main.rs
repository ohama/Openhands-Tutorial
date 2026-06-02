use std::io::{Read, Write};
use std::net::TcpListener;

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").expect("Failed to bind to port 8080");
    println!("Listening on 0.0.0.0:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(mut stream) => {
                let mut buffer = [0u8; 1024];
                let _ = stream.read(&mut buffer);
                let response = "HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nhello\n";
                let _ = stream.write_all(response.as_bytes());
                let _ = stream.flush();
            }
            Err(e) => {
                eprintln!("Connection error: {}", e);
            }
        }
    }
}
