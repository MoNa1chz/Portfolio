from fastapi import APIRouter, Request
import redis, json, uuid
from datetime import datetime

router = APIRouter()
r = redis.Redis(host="redis", port=6379, decode_responses=True)

@router.post("/api/stateful/login")
async def login(request: Request):
    body = await request.json()

    session_id = str(uuid.uuid4())

    session_data = {
        "id": session_id,
        "data": body,
        "created_at": datetime.utcnow().isoformat()
    }

    r.setex(f"session:{session_id}", 300, json.dumps(session_data))

    return {
        "status": "success",
        "session_id": session_id
    }
    