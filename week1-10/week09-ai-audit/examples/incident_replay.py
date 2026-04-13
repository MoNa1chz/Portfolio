"""
Incident Replay: สืบสวนหลังเกิดปัญหา
"""
from audit_events import AppendOnlyAuditStore, make_event
from policy_snapshots import POLICY_V3_2, POLICY_V3_3, get_policy

def replay_decision(store: AppendOnlyAuditStore, decision_id: str) -> dict:
    """
    Replay การตัดสินใจ เพื่อสืบสวนว่าเกิดอะไรขึ้น
    """
    print(f"\n[Replay] === Investigating {decision_id} ===")
    
    entry = store.get(decision_id)
    if not entry:
        return {"error": "Not found"}
    
    # Step 1: ดูข้อมูลเดิม
    original_action = entry["output"]["action"]
    original_confidence = entry["output"]["confidence"]
    original_policy_version = entry["policy_version"]
    
    print(f"[Replay] Original: {original_action} (confidence={original_confidence:.2f})")
    print(f"[Replay] Policy used: {original_policy_version}")
    
    # Step 2: Replay ด้วย policy เดิม
    old_policy = get_policy(original_policy_version)
    replayed = old_policy.apply(entry["agent_name"], original_confidence)
    match = "✅" if replayed == original_action else "❌"
    print(f"[Replay] Replayed with {original_policy_version}: {replayed} {match}")
    
    # Step 3: ทดสอบด้วย policy ใหม่
    new_policy = POLICY_V3_3
    new_decision = new_policy.apply(entry["agent_name"], original_confidence)
    changed = "⚠️  WOULD CHANGE" if new_decision != original_action else "✅ same"
    print(f"[Replay] With new policy (v3.3): {new_decision} {changed}")
    
    return {
        "decision_id": decision_id,
        "original": original_action,
        "replayed_same_policy": replayed,
        "with_new_policy": new_decision,
        "policy_change_fixes_it": new_decision != original_action
    }


def incident_investigation(store: AppendOnlyAuditStore, suspicious_agent: str):
    """
    สืบสวน pattern — มี agent ไหนทำงานผิดปกติ?
    """
    print(f"\n[Investigation] === Agent: {suspicious_agent} ===")
    
    entries = store.query_by_agent(suspicious_agent)
    if not entries:
        print("ไม่พบ entries")
        return
    
    total = len(entries)
    rejects = [e for e in entries if e["output"]["action"] == "reject"]
    escalates = [e for e in entries if e["output"]["action"] == "escalate"]
    accepts = [e for e in entries if e["output"]["action"] == "accept"]
    
    print(f"  Total decisions: {total}")
    print(f"  Accept:   {len(accepts):3} ({len(accepts)/total:.0%})")
    print(f"  Escalate: {len(escalates):3} ({len(escalates)/total:.0%})")
    print(f"  Reject:   {len(rejects):3} ({len(rejects)/total:.0%})")
    
    # ตรวจ mode collapse
    if len(rejects) / total > 0.5:
        print(f"\n  ⚠️  WARNING: reject rate สูงมาก → อาจเกิด mode collapse")
        print(f"  → แนะนำ: human audit + retrain model")
    
    # ตรวจ confidence distribution
    confidences = [e["output"]["confidence"] for e in entries]
    avg_conf = sum(confidences) / len(confidences)
    print(f"\n  Average confidence: {avg_conf:.2f}")
    if avg_conf > 0.90:
        print(f"  ⚠️  Confidence สูงผิดปกติ → model อาจ overfit")


# ทดสอบ
if __name__ == "__main__":
    store = AppendOnlyAuditStore()
    
    # สร้าง events จำลอง incident
    # security agent reject สูงผิดปกติ
    test_data = [
        ("security_agent", "accept", 0.20),
        ("security_agent", "reject", 0.97),
        ("security_agent", "reject", 0.93),
        ("security_agent", "reject", 0.91),
        ("security_agent", "escalate", 0.75),
        ("privacy_agent",  "accept", 0.25),
        ("privacy_agent",  "escalate", 0.65),
    ]
    
    prev = "GENESIS"
    ids = []
    for agent, action, conf in test_data:
        e = make_event(
            agent_name=agent,
            model_version="v2.1",
            policy_version="v3.2",
            inputs={"file_hash": f"h{len(ids)}", "file_type": "pdf"},
            action=action,
            confidence=conf,
            prev_hash=prev
        )
        h = store.append(e)
        ids.append(e.decision_id)
        prev = h
    
    # Replay การตัดสินใจที่น่าสงสัย
    print("=== Replay Decision ===")
    result = replay_decision(store, ids[2])  # reject ที่สอง
    print(f"\nSummary: {result}")
    
    # สืบสวน agent ทั้งหมด
    print("\n=== Full Investigation ===")
    incident_investigation(store, "security_agent")
    incident_investigation(store, "privacy_agent")
    
    # Integrity check
    print("\n=== Chain Integrity ===")
    store.verify_integrity()