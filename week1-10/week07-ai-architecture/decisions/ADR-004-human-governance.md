# ADR-004: Human-in-the-Loop Design

## Context
AI ตัดสินใจได้ แต่ human ต้องเข้ามาแทรกได้เสมอ
ต้องออกแบบว่า human เข้ามา "ตรงไหน" และ "ยังไง"

## Escalation Triggers (เมื่อไหร่ส่งให้ human)
| เงื่อนไข | Action |
|---------|--------|
| Risk score 0.3 - 0.95 (gray zone) | Queue ให้ human review |
| Model confidence < 60% | Human decides |
| Budget เกิน | Human decides |
| Model drift detected | Freeze AI, human reviews |
| Human request override | Human always wins |

## Human Override Design
```python
# Human สามารถ override ได้เสมอ
# และ override จะถูก log เป็น training data

POST /admin/decisions/{case_id}/override
{
  "decision": "approve",  # หรือ "reject"
  "reason": "false positive - legitimate business file",
  "reviewer_id": "admin-007"
}
```

## Governance Rules
1. Human override = final (AI ทำซ้ำไม่ได้)
2. Override ทุกครั้งต้องมี reason
3. Override log ส่งไป training pipeline (improve model)
4. ถ้า override > 10% of decisions → review autonomy level

## Kill Switch
ถ้า AI ทำงานผิดปกติ:
```
POST /admin/ai/disable
→ ระบบกลับไปใช้ rule-based ทันที
→ ไม่ต้อง deploy ใหม่
→ Human review ทุก case แทน
```