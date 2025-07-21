from supabase import create_client
from app.core.config import settings
from fastapi import APIRouter

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login", summary="End point for google login")
def login_with_google():
    auth_url = supabase.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": "http://localhost:8000"}}
    )
    
    return (
        {"status": "success", "provider": auth_url["provider"], "auth_url": auth_url["url"]}
        if auth_url
        else {"status": "success", "auth_url": "", "message": "Try logging in again"}
    )

@router.get("/logout", summary="End point for logout")
def logout_user():
    user = supabase.auth.get_user()
    # print(user)
    supabase.auth.sign_out()
    return (
            {"status": "success", "message": "Successfully logged out"}
            )

