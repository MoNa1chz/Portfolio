# ADR-002: Coordination Pattern

## Options

### Option A: Sequential Pipeline
Security → Privacy → Compliance → Efficiency
- Pro: เห็นผลก่อนหน้า, ง่าย debug
- Con: ถ้า agent นึง down = ทุกอย่างหยุด

### Option B: Parallel + Vote (เลือกแบบนี้)
Security ─┐
Privacy  ─┤→ [Vote Merger] → Final Decision
Compliance┤
Efficiency┘
- Pro: ไม่มี single point of failure
- Con: ต้องออกแบบ merge logic

### Option C: Centralized Authority
- Con: Security agent กลาย bottleneck

## Decision: Option B (Parallel + Vote)

## Merge Logic
1. ถ้าทุก agent เห็นตรงกัน → ทำตามนั้น
2. ถ้า agent ใดมี confidence > 95% → ทำตาม agent นั้น
3. ถ้าขัดแย้งและไม่มีใครมั่นใจมาก → escalate human

## Priority (เมื่อขัดแย้ง)
Security > Privacy > Compliance > Efficiency
เพราะ security failure มีผลร้ายแรงที่สุด