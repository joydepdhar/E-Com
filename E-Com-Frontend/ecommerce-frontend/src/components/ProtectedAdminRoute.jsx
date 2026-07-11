import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../pages/AuthContext";

function ProtectedAdminRoute({ children }) {
  const { user, loading } = useContext(AuthContext);

  // Show loading while user data is being fetched
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="text-white mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  const isAdmin = user?.is_superuser || user?.role?.toString()?.toLowerCase() === "admin";
  if (!isAdmin) {
    if (user.is_staff) {
      return <Navigate to="/staff" />;
    }
    return <Navigate to="/customer" />;
  }

  return children;
}

export default ProtectedAdminRoute;
