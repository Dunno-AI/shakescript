import React, { useState } from "react";
import { motion } from "framer-motion";
import { Menu, X } from "lucide-react";
import { Link } from "react-router-dom";

export const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const navItems = [
    { name: "Home", href: "/" },
    { name: "About", href: "/developers" },
    { name: "Statistics", href: "/stats" },
    { name: "Enterprise", href: "/enterprise" },
    { name: "Blog", href: "/blog" },
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
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6">
              <Link
                to="/dashboard"
                className="ml-4 px-4 py-2 rounded-md text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-700"
              >
                Start your project
              </Link>
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
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="pt-4 pb-3 border-t border-gray-700">
          <div className="flex items-center px-5">
            <Link to="/signin" className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:text-white">
              Sign in
            </Link>
            <Link
              to="/start"
              className="ml-4 block px-3 py-2 rounded-md text-base font-medium bg-emerald-600 text-white hover:bg-emerald-700"
            >
              Start your project
            </Link>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};