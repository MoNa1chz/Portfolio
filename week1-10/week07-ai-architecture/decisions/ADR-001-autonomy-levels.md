# ADR-001: Autonomy Levels per Decision Type

## Context
ระบบ upload ไฟล์ตอนนี้มี AI ช่วยตัดสินใจ
ต้องกำหนดว่าแต่ละการตัดสินใจ AI มีอิสระแค่ไหน

## The Four Levels
| Level | ชื่อ | AI ทำอะไร | Human ทำอะไร |
|-------|------|-----------|--------------|
| 0 | Assist | แนะนำ | ตัดสินใจเอง |
| 1 | Govern | ทำได้ถ้ามั่นใจ > 95% | ดู escalation |
| 2 | Adapt | ทดลองในขอบเขต budget | ดู budget |
| 3 | Autonomous | ตัดสินใจเอง | review หลังเกิดเหตุ |

## Decision: Autonomy per Feature

| Feature | Level | เหตุผล |
|---------|-------|--------|
| Malware scan | 1 (Govern) | Auto-reject ได้ถ้า confidence > 95% |
| Privacy check | 0 (Assist) | มีผลกฎหมาย ต้องให้ human ตัดสิน |
| Spam filter | 2 (Adapt) | ผิดพลาดได้บ้าง ไม่ critical |
| Compression | 3 (Autonomous) | ไม่มีความเสี่ยง AI ตัดสินเองได้ |

## Reasoning
- ยิ่ง consequence ร้ายแรง → Level ยิ่งต่ำ (human มีส่วนมาก)
- ยิ่ง reversible → Level ยิ่งสูง (AI ตัดสินเองได้)

## If Requirements Change
ถ้า accuracy ของ model ดีขึ้นมาก อาจ upgrade level ได้
แต่ต้องผ่าน: accuracy stable > 4 weeks + stakeholder approval
