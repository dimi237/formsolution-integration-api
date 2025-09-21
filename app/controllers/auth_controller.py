from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
import httpx
from app import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.auth_model import LoginRequest
from app.settings import Settings

load_dotenv() 

required_settings = ["BASE_URL"]

try:
    settings = Settings()
except Exception as exc:
    print("❌ Impossible de charger les settings :", exc)
    raise SystemExit(1)

class AuthController:

    async def login(self, payload: LoginRequest, response: Response):
        # Vérification via service externe
        async with httpx.AsyncClient(timeout=10.0,auth=(payload.username, payload.password)) as client:
            resp = await client.get(f"{settings.BASE_URL}/auth/me")
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        account = resp.json().get('account')
        print(account)
        if account.get("name") != payload.username:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"sub": account["name"], "account": account})
        refresh_token = create_refresh_token({"sub": account["name"]})

        # Stocker en cookies HttpOnly
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=7 * 24 * 60 * 60
        )
        return {"message": "Login successful"}

    async def refresh (self, request: Request, response: Response):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Missing refresh token")

        payload = verify_token(refresh_token, "refresh")
        username = payload.get("sub")

        new_access = create_access_token({"sub": username})
        new_refresh = create_refresh_token({"sub": username})

        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=15 * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=7 * 24 * 60 * 60
        )
        return {"message": "Token refreshed"}
