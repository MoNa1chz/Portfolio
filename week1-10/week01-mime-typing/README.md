# MIME-Based Socket File Transfer

A professional client/server model for MIME-based data transmission with JSON headers and reliable socket communication.

## Project Overview

This project implements a TCP-based file transfer system where the client sends files with MIME type metadata, and the server receives and stores them with appropriate file extensions. The design follows a clean separation of concerns with a shared protocol module, making it easy to extend and maintain.

### Key Features

- **JSON Header Protocol**: Each file transmission is preceded by a JSON header containing MIME type and size, terminated by a newline.
- **Reliable Data Transfer**: Helper functions ensure exact byte reads/writes over sockets, preventing short reads.
- **Multiple File Support**: Single connection can transmit multiple files sequentially.
- **Enhanced Server**:
  - Configurable host, port, and storage directory
  - Graceful shutdown with signal handling (SIGINT, SIGTERM)
  - Error handling and logging
  - Optional acknowledgment messages
- **Enhanced Client**:
  - Command-line argument support for files, host, port
  - Detailed logging and error reporting
  - Timeout configuration
- **Concurrent Connections** (optional): Threaded server version supports multiple simultaneous clients.
- **Testing**: Integration and unit tests verify functionality.

## Directory Structure

```
week01-mime-typing/
├── assets/                     # Sample files to send
│   ├── notes.txt
│   └── sample.png
├── client/                     # Client implementations
│   ├── main.py                # Basic client (proof-of-concept)
│   └── main_enhanced.py       # Enhanced client with CLI args
├── server/                     # Server implementations
│   ├── main.py                # Basic server (single connection)
│   ├── main_enhanced.py       # Enhanced server with error handling
│   └── main_threaded.py       # Threaded server for concurrent clients
├── shared/                     # Shared protocol library
│   ├── __init__.py
│   └── protocol.py            # prepare_packet, read_exactly
├── storage/                    # Server saves received files here
├── tests/                      # Test suite (optional)
├── test_basic.py              # Basic process test
├── test_integration.py        # Integration test with threading
├── Dockerfile.server          # Docker container for server
├── README.md                  # This file
└── source.md                  # Original specification
```

## Quick Start (Proof of Concept)

1. **Start the server** (basic version):
   ```bash
   cd server
   python main.py
   ```
   Server listens on `127.0.0.1:65432`.

2. **Send files** (basic client):
   ```bash
   cd client
   python main.py
   ```
   The client sends `assets/notes.txt` and `assets/sample.png`.

3. **Check results**:
   Received files appear in `storage/` with names like `received_xxxx.ext`.

## Enhanced Usage

### Enhanced Server

```bash
cd server
python main_enhanced.py --host 0.0.0.0 --port 8888 --storage ../received_files --verbose
```

Options:
- `--host`: Bind address (default: 127.0.0.1)
- `--port`: Port to listen (default: 65432)
- `--storage`: Directory to save files (default: storage)
- `--verbose`: Enable debug logging

### Enhanced Client

```bash
cd client
python main_enhanced.py ../assets/notes.txt ../assets/sample.png --host 127.0.0.1 --port 8888 --timeout 30 --verbose
```

Options:
- Positional arguments: list of files to send
- `--host`: Server address (default: 127.0.0.1)
- `--port`: Server port (default: 65432)
- `--timeout`: Socket timeout in seconds (default: 10)
- `--verbose`: Enable debug logging
### Threaded Server (Concurrent Clients)

```bash
cd server
python main_threaded.py --port 9999
```
This version spawns a new thread for each client connection, allowing multiple simultaneous transfers.

### Docker Container

A Dockerfile is provided to run the enhanced server in a container.

**Build the image:**
```bash
docker build -f Dockerfile.server -t mime-server:latest .
```

**Run the container:**
```bash
docker run -d --name mime-server -p 65432:65432 -v /path/to/storage:/storage mime-server:latest
```

The container runs the enhanced server (`server/main_enhanced.py`) bound to `0.0.0.0:65432` and stores received files in `/storage` (mounted volume). Use `docker logs mime-server` to view logs.


## Protocol Specification

Each transmitted file is represented as:

```
[UTF-8 JSON header] + '\n' + [binary data]
```

The JSON header format:
```json
{
  "mime_type": "text/plain",
  "size": 1234
}
```

The server reads until newline to get the header, parses it, then reads exactly `size` bytes of payload.

## Design Decisions

- **JSON Headers**: Flexible for adding metadata (filename, timestamp, checksum) without breaking protocol.
- **Newline Terminator**: Simple delimiter that works with `readline()` and is human-readable.
- **Helper Functions**: `read_exactly` ensures reliable data transmission over TCP streams.
- **Separation of Concerns**: Shared protocol module used by both client and server ensures consistency.
- **Error Handling**: Enhanced versions include comprehensive error checking and logging.
- **Graceful Shutdown**: Server responds to signals and cleans up resources.

## Testing

Run the integration test to verify the basic functionality:

```bash
python test_integration.py
```

This starts a server thread, sends sample files, and validates that they are saved correctly.

## Development Phases

### Phase 1: Minimal Proof of Concept
- Analyzed requirements from `source.md`
- Created directory structure (`shared/`, `server/`, `client/`, `assets/`, `storage/`)
- Implemented `shared/protocol.py` with `prepare_packet` and `read_exactly`
- Implemented basic server (`server/main.py`) with single connection loop
- Implemented basic client (`client/main.py`) with hardcoded file list
- Created sample files in `assets/`
- Tested basic functionality with `test_integration.py`

### Phase 2: Enhancements
- Enhanced server with error handling, graceful shutdown, configurable parameters (`server/main_enhanced.py`)
- Enhanced client with command-line arguments, logging, timeout (`client/main_enhanced.py`)
- Added logging and debugging output
- Implemented multiple file transfers in a single connection (already supported)
- Added support for concurrent connections with threaded server (`server/main_threaded.py`)
- Created comprehensive README documentation

## Dependencies

- Python 3.6+
- No external packages required (uses only standard library)

## Future Improvements

- Add file checksums to detect corruption
- Support for compression (gzip)
- Authentication and encryption (TLS)
- REST API for server management
- Graphical user interface
- Performance benchmarking
- Docker containerization

## License

Educational project - free to use and modify.