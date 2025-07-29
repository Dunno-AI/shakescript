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
import { UserProfile } from "@/types/user_schema";
import toast from "react-hot-toast";

interface AuthContextType {
  session: Session | null;
  user: User | null;
  profile: UserProfile | null;
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

  const fetchProfile = useCallback(async (currentUser: User) => {
    const { data, error } = await supabase
      .from("users")
      .select("*")
      .eq("auth_id", currentUser.id)
      .single();

    if (error) {
      console.error("Error fetching user profile:", error.message);
      setProfile(null);
    } else {
      setProfile(data);
    }
  }, []);

  const fetchSessionAndProfile = useCallback(async () => {
    setLoading(true);
    const { data, error } = await supabase.auth.getSession();

    if (error) {
      console.error("Error fetching session:", error.message);
      setSession(null);
      setUser(null);
      setProfile(null);
    } else {
      setSession(data.session);
      const currentUser = data.session?.user ?? null;
      setUser(currentUser);
      if (currentUser) await fetchProfile(currentUser);
      else setProfile(null);
    }

    setLoading(false);
  }, [fetchProfile]);

  useEffect(() => {
    fetchSessionAndProfile();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        switch (event) {
          case "SIGNED_IN":
            setSession(session);
            const signedInUser = session?.user ?? null;
            setUser(signedInUser);
            if (signedInUser) {
              fetchProfile(signedInUser);
              if (!sessionStorage.getItem('loginToastShown')) {
                toast.success("Successfully logged in!");
                sessionStorage.setItem('loginToastShown', 'true');
              }
            }
            break;
          case "SIGNED_OUT":
            setSession(null);
            setUser(null);
            setProfile(null);
            sessionStorage.removeItem('loginToastShown');
            break;
          case "TOKEN_REFRESHED":
            setSession(session);
            if (session?.user) setUser(session.user);
            break;
          default:
            break;
        }
      }
    );

    return () => {
      listener.subscription.unsubscribe();
    };
  }, [fetchSessionAndProfile, fetchProfile]);

  const signOut = async (navigate: NavigateFunction) => {
    try {
      await supabase.auth.signOut();
      localStorage.clear();
      sessionStorage.removeItem('loginToastShown');
      setSession(null);
      setUser(null);
      setProfile(null);
      toast.success("Successfully logged out!");
      navigate("/");
    } catch (err) {
      console.error("Sign-out error:", err);
      toast.error("Failed to log out.");
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