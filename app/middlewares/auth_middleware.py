from fastapi import Request, Response
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
    async def dispatch(self, request: Request, call_next
                       ):
        if any(request.url.path.startswith(path) for path in WHITELIST):
            return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            return JSONResponse(
                status_code=403,
                content={"detail": "Missing access token"}
            )

        verify_token(token, "access")
        return await call_next(request)
