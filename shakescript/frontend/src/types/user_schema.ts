// src/types/user_schema.ts

export interface UserProfile {
    id: number;
    auth_id: string;
    email: string;
    name: string;
    is_premium: boolean;
    avatar_url: string | null;
    created_at: string;
}

export interface UserStats {
    total_stories: number;
    total_episodes: number;
    episodes_day_count: number;
    episodes_month_count: number;
    completed_stories: number;
    in_progress_stories: number;
    account_age_days: number;
    last_active: string | null;
}

export interface UserDashboard {
    user: UserProfile;
    stats: UserStats;
    recent_stories: any[]; 
    premium_status: boolean;
}
