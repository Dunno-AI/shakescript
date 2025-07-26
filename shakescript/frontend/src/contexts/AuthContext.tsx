import React, {
  createContext,
  useState,
  useEffect,
  useContext,
  ReactNode,
  useCallback,
} from "react";
import { Session, User } from "@supabase/supabase-js";
import { supabase } from "../lib/supabaseClient";
import { NavigateFunction } from "react-router-dom";
import { UserProfile } from "@/types/user_schema"; // Make sure you have this type defined

interface AuthContextType {
  session: Session | null;
  user: User | null;
  profile: UserProfile | null; // Add a state for the detailed profile
  loading: boolean;
  signOut: (navigate: NavigateFunction) => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchSessionAndProfile = useCallback(async () => {
    setLoading(true);
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error) {
      console.error("Error fetching session:", error.message);
    } else {
      setSession(session);
      const currentUser = session?.user ?? null;
      setUser(currentUser);

      if (currentUser) {
        // --- NEW: Fetch the user's public profile from your 'users' table ---
        const { data: profileData, error: profileError } = await supabase
          .from("users")
          .select("*")
          .eq("auth_id", currentUser.id)
          .single();

        if (profileError) {
          console.error("Error fetching user profile:", profileError.message);
          setProfile(null);
        } else {
          setProfile(profileData);
        }
      } else {
        setProfile(null);
      }
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchSessionAndProfile();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        // Refetch everything on auth state change to stay in sync
        fetchSessionAndProfile();
      },
    );

    return () => {
      listener.subscription.unsubscribe();
    };
  }, [fetchSessionAndProfile]);

  const signOut = async (navigate: NavigateFunction) => {
    try {
      await supabase.auth.signOut();
      localStorage.clear();
      // Clear all states on sign out
      setSession(null);
      setUser(null);
      setProfile(null);
      navigate("/");
    } catch (err) {
      console.error("Sign-out error:", err);
    }
  };

  const value = {
    session,
    user,
    profile,
    loading,
    signOut,
    refreshAuth: fetchSessionAndProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
