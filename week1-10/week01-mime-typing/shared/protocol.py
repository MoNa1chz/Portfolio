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