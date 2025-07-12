import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export const Story = () => {
  return (
    <div className="flex-1 overflow-y-auto pb-32 relative">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[#0A0A0A]">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#18181b_1px,transparent_1px),linear-gradient(to_bottom,#18181b_1px,transparent_1px)] bg-[size:24px_24px]"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0A0A0A] to-[#0A0A0A]"></div>
      </div>

      <div className="relative">
        <div className="min-h-[80vh] flex flex-col items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-6 max-w-2xl mx-auto"
          >
            <div className="flex items-center justify-center">
              <Sparkles className="w-12 h-12 text-emerald-500" />
            </div>
            <h1 className="text-5xl font-bold text-zinc-100">
              Create Your Story
            </h1>
            <p className="text-xl text-zinc-400 max-w-lg mx-auto">
              Click the "New Thread" button to start generating your unique
              story with AI-powered storytelling.
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
};
