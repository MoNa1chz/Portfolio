# ADR-004: Regulatory Requirements → Architecture

## Domain: Content Moderation

## Regulation 1: Right to Explanation
**กฎหมายบอกว่า**: ผู้ใช้มีสิทธิรู้ว่าทำไมถึงถูกปฏิเสธ

**Architecture**:
- ทุก decision มี decision_id
- GET /decisions/{id}/explanation endpoint
- Response: plain English ไม่ใช่ technical jargon

---

## Regulation 2: Data Minimization
**กฎหมายบอกว่า**: เก็บข้อมูลเท่าที่จำเป็นเท่านั้น

**Architecture**:
- Agent เห็นแค่ fields ที่ตัดสินใจจำเป็น
- user_id → hash ก่อน log (ไม่เก็บ raw)
- file content → เก็บแค่ hash ไม่เก็บ content จริง

---

## Regulation 3: Human Oversight
**กฎหมายบอกว่า**: บาง decision ต้องมี human review

**Architecture**:
- DECISION_LEVELS map ต่อ decision type
- Level 0 = human เสมอ (เช่น user ban)
- Log ว่า human involved หรือเปล่า

---

## Regulation 4: Non-Discrimination
**กฎหมายบอกว่า**: ห้ามตัดสินใจโดยใช้ protected characteristics

**Architecture**:
- Agent ไม่เห็น user_id, location, demographics
- Monitor rejection rate แยกตาม group
- Alert ถ้า disparity > 2×

---

## Regulation 5: Audit Trail
**กฎหมายบอกว่า**: ต้องเก็บหลักฐานการตัดสินใจ

**Architecture**:
- Append-only log
- Cryptographic hash chain
- Retention ≥ 3 ปี
- Backup offsite
