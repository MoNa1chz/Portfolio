import grpc
import asyncio
import uuid
from back_end_bus.protobuf.generated import upload_pb2, upload_pb2_grpc
from back_end_bus.event_bus import bus, handlers # import handlers เพื่อ register

class UploadServicer(upload_pb2_grpc.UploadServiceServicer):
    async def UploadStream(self, request_iterator, context):
        file_id = str(uuid.uuid4())
        total_bytes = 0
        expected_seq = 1

        async for chunk in request_iterator:
            if chunk.sequence != expected_seq:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Out of order")
            total_bytes += len(chunk.data)
            expected_seq += 1
            print(f"[UploadService] รับ chunk #{chunk.sequence} ({len(chunk.data)} bytes)")

        print(f"[UploadService] ✅ ครบ {total_bytes} bytes → file_id={file_id}")
        await bus.publish("file.uploaded", {"file_id": file_id})
        return upload_pb2.UploadAck(
            file_id=file_id,
            bytes_received=total_bytes
        )

async def serve():
    server = grpc.aio.server()
    upload_pb2_grpc.add_UploadServiceServicer_to_server(UploadServicer(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("[UploadService] 🟢 รอรับ gRPC ที่ port 50051")
    
    # รัน event bus ไปพร้อมกัน
    await asyncio.gather(
        server.wait_for_termination(),
        bus.run()
    )

if __name__ == "__main__":
    asyncio.run(serve())