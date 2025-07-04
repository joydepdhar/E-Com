import React from 'react';

function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-6">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p>&copy; {new Date().getFullYear()} E-Store. All rights reserved.</p>
        <p className="mt-2 text-sm text-gray-400">Made with ❤️ by Joydep Dhar</p>
      </div>
    </footer>
  );
}

export default Footer;
