"""
Coordination: Parallel agents + Vote merger
"""
from agent_roles import (
    FileInput, security_view, privacy_view,
    compliance_view, efficiency_view,
    security_agent, privacy_agent,
    compliance_agent, efficiency_agent
)

PRIORITY = ["security", "privacy", "compliance", "efficiency"]

def vote_merger(decisions: dict[str, tuple[str, float]]) -> dict:
    """
    รวมผลจากทุก agent
    Returns: {"action": ..., "reason": ..., "escalate": bool}
    """
    print("\n[Merger] รับผลจาก agents:")
    for agent, (action, conf) in decisions.items():
        print(f"  {agent:12} → {action} (confidence={conf:.2f})")
    
    # Rule 1: ถ้าทุก agent เห็นตรงกัน
    actions = [d[0] for d in decisions.values()]
    if len(set(actions)) == 1:
        action = actions[0]
        print(f"[Merger] ✅ ทุก agent เห็นตรงกัน → {action}")
        return {"action": action, "reason": "unanimous", "escalate": False}
    
    # Rule 2: มี agent ไหนมั่นใจ > 95% ไหม?
    for agent_name in PRIORITY:  # ตาม priority
        action, conf = decisions[agent_name]
        if conf > 0.95:
            print(f"[Merger] ✅ {agent_name} มั่นใจ {conf:.0%} → {action}")
            return {"action": action, "reason": f"{agent_name}_high_confidence", "escalate": False}
    
    # Rule 3: ขัดแย้งและไม่มีใครมั่นใจ → escalate
    print("[Merger] ⚠️  ขัดแย้ง ไม่มีใครมั่นใจ → escalate to human")
    return {
        "action": "pending",
        "reason": "agent_disagreement",
        "escalate": True,
        "details": decisions
    }


def process_file(file: FileInput) -> dict:
    """รัน agents แบบ parallel แล้ว merge ผล"""
    print(f"\n{'='*50}")
    print(f"Processing: {file.filename}")
    
    # Parallel decisions (จำลอง)
    decisions = {
        "security":   security_agent(security_view(file)),
        "privacy":    privacy_agent(privacy_view(file)),
        "compliance": compliance_agent(compliance_view(file)),
        "efficiency": efficiency_agent(efficiency_view(file)),
    }
    
    result = vote_merger(decisions)
    print(f"[Final] → {result['action']} ({result['reason']})")
    return result


# ทดสอบ 3 scenarios
if __name__ == "__main__":
    
    # Scenario 1: ไฟล์ปกติ → ทุกคนเห็นตรงกัน
    normal = FileInput(
        content=b"Normal report",
        filename="report.pdf",
        size=100_000,
        file_type="pdf",
        user_id="user-1",
        upload_cost=0.03
    )
    process_file(normal)

    # Scenario 2: ไฟล์ .exe → Security reject ด้วย confidence สูง
    malware = FileInput(
        content=b"MZ\x90\x00suspicious",
        filename="install.exe",
        size=500_000,
        file_type="exe",
        user_id="user-2",
        upload_cost=0.05
    )
    process_file(malware)

    # Scenario 3: ไฟล์ที่ agents ขัดแย้ง → escalate
    ambiguous = FileInput(
        content=b"email: someone@example.com in a music file",
        filename="playlist.mp3",
        size=5_000_000,
        file_type="mp3",
        user_id="user-3",
        upload_cost=0.09
    )
    process_file(ambiguous)
    