# app/api/routes/auth_routes.py

from fastapi import APIRouter, HTTPException, Depends
from supabase import Client
from app.api.dependencies import (
    get_current_user,
    get_user_client,
    supabase_client,
)  # Import the base client

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login", summary="End point for google login")
def login_with_google():
    try:
        # Use the imported base client for the unauthenticated sign-in flow
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
        # This uses the authenticated client passed by the dependency
        client.auth.sign_out()
        return {"status": "success", "message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-token")
def debug_token(
    user: dict = Depends(get_current_user), client: Client = Depends(get_user_client)
):
    # This uses the authenticated client to get the session
    session = client.auth.get_session()
    if session:
        return {"token": session.access_token, "auth_id": user["id"]}
    raise HTTPException(status_code=404, detail="No active session found.")
