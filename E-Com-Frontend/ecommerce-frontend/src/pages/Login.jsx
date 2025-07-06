import React, { useState, useContext } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../pages/AuthContext";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const { login } = useContext(AuthContext);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const res = await axios.post(`${BACKEND_URL}/api/user_app/login/`, {
        username,
        password,
      });

      console.log("Tokens from backend:", res.data.access, res.data.refresh);

      // Await login to ensure tokens are stored and profile is fetched before redirect
      await login(username, res.data.access, res.data.refresh);

      alert("Login successful!");
      navigate("/shop");
    } catch (err) {
      console.error("Login error:", err.response);
      const detail =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        "Invalid username or password. Please try again.";
      setError(detail);
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
            Username
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
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
          className="w-full bg-[#38bdf8] hover:bg-[#7b2cbf] text-[#0f172a] font-bold py-2 px-4 rounded transition"
        >
          Login
        </button>
      </form>
    </div>
  );
}

export default Login;
