"""
Human-in-the-Loop: Escalation และ Override patterns
"""
import uuid
from datetime import datetime

# จำลอง escalation queue
escalation_queue = []
audit_log_store = []

def escalate(file_name: str, risk_score: float, reason: str) -> str:
    case_id = str(uuid.uuid4())[:8]
    case = {
        "case_id": case_id,
        "file": file_name,
        "risk_score": risk_score,
        "reason": reason,
        "status": "pending_human",
        "created_at": datetime.now().isoformat()
    }
    escalation_queue.append(case)
    print(f"[Escalation] 📋 Case {case_id} created — {reason}")
    return case_id

def human_override(case_id: str, decision: str, reviewer: str, reason: str):
    """Human override — final และ log เสมอ"""
    # หา case
    case = next((c for c in escalation_queue if c["case_id"] == case_id), None)
    if not case:
        print(f"[Override] ❌ Case {case_id} not found")
        return
    
    # Update
    case["status"] = f"human_{decision}d"
    case["reviewer"] = reviewer
    case["override_reason"] = reason
    
    # Audit log (immutable)
    audit_log_store.append({
        "event": "human_override",
        "case_id": case_id,
        "decision": decision,
        "reviewer": reviewer,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"[Override] ✅ Case {case_id} → {decision} by {reviewer}")
    print(f"[Audit]    📝 Logged permanently")

def kill_switch():
    """ปิด AI ทั้งหมดทันที — fallback to rule-based"""
    print("[KillSwitch] 🔴 AI DISABLED — switching to rule-based")
    print("[KillSwitch] All pending cases → human review")
    for case in escalation_queue:
        if case["status"] == "pending_human":
            print(f"  → Case {case['case_id']} needs human review")


# ทดสอบ
if __name__ == "__main__":
    print("=== Gray Zone → Escalation ===")
    case_id = escalate(
        file_name="document.pdf",
        risk_score=0.65,
        reason="Gray zone (0.3-0.95)"
    )
    
    print("\n=== Human Reviews and Overrides ===")
    human_override(
        case_id=case_id,
        decision="approve",
        reviewer="admin-007",
        reason="Checked manually — legitimate business document"
    )
    
    print("\n=== Emergency Kill Switch ===")
    escalate("suspicious.exe", 0.55, "Gray zone")
    kill_switch()
    
    print("\n=== Audit Log ===")
    for entry in audit_log_store:
        print(f"  {entry['timestamp']}: {entry['event']} → {entry['decision']} by {entry['reviewer']}")


