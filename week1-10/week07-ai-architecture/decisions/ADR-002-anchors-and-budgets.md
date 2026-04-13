# ADR-002: Anchors & Budgets

## Context
AI ต้องมีขอบเขตที่ชัดเจน — สิ่งที่ทำไม่ได้เลย (Anchors)
และสิ่งที่ทำได้แต่มีขีดจำกัด (Budgets)

## Anchors (ห้ามทำเด็ดขาด)
| Anchor | เหตุผล | วิธี Enforce |
|--------|--------|--------------|
| Model ห้ามเห็น PII | กฎหมาย PDPA/GDPR | Type system (PII class) |
| Model ห้าม override human decision | Trust | Code: human decisions are final |
| Output ทุกอย่างต้อง log | Audit | Immutable append-only log |
| Model ห้าม execute code | Security | Sandbox isolation |

## Budgets (ทำได้แต่มีขีดจำกัด)
| Budget | ขีดจำกัด | เกินแล้วทำอะไร |
|--------|----------|----------------|
| False positive rate | < 2% | Escalate to human |
| Processing time | < 100ms per file | Fallback to rule-based |
| Retry cost | < $0.01 per file | Stop retry, escalate |
| Exploration (strategies) | max 3 tries | Escalate to human |

## Reasoning
- Anchors ป้องกันความผิดพลาดที่ร้ายแรงและย้อนกลับไม่ได้
- Budgets ป้องกัน AI "ลองผิดลองถูก" แบบไม่มีขีดจำกัด