import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

  const setAccessToken = (token) => {
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
  };

  const setRefreshToken = (token) => {
    if (token) {
      localStorage.setItem("refresh_token", token);
    } else {
      localStorage.removeItem("refresh_token");
    }
  };

  const logout = () => {
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem("username");
    setUser(null);
  };

  const refreshAccessToken = async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      return null;
    }

    try {
      const response = await axios.post(`${BACKEND_URL}/api/user_app/token/refresh/`, {
        refresh: refreshToken,
      });
      const { access } = response.data;
      setAccessToken(access);
      return access;
    } catch (error) {
      console.error("Token refresh failed:", error);
      logout();
      return null;
    }
  };

  const fetchUserProfile = async (accessToken, retry = true) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/user_app/profile/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      return response.data;
    } catch (error) {
      if (retry && error.response?.status === 401) {
        const refreshedAccess = await refreshAccessToken();
        if (refreshedAccess) {
          return fetchUserProfile(refreshedAccess, false);
        }
      }
      console.error("Failed to fetch profile:", error);
      return null;
    }
  };

  useEffect(() => {
    axios.defaults.baseURL = BACKEND_URL;

    const requestInterceptor = axios.interceptors.request.use((config) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (
          error.response?.status === 401 &&
          originalRequest &&
          !originalRequest._retry &&
          localStorage.getItem("refresh_token")
        ) {
          originalRequest._retry = true;
          const newAccessToken = await refreshAccessToken();
          if (newAccessToken) {
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return axios(originalRequest);
          }
        }
        return Promise.reject(error);
      }
    );

    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
      fetchUserProfile(accessToken).then((profile) => {
        if (profile) {
          setUser(profile);
        }
        setLoading(false);
      });
    } else {
      setLoading(false);
    }

    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, []);

  const login = async (usernameOrEmail, accessToken, refreshToken) => {
    setAccessToken(accessToken);
    setRefreshToken(refreshToken);

    const profile = await fetchUserProfile(accessToken);
    const finalUsername = profile?.username || usernameOrEmail;
    localStorage.setItem("username", finalUsername);

    if (profile) {
      setUser(profile);
      return profile;
    }

    const fallbackUser = { username: finalUsername };
    setUser(fallbackUser);
    return fallbackUser;
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
