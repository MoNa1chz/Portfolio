# ADR-003: Evidence Pipeline

## Context
ต้องออกแบบว่า "อะไร" ถูก log "ที่ไหน" และ "ใครเข้าถึงได้"

## What Gets Logged

### ทุก AI Decision ต้องมี:
- decision_id (unique)
- timestamp (ISO 8601)
- agent_name + model_version
- inputs (sanitized — ไม่มี PII)
- output (action + confidence)
- policy_version ที่ใช้ตอนนั้น
- human_involved (true/false)
- budget_status ณ ตอนนั้น

### ทุก Human Override ต้องมี:
- case_id ที่ override
- reviewer_id (hashed)
- decision + reason
- timestamp

## Where It's Stored
| ประเภท | Storage | Retention |
|--------|---------|-----------|
| AI decisions | Append-only DB | 3 ปี |
| Human overrides | Append-only DB | 5 ปี |
| Policy snapshots | Versioned store | ตลอดไป |
| Model versions | Model registry | ตลอดไป |

## Who Can Access
| Role | เห็นอะไร |
|------|---------|
| Developer | log ของ service ตัวเอง |
| Auditor | ทุกอย่าง (read-only) |
| User | explanation ของ decision ตัวเอง |
| Regulator | ตามที่ขอ + court order |

## Integrity
- ทุก log entry มี hash ของ entry ก่อนหน้า (chain)
- ถ้าใครแก้ไข → hash ไม่ตรง → detect ได้ทันที