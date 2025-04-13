"use client"

import React, { useState, useEffect, createContext, useContext } from "react"
import { motion } from "framer-motion"
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts"
import { GlassCard } from "../ui/glass-card"

interface TabsContextType {
  activeTab: string
  setActiveTab: (value: string) => void
}

const TabsContext = createContext<TabsContextType | undefined>(undefined)

const useTabs = () => {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error("Tabs components must be used within a Tabs component")
  }
  return context
}

const Tabs = ({ defaultValue, children }: { defaultValue: string; children: React.ReactNode }) => {
  const [activeTab, setActiveTab] = useState(defaultValue)
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="w-full">{children}</div>
    </TabsContext.Provider>
  )
}

const TabsList = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="grid w-full max-w-md mx-auto grid-cols-3 mb-8 bg-gray-900 border border-gray-800">
      {children}
    </div>
  )
}

const TabsTrigger = ({ value, children }: { value: string; children: React.ReactNode }) => {
  const { activeTab, setActiveTab } = useTabs()
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`px-4 py-2 text-sm font-medium ${
        activeTab === value
          ? "bg-gray-800 text-white"
          : "text-gray-400 hover:text-white hover:bg-gray-800"
      }`}
    >
      {children}
    </button>
  )
}

const TabsContent = ({ value, children }: { value: string; children: React.ReactNode }) => {
  const { activeTab } = useTabs()
  return activeTab === value ? <div>{children}</div> : null
}


const CardHeader = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => {
  return <div className={`mb-4 ${className}`}>{children}</div>
}

const CardTitle = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => {
  return <h3 className={`text-xl font-semibold ${className}`}>{children}</h3>
}

const CardDescription = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => {
  return <p className={`text-gray-400 ${className}`}>{children}</p>
}

const CardContent = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => {
  return <div className={className}>{children}</div>
}

interface ChartDataItem {
  attribute: string
  fullName: string
  story1: number
  story2: number
  baseline: number
}

interface TrendDataItem {
  metric: string
  fullName: string
  story1: number
  story2: number
  baseline: number
}

