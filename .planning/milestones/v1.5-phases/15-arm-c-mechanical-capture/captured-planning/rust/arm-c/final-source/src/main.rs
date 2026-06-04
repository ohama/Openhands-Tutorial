use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn handle_client(mut stream: TcpStream) {
    // Read just a few bytes from the request to avoid deadlocking.
    // The client sends a request and waits for our response — it never closes.
    let mut buf = [0u8; 1024];
    let _ = stream.read(&mut buf);

    let body = "hello\n";
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
        body.len(),
        body
    );

    let _ = stream.write_all(response.as_bytes());
    let _ = stream.flush();
}

fn main() {
    let listener = TcpListener::bind("0.0.0.0:8080").expect("Failed to bind to port 8080");
    println!("Listening on 0.0.0.0:8080");

    for stream in listener.incoming() {
        match stream {
            Ok(conn) => {
                handle_client(conn);
            }
            Err(e) => {
                eprintln!("Connection error: {}", e);
            }
        }
    }
}
