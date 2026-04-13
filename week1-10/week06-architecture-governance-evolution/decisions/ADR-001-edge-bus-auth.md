# ADR-001: Centralized Authentication at Edge Bus

## Context
ระบบมีหลาย services (Upload, Metadata, Processing)
แต่ละ service ต้องรู้ว่า request มาจากใคร และมีสิทธิ์ไหม

## Options

### Option A: Each Service Authenticates
- Upload Service ตรวจ JWT เอง
- Metadata Service ตรวจ JWT เอง  
- Processing Service ตรวจ JWT เอง

### Option B: Edge Bus Authenticates Once (เลือกแบบนี้)
- Edge Bus ตรวจ JWT ครั้งเดียว
- Back-End Services เชื่อใจว่า Edge ทำแล้ว

## Decision: Option B

## Reasoning
- ตรวจครั้งเดียว = audit log อยู่ที่เดียว
- เปลี่ยน auth method ครั้งเดียว (แก้ที่ Edge อย่างเดียว)
- Services ข้างในเร็วขึ้น ไม่ต้อง verify ซ้ำ

## Trade-offs Accepted
| มิติ | ผลกระทบ |
|------|----------|
| Reliability | Edge down = ทุกอย่าง down (แก้ด้วย clustering) |
| Flexibility | Services ทำ custom auth เองไม่ได้ (ตั้งใจ) |
| Security | Edge compromise = ทุก service โดน (ยอมรับ) |

## If Requirements Change
ถ้าต้องการ per-service auth ในอนาคต:
1. เพิ่ม local verification ใน services
2. Edge ยังตรวจอยู่ (defense in depth)
3. ค่าใช้จ่าย: CPU เพิ่มขึ้น 2×