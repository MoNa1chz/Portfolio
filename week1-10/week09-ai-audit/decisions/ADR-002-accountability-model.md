# ADR-002: Accountability Chain

## Context
เมื่อเกิดปัญหา ต้องรู้ว่าใครรับผิดชอบส่วนไหน

## Accountability Chain
Data Owner
→ รับผิดชอบ: ข้อมูล training, consent, qualityData Scientist
→ รับผิดชอบ: model design, validation, bias testingModel v2.1
→ รับผิดชอบ: prediction + confidence scorePolicy v3.2 (Product Team)
→ รับผิดชอบ: เมื่อไหร่เชื่อ model, เมื่อไหร่ escalateAI Agent
→ รับผิดชอบ: ทำตาม policy, log ทุกอย่างHuman Reviewer (เมื่อ escalate)
→ รับผิดชอบ: final decision + เหตุผลSystem
→ รับผิดชอบ: execute + log ผล

## Rule: ไม่มีใคร "just following orders"
แต่ละ actor ต้อง document การตัดสินใจของตัวเอง

## Accountability Matrix
| ถามว่า | ตอบได้จาก |
|--------|-----------|
| ข้อมูล training มาจากไหน? | Data Owner log |
| Model ตัดสินใจยังไง? | Model audit + explainability |
| Policy อนุญาตอะไร? | Policy snapshot |
| Human ตัดสินอะไร? | Escalation log |
| ระบบ execute อะไร? | System event log |