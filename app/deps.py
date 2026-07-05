"""Shared FastAPI dependencies."""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security import decode_token

bearer = HTTPBearer(auto_error=False)


def current_user_id(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> int:
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])
