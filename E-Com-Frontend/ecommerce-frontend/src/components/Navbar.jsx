import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        {/* Logo */}
        <Link to="/" className="text-xl font-bold text-blue-600">
          E-Store
        </Link>

        {/* Navigation Links */}
        <nav className="space-x-6 hidden md:block">
          <Link to="/" className="text-gray-700 hover:text-blue-600 transition">Home</Link>
          <Link to="/shop" className="text-gray-700 hover:text-blue-600 transition">Shop</Link>
          <Link to="/cart" className="text-gray-700 hover:text-blue-600 transition">Cart</Link>
          <Link to="/login" className="text-gray-700 hover:text-blue-600 transition">Login</Link>
        </nav>

        {/* Mobile Menu Placeholder (optional dropdown) */}
        <div className="md:hidden">
          {/* You can add a hamburger menu here later */}
        </div>
      </div>
    </header>
  );
}

export default Navbar;
