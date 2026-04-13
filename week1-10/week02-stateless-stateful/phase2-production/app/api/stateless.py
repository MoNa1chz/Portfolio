from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/api/stateless/info")
def stateless_info():
    return {
        "status": "success",
        "message": "I have no memory",
        "timestamp": datetime.utcnow().isoformat()
    }