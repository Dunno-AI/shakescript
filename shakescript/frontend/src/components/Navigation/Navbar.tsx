import React, { useState } from "react";
import { motion } from "framer-motion";
import { Menu, X, LogIn, LogOut } from "lucide-react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useSmoothScroll } from "../../lib/useSmoothScroll";
import { useAuth } from "../../contexts/AuthContext";
import { supabase } from "../../lib/supabaseClient";

export const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { session, signOut } = useAuth();
  const smoothScroll = useSmoothScroll();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleSignOut = async () => {
    await signOut(navigate);
  };

  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    });

    if (error) console.error('Login error:', error.message);
  };

  const navItems = [
    { name: "Home", href: "/" },
    { name: "About", href: "/#start-building" },
    { name: "Statistics", href: "/stats" }
  ];

  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 bg-black/50 backdrop-blur-lg border border-[#2a2a2a]"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link to="/" className="flex items-center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21.3333 4L14.3333 11L21.3333 18H14.3333L7.33334 11L14.3333 4H21.3333Z" fill="#3ECF8E" />
                  <path
                    d="M7.33334 4L14.3333 11L7.33334 18H14.3333L21.3333 11L14.3333 4H7.33334Z"
                    fill="#3ECF8E"
                    fillOpacity="0.4"
                  />
                </svg>
                <span className="ml-2 text-white text-xl font-bold">ShakeScript</span>
              </Link>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {navItems.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-300 hover:text-white px-5 py-2 rounded-md text-m font-medium"
                    onClick={async e => {
                      if (item.name === "About") {
                        e.preventDefault();
                        if (location.pathname !== "/") {
                          navigate("/");
                          setTimeout(() => smoothScroll("start-building"), 50);
                        } else {
                          smoothScroll("start-building");
                        }
                      } else if (item.name === "Home") {
                        e.preventDefault();
                        if (location.pathname !== "/") {
                          navigate("/");
                          setTimeout(() => smoothScroll(), 50);
                        } else {
                          smoothScroll();
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
            <div className="ml-4 flex items-center md:ml-6 gap-2">
              {session ? (
                <>
                  <Link
                    to="/dashboard"
                    className="px-4 py-2 rounded-md text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-700"
                  >
                    Start your project
                  </Link>
                  <button
                    onClick={handleSignOut}
                    className="px-4 py-2 rounded-md text-sm font-medium bg-zinc-700 text-white hover:bg-zinc-800 flex items-center gap-2"
                    style={{ marginLeft: '0.5rem' }}
                  >
                    <LogOut size={16} />
                    Logout
                  </button>
                </>
              ) : (
                <button
                  onClick={handleLogin}
                  className="px-4 py-2 rounded-md text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-700 flex items-center gap-2"
                >
                  <LogIn size={16} />
                  Login
                </button>
              )}
            </div>
          </div>
          <div className="-mr-2 flex md:hidden">
            <button
              onClick={toggleMenu}
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none"
              aria-controls="mobile-menu"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {isMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className={`${isMenuOpen ? "block" : "hidden"} md:hidden`} id="mobile-menu">
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
              onClick={async e => {
                if (item.name === "About") {
                  e.preventDefault();
                  if (location.pathname !== "/") {
                    navigate("/");
                    setTimeout(() => smoothScroll("start-building"), 50);
                  } else {
                    smoothScroll("start-building");
                  }
                } else if (item.name === "Home") {
                  e.preventDefault();
                  if (location.pathname !== "/") {
                    navigate("/");
                    setTimeout(() => smoothScroll(), 50);
                  } else {
                    smoothScroll();
                  }
                }
              }}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="pt-4 pb-3 border-t border-gray-700">
          <div className="flex items-center px-5">
            {session ? (
              <Link
                to="/dashboard"
                className="ml-4 block px-3 py-2 rounded-md text-base font-medium bg-emerald-600 text-white hover:bg-emerald-700"
              >
                Start your project
              </Link>
            ) : (
              <button
                onClick={handleLogin}
                className="ml-4 block px-3 py-2 rounded-md text-base font-medium bg-emerald-600 text-white hover:bg-emerald-700"
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};