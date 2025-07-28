# app/api/dependencies.py
import logging
import requests
from fastapi import Depends, Header, HTTPException, status
from supabase import create_client, Client
from app.core.config import settings
from app.services.core_service import StoryService

# Base Supabase client
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_user_client(authorization: str = Header(...)) -> tuple[Client, dict]:
    """
    Validates the user's JWT and returns an authenticated Supabase client with user info.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Must be 'Bearer <token>'.",
        )

    token = authorization.split("Bearer ")[1]
    logging.info(f"Received token: {token[:20]}...")

    try:
        verify_url = f"{settings.SUPABASE_URL}/auth/v1/user"
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": settings.SUPABASE_KEY,
            "Content-Type": "application/json",
        }

        response = requests.get(verify_url, headers=headers)
        logging.info(f"Auth API response status: {response.status_code}")

        if response.status_code != 200:
            logging.error(
                f"Token verification failed: {response.status_code} - {response.text}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Invalid user token or user not found.",
            )

        user_data = response.json()
        logging.info(f"Successfully authenticated user: {user_data.get('id')}")

        # Create authenticated client
        user_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

        user_client.postgrest.auth(token)

        return user_client, user_data

    except HTTPException:
        raise
    except requests.RequestException as e:
        logging.error(f"Network error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Network error.",
        )
    except Exception as e:
        logging.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid user token or user not found.",
        )


def get_story_service(auth_data: tuple = Depends(get_user_client)) -> StoryService:
    """
    Provides a StoryService with an authenticated Supabase client.
    """
    client, user_data = auth_data
    return StoryService(client)


def get_current_user(auth_data: tuple = Depends(get_user_client)) -> dict:
    """
    Returns the current user's auth ID and email.
    """
    client, user_data = auth_data
    return {"auth_id": user_data.get("id"), "email": user_data.get("email")}


def get_user_client_simple(authorization: str = Header(...)) -> Client:
    """
    Just create authenticated client without validation.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Must be 'Bearer <token>'.",
        )

    token = authorization.split("Bearer ")[1]

    try:
        # Create client and set auth token
        user_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        user_client.postgrest.auth(token)

        # Test by making a simple query to your users table
        result = user_client.table("users").select("id, email").limit(1).execute()

        logging.info(f"Successfully created authenticated client")
        return user_client

    except Exception as e:
        logging.error(f"Authentication failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Invalid user token or user not found.",
        )
