import React from "react";
import { motion } from "framer-motion";
import { Github } from "lucide-react";
import DashboardImg  from "../../assets/images/start-generating.png";

interface StartBuildingSectionProps {
  className?: string;
}

export const StartBuildingSection: React.FC<StartBuildingSectionProps> = ({ className }) => {
  return (
    <motion.section
      className={`bg-black text-white w-full py-20 flex flex-col items-center justify-center ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.4 }}
    >
      <motion.h2
        className="text-4xl font-bold text-white mb-4 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        Start generating in seconds
      </motion.h2>

      <motion.p
        className="text-gray-400 text-center max-w-2xl mb-10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        Kickstart your next project with AI-powered storytelling on ShakeScript.
      </motion.p>

      <motion.div
        className="flex flex-wrap gap-4 justify-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
      >
        <button className="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-md transition-colors duration-300 flex items-center gap-2">
          View all examples
        </button>
        <button className="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-md transition-colors duration-300 flex items-center gap-2">
          <Github className="w-5 h-5" />
          Official GitHub library
        </button>
      </motion.div>

      <motion.div
        initial={{
          opacity: 0,
          y: 10,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          duration: 0.3,
          delay: 1.2,
        }}
        className="relative z-10 mt-20 w-[70%] rounded-3xl border border-neutral-200 bg-neutral-100 p-4 shadow-md dark:border-neutral-800 dark:bg-neutral-900"
      >
        <div className="w-full overflow-hidden rounded-xl border border-gray-300 dark:border-gray-700">
          <img
            src={DashboardImg}
            alt="Landing page preview"
            className="aspect-[1919/908] h-auto w-full object-cover"
            loading="lazy"
          />
        </div>
      </motion.div>
    </motion.section>
  );
};