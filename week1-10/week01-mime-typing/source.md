# MIME-Based Client/Server Model

## 1. Repository Structure
A clean structure ensures that both the client and server use the same "source of truth" for the protocol headers.

```
mime-socket-project/
├── shared/
│   ├── __init__.py
│   └── protocol.py      # Shared header logic & MIME constants
├── server/
│   ├── main.py          # Server entry point
│   └── storage/         # Directory for received files
├── client/
│   ├── main.py          # Client entry point
│   └── assets/          # Files to be sent (images, txt, etc.)
└── README.md
```

## 2. Implementation: The Codebase

### A. Shared Protocol (`shared/protocol.py`)
This module handles the "Envelope" creation. We will use a JSON header followed by a newline, which is more flexible than fixed-length strings.

```python
import json

HEADER_TERMINATOR = b'\n'

def prepare_packet(mime_type, data):
    """Wraps data in a JSON header."""
    header = {
        "mime_type": mime_type,
        "size": len(data)
    }
    # Encode header + newline + binary data
    header_bytes = json.dumps(header).encode('utf-8') + HEADER_TERMINATOR
    return header_bytes + data

def read_exactly(sock, n):
    """Helper to ensure we read exactly n bytes from a socket."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
```

### B. The Server (`server/main.py`)
The server listens, parses the JSON header to find the MIME type, and saves the file accordingly.

```python
import socket
import os
from shared.protocol import HEADER_TERMINATOR, read_exactly

def start_server(host='127.0.0.1', port=65432):
    if not os.path.exists('storage'):
        os.makedirs('storage')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            # Buffered reader to find the newline terminator
            reader = conn.makefile('rb')

            while True:
                header_line = reader.readline()
                if not header_line:
                    break

                header = json.loads(header_line.decode('utf-8'))
                print(f"Receiving: {header['mime_type']} ({header['size']} bytes)")

                # Use helper to read the exact payload size
                payload = read_exactly(conn, header['size'])

                # Save based on MIME (Simplified extension mapping)
                ext = header['mime_type'].split('/')[-1]
                filename = f"storage/received_{os.urandom(2).hex()}.{ext}"
                with open(filename, 'wb') as f:
                    f.write(payload)
                print(f"Saved to {filename}")

if __name__ == "__main__":
    start_server()
```

### C. The Client (`client/main.py`)
The client iterates through files, determines their MIME type, and packs them.

```python
import socket
import mimetypes
from shared.protocol import prepare_packet

def send_files(file_list, host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        for file_path in file_list:
            # Guess MIME type (e.g., 'image/jpeg')
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or 'application/octet-stream'

            with open(file_path, 'rb') as f:
                data = f.read()

            packet = prepare_packet(mime_type, data)
            s.sendall(packet)
            print(f"Sent {file_path} as {mime_type}")

if __name__ == "__main__":
    # Example: List your actual files here
    files = ['assets/sample.png', 'assets/notes.txt']
    send_files(files)
```

## 3. Walkthrough of the Process

1. **Handshake**: The client establishes a TCP connection.
2. **Header Transmission**: The client sends a JSON string (metadata) ending with `\n`.
3. **Data Transmission**: Immediately after the newline, the raw binary data is sent.
4. **Persistence**: The server uses the MIME type to decide the file extension and writes the buffer to the disk.

## 4. Why This Approach? (Design Decisions)

- **JSON vs Fixed Length**: JSON headers allow you to add more metadata later (like filename, timestamp, or encoding) without breaking the protocol structure.
- **Newline Terminator**: Using `\n` to separate metadata from payload is a standard pattern (similar to HTTP's `\r\n\r\n`), making the "boundary" easy to find for the receiver.
- **read_exactly Helper**: This is the most critical part of socket programming. It prevents "Short Reads" where large files are cut off due to network congestion.

