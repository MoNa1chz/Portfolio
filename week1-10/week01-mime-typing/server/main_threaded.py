"""
Threaded MIME socket server supporting concurrent client connections.
"""
import socket
import os
import json
import signal
import sys
import argparse
import logging
import threading
from shared.protocol import HEADER_TERMINATOR

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def read_exactly_from_reader(reader, n):
    """Helper to ensure we read exactly n bytes from a buffered reader."""
    data = b''
    while len(data) < n:
        chunk = reader.read(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def handle_client_connection(conn, addr, storage_dir='storage'):
    """Handle a single client connection, processing multiple files."""
    logger.info(f"Thread {threading.current_thread().name} handling connection from {addr}")
    try:
        reader = conn.makefile('rb')
        while True:
            header_line = reader.readline()
            if not header_line:
                logger.info(f"Client {addr} closed connection")
                break
            
            try:
                header = json.loads(header_line.decode('utf-8'))
                mime_type = header.get('mime_type', 'application/octet-stream')
                size = header.get('size', 0)
                logger.info(f"Receiving {mime_type} ({size} bytes) from {addr}")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Invalid header from {addr}: {e}")
                conn.sendall(b'ERROR: Invalid header\n')
                break
            
            payload = read_exactly_from_reader(reader, size)
            if payload is None:
                logger.error(f"Connection closed before receiving full payload from {addr}")
                break
            
            # Determine file extension
            ext = mime_type.split('/')[-1]
            import random
            filename = os.path.join(storage_dir, f"received_{random.randbytes(2).hex()}.{ext}")
            try:
                with open(filename, 'wb') as f:
                    f.write(payload)
                logger.info(f"Saved to {filename}")
                # Optional: send acknowledgment
                conn.sendall(b'OK\n')
            except OSError as e:
                logger.error(f"Failed to write file {filename}: {e}")
                conn.sendall(b'ERROR: File write failed\n')
                break
    except ConnectionError as e:
        logger.warning(f"Connection error with {addr}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error handling {addr}: {e}")
    finally:
        conn.close()
        logger.info(f"Connection with {addr} closed")

def start_server(host='127.0.0.1', port=65432, storage_dir='storage'):
    """Start the server with configurable host, port, and storage directory."""
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
        logger.info(f"Created storage directory: {storage_dir}")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen()
        logger.info(f"Threaded server listening on {host}:{port}")
    except OSError as e:
        logger.error(f"Failed to bind {host}:{port}: {e}")
        sys.exit(1)
    
    # Graceful shutdown handling
    shutdown = False
    def signal_handler(sig, frame):
        nonlocal shutdown
        logger.info("Shutdown signal received, stopping server...")
        shutdown = True
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    active_threads = []
    
    try:
        while not shutdown:
            try:
                server_socket.settimeout(1.0)  # allow checking shutdown flag
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue
            except OSError as e:
                if shutdown:
                    break
                logger.error(f"Accept error: {e}")
                continue
            
            # Create a new thread for this client
            client_thread = threading.Thread(
                target=handle_client_connection,
                args=(conn, addr, storage_dir),
                name=f"Client-{addr[0]}:{addr[1]}",
                daemon=True
            )
            client_thread.start()
            active_threads.append(client_thread)
            logger.debug(f"Started thread {client_thread.name}")
            
            # Clean up finished threads
            active_threads = [t for t in active_threads if t.is_alive()]
    finally:
        logger.info("Shutting down server socket, waiting for client threads...")
        server_socket.close()
        # Optionally wait for threads to finish (with timeout)
        for t in active_threads:
            if t.is_alive():
                t.join(timeout=5.0)
        logger.info("Server stopped")

def main():
    parser = argparse.ArgumentParser(description='Threaded MIME socket file transfer server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=65432, help='Port to listen (default: 65432)')
    parser.add_argument('--storage', default='storage', help='Storage directory (default: storage)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Starting threaded server with host={args.host}, port={args.port}, storage={args.storage}")
    start_server(args.host, args.port, args.storage)

if __name__ == "__main__":
    main()