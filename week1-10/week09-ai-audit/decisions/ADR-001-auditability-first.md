# ADR-001: Auditability as Architecture (Not Afterthought)

## Context
ระบบ content moderation จาก Week 08 ทำงานดี
แต่ถ้าถูกถามว่า "ทำไมถึง reject ไฟล์นี้?" — ตอบไม่ได้

## Problem
ถ้าไม่ออกแบบ audit ตั้งแต่แรก:
- Log หายไปแล้ว → ตอบ regulator ไม่ได้
- ไม่รู้ว่า model version ไหนตัดสิน → replay ไม่ได้
- ไม่มีหลักฐาน → แพ้คดีได้

## Decision: Audit-First Design

### กฎ 3 ข้อที่ห้ามละเมิด
1. ทุก decision ต้องมี decision_id ที่ unique
2. ทุก decision ต้อง log ก่อน execute เสมอ
3. Audit log ต้องเป็น append-only (แก้ไขไม่ได้)

## Trade-offs
| มิติ | ผลกระทบ |
|------|----------|
| Performance | log async → ไม่กระทบ latency |
| Storage | เพิ่มขึ้น ~10% → คุ้มค่า |
| Complexity | ต้องออกแบบ schema ดีๆ → ลงทุนครั้งเดียว |

## Regulatory Basis
- PDPA (ไทย): สิทธิรับรู้การตัดสินใจ
- GDPR (EU): Right to Explanation
- ถ้าไม่มี audit → โดนปรับได้