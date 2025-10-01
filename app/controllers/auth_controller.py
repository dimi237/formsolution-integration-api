from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
import httpx
from app import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.auth_model import LoginRequest, TokenResponse
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
        
        if not account:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        print(account)
        if account.get("name") != payload.username:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"sub": account["name"], "account": account})
        refresh_token = create_refresh_token({"sub": account["name"]})

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


    async def refresh (self, token: str):
        if not token:
            raise HTTPException(status_code=401, detail="Missing refresh token")

        payload = verify_token(token, "refresh")
        username = payload.get("sub")

        new_access = create_access_token({"sub": username})
        new_refresh = create_refresh_token({"sub": username})

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
