from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import verify_token

WHITELIST = [
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/docs",
    "/openapi.json"
]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(path) for path in WHITELIST):
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing access token"}
            )


        token = auth_header.split(" ")[1]

        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing access token"}
            )

        verify_token(token, "access")
        return await call_next(request)
