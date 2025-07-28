from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(BaseModel):
    auth_id: str  
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    auth_id: str  
    is_premium: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfile(BaseModel):
    user: UserResponse
    stats: "UserStats"  

class UserStats(BaseModel):
    total_stories: int
    total_episodes: int
    episodes_day_count: int 
    episodes_month_count: int
    completed_stories: int
    in_progress_stories: int
    account_age_days: int
    last_active: Optional[datetime] = None

class UserDashboard(BaseModel):
    user: UserResponse
    stats: UserStats
    recent_stories: list  
    premium_status: bool

class CurrentUser(BaseModel):
    id: int
    auth_id: str
    email: str
    name: str
    is_premium: bool
