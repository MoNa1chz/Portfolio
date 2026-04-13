import subprocess
import time
import os
import sys

def cleanup():
    # Clear storage directory
    if os.path.exists('storage'):
        for f in os.listdir('storage'):
            os.remove(os.path.join('storage', f))

def main():
    cleanup()
    
    # Start server as a background process
    server = subprocess.Popen([sys.executable, 'server/main.py'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    print(f"Server started with PID {server.pid}")
    
    # Give server time to bind
    time.sleep(2)
    
    # Run client
    print("Starting client...")
    client = subprocess.run([sys.executable, 'client/main.py'], 
                            capture_output=True, text=True)
    print("Client stdout:", client.stdout)
    if client.stderr:
        print("Client stderr:", client.stderr)
    
    # Give server time to process
    time.sleep(1)
    
    # Terminate server
    server.terminate()
    server.wait(timeout=5)
    print("Server terminated.")
    
    # Check storage for received files
    if os.path.exists('storage'):
        files = os.listdir('storage')
        print(f"Files in storage: {files}")
        for f in files:
            print(f"  - {f}")
    else:
        print("Storage directory not created.")

if __name__ == '__main__':
    main()