import React, { useState, useContext } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../pages/AuthContext";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

function Login() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const { login } = useContext(AuthContext);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const payload = {
        username: identifier,
        password,
      };

      const res = await axios.post(`${BACKEND_URL}/api/user_app/login/`, payload);

      const accessToken =
        res.data?.access ||
        res.data?.access_token ||
        res.data?.token?.access ||
        res.data?.tokens?.access;
      const refreshToken =
        res.data?.refresh ||
        res.data?.refresh_token ||
        res.data?.token?.refresh ||
        res.data?.tokens?.refresh;

      if (!accessToken || !refreshToken) {
        console.error("Login response body:", res.data);
        throw new Error("Login response did not include access tokens.");
      }

      const userProfile = await login(identifier, accessToken, refreshToken);

      alert("Login successful!");

      const isAdmin =
        userProfile?.is_superuser ||
        userProfile?.role?.toString()?.toLowerCase() === "admin";
      const isStaff = userProfile?.is_staff && !isAdmin;

      if (isAdmin) {
        navigate("/admin");
      } else if (isStaff) {
        navigate("/staff");
      } else {
        navigate("/customer");
      }
    } catch (err) {
      console.error("Login error:", err);
      const detail =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        err.response?.data?.error ||
        err.message ||
        "Invalid username or password. Please try again.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white flex items-center justify-center px-4">
      <form
        onSubmit={handleLogin}
        className="bg-[#1e293b] p-8 rounded-xl shadow-lg w-full max-w-md"
      >
        <h2 className="text-2xl font-bold mb-6 text-center text-[#38bdf8]">
          Login to AuraArcade
        </h2>

        {error && (
          <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
        )}

        <div className="mb-4">
          <label htmlFor="username" className="block mb-1 text-sm font-medium">
            Username or Email
          </label>
          <input
            type="text"
            id="username"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            className="w-full px-4 py-2 rounded bg-[#0f172a] border border-[#7b2cbf] text-white focus:outline-none focus:ring-2 focus:ring-[#38bdf8]"
            required
          />
        </div>

        <div className="mb-1">
          <label htmlFor="password" className="block mb-1 text-sm font-medium">
            Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 rounded bg-[#0f172a] border border-[#7b2cbf] text-white focus:outline-none focus:ring-2 focus:ring-[#38bdf8]"
            required
          />
        </div>

        <div className="text-right mb-6">
          <Link
            to="/forgot-password"
            className="text-sm text-[#38bdf8] hover:text-[#7b2cbf]"
          >
            Forgot Password?
          </Link>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[#38bdf8] hover:bg-[#7b2cbf] disabled:bg-gray-500 text-[#0f172a] font-bold py-2 px-4 rounded transition"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}

export default Login;
