from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from jose import jwt
from app.config import SECRET_KEY, ALGORITHM  # apne config.py ke actual variable names check karke daalo

def get_tenant_key(request: Request) -> str:
    """
    Rate limit ka 'key' tenant_id hoga, IP nahi.
    Agar token decode na ho paaye (login route, ya invalid token),
    IP address pe fallback kar jaate hain.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return get_remote_address(request)

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return f"tenant:{payload.get('tenant_id', 'unknown')}"
    except Exception:
        return get_remote_address(request)

import os

redis_url = os.getenv("REDIS_URL")
if redis_url:
    storage_uri = redis_url.strip('"').strip("'")
else:
    storage_uri = "memory://"

limiter = Limiter(key_func=get_tenant_key, storage_uri=storage_uri)