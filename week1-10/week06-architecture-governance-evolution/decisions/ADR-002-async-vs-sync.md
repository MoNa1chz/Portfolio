# ADR-002: Async Events vs Synchronous RPC

## Context
หลัง upload ไฟล์เสร็จ ต้องทำ:
- Scan malware
- AI analysis  
- Update metadata

## Options

### Option A: Synchronous (รอทุกอย่างเสร็จก่อน return)
Client รอ → Upload → Scan → AI → Metadata → Response
ใช้เวลา: ~35 วินาที

### Option B: Async Events (return ทันที แล้วทำต่อ background)
Client รอ → Upload → Response ทันที
Background: Scan → AI → Metadata
ใช้เวลา Client รอ: ~100ms

## Decision: Option B (Async)

## Reasoning
- UX ดีกว่ามาก (ไม่รอ 35 วินาที)
- ถ้า AI service crash → upload ยังสำเร็จ
- Scale AI service แยกจาก Upload ได้

## Trade-offs Accepted
| มิติ | ผลกระทบ |
|------|----------|
| Complexity | ต้องมี event bus, trace IDs |
| Consistency | ไฟล์ upload แล้วแต่ยังไม่ process ทันที |
| Debugging | ต้องติดตาม trace_id ข้าม services |

## Rule: เมื่อไหร่ใช้ Sync vs Async
- Sync: ต้องการผลทันที เช่น auth check, metadata lookup
- Async: งานหนัก, ไม่ต้องการผลทันที เช่น AI, processing