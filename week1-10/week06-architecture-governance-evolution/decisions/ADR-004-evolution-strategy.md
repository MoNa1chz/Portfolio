# ADR-004: Safe Evolution Strategy (Zero Downtime)

## Context
ต้องเพิ่ม AI service ใน Week 07
ห้าม downtime, ห้าม break clients

## Pattern: Strangler Fig

### Timeline
Week 1: Build v2 beside v1
Week 2: Route 10% traffic to v2 (canary)
Week 3: Route 50% traffic (if no errors)
Week 4: Route 100%, shutdown v1

### Implementation ด้วย Feature Flag
```python
@app.post("/files")
async def upload_file(file: UploadFile):
    user_id = get_user_id()
    
    if feature_flag("ai_enabled", user_id, percent=10):
        # 10% ของ users ใช้ v2 (มี AI)
        result = await upload_v2_with_ai(file)
    else:
        # 90% ยังใช้ v1 (ไม่มี AI)
        result = await upload_v1(file)
    
    return result
```

## Kill Switch
ถ้า v2 มีปัญหา:
1. เปลี่ยน percent=10 → percent=0
2. ไม่ต้อง deploy ใหม่
3. v1 รับ traffic ทั้งหมดทันที

## Trade-offs
| มิติ | ผลกระทบ |
|------|----------|
| Complexity | ต้องรัน 2 versions พร้อมกัน |
| Cost | Infrastructure เพิ่ม 2× ชั่วคราว |
| Safety | Rollback ทำได้ทันที ไม่มี downtime |
```

---

## ขั้นตอนที่ 6 — วาด Architecture Diagram

สร้างไฟล์ `diagrams/architecture-v1.mmd` (Mermaid format):
```
graph TD
    Client["🖥️ Client\n(public internet)"]
    
    subgraph Edge["EDGE BUS (Public Zone)"]
        Auth["Auth Middleware\nJWT Verify"]
        Policy["Policy Check\nOPA"]
        Audit["Audit Log\n(immutable)"]
        GW["FastAPI Gateway\n:8000"]
    end
    
    subgraph Backend["BACK-END BUS (Private Zone)"]
        Upload["Upload Service\n:50051 gRPC"]
        EventBus["Event Bus\nasync"]
        Process["Processing Service"]
        Meta["Metadata Service"]
    end
    
    Client -->|HTTPS| GW
    GW --> Auth
    Auth --> Policy
    Policy --> Audit
    Audit -->|gRPC stream| Upload
    Upload -->|publish| EventBus
    EventBus -->|file.uploaded| Process
    EventBus -->|file.uploaded| Meta
    