export default function StatsDashboard() {
  const [animationStep, setAnimationStep] = useState(0)
  const attributes = [
    { full: "Plot / Structure", short: "P/S" },
    { full: "World-Building / Setting", short: "W/S" },
    { full: "Character Development", short: "CD" },
    { full: "Emotional Engagement / Impact", short: "E/I" },
    { full: "Writing Style", short: "WS" },
    { full: "Themes / Symbolism", short: "T/S" },
  ]

  const chartData = [
    { attribute: "P/S", fullName: "Plot / Structure", story1: 9.5, story2: 9.0, baseline: 7.5 },
    { attribute: "W/S", fullName: "World-Building / Setting", story1: 9.5, story2: 9.8, baseline: 7.2 },
    { attribute: "CD", fullName: "Character Development", story1: 9.0, story2: 9.5, baseline: 7.8 },
    { attribute: "E/I", fullName: "Emotional Engagement / Impact", story1: 9.2, story2: 9.4, baseline: 7.4 },
    { attribute: "WS", fullName: "Writing Style", story1: 8.8, story2: 8.8, baseline: 7.0 },
    { attribute: "T/S", fullName: "Themes / Symbolism", story1: 9.4, story2: 9.6, baseline: 7.3 },
  ]

  const radarChartData = attributes.map(({ full }) => {
    const match = chartData.find((item) => item.fullName === full)
    if (!match) return null
    return {
      attribute: full,
      "Shakescript AI - Story 1": match.story1 * (animationStep / 100),
      "Shakescript AI - Story 2": match.story2 * (animationStep / 100),
      "Baseline LLM": match.baseline * (animationStep / 100),
    }
  }).filter(Boolean)

  const barChartData = chartData.map((item) => ({
    attribute: item.fullName,
    story1: item.story1 * (animationStep / 100),
    story2: item.story2 * (animationStep / 100),
    baseline: item.baseline * (animationStep / 100),
  }))

  const trendData = attributes.map(({ full, short }) => {
    const match = chartData.find((item) => item.fullName === full)
    if (!match) return null
    return {
      metric: short,
      fullName: full,
      story1: match.story1 * (animationStep / 100),
      story2: match.story2 * (animationStep / 100),
      baseline: match.baseline * (animationStep / 100),
    }
  }).filter((item): item is TrendDataItem => item !== null)

  const getAverageImprovement = (
    data: ChartDataItem[],
    key1: 'story1' | 'story2',
    key2: 'story1' | 'story2',
    baselineKey: 'baseline'
  ): string => {
    const sum = data.reduce((acc: number, item: ChartDataItem) => {
      const improvement = ((item[key1] + item[key2]) / 2) - item[baselineKey]
      return acc + improvement
    }, 0)
    return (sum / data.length).toFixed(1)
  }

  const story1Improvement = getAverageImprovement(chartData, 'story1', 'story1', 'baseline')
  const story2Improvement = getAverageImprovement(chartData, 'story2', 'story2', 'baseline')
  const overallImprovement = getAverageImprovement(chartData, 'story1', 'story2', 'baseline')

  useEffect(() => {
    const timer = setTimeout(() => {
      if (animationStep < 100) {
        setAnimationStep((prev) => prev + 2)
      }
    }, 40)

    return () => clearTimeout(timer)
  }, [animationStep])

  const chartColors = {
    story1: "rgba(16, 185, 129, 0.7)", // Lighter emerald
    story2: "rgba(139, 92, 246, 0.7)", // Lighter purple
    baseline: "rgba(249, 115, 22, 0.7)", // Lighter orange
  }

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }} 
      animate={{ opacity: 1, scale: 1 }} 
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-black text-white p-12"
    >
      <div className="max-w-7xl mx-auto mt-16">
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-4">Statistical Analysis</h1>
          <p className="text-gray-400 text-lg">Comprehensive analysis of story quality metrics and performance trends</p>
        </div>

        <Tabs defaultValue="charts">
          <TabsList>
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="data">Raw Data</TabsTrigger>
          </TabsList>

          <TabsContent value="charts">
            <div className="space-y-12">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                {/* Radar Chart */}
                <GlassCard glowColor="purple" className="p-8 border border-gray-800">
                  <CardHeader className="px-0 pt-0 mb-8">
                    <CardTitle className="text-2xl text-purple-400">Story Quality Radar Analysis</CardTitle>
                    <CardDescription className="text-gray-400 text-lg">Comparing six key storytelling metrics</CardDescription>
                  </CardHeader>
                  <CardContent className="px-0 pb-0">
                    <div className="w-full h-[400px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart
                          outerRadius={130}
                          data={radarChartData}
                          margin={{ top: 20, right: 30, left: 20, bottom: 30 }}
                        >
                          <PolarGrid stroke="#374151" />
                          <PolarAngleAxis 
                            dataKey="attribute" 
                            tick={{ 
                              fill: "#e5e7eb", 
                              fontSize: 11,
                              dy: 5
                            }}
                            tickSize={15}
                            style={{
                              whiteSpace: "normal",
                              maxWidth: "120px"
                            }}
                          />
                          <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: "#e5e7eb" }} />
                          <Radar
                            name="Story 1"
                            dataKey="Shakescript AI - Story 1"
                            stroke={chartColors.story1}
                            fill={chartColors.story1}
                            fillOpacity={0.3}
                          />
                          <Radar
                            name="Story 2"
                            dataKey="Shakescript AI - Story 2"
                            stroke={chartColors.story2}
                            fill={chartColors.story2}
                            fillOpacity={0.3}
                          />
                          <Radar
                            name="Baseline"
                            dataKey="Baseline LLM"
                            stroke={chartColors.baseline}
                            fill={chartColors.baseline}
                            fillOpacity={0.3}
                            strokeDasharray="5 5"
                          />
                          <Legend 
                            wrapperStyle={{ color: "#e5e7eb", paddingTop: "20px" }} 
                            verticalAlign="bottom" 
                            height={36}
                          />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </GlassCard>

                {/* Bar Chart */}
                <GlassCard glowColor="orange" className="p-8 border border-gray-800">
                  <CardHeader className="px-0 pt-0 mb-8">
                    <CardTitle className="text-2xl text-orange-400">Attribute Comparison</CardTitle>
                    <CardDescription className="text-gray-400 text-lg">Performance across key metrics</CardDescription>
                  </CardHeader>
                  <CardContent className="px-0 pb-0">
                    <div className="w-full h-[400px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={barChartData}
                          layout="vertical"
                          margin={{ top: 20, right: 30, left: 60, bottom: 30 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false} />
                          <XAxis type="number" domain={[0, 10]} tick={{ fill: "#e5e7eb" }} />
                          <YAxis 
                            dataKey="attribute" 
                            type="category" 
                            tick={{ fill: "#e5e7eb", fontSize: 11 }} 
                            width={150}
                          />
                          <Tooltip
                            contentStyle={{ backgroundColor: "#1f2937", borderColor: "#4b5563", color: "#e5e7eb" }}
                            itemStyle={{ color: "#e5e7eb", padding: "4px 8px" }}
                          />
                          <Legend 
                            wrapperStyle={{ color: "#e5e7eb", paddingTop: "20px" }} 
                            formatter={(value) => <span style={{ padding: "0 8px" }}>{value}</span>}
                          />
                          <Bar dataKey="story1" name="Story 1" fill={chartColors.story1} radius={[0, 4, 4, 0]} />
                          <Bar dataKey="story2" name="Story 2" fill={chartColors.story2} radius={[0, 4, 4, 0]} />
                          <Bar dataKey="baseline" name="Baseline" fill={chartColors.baseline} radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </GlassCard>
              </div>

              {/* Worm Chart */}
              <GlassCard glowColor="emerald" className="p-8 border border-gray-800">
                <CardHeader className="px-0 pt-0 mb-8">
                  <CardTitle className="text-2xl text-emerald-400">Comparative Performance Trends</CardTitle>
                  <CardDescription className="text-gray-400 text-lg">
                    Detailed comparison of story attributes across models
                  </CardDescription>
                </CardHeader>
                <CardContent className="px-0 pb-0">
                  <div className="w-full h-[500px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 30 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis 
                          dataKey="metric" 
                          tick={{ fill: "#e5e7eb", fontSize: 12 }}
                          height={40}
                          interval={0}
                        />
                        <YAxis
                          domain={[6.5, 10]}
                          tick={{ fill: "#e5e7eb" }}
                          label={{
                            value: "Quality Score",
                            angle: -90,
                            position: "insideLeft",
                            fill: "#e5e7eb",
                          }}
                        />
                        <Tooltip
                          contentStyle={{ backgroundColor: "#1f2937", borderColor: "#4b5563", color: "#e5e7eb" }}
                          itemStyle={{ color: "#e5e7eb", padding: "4px 8px" }}
                          labelFormatter={(label: string) => {
                            const item = trendData.find(d => d.metric === label)
                            return item ? item.fullName : label
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="story1"
                          name="Story 1"
                          stroke={chartColors.story1}
                          strokeWidth={3}
                          dot={{ r: 5, strokeWidth: 2, fill: chartColors.story1 }}
                          activeDot={{ r: 7 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="story2"
                          name="Story 2"
                          stroke={chartColors.story2}
                          strokeWidth={3}
                          dot={{ r: 5, strokeWidth: 2, fill: chartColors.story2 }}
                          activeDot={{ r: 7 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="baseline"
                          name="Baseline"
                          stroke={chartColors.baseline}
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={{ r: 4, strokeWidth: 2, fill: chartColors.baseline }}
                          activeDot={{ r: 6 }}
                        />
                        <Legend
                          wrapperStyle={{ color: "#e5e7eb" }}
                          verticalAlign="bottom"
                          height={36}
                          layout="horizontal"
                          formatter={(value) => <span style={{ padding: "0 8px" }}>{value}</span>}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-gray-400 border-t border-gray-800 pt-6">
                    {attributes.map(({ short, full }) => (
                      <div key={short} className="flex items-center space-x-2">
                        <span className="font-medium text-emerald-400">{short}:</span>
                        <span>{full}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </GlassCard>

              {/* Loading Progress */}
              <motion.div
                className="flex flex-col items-center mt-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <div className="bg-gray-800 h-2 w-64 rounded-full overflow-hidden">
                  <motion.div
                    className="bg-emerald-400 h-full"
                    initial={{ width: "0%" }}
                    animate={{ width: `${animationStep}%` }}
                    transition={{ duration: 0.1 }}
                  ></motion.div>
                </div>
                <p className="text-gray-400 mt-4 text-lg">Data Visualization: {animationStep}%</p>
              </motion.div>
            </div>
          </TabsContent>

          <TabsContent value="trends">
            <div className="space-y-12">
              <GlassCard glowColor="purple" className="p-8 border border-gray-800">
                <CardHeader className="px-0 pt-0 mb-8">
                  <CardTitle className="text-2xl text-purple-400">Quality Metrics Trends</CardTitle>
                  <CardDescription className="text-gray-400 text-lg">Story quality comparison across key metrics</CardDescription>
                </CardHeader>
                <CardContent className="px-0 pb-0">
                  <div className="w-full h-[500px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 120 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis 
                          dataKey="metric" 
                          tick={{ fill: "#e5e7eb", fontSize: 12 }} 
                          angle={0} 
                          interval={0}
                        />
                        <YAxis
                          domain={[6.5, 10]}
                          tick={{ fill: "#e5e7eb" }}
                          label={{
                            value: "Quality Score",
                            angle: -90,
                            position: "insideLeft",
                            fill: "#e5e7eb",
                          }}
                        />
                        <Tooltip
                          contentStyle={{ backgroundColor: "#1f2937", borderColor: "#4b5563", color: "#e5e7eb" }}
                          itemStyle={{ color: "#e5e7eb", padding: "4px 8px" }}
                          labelFormatter={(label: string) => {
                            const item = trendData.find(d => d.metric === label)
                            return item ? item.fullName : label
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="story1"
                          name="Story 1"
                          stroke={chartColors.story1}
                          strokeWidth={3}
                          dot={{ r: 5, strokeWidth: 2, fill: chartColors.story1 }}
                          activeDot={{ r: 7 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="story2"
                          name="Story 2"
                          stroke={chartColors.story2}
                          strokeWidth={3}
                          dot={{ r: 5, strokeWidth: 2, fill: chartColors.story2 }}
                          activeDot={{ r: 7 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="baseline"
                          name="Baseline"
                          stroke={chartColors.baseline}
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={{ r: 4, strokeWidth: 2, fill: chartColors.baseline }}
                          activeDot={{ r: 6 }}
                        />
                        <Legend
                          wrapperStyle={{ color: "#e5e7eb" }}
                          verticalAlign="bottom"
                          height={60}
                          layout="horizontal"
                          margin={{ top: 40 }}
                          formatter={(value) => <span style={{ padding: "0 8px" }}>{value}</span>}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-8 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-gray-400">
                    {attributes.map(({ short, full }) => (
                      <div key={short} className="flex items-center space-x-2">
                        <span className="font-medium">{short}:</span>
                        <span>{full}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </GlassCard>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <GlassCard className="stat-card p-8 border border-gray-800">
                  <p className="text-gray-400 mb-4 text-lg">Story 1 Performance</p>
                  <p className="text-3xl font-bold text-emerald-400">+{story1Improvement}</p>
                  <p className="text-sm text-gray-500 mt-2">Points above baseline</p>
                  <p className="text-sm text-gray-400 mt-2">Average improvement across all metrics</p>
                </GlassCard>

                <GlassCard className="stat-card p-8 border border-gray-800">
                  <p className="text-gray-400 mb-4 text-lg">Story 2 Performance</p>
                  <p className="text-3xl font-bold text-purple-400">+{story2Improvement}</p>
                  <p className="text-sm text-gray-500 mt-2">Points above baseline</p>
                  <p className="text-sm text-gray-400 mt-2">Average improvement across all metrics</p>
                </GlassCard>

                <GlassCard className="stat-card p-8 border border-gray-800">
                  <p className="text-gray-400 mb-4 text-lg">Overall Improvement</p>
                  <p className="text-3xl font-bold text-orange-400">+{overallImprovement}</p>
                  <p className="text-sm text-gray-500 mt-2">Points above baseline</p>
                  <p className="text-sm text-gray-400 mt-2">Combined average improvement</p>
                </GlassCard>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="data">
            <GlassCard glowColor="emerald" className="p-8 border border-gray-800">
              <CardHeader className="px-0 pt-0 mb-8">
                <CardTitle className="text-2xl text-emerald-400">Raw Quality Metrics</CardTitle>
                <CardDescription className="text-gray-400 text-lg">Detailed scores for all story attributes</CardDescription>
              </CardHeader>
              <CardContent className="px-0 pb-0">
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b border-gray-800">
                        <th className="text-left py-4 px-6 text-gray-400 text-lg">Attribute</th>
                        <th className="text-center py-4 px-6 text-emerald-400 text-lg">Story 1</th>
                        <th className="text-center py-4 px-6 text-purple-400 text-lg">Story 2</th>
                        <th className="text-center py-4 px-6 text-orange-400 text-lg">Baseline</th>
                        <th className="text-center py-4 px-6 text-emerald-500 text-lg">Improvement</th>
                      </tr>
                    </thead>
                    <tbody>
                      {chartData.map((row, index) => (
                        <tr key={index} className="border-b border-gray-800">
                          <td className="py-4 px-6 text-gray-300 text-lg">{row.fullName}</td>
                          <td className="text-center py-4 px-6 text-gray-300 text-lg">{row.story1.toFixed(1)}</td>
                          <td className="text-center py-4 px-6 text-gray-300 text-lg">{row.story2.toFixed(1)}</td>
                          <td className="text-center py-4 px-6 text-gray-300 text-lg">{row.baseline.toFixed(1)}</td>
                          <td className="text-center py-4 px-6 text-emerald-400 text-lg">
                            +{((row.story1 + row.story2) / 2 - row.baseline).toFixed(1)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </GlassCard>
          </TabsContent>
        </Tabs>
      </div>
    </motion.div>
  )
}
