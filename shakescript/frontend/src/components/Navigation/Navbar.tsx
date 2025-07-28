import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Menu, X, LogIn, LogOut, User } from "lucide-react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useSmoothScroll } from "../../lib/useSmoothScroll";
import { useAuth } from "../../contexts/AuthContext";

export const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { session, profile, signOut } = useAuth();
  const smoothScroll = useSmoothScroll();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  const handleSignOut = async () => await signOut(navigate);

  const navItems = [
    { name: "Home", href: "/" },
    { name: "About", href: "/#start-building" },
    { name: "Statistics", href: "/stats", mobileOnly: false },
    ...(session
      ? [
        { name: "Dashboard", href: "/dashboard" },
        { name: "Library", href: "/dashboard/library" },
      ]
      : []),
  ];

  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 bg-black/50 backdrop-blur-lg border-b border-zinc-800"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link to="/" className="flex items-center">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M21.3333 4L14.3333 11L21.3333 18H14.3333L7.33334 11L14.3333 4H21.3333Z"
                    fill="#3ECF8E"
                  />
                  <path
                    d="M7.33334 4L14.3333 11L7.33334 18H14.3333L21.3333 11L14.3333 4H7.33334Z"
                    fill="#3ECF8E"
                    fillOpacity="0.4"
                  />
                </svg>
                <span className="ml-2 text-white text-xl font-bold">
                  ShakeScript
                </span>
              </Link>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {navItems.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium ${item.name === "Statistics" ? "hidden md:block" : ""}`}
                    onClick={(e) => {
                      if (item.href.includes("/#")) {
                        e.preventDefault();
                        const targetId = item.href.split("/#")[1];
                        if (location.pathname !== "/") {
                          navigate("/");
                          setTimeout(() => smoothScroll(targetId), 100);
                        } else {
                          smoothScroll(targetId);
                        }
                      }
                    }}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6 gap-4">
              {session && profile ? (
                <div className="relative" ref={dropdownRef}>
                  <button onClick={() => setIsDropdownOpen(!isDropdownOpen)}>
                    <img
                      src={
                        profile.avatar_url ||
                        `https://i.pravatar.cc/100?u=${profile.auth_id}`
                      }
                      alt="User Avatar"
                      className="w-9 h-9 rounded-full border-2 border-zinc-700 hover:border-emerald-500 transition-colors"
                    />
                  </button>
                  {isDropdownOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 mt-2 w-48 bg-zinc-900 border border-zinc-800 rounded-md shadow-lg py-1"
                    >
                      <Link
                        to="/dashboard/userstats"
                        className="flex items-center gap-2 w-full text-left px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-white"
                      >
                        <User size={16} /> My Profile
                      </Link>
                      <button
                        onClick={handleSignOut}
                        className="flex items-center gap-2 w-full text-left px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-white"
                      >
                        <LogOut size={16} /> Logout
                      </button>
                    </motion.div>
                  )}
                </div>
              ) : (
                location.pathname !== "/login" && (
                  <button
                    onClick={() => navigate("/login")}
                    className="px-4 py-2 rounded-md text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-700 flex items-center gap-2"
                  >
                    <LogIn size={16} />
                    Login
                  </button>
                )
              )}
            </div>
          </div>
          <div className="-mr-2 flex md:hidden">
            <button
              onClick={toggleMenu}
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none"
            >
              {isMenuOpen ? (
                <X className="block h-6 w-6" />
              ) : (
                <Menu className="block h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {navItems
              .filter((item) => item.name !== "Statistics")
              .map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                  onClick={() => toggleMenu()}
                >
                  {item.name}
                </Link>
              ))}
          </div>
          <div className="pt-4 pb-3 border-t border-gray-700">
            {session ? (
              <div className="px-5">
                <button
                  onClick={() => {
                    handleSignOut();
                    toggleMenu();
                  }}
                  className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700"
                >
                  Logout
                </button>
              </div>
            ) : (
              location.pathname !== "/login" && (
                <div className="px-5">
                  <button
                    onClick={() => {
                      navigate("/login");
                      toggleMenu();
                    }}
                    className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700"
                  >
                    Login
                  </button>
                </div>
              )
            )}
          </div>
        </div>
      )}
    </motion.nav>
  );
};
