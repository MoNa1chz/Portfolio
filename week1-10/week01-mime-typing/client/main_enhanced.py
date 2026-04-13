"""
Enhanced MIME socket client with command-line arguments, error handling, and logging.
"""
import socket
import mimetypes
import argparse
import logging
import sys
import os
from shared.protocol import prepare_packet

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def send_files(file_list, host='127.0.0.1', port=65432, timeout=10):
    """
    Send multiple files over a single socket connection.
    
    Args:
        file_list: list of file paths to send
        host: server hostname/IP
        port: server port
        timeout: socket timeout in seconds
    """
    total_sent = 0
    total_failed = 0
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        logger.info(f"Connected to {host}:{port}")
    except (socket.error, ConnectionRefusedError) as e:
        logger.error(f"Failed to connect to {host}:{port}: {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected connection error: {e}")
        return False
    
    try:
        for file_path in file_list:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                total_failed += 1
                continue
            
            try:
                mime_type, _ = mimetypes.guess_type(file_path)
                mime_type = mime_type or 'application/octet-stream'
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                packet = prepare_packet(mime_type, data)
                sock.sendall(packet)
                total_sent += 1
                logger.info(f"Sent {file_path} ({len(data)} bytes) as {mime_type}")
            except OSError as e:
                logger.error(f"Failed to read {file_path}: {e}")
                total_failed += 1
            except socket.error as e:
                logger.error(f"Network error while sending {file_path}: {e}")
                total_failed += 1
                break
            except Exception as e:
                logger.exception(f"Unexpected error sending {file_path}: {e}")
                total_failed += 1
    finally:
        sock.close()
        logger.info(f"Connection closed. Sent: {total_sent}, Failed: {total_failed}")
    
    return total_failed == 0

def main():
    parser = argparse.ArgumentParser(description='MIME socket file transfer client')
    parser.add_argument('files', nargs='+', help='Files to send')
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=65432, help='Server port (default: 65432)')
    parser.add_argument('--timeout', type=int, default=10, help='Socket timeout in seconds (default: 10)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Starting client with {len(args.files)} files to {args.host}:{args.port}")
    success = send_files(args.files, args.host, args.port, args.timeout)
    
    if success:
        logger.info("All files sent successfully")
        sys.exit(0)
    else:
        logger.error("Some files failed to send")
        sys.exit(1)

if __name__ == "__main__":
    main()