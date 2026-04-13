# ADR-004: Collective Governance

## Global Anchors (ละเมิดไม่ได้เลย)

| Anchor | Rule | ถ้าละเมิด |
|--------|------|----------|
| Throughput | accept/flag ≥ 95% | หยุดระบบ + human |
| Fairness | ไม่มี user ถูก reject > 3× average | escalate fairness team |
| Cost | avg cost per file < $0.10 | escalate infra team |
| Auditability | ทุก decision ต้อง log | หยุดระบบ |

## Shared Rejection Budget
| Agent | Budget |
|-------|--------|
| Security | 3% |
| Privacy | 1% |
| Compliance | 1% |
| รวมสูงสุด | 5% |

## Human Intervention Points
- acceptance rate < 90% → product team
- user rejection rate > 3× avg → fairness team  
- cost > $0.12/file → infra team
- agents ขัดแย้งและ confidence < 0.8 → on-call engineer

## Kill Switch
POST /admin/agents/disable-all
→ fallback to rule-based ทั้งหมด
→ human review ทุก case