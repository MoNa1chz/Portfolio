import grpc
from fastapi import FastAPI, UploadFile, HTTPException, Header
from back_end_bus.protobuf.generated import upload_pb2, upload_pb2_grpc

app = FastAPI()

channel = grpc.aio.insecure_channel("localhost:50051")
stub = upload_pb2_grpc.UploadServiceStub(channel)

def verify_token(token: str):
    if token != "secret-token":
        raise HTTPException(401, "Unauthorized")
    return {"user_id": "user-123"}

@app.post("/files")
async def upload_file(
    file: UploadFile,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    print(f"[EdgeBus] 🔐 {user['user_id']} upload {file.filename}")

    CHUNK_SIZE = 64 * 1024  # 64KB

    async def chunk_generator():
        seq = 1
        while True:
            data = await file.read(CHUNK_SIZE)
            if not data:
                break
            yield upload_pb2.UploadChunk(data=data, sequence=seq)
            seq += 1

    response = await stub.UploadStream(chunk_generator())
    print(f"[EdgeBus] ✅ file_id={response.file_id}")

    return {
        "file_id": response.file_id,
        "bytes": response.bytes_received,
        "status": "queued"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}