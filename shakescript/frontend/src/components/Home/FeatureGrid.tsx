import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Database, Lock, Zap, HardDrive, Radio, CuboidIcon as Cube } from 'lucide-react';

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: React.ReactNode
  visual: React.ReactNode
  delay: number
}

const FeatureCard = ({ icon, title, description, visual, delay }: FeatureCardProps) => {
  return (
    <motion.div
      className="bg-black border border-zinc-800 rounded-xl p-6 overflow-hidden relative"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: delay * 0.1 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex flex-col h-full">
        <div className="flex items-center gap-2 mb-3">
          <div className="text-emerald-400">{icon}</div>
          <h3 className="text-white font-medium">{title}</h3>
        </div>
        <div className="text-zinc-400 text-sm mb-4">{description}</div>
        <div className="mt-auto">{visual}</div>
      </div>
    </motion.div>
  )
}

const FeatureGrid: React.FC = () => {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="w-full bg-black py-16">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Postgres Database */}
          <FeatureCard
            icon={<Database className="h-5 w-5" />}
            title="Postgres Database"
            description={
              <div>
                <p className="mb-2">
                Powers story generation pipeline by maintaining a <span className="text-white font-medium">structured, and scalabale</span> data management system. 
                </p>
                <ul className="space-y-1 mt-4">
                  <li className="flex items-center gap-2">
                    <svg
                      className="h-4 w-4 text-emerald-400"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M5 13L9 17L19 7"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <span>Stores metadata related to Story</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <svg
                      className="h-4 w-4 text-emerald-400"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M5 13L9 17L19 7"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <span>RLS for fine-grained data access control</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <svg
                      className="h-4 w-4 text-emerald-400"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M5 13L9 17L19 7"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <span>Easy to extend</span>
                  </li>
                </ul>
              </div>
            }
            visual={
              <motion.div
                className="h-40 flex items-center justify-center"
                animate={{
                  rotate: [0, 5, 0, -5, 0],
                }}
                transition={{
                  repeat: Number.POSITIVE_INFINITY,
                  duration: 10,
                  ease: "easeInOut",
                }}
              >
                <svg
                  width="120"
                  height="120"
                  viewBox="0 0 120 120"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="opacity-30"
                >
                  <path
                    d="M60 10C32.4 10 10 32.4 10 60C10 87.6 32.4 110 60 110C87.6 110 110 87.6 110 60C110 32.4 87.6 10 60 10ZM60 100C37.9 100 20 82.1 20 60C20 37.9 37.9 20 60 20C82.1 20 100 37.9 100 60C100 82.1 82.1 100 60 100Z"
                    fill="#333"
                  />
                  <path
                    d="M60 30C43.4 30 30 43.4 30 60C30 76.6 43.4 90 60 90C76.6 90 90 76.6 90 60C90 43.4 76.6 30 60 30ZM60 80C48.9 80 40 71.1 40 60C40 48.9 48.9 40 60 40C71.1 40 80 48.9 80 60C80 71.1 71.1 80 60 80Z"
                    fill="#444"
                  />
                </svg>
              </motion.div>
            }
            delay={0}
          />

          {/* Authentication */}
          <FeatureCard
            icon={<Lock className="h-5 w-5" />}
            title="Vector Database"
            description={
              <div>
                <p>Stores embedding vectors for fast similarity searching and retrieval of relevant context chunks.</p>
              </div>
            }
            visual={
              <div className="mt-4">
                <motion.div
                  className="space-y-3"
                  animate={{ y: [0, -5, 0] }}
                  transition={{ repeat: Number.POSITIVE_INFINITY, duration: 5, ease: "easeInOut" }}
                >
                  <div className="flex gap-3">
                    <div className="bg-zinc-800 rounded p-2 text-xs text-zinc-400 w-full">"The guardian's words stirred something within him..."</div>
                    <div className="bg-zinc-800 rounded p-2 text-xs text-zinc-400 w-full">[0.153, -0.450, 0.775, -0.293, 0.670, ...]</div>
                  </div>
                  <div className="flex gap-3">
                    <div className="bg-zinc-800 rounded p-2 text-xs text-zinc-400 w-full h-8">"As the campfire.."</div>
                    <div className="bg-zinc-800 rounded p-2 text-xs text-zinc-400 w-full h-8">[0.770, -0.298, 0.665, ...]</div>
                  </div>
                  <div className="flex gap-3">
                    <div className="bg-zinc-800 rounded p-2 text-xs text-zinc-400 w-full">"Enemies ambushed the warrior.."</div>
                    <div className="bg-zinc-800 rounded p-2 text-xs text-zinc-400 w-full">[0.170, -0.410, 0.820, -0.265, 0.700, ...]</div>
                  </div>
                </motion.div>
              </div>
            }
            delay={1}
          />

          {/* Edge Functions */}
          <FeatureCard
            icon={<Zap className="h-5 w-5" />}
            title="FastAPI Backend"
            description={
              <div>
                <p>FastAPI backend serves as the core API layer for handling requests and integrating frontend, AI model, and databases.</p>
              </div>
            }
            visual={
              <motion.div
                className="h-40 relative"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ repeat: Number.POSITIVE_INFINITY, duration: 5, ease: "easeInOut" }}
              >
                <div className="absolute inset-0">
                  <svg viewBox="0 0 200 100" className="w-full h-full opacity-30">
                    <motion.path
                      d="M10,50 Q50,10 100,50 T190,50"
                      stroke="#3ECF8E"
                      strokeWidth="0.5"
                      fill="transparent"
                      animate={{
                        d: [
                          "M10,50 Q50,10 100,50 T190,50",
                          "M10,50 Q50,90 100,50 T190,50",
                          "M10,50 Q50,10 100,50 T190,50",
                        ],
                      }}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 10, ease: "easeInOut" }}
                    />
                    <motion.circle
                      cx="30"
                      cy="50"
                      r="2"
                      fill="#3ECF8E"
                      animate={{ cy: [50, 30, 50, 70, 50] }}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 10, ease: "easeInOut" }}
                    />
                    <motion.circle
                      cx="100"
                      cy="50"
                      r="2"
                      fill="#3ECF8E"
                      animate={{ cy: [50, 70, 50, 30, 50] }}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 10, ease: "easeInOut" }}
                    />
                    <motion.circle
                      cx="170"
                      cy="50"
                      r="2"
                      fill="#3ECF8E"
                      animate={{ cy: [50, 30, 50, 70, 50] }}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 10, ease: "easeInOut" }}
                    />
                  </svg>
                </div>
                <div className="absolute bottom-4 left-4 text-xs text-emerald-400 font-mono">
                  $ uvicorn main:app --reload
                </div>
              </motion.div>
            }
            delay={2}
          />

          {/* Storage */}
          <FeatureCard
            icon={<HardDrive className="h-5 w-5" />}
            title="Storage"
            description={
              <div>
                <p>Splits long episodes into smaller, manageable text chunks and stores them with vector representations.</p>
              </div>
            }
            visual={
              <div className="grid grid-cols-5 gap-2 mt-4">
                {[...Array(15)].map((_, i) => (
                  <motion.div
                    key={i}
                    className={`bg-zinc-800 rounded-md aspect-square flex items-center justify-center ${i >= 10 ? "hidden sm:flex" : ""}`}
                    initial={{ opacity: 0.5 }}
                    animate={{
                      opacity: [0.5, 0.8, 0.5],
                      scale: [1, i % 3 === 0 ? 1.1 : 1, 1],
                    }}
                    transition={{
                      repeat: Number.POSITIVE_INFINITY,
                      duration: 3 + (i % 5),
                      delay: i * 0.2,
                      ease: "easeInOut",
                    }}
                  >
                    {i % 3 === 0 ? (
                      <svg className="w-4 h-4 text-zinc-500" viewBox="0 0 24 24" fill="none">
                        <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="2" />
                        <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
                        <path d="M21 15L16 10L6 20" stroke="currentColor" strokeWidth="2" />
                      </svg>
                    ) : i % 3 === 1 ? (
                      <svg className="w-4 h-4 text-zinc-500" viewBox="0 0 24 24" fill="none">
                        <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="2" />
                        <path d="M8 12H16M8 8H16M8 16H12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4 text-zinc-500" viewBox="0 0 24 24" fill="none">
                        <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="2" />
                        <path d="M12 8V16M8 12H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      </svg>
                    )}
                  </motion.div>
                ))}
              </div>
            }
            delay={3}
          />

          {/* Realtime */}
          <FeatureCard
            icon={<Radio className="h-5 w-5" />}
            title="Similarity Search (via Embeddings)"
            description={
              <div>
                <p>Fetches the most relevant past chunks to maintain coherence across episodes.

</p>
              </div>
            }
            visual={
              <div className="h-40 relative">
                <motion.div
                  className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
                  animate={{
                    scale: [1, 1.1, 1],
                    rotate: [0, 5, 0, -5, 0],
                  }}
                  transition={{
                    repeat: Number.POSITIVE_INFINITY,
                    duration: 8,
                    ease: "easeInOut",
                  }}
                >
                  <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <motion.path
                      d="M50 10C27.9 10 10 27.9 10 50C10 72.1 27.9 90 50 90C72.1 90 90 72.1 90 50C90 27.9 72.1 10 50 10Z"
                      stroke="#333"
                      strokeWidth="1"
                      animate={{
                        d: [
                          "M50 10C27.9 10 10 27.9 10 50C10 72.1 27.9 90 50 90C72.1 90 90 72.1 90 50C90 27.9 72.1 10 50 10Z",
                          "M50 15C30.7 15 15 30.7 15 50C15 69.3 30.7 85 50 85C69.3 85 85 69.3 85 50C85 30.7 69.3 15 50 15Z",
                          "M50 10C27.9 10 10 27.9 10 50C10 72.1 27.9 90 50 90C72.1 90 90 72.1 90 50C90 27.9 72.1 10 50 10Z",
                        ],
                      }}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 8, ease: "easeInOut" }}
                    />
                    <motion.circle
                      cx="30"
                      cy="40"
                      r="5"
                      fill="#3ECF8E"
                      fillOpacity="0.3"
                      animate={{
                        cx: [30, 35, 30],
                        cy: [40, 45, 40],
                        fillOpacity: [0.3, 0.6, 0.3],
                      }}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 5, ease: "easeInOut" }}
                    />
                    <motion.circle
                      cx="70"
                      cy="60"
                      r="5"
                      fill="#3ECF8E"
                      fillOpacity="0.3"
                      animate={{
                        cx: [70, 65, 70],
                        cy: [60, 55, 60],
                        fillOpacity: [0.3, 0.6, 0.3],
                      }}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 5, ease: "easeInOut" }}
                    />
                  </svg>
                </motion.div>
                <motion.div
                  className="absolute top-1/4 left-1/2 transform -translate-x-1/2 bg-zinc-800 rounded-full px-3 py-1 text-xs text-zinc-400"
                  animate={{ y: [0, -5, 0] }}
                  transition={{ repeat: Number.POSITIVE_INFINITY, duration: 3, ease: "easeInOut" }}
                >
                  <span className="flex items-center gap-1">
                    <span className="block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>•••</span>
                  </span>
                </motion.div>
              </div>
            }
            delay={4}
          />

          {/* Vector */}
          <FeatureCard
            icon={<Cube className="h-5 w-5" />}
            title="AI Model"
            description={
              <div>
                <p>
                The core language model that generates story episodes based on the {" "}
                  <span className="text-white">processed prompt and contextual data.</span>.
                </p>
              </div>
            }
            visual={
              <div className="h-40 relative">
                <motion.div
                  className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
                  animate={{
                    rotateY: [0, 180, 360],
                    rotateX: [0, 180, 360],
                  }}
                  transition={{
                    repeat: Number.POSITIVE_INFINITY,
                    duration: 20,
                    ease: "linear",
                  }}
                  style={{ transformStyle: "preserve-3d" }}
                >
                  <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M60 20L20 40V80L60 100L100 80V40L60 20Z"
                      stroke="#333"
                      strokeWidth="1"
                      fill="transparent"
                    />
                    <path d="M60 20V60M60 60V100M60 60L20 40M60 60L100 40" stroke="#333" strokeWidth="1" />
                    <motion.circle cx="60" cy="20" r="2" fill="#3ECF8E" fillOpacity="0.8" />
                    <motion.circle cx="20" cy="40" r="2" fill="#3ECF8E" fillOpacity="0.8" />
                    <motion.circle cx="100" cy="40" r="2" fill="#3ECF8E" fillOpacity="0.8" />
                    <motion.circle cx="60" cy="100" r="2" fill="#3ECF8E" fillOpacity="0.8" />
                    <motion.circle cx="20" cy="80" r="2" fill="#3ECF8E" fillOpacity="0.8" />
                    <motion.circle cx="100" cy="80" r="2" fill="#3ECF8E" fillOpacity="0.8" />
                    <motion.circle cx="60" cy="60" r="2" fill="#3ECF8E" fillOpacity="0.8" />

                    {/* Random dots */}
                    {[...Array(10)].map((_, i) => (
                      <motion.circle
                        key={i}
                        cx={30 + Math.random() * 60}
                        cy={30 + Math.random() * 60}
                        r="1"
                        fill="#3ECF8E"
                        fillOpacity="0.6"
                        animate={{
                          opacity: [0, 1, 0],
                          r: [1, 1.5, 1],
                        }}
                        transition={{
                          repeat: Number.POSITIVE_INFINITY,
                          duration: 3 + (i % 3),
                          delay: i * 0.5,
                          ease: "easeInOut",
                        }}
                      />
                    ))}
                  </svg>
                </motion.div>
                <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-4">
                  <div className="bg-zinc-800 rounded px-2 py-1 text-xs text-zinc-400 flex items-center gap-1">
                    <span className="block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>OpenAI</span>
                  </div>
                  <div className="bg-zinc-800 rounded px-2 py-1 text-xs text-zinc-400 flex items-center gap-1">
                    <span className="block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>Gemini</span>
                  </div>
                </div>
              </div>
            }
            delay={5}
          />
        </div>

        <motion.div
          className="text-center mt-16 text-zinc-300"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <h2 className="text-2xl font-medium">
            Use one or all. <span className="text-zinc-500">Best of breed products. Integrated as a platform.</span>
          </h2>
        </motion.div>
      </div>
    </div>
  )
}


export default FeatureGrid;
