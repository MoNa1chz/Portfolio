"""
Policy Snapshots: Version ทุก policy เพื่อ replay ได้
"""
from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass
class PolicyRule:
    """Rule เดียวใน policy"""
    section: str
    description: str
    auto_reject_threshold: float  # reject ถ้า confidence > นี้
    escalate_threshold: float     # escalate ถ้า confidence อยู่ใน range นี้
    auto_accept_threshold: float  # accept ถ้า confidence < นี้

@dataclass
class PolicySnapshot:
    """Snapshot ของ policy ทั้งหมด ณ เวลาหนึ่ง"""
    version: str
    effective_date: str
    author: str
    rules: dict[str, PolicyRule]
    
    def apply(self, agent: str, confidence: float) -> str:
        """ตัดสินใจตาม policy นี้"""
        rule = self.rules.get(agent)
        if not rule:
            return "escalate"  # ไม่รู้จัก agent → escalate ไว้ก่อน
        
        if confidence > rule.auto_reject_threshold:
            return "reject"
        elif confidence > rule.escalate_threshold:
            return "escalate"
        else:
            return "accept"


# Policy versions
POLICY_V3_2 = PolicySnapshot(
    version="v3.2",
    effective_date="2026-01-01",
    author="product-team",
    rules={
        "security_agent": PolicyRule(
            section="4.1",
            description="Security auto-reject if very confident",
            auto_reject_threshold=0.95,
            escalate_threshold=0.70,
            auto_accept_threshold=0.70
        ),
        "privacy_agent": PolicyRule(
            section="4.2",
            description="Privacy always escalates in gray zone",
            auto_reject_threshold=0.95,
            escalate_threshold=0.50,
            auto_accept_threshold=0.50
        ),
    }
)

POLICY_V3_3 = PolicySnapshot(
    version="v3.3",
    effective_date="2026-03-01",
    author="product-team",
    rules={
        "security_agent": PolicyRule(
            section="4.1",
            description="Tighter threshold after incident",
            auto_reject_threshold=0.90,  # เข้มขึ้น จาก 0.95
            escalate_threshold=0.60,
            auto_accept_threshold=0.60
        ),
        "privacy_agent": PolicyRule(
            section="4.2",
            description="Privacy unchanged",
            auto_reject_threshold=0.95,
            escalate_threshold=0.50,
            auto_accept_threshold=0.50
        ),
    }
)

# Policy Registry
POLICY_REGISTRY = {
    "v3.2": POLICY_V3_2,
    "v3.3": POLICY_V3_3,
}

def get_policy(version: str) -> PolicySnapshot:
    if version not in POLICY_REGISTRY:
        raise ValueError(f"Policy {version} not found")
    return POLICY_REGISTRY[version]


# ทดสอบ
if __name__ == "__main__":
    print("=== Policy v3.2 vs v3.3 ===")
    
    test_cases = [
        ("security_agent", 0.92, "borderline case"),
        ("security_agent", 0.97, "high confidence"),
        ("privacy_agent", 0.75, "medium confidence"),
    ]
    
    for agent, confidence, desc in test_cases:
        v32 = POLICY_V3_2.apply(agent, confidence)
        v33 = POLICY_V3_3.apply(agent, confidence)
        changed = "⚠️  CHANGED" if v32 != v33 else "✅ same"
        print(f"\n{desc} (confidence={confidence})")
        print(f"  v3.2 → {v32}")
        print(f"  v3.3 → {v33}  {changed}")
    
    print("\n=== Replay: ถ้าใช้ v3.3 ตั้งแต่แรก ผลต่างไหม? ===")
    historical_confidence = 0.92
    old_decision = POLICY_V3_2.apply("security_agent", historical_confidence)
    new_decision = POLICY_V3_3.apply("security_agent", historical_confidence)
    print(f"Original (v3.2): {old_decision}")
    print(f"New policy (v3.3): {new_decision}")
    if old_decision != new_decision:
        print("→ Policy change จะแก้ปัญหานี้ได้!")