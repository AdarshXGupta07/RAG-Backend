from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import SessionLocal
import redis
import os

router = APIRouter()

@router.get("/health")
def health_check():
    result = {"database": "unknown", "redis": "unknown"}
    healthy = True

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        result["database"] = "connected"
    except Exception as e:
        result["database"] = f"error: {str(e)}"
        healthy = False

    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()
        result["redis"] = "connected"
    except Exception as e:
        result["redis"] = f"error: {str(e)}"
        healthy = False

    result["status"] = "healthy" if healthy else "unhealthy"
    return JSONResponse(content=result, status_code=200 if healthy else 503)