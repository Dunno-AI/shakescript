from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user, get_user_client
from app.services.db_service import DBService
from ...models.user_schema import UserDashboard, UserResponse, UserStats
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=UserDashboard, summary="Get all user dashboard data")
def get_user_dashboard(
    user: dict = Depends(get_current_user),
    # We need the authenticated client to initialize the DB service
    auth_data: tuple = Depends(get_user_client),
):
    """
    Retrieves all necessary data for the user dashboard, including the user profile,
    detailed statistics, and a list of recent stories.
    """
    client, user_data = auth_data
    auth_id = user.get("auth_id")
    if not auth_id:
        raise HTTPException(
            status_code=403, detail="Could not identify user from token."
        )

    # Initialize the DB service with the authenticated client
    db_service = DBService(client)

    # 1. Fetch User Profile
    profile_data = db_service.get_user_profile(auth_id)
    if "error" in profile_data:
        raise HTTPException(status_code=404, detail=profile_data["error"])

    # We need the 'created_at' datetime object for stats calculation
    created_at_str = profile_data.get("created_at")
    # Convert string to datetime object
    created_at = datetime.fromisoformat(created_at_str)

    # 2. Fetch User Stats
    stats_data = db_service.get_user_stats(auth_id, created_at)

    # 3. Fetch Recent Stories
    recent_stories_data = db_service.get_recent_stories(auth_id)

    # 4. Construct the final response object
    user_response = UserResponse(**profile_data)
    user_stats = UserStats(**stats_data)

    return UserDashboard(
        user=user_response,
        stats=user_stats,
        recent_stories=recent_stories_data,
        premium_status=user_response.is_premium,
    )
