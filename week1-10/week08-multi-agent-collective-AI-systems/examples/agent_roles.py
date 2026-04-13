"""
Agent Roles: แต่ละ agent เห็นอะไรได้บ้าง
"""
from dataclasses import dataclass
from typing import Optional
import random

@dataclass
class FileInput:
    """ข้อมูล input ทั้งหมด — แต่ละ agent เห็นได้บางส่วน"""
    content: bytes
    filename: str
    size: int
    file_type: str
    user_id: str        # PII — บาง agent ไม่ควรเห็น
    upload_cost: float  # ข้อมูล pricing

@dataclass
class AgentView:
    """สิ่งที่ agent เห็นได้จริงๆ"""
    content: Optional[bytes]
    filename: str
    size: int
    file_type: str
    user_id: Optional[str]
    upload_cost: Optional[float]

def security_view(f: FileInput) -> AgentView:
    """Security เห็น content แต่ไม่เห็น user_id และ cost"""
    return AgentView(
        content=f.content,
        filename=f.filename,
        size=f.size,
        file_type=f.file_type,
        user_id=None,         # ไม่เห็น — ป้องกัน bias
        upload_cost=None      # ไม่เห็น — ไม่ใช่หน้าที่
    )

def privacy_view(f: FileInput) -> AgentView:
    """Privacy เห็น content (text) แต่ไม่เห็น cost"""
    return AgentView(
        content=f.content,
        filename=f.filename,
        size=f.size,
        file_type=f.file_type,
        user_id=None,
        upload_cost=None
    )

def compliance_view(f: FileInput) -> AgentView:
    """Compliance เห็นแค่ metadata ไม่เห็น raw content"""
    return AgentView(
        content=None,         # ไม่ต้องเห็น raw bytes
        filename=f.filename,
        size=f.size,
        file_type=f.file_type,
        user_id=None,
        upload_cost=None
    )

def efficiency_view(f: FileInput) -> AgentView:
    """Efficiency เห็น size, type, cost แต่ไม่เห็น content"""
    return AgentView(
        content=None,
        filename=f.filename,
        size=f.size,
        file_type=f.file_type,
        user_id=None,
        upload_cost=f.upload_cost
    )


# Agent functions (จำลอง ML model)
def security_agent(view: AgentView) -> tuple[str, float]:
    """คืน (decision, confidence)"""
    # จำลอง: ไฟล์ .exe มีความเสี่ยงสูง
    if view.filename.endswith(".exe"):
        return ("reject", 0.97)
    elif view.size > 10_000_000:
        return ("flag", 0.75)
    else:
        return ("accept", 0.90)

def privacy_agent(view: AgentView) -> tuple[str, float]:
    if view.content and b"SSN" in view.content:
        return ("reject", 0.96)
    elif view.content and b"email" in view.content.lower():
        return ("flag", 0.65)
    else:
        return ("accept", 0.88)

def compliance_agent(view: AgentView) -> tuple[str, float]:
    if view.file_type in ["mp3", "mp4", "mov"]:
        return ("flag", 0.72)
    else:
        return ("accept", 0.85)

def efficiency_agent(view: AgentView) -> tuple[str, float]:
    # Efficiency ไม่ reject — แค่แนะนำ strategy
    if view.upload_cost and view.upload_cost > 0.08:
        return ("flag", 0.60)   # แพงเกิน flag ให้รู้
    else:
        return ("accept", 0.95)


# ทดสอบ
if __name__ == "__main__":
    file = FileInput(
        content=b"Normal document content",
        filename="report.pdf",
        size=500_000,
        file_type="pdf",
        user_id="user-123",
        upload_cost=0.05
    )
    
    print("=== Agent Visibility Test ===")
    sv = security_view(file)
    ev = efficiency_view(file)
    print(f"Security sees user_id: {sv.user_id}")     # None
    print(f"Efficiency sees content: {ev.content}")   # None
    print(f"Efficiency sees cost: {ev.upload_cost}")  # 0.05
    
    print("\n=== Agent Decisions ===")
    print(f"Security:   {security_agent(sv)}")
    print(f"Privacy:    {privacy_agent(privacy_view(file))}")
    print(f"Compliance: {compliance_agent(compliance_view(file))}")
    print(f"Efficiency: {efficiency_agent(efficiency_view(file))}")