// AuthContext.jsx
import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check localStorage for tokens and user info on mount
    const accessToken = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");
    if (accessToken && username) {
      setUser({ username });
    }
  }, []);

  const login = (username, accessToken, refreshToken) => {
    // Save tokens and username in localStorage
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    localStorage.setItem("username", username);
    setUser({ username });
  };

  const logout = () => {
    // Remove tokens and username from localStorage
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("username");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
