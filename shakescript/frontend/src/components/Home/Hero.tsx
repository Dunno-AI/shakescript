import React from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { cn } from "../../lib/utils";
import { Sparkles } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

export const HeroSection: React.FC = () => {
  const { session } = useAuth();
  const navigate = useNavigate();

  const handleStartProject = () => {
    if (session) {
      navigate("/dashboard");
    } 
    else{
      navigate("/login");
    }
  };

  return (
    <section className="relative w-full min-h-screen flex flex-col items-center justify-center overflow-hidden bg-gradient-to-b from-black via-zinc-900 to-black">
      {/* Animated Grid Background */}
      <div
        className={cn(
          "absolute inset-0 transition-opacity duration-[3s]",
          "[background-size:50px_50px]",
          "[background-image:linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)]",
          "dark:[background-image:linear-gradient(to_right,#27272a_1px,transparent_1px),linear-gradient(to_bottom,#27272a_1px,transparent_1px)]"
        )}
      />

      {/* Radial Gradient */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center dark:bg-black [mask-image:radial-gradient(ellipse_at_center,transparent_0%,black_60%)]"></div>

      {/* Glowing Orb */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[300px] w-[300px] bg-emerald-500/30 rounded-full blur-[120px] animate-pulse" />
      
      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-center gap-2 mb-8"
        >
          <Sparkles className="w-5 h-5 text-emerald-400" />
          <span className="text-emerald-400 font-medium">AI-Powered Storytelling</span>
        </motion.div>

        <motion.h1
          className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-300 tracking-tight mb-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Turn Ideas into Stories
          <br />
          <motion.span 
            className="bg-gradient-to-r from-emerald-400 via-emerald-500 to-emerald-600 bg-clip-text text-transparent"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            Leverage Power of AI
          </motion.span>
        </motion.h1>

        <motion.p
          className="text-zinc-400 text-lg md:text-xl max-w-3xl mx-auto mb-6 leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          ShakeScript AI Brings Your Stories to Life.
        </motion.p>

        <motion.p
          className="text-zinc-500 max-w-2xl mx-auto mb-10 leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Start your project with AI-powered story generation, seamless project management, instant editing, creative customization on ShakeScript.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex items-center justify-center gap-4"
        >
          <motion.button 
            onClick={handleStartProject}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-lg font-medium shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all duration-300"
          >
            Start your project
          </motion.button>
        </motion.div>
      </div>

      {/* Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-black to-transparent" />
    </section>
  );
};
