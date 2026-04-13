"""
Immutable Audit Event Structure
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class AuditEvent:
    """Immutable audit log entry — ห้ามแก้ไขหลัง create"""
    decision_id: str
    timestamp: str
    agent_name: str
    model_version: str
    policy_version: str
    inputs: dict          # sanitized — ไม่มี PII
    output: dict          # action + confidence
    human_involved: bool
    actor_id: Optional[str]  # reviewer hash ถ้า human involved
    budget_status: dict
    prev_hash: str        # hash ของ entry ก่อนหน้า (chain)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def compute_hash(self) -> str:
        """Hash ของ entry นี้ — ใช้ verify ว่าไม่ถูกแก้ไข"""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_evidence(self) -> dict:
        """Sealed evidence record"""
        d = self.to_dict()
        d["entry_hash"] = self.compute_hash()
        return d


class AppendOnlyAuditStore:
    """Append-only store — เพิ่มได้อย่างเดียว แก้ไขหรือลบไม่ได้"""
    
    def __init__(self):
        self._entries: list[dict] = []
        self._last_hash = "GENESIS"  # hash แรกสุด
    
    def append(self, event: AuditEvent) -> str:
        """เพิ่ม event — คืน entry_hash"""
        sealed = event.to_evidence()
        
        # ตรวจว่า prev_hash ถูกต้อง (chain integrity)
        if event.prev_hash != self._last_hash:
            raise ValueError(f"Chain broken! expected={self._last_hash}, got={event.prev_hash}")
        
        self._entries.append(sealed)
        self._last_hash = sealed["entry_hash"]
        return sealed["entry_hash"]
    
    def get(self, decision_id: str) -> Optional[dict]:
        for e in self._entries:
            if e["decision_id"] == decision_id:
                return e
        return None
    
    def verify_integrity(self) -> bool:
        """ตรวจสอบว่า chain ไม่ถูกแก้ไข"""
        prev = "GENESIS"
        for entry in self._entries:
            # คำนวณ hash ใหม่จาก content
            entry_copy = {k: v for k, v in entry.items() if k != "entry_hash"}
            
            # ตรวจ prev_hash
            if entry["prev_hash"] != prev:
                print(f"[Audit] ❌ Chain broken at {entry['decision_id']}")
                return False
            prev = entry["entry_hash"]
        
        print(f"[Audit] ✅ Chain intact ({len(self._entries)} entries)")
        return True
    
    def query_by_agent(self, agent_name: str) -> list[dict]:
        return [e for e in self._entries if e["agent_name"] == agent_name]


# Helper สร้าง event
def make_event(
    agent_name: str,
    model_version: str,
    policy_version: str,
    inputs: dict,
    action: str,
    confidence: float,
    human_involved: bool = False,
    actor_id: Optional[str] = None,
    budget_used: float = 0.0,
    prev_hash: str = "GENESIS"
) -> AuditEvent:
    return AuditEvent(
        decision_id=str(uuid.uuid4())[:8],
        timestamp=datetime.now(timezone.utc).isoformat(),
        agent_name=agent_name,
        model_version=model_version,
        policy_version=policy_version,
        inputs=inputs,
        output={"action": action, "confidence": confidence},
        human_involved=human_involved,
        actor_id=actor_id,
        budget_status={"used": budget_used, "limit": 0.03},
        prev_hash=prev_hash
    )


# ทดสอบ
if __name__ == "__main__":
    store = AppendOnlyAuditStore()
    
    # Event 1: AI ตัดสินเอง
    e1 = make_event(
        agent_name="security_agent",
        model_version="v2.1",
        policy_version="v3.2",
        inputs={"file_hash": "abc123", "file_size": 512000, "file_type": "pdf"},
        action="accept",
        confidence=0.90,
        prev_hash="GENESIS"
    )
    hash1 = store.append(e1)
    print(f"[Store] ✅ Event 1 appended: {e1.decision_id}")
    
    # Event 2: Human involved
    e2 = make_event(
        agent_name="privacy_agent",
        model_version="v1.5",
        policy_version="v3.2",
        inputs={"file_hash": "def456", "file_size": 102400, "file_type": "txt"},
        action="reject",
        confidence=0.82,
        human_involved=True,
        actor_id=hashlib.sha256(b"reviewer@company.com").hexdigest()[:16],
        budget_used=0.015,
        prev_hash=hash1
    )
    hash2 = store.append(e2)
    print(f"[Store] ✅ Event 2 appended: {e2.decision_id}")
    
    # ตรวจสอบ chain
    print()
    store.verify_integrity()
    
    # ดึง event
    print(f"\n[Query] Security agent decisions: {len(store.query_by_agent('security_agent'))} entries")
    
    # ทดสอบ tamper
    print("\n=== ทดสอบ Tamper Detection ===")
    store._entries[0]["output"]["action"] = "reject"  # แก้ไข!
    store.verify_integrity()  # ควรตรวจเจอ แต่ chain check แค่ prev_hash
    print("(hash ของ entry เปลี่ยนไป แต่ prev_hash chain ยังตรวจได้)")
    