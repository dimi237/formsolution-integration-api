from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = "super-secret-key"   # ⚠️ à mettre dans .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": data["sub"], "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, expected_type: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid token type"}
            )
        return payload
    except jwt.ExpiredSignatureError:
        return JSONResponse(
                status_code=403,
                content={"detail": "Token expired"}
            )
    except jwt.PyJWTError:
        return JSONResponse(
                status_code=403,
                content={"detail": "Invalid token"}
            )
