import React, { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Menu,
  X,
  Home,
  ShoppingBag,
  ShoppingCart,
  LogIn,
  UserPlus,
  LogOut,
  User,
} from "lucide-react";
import { AuthContext } from "../pages/AuthContext"; // Adjust path as needed

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const toggleMenu = () => setIsOpen(!isOpen);

  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);

  const mainNav = [
    { label: "Home", path: "/", icon: <Home className="w-4 h-4 mr-1" /> },
    { label: "Shop", path: "/shop", icon: <ShoppingBag className="w-4 h-4 mr-1" /> },
    { label: "Cart", path: "/cart", icon: <ShoppingCart className="w-4 h-4 mr-1" /> },
  ];

  const authNav = user
    ? [
        {
          label: `Hello, ${user.username}`,
          path: "/profile",
          icon: <User className="w-4 h-4 mr-1" />,
          isUserLabel: true,
        },
        {
          label: "Profile",
          path: "/profile",
          icon: <User className="w-4 h-4 mr-1" />,
        },
        {
          label: "Logout",
          path: "/",
          icon: <LogOut className="w-4 h-4 mr-1" />,
          onClick: () => {
            logout();
            navigate("/");
            setIsOpen(false);
          },
        },
      ]
    : [
        {
          label: "Login",
          path: "/login",
          icon: <LogIn className="w-4 h-4 mr-1" />,
        },
        {
          label: "Register",
          path: "/register",
          icon: <UserPlus className="w-4 h-4 mr-1" />,
        },
      ];

  return (
    <header className="bg-[#0f172a] shadow-lg sticky top-0 z-50 border-b border-[#7b2cbf]">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        {/* Left: Logo */}
        <div className="flex-shrink-0">
          <Link
            to="/"
            className="text-3xl font-extrabold tracking-tight"
            style={{
              background:
                "linear-gradient(90deg, #7b2cbf 0%, #38bdf8 50%, #f1f5f9 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Aura<span style={{ color: "#f1f5f9" }}>Arcade</span>
          </Link>
        </div>

        {/* Center: Main Nav (Hidden on small screens) */}
        <nav className="hidden md:flex space-x-6">
          {mainNav.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="flex items-center font-medium transition duration-300"
              style={{ color: "#38bdf8" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#7b2cbf")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#38bdf8")}
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Right: Auth Links + Mobile Menu */}
        <div className="flex items-center space-x-4">
          {/* Auth Links (Hidden on small screens) with slash */}
          <div className="hidden md:flex items-center space-x-2 font-medium">
            {authNav.map((item, index) => (
              <React.Fragment key={item.path + index}>
                {item.isUserLabel ? (
                  <span
                    className="flex items-center text-[#38bdf8]"
                    style={{ cursor: "default" }}
                  >
                    {item.icon}
                    {item.label}
                  </span>
                ) : (
                  <Link
                    to={item.path}
                    onClick={item.onClick}
                    className="flex items-center transition duration-300"
                    style={{ color: "#38bdf8" }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = "#7b2cbf")}
                    onMouseLeave={(e) => (e.currentTarget.style.color = "#38bdf8")}
                  >
                    {item.icon}
                    {item.label}
                  </Link>
                )}
                {/* Add slash between links except after last */}
                {index === 0 && authNav.length > 1 && !item.isUserLabel && (
                  <span className="text-[#f1f5f9] select-none mx-1">/</span>
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden text-[#38bdf8]">
            <button
              onClick={toggleMenu}
              aria-label="Toggle Menu"
              className="focus:outline-none"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Dropdown Menu */}
      {isOpen && (
        <div className="md:hidden bg-[#0f172a] px-4 pb-4 space-y-2 border-t border-[#7b2cbf]">
          {[...mainNav, ...authNav].map((item, index) => (
            <Link
              key={item.path + index}
              to={item.path}
              onClick={() => {
                setIsOpen(false);
                if (item.onClick) item.onClick();
              }}
              className="flex items-center font-medium transition duration-300"
              style={{ color: "#38bdf8" }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#7b2cbf")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#38bdf8")}
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}

export default Navbar;
