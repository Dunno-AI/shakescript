from fastapi import Depends, Header, HTTPException, status
from supabase import create_client, Client
from app.services.core_service import StoryService
from app.core.config import settings

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# Provide StoryService instance
def get_story_service() -> StoryService:
    return StoryService()


# Authenticated user dependency


# dependencies.py
async def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = authorization.split("Bearer ")[1]

    try:
        # Correct usage: Pass as JWT
        user_response = supabase.auth.get_user(jwt=token)
        if user_response and user_response.user:
            return {
                "id": user_response.user.id,
                "email": user_response.user.email,
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    except Exception as e:
        import logging

        logging.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )
