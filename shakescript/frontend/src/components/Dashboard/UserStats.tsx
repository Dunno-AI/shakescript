import React from "react";
import {
  Loader2,
  AlertTriangle,
  Sparkles,
  BookOpen,
  Calendar,
  TrendingUp,
} from "lucide-react";
import { useDashboard } from "../../contexts/DashboardContext";
import { DashboardCharts } from "./DashboardCharts";
import { useAuth } from "../../contexts/AuthContext";

export default function UserStats() {
  const { dashboardData, loading, error } = useDashboard();
  const { user: authUser } = useAuth();

  if (loading) {
    return (
      <div className="w-full h-full min-h-screen flex items-center justify-center bg-zinc-950 text-white">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
        <span className="ml-4">Loading Dashboard...</span>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="w-full h-full min-h-screen flex flex-col items-center justify-center bg-zinc-950 text-red-400">
        <AlertTriangle className="w-12 h-12 mb-4" />
        <p>Failed to load dashboard data.</p>
        <p className="text-sm text-zinc-500 mt-2">{error}</p>
      </div>
    );
  }

  const { user: profile, stats, recent_stories } = dashboardData;

  const avatarUrl =
    profile.avatar_url ||
    authUser?.user_metadata.avatar_url ||
    `https://i.pravatar.cc/100?u=${profile.auth_id}`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.1),transparent_50%)] pointer-events-none" />

      <div className="relative z-10 overflow-y-auto h-screen">
        <div className="container mx-auto px-6 py-8 max-w-7xl">
          {/* Header Section */}
          <div className="bg-gradient-to-r from-zinc-900/80 to-zinc-800/80 backdrop-blur-sm rounded-3xl p-8 mb-8 border border-zinc-700/50 hover:border-emerald-500/30 transition-all duration-500">
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
              <div className="relative">
                <img
                  src={avatarUrl}
                  alt="avatar"
                  className="w-24 h-24 rounded-2xl border-4 border-emerald-400/50 object-cover shadow-2xl"
                />
                {profile.is_premium && (
                  <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-emerald-500 rounded-full border-4 border-zinc-900 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>

              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-zinc-300 bg-clip-text text-transparent">
                    {profile.name}
                  </h1>
                </div>
                <div className="flex flex-wrap items-center gap-4 text-sm">
                  {profile.is_premium && (
                    <span className="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 py-2 rounded-full font-medium shadow-lg">
                      ✨ Premium
                    </span>
                  )}
                  <div className="flex items-center gap-2 text-zinc-400">
                    <Calendar className="w-4 h-4" />
                    <span>
                      Joined{" "}
                      {new Date(profile.created_at).toLocaleDateString(
                        "en-US",
                        { month: "long", day: "numeric", year: "numeric" },
                      )}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 rounded-2xl p-6 border border-emerald-500/30 backdrop-blur-sm hover:scale-105 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                  <BookOpen className="w-6 h-6 text-emerald-400" />
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-emerald-400 mb-1">
                    {stats.total_stories}
                  </div>
                  <div className="text-sm text-emerald-300/80">
                    Stories Generated
                  </div>
                </div>
              </div>
              <div className="h-2 bg-emerald-500/20 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full"
                  style={{ width: `${(stats.total_stories / 10) * 100}%` }}
                />
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-2xl p-6 border border-blue-500/30 backdrop-blur-sm hover:scale-105 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-blue-400" />
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-blue-400 mb-1">
                    {stats.total_episodes}
                  </div>
                  <div className="text-sm text-blue-300/80">Total Episodes</div>
                </div>
              </div>
              <div className="h-2 bg-blue-500/20 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full"
                  style={{ width: `${(stats.total_episodes / 100) * 100}%` }}
                />
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-2xl p-6 border border-purple-500/30 backdrop-blur-sm hover:scale-105 transition-all duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-400" />
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-purple-400 mb-1">
                    {stats.in_progress_stories}
                  </div>
                  <div className="text-sm text-purple-300/80">In Progress</div>
                </div>
              </div>
              <div className="h-2 bg-purple-500/20 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-purple-400 rounded-full"
                  style={{
                    width: `${(stats.in_progress_stories / stats.total_stories) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>

          {/* Usage Table */}
          <div className="bg-gradient-to-br from-zinc-900/80 to-zinc-800/80 backdrop-blur-sm rounded-2xl p-8 mb-12 border border-zinc-700/50 hover:border-emerald-500/30 transition-all duration-500">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-emerald-400" />
              </div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-white to-zinc-300 bg-clip-text text-transparent">
                Usage Analytics
              </h3>
              <span className="text-emerald-400 text-sm bg-emerald-500/10 px-3 py-1 rounded-full">
                Episodes
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-zinc-700/50">
                    <th className="text-left py-4 px-2 font-semibold text-zinc-300">
                      USER
                    </th>
                    <th className="text-center py-4 px-2 font-semibold text-zinc-300">
                      TODAY (24H)
                    </th>
                    <th className="text-center py-4 px-2 font-semibold text-zinc-300">
                      THIS MONTH
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="hover:bg-zinc-800/30 transition-colors duration-200">
                    <td className="py-6 px-2">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                          <span className="text-emerald-400 font-medium text-sm">
                            You
                          </span>
                        </div>
                        <span className="text-zinc-200 font-medium">You</span>
                      </div>
                    </td>
                    <td className="py-6 px-2 text-center">
                      <div className="inline-flex items-center gap-2">
                        <span className="text-2xl font-bold text-zinc-300">
                          {stats.episodes_day_count || 0}
                        </span>
                        <span className="text-zinc-500">/ 15</span>
                      </div>
                      <div className="w-24 h-2 bg-zinc-700 rounded-full mx-auto mt-2 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full"
                          style={{
                            width: `${(stats.episodes_day_count / 15) * 100}%`,
                          }}
                        />
                      </div>
                    </td>
                    <td className="py-6 px-2 text-center">
                      <div className="inline-flex items-center gap-2">
                        <span className="text-2xl font-bold text-zinc-300">
                          {stats.episodes_month_count || 0}
                        </span>
                        <span className="text-zinc-500">/ 30</span>
                      </div>
                      <div className="w-24 h-2 bg-zinc-700 rounded-full mx-auto mt-2 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full"
                          style={{
                            width: `${(stats.episodes_month_count / 30) * 100}%`,
                          }}
                        />
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Charts Section */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-r from-emerald-500 to-emerald-600 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-zinc-300 bg-clip-text text-transparent">
                Story Analytics
              </h2>
            </div>
            <DashboardCharts recentStories={recent_stories} />
          </div>

          <div className="h-20" />
        </div>
      </div>
    </div>
  );
}
