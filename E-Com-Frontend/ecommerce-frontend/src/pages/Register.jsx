import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Register() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    address: "",
    phone: "",
    profile_picture: null,
  });

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === "profile_picture") {
      setFormData((prev) => ({ ...prev, profile_picture: files[0] }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    const payload = new FormData();
    payload.append("username", formData.username);
    payload.append("email", formData.email);
    payload.append("password", formData.password);
    payload.append("password2", formData.confirmPassword); // match your backend serializer
    payload.append("address", formData.address);
    payload.append("phone", formData.phone);
    if (formData.profile_picture) {
      payload.append("profile_picture", formData.profile_picture);
    }

    try {
      setLoading(true);

      await axios.post(`${BACKEND_URL}/api/user_app/register/`, payload);
      setLoading(false);
      navigate("/login");
    } catch (err) {
      setLoading(false);

      if (!err.response) {
        setError("Network error. Please check your backend and internet connection.");
        return;
      }

      const errors = err.response.data || {};
      const errorMsg =
        errors.username?.[0] ||
        errors.email?.[0] ||
        errors.password?.[0] ||
        errors.password2?.[0] ||
        errors.non_field_errors?.[0] ||
        errors.detail ||
        "Registration failed. Please check all fields.";

      setError(errorMsg);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] to-[#1e293b] text-white flex items-center justify-center px-4">
      <form
        onSubmit={handleRegister}
        className="bg-[#1e293b] border border-[#7b2cbf] p-10 rounded-2xl shadow-2xl w-full max-w-lg space-y-5"
      >
        <h2 className="text-3xl font-bold text-center text-[#38bdf8]">Join AuraArcade</h2>
        <p className="text-center text-gray-400 text-sm mb-4">
          Create your account to start shopping!
        </p>

        {error && <p className="text-red-500 text-sm text-center">{error}</p>}

        <div className="grid grid-cols-1 gap-4">
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-[#0f172a] border border-[#38bdf8] placeholder-gray-400 text-white focus:ring-2 focus:ring-[#7b2cbf] outline-none"
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-[#0f172a] border border-[#38bdf8] placeholder-gray-400 text-white focus:ring-2 focus:ring-[#7b2cbf] outline-none"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-[#0f172a] border border-[#38bdf8] placeholder-gray-400 text-white focus:ring-2 focus:ring-[#7b2cbf] outline-none"
            required
          />
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-[#0f172a] border border-[#38bdf8] placeholder-gray-400 text-white focus:ring-2 focus:ring-[#7b2cbf] outline-none"
            required
          />
          <input
            type="text"
            name="address"
            placeholder="Address"
            value={formData.address}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-[#0f172a] border border-[#38bdf8] placeholder-gray-400 text-white focus:ring-2 focus:ring-[#7b2cbf] outline-none"
          />
          <input
            type="tel"
            name="phone"
            placeholder="Phone"
            value={formData.phone}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-[#0f172a] border border-[#38bdf8] placeholder-gray-400 text-white focus:ring-2 focus:ring-[#7b2cbf] outline-none"
          />
          <input
            type="file"
            name="profile_picture"
            accept="image/*"
            onChange={handleChange}
            className="w-full text-sm text-gray-300"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full mt-6 py-3 text-[#0f172a] font-semibold text-lg rounded-lg transition-all duration-200 ${
            loading ? "bg-gray-400 cursor-not-allowed" : "bg-[#38bdf8] hover:bg-[#7b2cbf] hover:text-white"
          }`}
        >
          {loading ? "Registering..." : "Register"}
        </button>
      </form>
    </div>
  );
}

export default Register;
