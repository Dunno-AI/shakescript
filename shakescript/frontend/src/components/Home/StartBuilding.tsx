import React from "react";
import { motion } from "framer-motion";
import { Github } from "lucide-react";
import DashboardImg from "../../assets/images/start-generating.png";
import { AnimatedBeamMultipleOutputDemo } from "../AnimatedBeam"; // Import the existing component

interface StartBuildingSectionProps {
  className?: string;
}

export const StartBuildingSection: React.FC<StartBuildingSectionProps> = ({
  className,
}) => {
  return (
    <motion.section
      className={`bg-black text-white w-full pt-0 pb-12 -mt-4 ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.4 }}
    >
      {/* Top section with two columns */}
      <div className="container mx-auto flex flex-col md:flex-row items-center justify-between mb-8">
        {/* Left side - Animated Beam Component */}
        <div className="w-full md:w-1/2 mb-10 md:mb-0">
          <AnimatedBeamMultipleOutputDemo />
        </div>

        {/* Right side - Content Section */}
        <div className="w-full md:w-1/2 flex flex-col items-center md:items-start px-6">
          <motion.h2
            className="text-4xl font-bold text-white mb-4 text-center md:text-left"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            Start generating in seconds
          </motion.h2>

          <motion.p
            className="text-gray-400 text-center md:text-left max-w-2xl mb-10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            Kickstart your next project with AI-powered storytelling on
            ShakeScript.
          </motion.p>

          <motion.div
            className="flex flex-wrap gap-4 justify-center md:justify-start"
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
        </div>
      </div>

      {/* Bottom section - Full width dashboard image */}
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
        className="container mx-auto relative z-10 w-[70%] rounded-3xl border border-neutral-800 bg-neutral-900 p-4 shadow-md"
      >
        <div className="w-full overflow-hidden rounded-xl border border-gray-700">
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
