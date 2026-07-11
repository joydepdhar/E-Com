import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../pages/AuthContext";

function ProtectedCustomerRoute({ children }) {
  const { user, loading } = useContext(AuthContext);

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

  if (user.is_staff) {
    const isAdmin = user?.is_superuser || user?.role?.toLowerCase?.() === "admin";
    return <Navigate to={isAdmin ? "/admin" : "/staff"} />;
  }

  return children;
}

export default ProtectedCustomerRoute;
