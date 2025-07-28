import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  Home,
  Library,
  ChevronLeft,
  ChevronRight,
  History,
  User,
  LogOut,
  PlusSquare,
} from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion"; // Import motion components

export const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut(navigate);
  };

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  // Animation variants for the text elements
  const textVariants = {
    hidden: { opacity: 0, x: -10, width: 0 },
    visible: {
      opacity: 1,
      x: 0,
      width: "auto",
      transition: { duration: 0.2, delay: 0.1 },
    },
    exit: { opacity: 0, x: -10, width: 0, transition: { duration: 0.1 } },
  };

  return (
    <div
      className={`relative bg-[#111111] border-r border-zinc-800 flex flex-col transition-all duration-300 ease-in-out ${isCollapsed ? "w-[80px]" : "w-[240px]"
        }`}
    >
      <div
        className={`p-6 flex items-center gap-2 ${isCollapsed ? "justify-center" : ""}`}
      >
        <div className="w-6 h-6 flex-shrink-0">
          <svg viewBox="0 0 24 24" className="text-emerald-500 w-6 h-6">
            <path
              fill="currentColor"
              d="M12 2L2 19h20L12 2zm0 3.8L18.5 17H5.5L12 5.8z"
            />
          </svg>
        </div>
        <AnimatePresence>
          {!isCollapsed && (
            <motion.span
              variants={textVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="font-semibold text-zinc-100 whitespace-nowrap"
            >
              Story Generator
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      <nav className="flex-1 px-4 flex flex-col">
        <ul className="space-y-1 flex-1">
          {/* Home Link */}
          <li>
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-sm ${isActive ? "text-zinc-100 bg-zinc-800" : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"} rounded-md ${isCollapsed ? "justify-center" : ""}`
              }
            >
              <Home size={16} />
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span
                    variants={textVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="whitespace-nowrap"
                  >
                    Home
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          </li>
          {/* Create Story Link */}
          <li>
            <NavLink
              to="/dashboard"
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-sm ${isActive ? "text-zinc-100 bg-zinc-800" : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"} rounded-md ${isCollapsed ? "justify-center" : ""}`
              }
            >
              <PlusSquare size={16} />
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span
                    variants={textVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="whitespace-nowrap"
                  >
                    Create Story
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          </li>
          {/* Continue Link */}
          <li>
            <NavLink
              to="/dashboard/continue"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-sm ${isActive ? "text-zinc-100 bg-zinc-800" : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"} rounded-md ${isCollapsed ? "justify-center" : ""}`
              }
            >
              <History size={16} />
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span
                    variants={textVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="whitespace-nowrap"
                  >
                    Continue
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          </li>
          {/* Library Link */}
          <li>
            <NavLink
              to="/dashboard/library"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-sm ${isActive ? "text-zinc-100 bg-zinc-800" : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"} rounded-md ${isCollapsed ? "justify-center" : ""}`
              }
            >
              <Library size={16} />
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span
                    variants={textVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="whitespace-nowrap"
                  >
                    Library
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          </li>
        </ul>
        <div className="mt-auto mb-2 space-y-2">
          {user && (
            <NavLink
              to="/dashboard/userstats"
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-sm ${isActive ? "text-zinc-100 bg-zinc-800" : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"} rounded-md ${isCollapsed ? "justify-center" : ""}`
              }
            >
              <img
                src={user.user_metadata.avatar_url}
                alt="avatar"
                className="w-6 h-6 rounded-full border border-emerald-500 object-cover flex-shrink-0"
              />
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span
                    variants={textVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="font-medium whitespace-nowrap"
                  >
                    {user.user_metadata.full_name}
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          )}
          <button
            onClick={handleSignOut}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded-md ${isCollapsed ? "justify-center" : ""}`}
          >
            <LogOut size={16} />
            <AnimatePresence>
              {!isCollapsed && (
                <motion.span
                  variants={textVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  className="whitespace-nowrap"
                >
                  Logout
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </nav>

      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-1/2 transform -translate-y-1/2 w-6 h-6 bg-zinc-800 border border-zinc-700 rounded-full flex items-center justify-center text-zinc-400 hover:text-zinc-100 hover:bg-zinc-700 transition-colors z-10"
      >
        {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>
    </div>
  );
};
