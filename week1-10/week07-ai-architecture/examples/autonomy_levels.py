"""
Decision Router: ส่ง decision ไปยัง level ที่ถูกต้อง
"""
from enum import IntEnum

class Level(IntEnum):
    ASSIST     = 0   # Human ตัดสินเสมอ
    GOVERN     = 1   # AI ตัดสินถ้ามั่นใจ > 95%
    ADAPT      = 2   # AI ตัดสินในขอบเขต budget
    AUTONOMOUS = 3   # AI ตัดสินเอง human review ทีหลัง

# กำหนด level ต่อ feature
DECISION_LEVELS = {
    "malware_scan":   Level.GOVERN,
    "privacy_check":  Level.ASSIST,
    "spam_filter":    Level.ADAPT,
    "compression":    Level.AUTONOMOUS,
}

async def route_decision(feature: str, risk_score: float, confidence: float):
    level = DECISION_LEVELS.get(feature, Level.ASSIST)
    
    print(f"\n[Decision] feature={feature} score={risk_score:.2f} confidence={confidence:.2f} level={level.name}")
    
    if level == Level.ASSIST:
        # Human ตัดสินเสมอ
        return {
            "status": "pending_human",
            "ai_score": risk_score,
            "message": "Awaiting human decision"
        }
    
    elif level == Level.GOVERN:
        if risk_score > 0.95:
            return {"status": "auto_rejected", "reason": "high_risk"}
        elif risk_score < 0.3:
            return {"status": "auto_accepted", "reason": "low_risk"}
        else:
            return {
                "status": "pending_human",
                "ai_score": risk_score,
                "message": "Gray zone — human required"
            }
    
    elif level == Level.ADAPT:
        # AI ตัดสินได้แต่ต้องอยู่ใน error budget
        error_budget = Budget("false_positive", limit=0.02)
        if error_budget.spend(1 - confidence):
            decision = "reject" if risk_score > 0.5 else "accept"
            return {"status": f"auto_{decision}d", "ai_score": risk_score}
        else:
            return {"status": "pending_human", "reason": "budget_exhausted"}
    
    elif level == Level.AUTONOMOUS:
        decision = "rejected" if risk_score > 0.5 else "accepted"
        return {"status": f"auto_{decision}", "ai_score": risk_score}


# ทดสอบ
import asyncio
from governance_types import Budget

async def main():
    # Malware scan — Level 1 (Govern)
    print("=== Malware Scan ===")
    r = await route_decision("malware_scan", risk_score=0.97, confidence=0.99)
    print(r)   # → auto_rejected

    r = await route_decision("malware_scan", risk_score=0.6, confidence=0.7)
    print(r)   # → pending_human (gray zone)

    # Privacy — Level 0 (Assist)
    print("\n=== Privacy Check ===")
    r = await route_decision("privacy_check", risk_score=0.99, confidence=0.99)
    print(r)   # → pending_human (human ตัดสินเสมอ)

    # Compression — Level 3 (Autonomous)
    print("\n=== Compression ===")
    r = await route_decision("compression", risk_score=0.1, confidence=0.95)
    print(r)   # → auto_accepted

asyncio.run(main())