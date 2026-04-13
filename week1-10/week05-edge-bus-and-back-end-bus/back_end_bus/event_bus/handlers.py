import asyncio
from back_end_bus.event_bus.bus import on

@on("file.uploaded")
async def handle_file_uploaded(data):
    print(f"[ProcessingService] 🔄 กำลัง process ไฟล์ {data['file_id']}")
    await asyncio.sleep(2)
    print(f"[ProcessingService] ✅ เสร็จแล้ว: {data['file_id']}")