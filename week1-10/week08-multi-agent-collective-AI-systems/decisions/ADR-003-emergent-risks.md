# ADR-003: Emergent Failure Risks

## Failure 1: Feedback Loop (Scale Oscillation)
**เกิดยังไง**:
Efficiency scales down → Security ต้องการ compute มากขึ้น
→ System ช้า → Efficiency scales up → วนซ้ำ

**Detection**: ถ้า std deviation ของ instance count สูง
**Prevention**: Scale เมื่อ signal stable > 5 นาที

---

## Failure 2: Reject Collusion
**เกิดยังไง**:
Privacy เรียน "reject ทุกอย่างที่มี text → ปลอดภัยที่สุด"
Security เรียน "reject ทุกอย่าง → ไม่มี malware"
→ ไฟล์ไม่ผ่านเลย

**Detection**: acceptance rate ต่ำกว่า 90%
**Prevention**: มี throughput budget — ต้อง accept ≥ 95%

---

## Failure 3: Mode Collapse
**เกิดยังไง**:
Compliance agent trained กับ music/movie data
→ เรียนแค่ "copyright violation" ไม่มีทาง accept

**Detection**: decision distribution — ถ้า 95%+ เป็น reject
**Prevention**: human audit monthly + retrain trigger

---

## Monitoring Checklist
| Metric | Warning Level | Action |
|--------|--------------|--------|
| Acceptance rate | < 90% | Escalate product team |
| Instance variance | σ > 3 | Check feedback loop |
| Agent reject rate | > budget | Freeze that agent |
| Decision distribution | 95% same | Human audit |