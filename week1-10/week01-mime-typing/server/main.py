import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import socket
import json
from shared.protocol import HEADER_TERMINATOR


def read_exactly_from_reader(reader, n):
    """Helper to ensure we read exactly n bytes from a buffered reader."""
    data = b''
    while len(data) < n:
        chunk = reader.read(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


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

                # Read the exact payload size from the same reader
                payload = read_exactly_from_reader(reader, header['size'])
                if payload is None:
                    print("Error: Connection closed before receiving full payload")
                    break

                # Save based on MIME (Simplified extension mapping)
                ext = header['mime_type'].split('/')[-1]
                filename = f"storage/received_{os.urandom(2).hex()}.{ext}"
                with open(filename, 'wb') as f:
                    f.write(payload)
                print(f"Saved to {filename}")


if __name__ == "__main__":
    start_server()