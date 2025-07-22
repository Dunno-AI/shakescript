from supabase import create_client, Client
from app.core.config import settings
from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import get_current_user

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login", summary="End point for google login")
def login_with_google():
    try:
        auth_response = supabase.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {"redirect_to": "http://localhost:3000/auth/callback"},
            }
        )

        if auth_response and isinstance(auth_response, dict):
            if "url" in auth_response:
                return {
                    "status": "success",
                    "provider": "google",
                    "auth_url": auth_response["url"],
                }
            elif "data" in auth_response and "url" in auth_response["data"]:
                return {
                    "status": "success",
                    "provider": "google",
                    "auth_url": auth_response["data"]["url"],
                }

        return {"status": "error", "message": "Failed to generate OAuth URL"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logout", summary="End point for logout")
def logout_user(user: dict = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return {"status": "success", "message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
