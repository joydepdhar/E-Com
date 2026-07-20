import React from "react";
import { Link } from "react-router-dom";

function ForgotPassword() {
  return (
    <div className="min-h-screen bg-[#0f172a] text-white flex items-center justify-center px-4">
      <div className="bg-[#1e293b] p-10 rounded-3xl shadow-xl w-full max-w-lg">
        <h1 className="text-3xl font-bold mb-4 text-[#38bdf8]">Forgot Password</h1>
        <p className="text-gray-300 mb-6">
          If you lost access to your account, please contact the site administrator or support team to reset your password.
        </p>
        <Link
          to="/login"
          className="inline-block bg-[#38bdf8] text-[#0f172a] font-semibold px-6 py-3 rounded-full hover:bg-[#7b2cbf] transition"
        >
          Return to Login
        </Link>
      </div>
    </div>
  );
}

export default ForgotPassword;
