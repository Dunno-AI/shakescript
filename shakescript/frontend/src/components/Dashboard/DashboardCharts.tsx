import React from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    Legend,
    PieChart,
    Pie,
    Cell,
} from "recharts";
import { Story } from "@/types/story";
import { Sparkles, TrendingUp, BookOpen } from "lucide-react";

interface DashboardChartsProps {
    recentStories: Story[];
}

const COLORS = [
    "#10B981",
    "#6366F1",
    "#A855F7",
    "#F59E0B",
    "#EF4444",
    "#71717A",
];

export const DashboardCharts: React.FC<DashboardChartsProps> = ({
    recentStories,
}) => {
    const genreData = recentStories.reduce(
        (acc: { [key: string]: number }, story) => {
            const genre = story.genre || "Uncategorized";
            acc[genre] = (acc[genre] || 0) + 1;
            return acc;
        },
        {},
    );

    const chartData = Object.entries(genreData).map(([name, value]) => ({
        name,
        value,
    }));

    if (chartData.length === 0) {
        return (
            <div className="bg-gradient-to-br from-zinc-900 to-zinc-800 rounded-2xl p-8 border border-zinc-700/50 text-center backdrop-blur-sm">
                <div className="flex items-center justify-center mb-4">
                    <BookOpen className="w-12 h-12 text-emerald-400" />
                </div>
                <h3 className="text-xl font-semibold text-zinc-300 mb-2">
                    Ready to Create Magic?
                </h3>
                <p className="text-zinc-400">
                    Start creating stories to see your genre analytics come to life!
                </p>
            </div>
        );
    }

    // --- FIX: Define a reusable style for the tooltips ---
    const tooltipStyle = {
        backgroundColor: "#ffffff", // Dark background
        border: "1px solid #3f3f46", // Subtle border
        borderRadius: "12px",
        color: "#18181b", // black text color
    };

    return (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            {/* Bar Chart */}
            <div className="bg-gradient-to-br from-zinc-900 to-zinc-800 rounded-2xl p-6 border border-zinc-700/50 backdrop-blur-sm hover:border-emerald-500/30 transition-all duration-300">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-emerald-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-zinc-100">
                        Stories by Genre
                    </h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                        data={chartData}
                        layout="vertical"
                        margin={{ left: 30, top: 10, right: 30, bottom: 20 }}
                    >
                        <XAxis
                            type="number"
                            stroke="#a1a1aa"
                            tick={{ fontSize: 12, fill: "#a1a1aa" }}
                            allowDecimals={false}
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            type="category"
                            dataKey="name"
                            stroke="#a1a1aa"
                            tick={{ fontSize: 12, fill: "#a1a1aa" }}
                            width={100}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip
                            cursor={{ fill: "rgba(16, 185, 129, 0.1)" }}
                            contentStyle={tooltipStyle} // Apply the fix
                        />
                        <Bar
                            dataKey="value"
                            name="Stories"
                            fill="url(#barGradient)"
                            barSize={20}
                            radius={[0, 8, 8, 0]}
                        />
                        <defs>
                            <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                                <stop offset="0%" stopColor="#10B981" />
                                <stop offset="100%" stopColor="#34D399" />
                            </linearGradient>
                        </defs>
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Pie Chart */}
            <div className="bg-gradient-to-br from-zinc-900 to-zinc-800 rounded-2xl p-6 border border-zinc-700/50 backdrop-blur-sm hover:border-emerald-500/30 transition-all duration-300">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-emerald-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-zinc-100">
                        Genre Distribution
                    </h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <PieChart margin={{ top: 20, right: 30, left: 30, bottom: 20 }}>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                            nameKey="name"
                            label={({ name, percent }) =>
                                `${name} ${(percent * 100).toFixed(0)}%`
                            }
                        >
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={COLORS[index % COLORS.length]}
                                />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={tooltipStyle} // Apply the fix
                        />
                        <Legend wrapperStyle={{ fontSize: "14px", color: "#a1a1aa" }} />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
