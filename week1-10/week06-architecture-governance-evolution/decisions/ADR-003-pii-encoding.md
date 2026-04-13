# ADR-003: PII Protection via Type System

## Context
ระบบรับ email, ชื่อ, และข้อมูลส่วนตัวของผู้ใช้
ต้องไม่ให้ข้อมูลนี้หลุดออก log

## Bad Approach (อย่าทำ)
เขียน policy ใน PDF ว่า "ห้าม log PII"
→ Developer ลืม → ข้อมูลหลุด → ปัญหา compliance

## Good Approach: Encode ใน Type System

สร้างไฟล์ตัวอย่าง `governance/pii.py`:
```python
class PII:
    """ข้อมูลส่วนตัว — ห้าม log เด็ดขาด"""
    __slots__ = ('_value',)
    
    def __init__(self, value):
        self._value = value
    
    def __repr__(self):
        return "<PII:hidden>"   # log เห็นแค่นี้
    
    def __str__(self):
        return "<PII:hidden>"   # print เห็นแค่นี้
    
    def get(self):
        return self._value      # ต้องเรียก .get() ตั้งใจเท่านั้น

# ใช้งาน
email = PII("alice@example.com")
print(f"User: {email}")         # → "User: <PII:hidden>"
logger.info(f"Login: {email}")  # → "Login: <PII:hidden>"
json.dumps({"email": email})    # → TypeError! (ป้องกันส่งออก API)
```

## Governance Rule
- ข้อมูลส่วนตัว → ต้องใส่ใน PII() เสมอ
- การ log จะปลอดภัยโดยอัตโนมัติ
- Code review ตรวจ: มีที่ไหน call .get() โดยไม่จำเป็นบ้าง?