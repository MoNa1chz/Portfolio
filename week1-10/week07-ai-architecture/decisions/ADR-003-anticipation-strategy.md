# ADR-003: Anticipative Action Strategy

## Context
ระบบควร "รู้ล่วงหน้า" ก่อนเกิดปัญหา
ไม่ใช่รอให้ crash แล้วค่อยแก้

## Signals ที่ใช้ตรวจจับ
| Signal | บ่งบอกอะไร | Action |
|--------|-----------|--------|
| CPU > 70% และกำลังเพิ่ม | จะ overload ใน 5 นาที | Auto-scale +2 instances |
| Error rate เพิ่ม 3× | Service กำลังมีปัญหา | Alert + human review |
| Upload rate ผิดปกติ | อาจถูก DDoS | Rate limiting |
| Model rejection เพิ่ม 30% | Model drift? | Freeze model + human review |

## Decision Flow (Anticipative)
```
Metrics เข้า Event Bus
    ↓
ML Predictor วิเคราะห์ trend
    ↓
ถ้า predicted_problem > threshold
    ├─ confidence สูง → Act automatically
    └─ confidence ต่ำ → Escalate to human
    ↓
Log ทุก anticipative action (ให้ human review ทีหลัง)
```

## Trade-offs
| มิติ | ผลกระทบ |
|------|----------|
| False alarm | Scale เพิ่มโดยไม่จำเป็น → เสียเงิน |
| Miss → | ไม่ scale ทัน → user เจอ latency |
| Decision: | ยอม false alarm ดีกว่า miss (cost < UX damage) |