import React, {
    createContext,
    useState,
    useContext,
    useEffect,
    ReactNode,
    useCallback,
} from "react";
import { UserDashboard } from "@/types/user_schema";
import { getDashboardData } from "@/lib/api";
import { useAuth } from "./AuthContext";

interface DashboardContextType {
    dashboardData: UserDashboard | null;
    loading: boolean;
    error: string | null;
    refreshDashboard: () => Promise<void>;
}

const DashboardContext = createContext<DashboardContextType | undefined>(
    undefined,
);

export const DashboardProvider: React.FC<{ children: ReactNode }> = ({
    children,
}) => {
    const [dashboardData, setDashboardData] = useState<UserDashboard | null>(
        null,
    );
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    const fetchDashboardData = useCallback(async () => {
        if (!user) return; // Don't fetch if no user

        setLoading(true);
        setError(null);
        try {
            const data = await getDashboardData();
            setDashboardData(data);
        } catch (err: any) {
            setError(err.message || "Failed to load dashboard data.");
        } finally {
            setLoading(false);
        }
    }, [user]);

    useEffect(() => {
        // Fetch data only when the user logs in
        if (user) {
            fetchDashboardData();
        }
    }, [user, fetchDashboardData]);

    const refreshDashboard = async () => {
        await fetchDashboardData();
    };

    const value = { dashboardData, loading, error, refreshDashboard };

    return (
        <DashboardContext.Provider value={value}>
            {children}
        </DashboardContext.Provider>
    );
};

export const useDashboard = (): DashboardContextType => {
    const context = useContext(DashboardContext);
    if (!context) {
        throw new Error("useDashboard must be used within a DashboardProvider");
    }
    return context;
};
