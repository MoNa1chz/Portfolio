import socket
import threading
import time
import os
import json
import mimetypes
from shared.protocol import prepare_packet, read_exactly

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433  # Different port to avoid conflict

def server_thread_func():
    """Run the server in a thread."""
    import socket as sock
    import os
    import json
    
    if not os.path.exists('storage'):
        os.makedirs('storage')
    
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as s:
        s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen()
        print(f"[Server] Listening on {SERVER_HOST}:{SERVER_PORT}")
        
        conn, addr = s.accept()
        with conn:
            print(f"[Server] Connected by {addr}")
            reader = conn.makefile('rb')
            
            while True:
                header_line = reader.readline()
                if not header_line:
                    break
                
                header = json.loads(header_line.decode('utf-8'))
                print(f"[Server] Receiving: {header['mime_type']} ({header['size']} bytes)")
                
                # Read exactly using reader
                data = b''
                n = header['size']
                while len(data) < n:
                    chunk = reader.read(n - len(data))
                    if not chunk:
                        print("[Server] Error: Connection closed before receiving full payload")
                        break
                    data += chunk
                if len(data) != n:
                    break
                
                ext = header['mime_type'].split('/')[-1]
                filename = f"storage/received_{os.urandom(2).hex()}.{ext}"
                with open(filename, 'wb') as f:
                    f.write(data)
                print(f"[Server] Saved to {filename}")
        print("[Server] Server thread exiting")

def client_send_files(file_list):
    """Send files using the client logic."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        
        for file_path in file_list:
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or 'application/octet-stream'
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            packet = prepare_packet(mime_type, data)
            s.sendall(packet)
            print(f"[Client] Sent {file_path} as {mime_type}")

def cleanup():
    if os.path.exists('storage'):
        for f in os.listdir('storage'):
            os.remove(os.path.join('storage', f))

def main():
    cleanup()
    
    # Start server thread
    server_thread = threading.Thread(target=server_thread_func, daemon=True)
    server_thread.start()
    
    # Give server time to bind
    time.sleep(1)
    
    # Prepare sample files
    sample_files = []
    if os.path.exists('assets/notes.txt'):
        sample_files.append('assets/notes.txt')
    if os.path.exists('assets/sample.png'):
        sample_files.append('assets/sample.png')
    
    if not sample_files:
        print("No sample files found in assets/")
        return
    
    print(f"[Test] Sending files: {sample_files}")
    client_send_files(sample_files)
    
    # Allow server to finish processing
    time.sleep(1)
    
    # Verify storage
    if os.path.exists('storage'):
        files = os.listdir('storage')
        print(f"[Test] Files in storage: {files}")
        for f in files:
            print(f"  - {f}")
        if len(files) == len(sample_files):
            print("[Test] SUCCESS: All files received.")
        else:
            print(f"[Test] FAILURE: Expected {len(sample_files)} files, got {len(files)}")
    else:
        print("[Test] FAILURE: Storage directory not created.")
    
    # Cleanup
    cleanup()

if __name__ == '__main__':
    main()