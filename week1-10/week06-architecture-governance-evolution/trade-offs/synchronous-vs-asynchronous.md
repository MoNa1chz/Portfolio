# Trade-off: Synchronous RPC vs Async Events

## เปรียบเทียบ

| มิติ | Sync (gRPC) | Async (Events) |
|------|-------------|----------------|
| Latency | ต่ำ (รู้ผลทันที) | สูง (รู้ผลทีหลัง) |
| Reliability | ถ้า service down = fail | ถ้า service down = retry ทีหลัง |
| Complexity | ง่าย | ซับซ้อน (ต้องมี event bus) |
| Scalability | Scale ยาก (tight coupling) | Scale ง่าย (loose coupling) |
| Debugging | ง่าย (stack trace ชัด) | ยาก (ต้องติดตาม trace_id) |

## กฎการเลือก

ใช้ **Sync** เมื่อ:
- ต้องการผลทันที (เช่น auth, validation)
- Operation เร็ว (< 100ms)
- Client ต้องรอผลก่อนทำต่อ

ใช้ **Async** เมื่อ:
- งานหนัก (เช่น AI, video processing)
- Client ไม่ต้องรอผล
- ต้องการ fault tolerance สูง
