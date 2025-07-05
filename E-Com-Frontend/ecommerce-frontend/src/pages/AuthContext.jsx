import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // optional loading state

  const BACKEND_URL = "https://e-com-fgbd.onrender.com";

  // Fetch user profile using token
  const fetchUserProfile = async (accessToken) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/user_app/profile/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      return response.data;
    } catch (error) {
      console.error("Failed to fetch profile:", error);
      return null;
    }
  };

  // Load user from localStorage on first mount
  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
      fetchUserProfile(accessToken).then((profile) => {
        if (profile) setUser(profile);
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  // Login and store user + tokens
  const login = async (username, accessToken, refreshToken) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    localStorage.setItem("username", username); // optional

    const profile = await fetchUserProfile(accessToken);
    if (profile) {
      setUser(profile);
    } else {
      setUser({ username }); // fallback
    }
  };

  // Logout: clear everything
  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("username");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
