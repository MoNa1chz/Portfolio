#!/usr/bin/env python3
"""
Final integration test for enhanced MIME socket project.
Tests both enhanced server and client with command-line arguments.
"""
import subprocess
import time
import os
import sys
import threading
import socket
import json

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65500  # Unique port for this test
STORAGE_DIR = 'test_storage'

def cleanup():
    """Remove test storage directory."""
    import shutil
    if os.path.exists(STORAGE_DIR):
        shutil.rmtree(STORAGE_DIR)

def start_enhanced_server():
    """Start enhanced server as a subprocess."""
    cmd = [
        sys.executable,
        'server/main_enhanced.py',
        '--host', SERVER_HOST,
        '--port', str(SERVER_PORT),
        '--storage', STORAGE_DIR,
        '--verbose'
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return proc

def send_files_with_enhanced_client(file_list):
    """Use enhanced client to send files."""
    cmd = [
        sys.executable,
        'client/main_enhanced.py',
        '--host', SERVER_HOST,
        '--port', str(SERVER_PORT),
        '--timeout', '5',
        '--verbose'
    ] + file_list
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def wait_for_server(host, port, max_attempts=30):
    """Wait until server is accepting connections."""
    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                return True
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.1)
    return False

def main():
    print("=== Final Integration Test ===")
    cleanup()
    
    # Ensure sample files exist
    sample_files = ['assets/notes.txt', 'assets/sample.png']
    missing = [f for f in sample_files if not os.path.exists(f)]
    if missing:
        print(f"Missing sample files: {missing}")
        print("Creating dummy files...")
        os.makedirs('assets', exist_ok=True)
        with open('assets/notes.txt', 'w') as f:
            f.write("Test content for final validation.\n")
        with open('assets/sample.png', 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n' + b'x' * 100)
    
    print("Starting enhanced server...")
    server_proc = start_enhanced_server()
    try:
        # Wait for server to be ready
        if not wait_for_server(SERVER_HOST, SERVER_PORT):
            print("ERROR: Server failed to start")
            server_proc.terminate()
            server_proc.wait(timeout=5)
            sys.exit(1)
        
        print(f"Server ready on {SERVER_HOST}:{SERVER_PORT}")
        time.sleep(0.5)
        
        print("Sending files via enhanced client...")
        retcode, stdout, stderr = send_files_with_enhanced_client(sample_files)
        
        print(f"Client exit code: {retcode}")
        if stdout:
            print("Client stdout:", stdout[:500])
        if stderr:
            print("Client stderr:", stderr[:500])
        
        if retcode != 0:
            print("ERROR: Client failed")
            server_proc.terminate()
            server_proc.wait(timeout=5)
            sys.exit(1)
        
        # Give server time to process
        time.sleep(1)
        
        # Check storage
        if os.path.exists(STORAGE_DIR):
            files = os.listdir(STORAGE_DIR)
            print(f"Files in storage: {files}")
            if len(files) == len(sample_files):
                print("SUCCESS: All files received.")
                # Verify file contents
                for f in files:
                    path = os.path.join(STORAGE_DIR, f)
                    size = os.path.getsize(path)
                    print(f"  - {f}: {size} bytes")
            else:
                print(f"FAILURE: Expected {len(sample_files)} files, got {len(files)}")
                sys.exit(1)
        else:
            print("FAILURE: Storage directory not created")
            sys.exit(1)
        
        print("Test passed.")
    finally:
        print("Terminating server...")
        server_proc.terminate()
        server_proc.wait(timeout=5)
        cleanup()

if __name__ == '__main__':
    main()