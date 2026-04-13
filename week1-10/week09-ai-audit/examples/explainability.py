"""
Decision Explainability: ตอบคำถาม "ทำไมถึงตัดสินแบบนี้?"
"""
from audit_events import AppendOnlyAuditStore, make_event
from policy_snapshots import POLICY_V3_2, get_policy

def explain_decision(store: AppendOnlyAuditStore, decision_id: str, requesting_user_hash: str) -> dict:
    """
    สร้าง human-readable explanation
    """
    entry = store.get(decision_id)
    if not entry:
        return {"error": "Decision not found"}
    
    policy = get_policy(entry["policy_version"])
    agent = entry["agent_name"]
    confidence = entry["output"]["confidence"]
    action = entry["output"]["action"]
    
    # สร้าง explanation ภาษาคน
    if action == "reject":
        what_happened = "ไฟล์ของคุณถูกปฏิเสธ"
        why = f"{agent} ตรวจพบความเสี่ยง (confidence={confidence:.0%})"
    elif action == "accept":
        what_happened = "ไฟล์ของคุณได้รับการอนุมัติ"
        why = f"{agent} ไม่พบความเสี่ยง (confidence={confidence:.0%})"
    else:
        what_happened = "ไฟล์ของคุณกำลังรอ human review"
        why = f"{agent} ไม่แน่ใจ (confidence={confidence:.0%}) จึงส่งให้คนตรวจ"
    
    rule = policy.rules.get(agent)
    policy_explanation = "ไม่พบ rule" if not rule else (
        f"Policy {entry['policy_version']} section {rule.section}: "
        f"{rule.description}"
    )
    
    return {
        "decision_id": decision_id,
        "timestamp": entry["timestamp"],
        "what_happened": what_happened,
        "why": why,
        "model_used": f"{agent} model {entry['model_version']}",
        "policy_rule": policy_explanation,
        "human_reviewed": entry["human_involved"],
        "your_options": [
            "ขอให้ human review ใหม่",
            "อุทธรณ์ผ่าน support@company.com",
            "ส่งไฟล์ใหม่"
        ] if action == "reject" else ["ไม่มีการดำเนินการเพิ่มเติม"]
    }


def generate_bias_report(store: AppendOnlyAuditStore) -> dict:
    """
    ตรวจสอบว่า agent ใดมี rejection rate สูงผิดปกติ
    """
    from collections import defaultdict
    
    agent_stats = defaultdict(lambda: {"total": 0, "reject": 0})
    
    for entry in store._entries:
        agent = entry["agent_name"]
        agent_stats[agent]["total"] += 1
        if entry["output"]["action"] == "reject":
            agent_stats[agent]["reject"] += 1
    
    print("\n[BiasReport] === Rejection Rate by Agent ===")
    rates = {}
    for agent, stats in agent_stats.items():
        rate = stats["reject"] / stats["total"] if stats["total"] > 0 else 0
        rates[agent] = rate
        flag = "⚠️" if rate > 0.10 else "✅"
        print(f"  {flag} {agent}: {rate:.0%} ({stats['reject']}/{stats['total']})")
    
    return rates


# ทดสอบ
if __name__ == "__main__":
    store = AppendOnlyAuditStore()
    
    # สร้าง events ตัวอย่าง
    events = [
        ("security_agent", "pdf", "accept", 0.20),
        ("security_agent", "exe", "reject", 0.97),
        ("privacy_agent",  "txt", "escalate", 0.75),
        ("security_agent", "pdf", "accept", 0.15),
        ("privacy_agent",  "doc", "accept", 0.30),
    ]
    
    prev = "GENESIS"
    ids = []
    for agent, ftype, action, conf in events:
        e = make_event(
            agent_name=agent,
            model_version="v2.1",
            policy_version="v3.2",
            inputs={"file_hash": f"hash_{ftype}", "file_type": ftype},
            action=action,
            confidence=conf,
            prev_hash=prev
        )
        h = store.append(e)
        ids.append(e.decision_id)
        prev = h
    
    # ขอ explanation
    print("=== User ขอ Explanation ===")
    explanation = explain_decision(
        store=store,
        decision_id=ids[1],  # exe ที่ถูก reject
        requesting_user_hash="user_abc123"
    )
    for k, v in explanation.items():
        print(f"  {k}: {v}")
    
    # Bias report
    generate_bias_report(store)