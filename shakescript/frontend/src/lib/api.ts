import { supabase } from "./supabaseClient"; 

const API_BASE_URL = `${import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000"}/api/v1`;

/**
 * A reusable fetch function that automatically includes the Supabase auth token.
 * @param url The API endpoint to call (e.g., '/dashboard/')
 * @param options Standard fetch options (method, body, etc.)
 * @returns The JSON response from the API.
 */
const authFetch = async (url: string, options: RequestInit = {}) => {
    const {
        data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
        // Redirect to login if the session is invalid
        window.location.href = "/login";
        throw new Error("User not authenticated");
    }

    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
            ...options.headers,
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.access_token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
            errorData.detail || `HTTP error! status: ${response.status}`,
        );
    }

    return response.json();
};

/**
 * Fetches the complete dashboard data for the authenticated user.
 */
export const getDashboardData = () => {
    return authFetch("/dashboard/");
};

/**
 * Updates the user's public profile information in the 'users' table.
 * @param profileData The data to update (e.g., { name, avatar_url }).
 */
export const updateUserProfile = async (profileData: {
    name?: string;
    avatar_url?: string;
}) => {
    const {
        data: { user },
    } = await supabase.auth.getUser();
    if (!user) throw new Error("User not found");

    const { data, error } = await supabase
        .from("users")
        .update(profileData)
        .eq("auth_id", user.id)
        .select()
        .single();

    if (error) throw error;
    return data;
};
