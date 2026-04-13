"""
Anchor Types: ทำให้ "ทำผิด" เป็นไปไม่ได้ ไม่ใช่แค่ห้าม
"""
import json

class PII:
    """ข้อมูลส่วนตัว — AI ห้ามเห็น, ห้าม log"""
    __slots__ = ('_value',)
    
    def __init__(self, value: str):
        self._value = value
    
    def __repr__(self):
        return "<PII:hidden>"
    
    def __str__(self):
        return "<PII:hidden>"
    
    def __json__(self):
        raise TypeError("PII cannot be serialized to JSON")
    
    def get(self) -> str:
        """ต้องเรียกตั้งใจ — ไม่หลุดโดยบังเอิญ"""
        return self._value


class Budget:
    """ขีดจำกัดที่ AI ต้องอยู่ใน"""
    
    def __init__(self, name: str, limit: float):
        self.name = name
        self.limit = limit
        self._used = 0.0
    
    def spend(self, amount: float) -> bool:
        """คืน True ถ้ายังมี budget เหลือ"""
        if self._used + amount > self.limit:
            print(f"[Budget] ❌ {self.name} exhausted: {self._used:.3f}/{self.limit}")
            return False
        self._used += amount
        print(f"[Budget] ✅ {self.name}: {self._used:.3f}/{self.limit}")
        return True
    
    @property
    def remaining(self) -> float:
        return self.limit - self._used


# ทดสอบ
if __name__ == "__main__":
    # PII ไม่หลุดออก log
    email = PII("alice@example.com")
    print(f"User email: {email}")           # → <PII:hidden>
    
    # PII serialize ไม่ได้
    try:
        json.dumps({"email": str(email)})
        print("email in json:", str(email)) # → <PII:hidden> ปลอดภัย
    except Exception as e:
        print(f"Error: {e}")
    
    # Budget ป้องกัน AI ใช้ทรัพยากรเกิน
    retry_budget = Budget("retry_cost", limit=0.01)
    retry_budget.spend(0.004)  # ✅
    retry_budget.spend(0.004)  # ✅
    retry_budget.spend(0.004)  # ❌ เกิน budget → escalate