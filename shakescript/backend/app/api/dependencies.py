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
async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Retrieves the current authenticated user from Supabase using the Bearer token.
    Returns a dictionary with user ID and email.
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
            )

        token = authorization.split("Bearer ")[1]
        user_response = supabase.auth.get_user(token)

        if user_response and user_response.user:
            return {"id": user_response.user.id, "email": user_response.user.email}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
