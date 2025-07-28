from fastapi import APIRouter, HTTPException, Depends
from supabase import Client
from app.api.dependencies import (
    get_current_user,
    get_user_client,
    supabase_client,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login", summary="End point for google login")
def login_with_google():
    try:
        auth_response = supabase_client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {"redirect_to": "http://localhost:3000/auth/callback"},
            }
        )

        if auth_response and hasattr(auth_response, "url"):
            return {
                "status": "success",
                "provider": "google",
                "auth_url": auth_response.url,
            }

        return {"status": "error", "message": "Failed to generate OAuth URL"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logout", summary="End point for logout")
def logout_user(client: Client = Depends(get_user_client)):
    try:
        client.auth.sign_out()
        return {"status": "success", "message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

