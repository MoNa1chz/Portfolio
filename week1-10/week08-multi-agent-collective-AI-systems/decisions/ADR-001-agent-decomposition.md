# ADR-001: Agent Decomposition

## Context
ระบบ upload ไฟล์ต้องบรรลุ 4 เป้าหมายพร้อมกัน
แต่ละเป้าหมายต้องการ data และ logic ต่างกัน
จึงแยกเป็น 4 agents

---

## Agent 1: Security Guardian
**Goal**: ตรวจ malware, exploit, pattern น่าสงสัย

| มิติ | รายละเอียด |
|------|-----------|
| เห็น | file content, file metadata, upload pattern |
| ไม่เห็น | user identity, pricing info |
| ตัดสินใจได้ | reject (>95%), flag (70-95%), accept (<70%) |
| ห้ามทำ | reject ไฟล์ที่ approved แล้ว, แก้ไขไฟล์, ใช้ user ID |
| Budget | reject ได้สูงสุด 3% |

---

## Agent 2: Privacy Guardian
**Goal**: ตรวจ PII, encryption, data redaction

| มิติ | รายละเอียด |
|------|-----------|
| เห็น | file content (text only), metadata |
| ไม่เห็น | pricing info, upload patterns |
| ตัดสินใจได้ | reject, flag for redaction, accept |
| ห้ามทำ | ดู raw bytes ที่ไม่ใช่ text, store PII ใน log |
| Budget | reject ได้สูงสุด 1% |

---

## Agent 3: Compliance Guardian  
**Goal**: ตรวจ copyright, licensing, retention rules

| มิติ | รายละเอียด |
|------|-----------|
| เห็น | file hash, metadata, content fingerprint |
| ไม่เห็น | raw content, user identity, cost |
| ตัดสินใจได้ | reject, flag for legal review, accept |
| ห้ามทำ | ตัดสินใจแทน legal team ใน ambiguous cases |
| Budget | reject ได้สูงสุด 1% |

---

## Agent 4: Efficiency Optimizer
**Goal**: compression, caching, cost optimization

| มิติ | รายละเอียด |
|------|-----------|
| เห็น | file size, type, load level, pricing |
| ไม่เห็น | file content, user identity |
| ตัดสินใจได้ | compress strategy, cache priority, cost estimate |
| ห้ามทำ | reject ไฟล์ (ไม่ใช่หน้าที่), override security decision |
| Budget | cost per file < $0.10 |

## Reasoning
แยก agents เพราะ:
- Security ต้องเห็น raw bytes → Privacy ไม่ควรเห็น
- Cost optimizer ไม่ควรรู้ว่าใครอัปโหลด → ป้องกัน bias
- แต่ละ goal มี failure mode ต่างกัน → isolate ความเสี่ยง