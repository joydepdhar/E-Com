import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "./AuthContext";
import { Package, ShoppingCart, Users, Truck, AlertTriangle } from "lucide-react";

import { BACKEND_URL } from "../config";

function StaffDashboard() {
  const { user } = useContext(AuthContext);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStaffDashboard();
  }, []);

  const fetchStaffDashboard = async () => {
    try {
      const accessToken = localStorage.getItem("access_token");
      if (!accessToken) {
        setError("Missing authentication token.");
        setLoading(false);
        return;
      }

      const response = await axios.get(`${BACKEND_URL}/api/store/staff/dashboard/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      setDashboard(response.data);
    } catch (err) {
      console.error("Failed to load staff dashboard:", err);
      setError(
        err.response?.data?.detail || "Unable to load staff dashboard. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const metric = (icon, label, value, color) => (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-gray-400 uppercase tracking-wide">{label}</h3>
        <div className={`p-2 rounded ${color}`}>
          {icon}
        </div>
      </div>
      <p className="text-3xl font-semibold">{value}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm text-sky-400 uppercase tracking-[0.3em]">
              Staff Dashboard
            </p>
            <h1 className="text-3xl font-bold">Welcome back, {user?.username || "Team Member"}</h1>
            <p className="mt-2 text-gray-400 max-w-2xl">
              Access your staff metrics, orders, and shipment details in one place.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="rounded-xl bg-gray-900 p-8 text-center">Loading staff data...</div>
        ) : error ? (
          <div className="rounded-xl bg-red-900 p-8 text-center text-red-200">{error}</div>
        ) : (
          <>
            <div className="grid gap-6 md:grid-cols-4">
              {metric(
                <Users size={20} className="text-white" />,
                "Assigned Orders",
                dashboard?.assigned_orders?.length ?? 0,
                "bg-indigo-600"
              )}
              {metric(
                <Truck size={20} className="text-white" />,
                "Pending Shipments",
                dashboard?.pending_shipments ?? 0,
                "bg-emerald-600"
              )}
              {metric(
                <ShoppingCart size={20} className="text-white" />,
                "Completed Orders",
                dashboard?.completed_orders ?? 0,
                "bg-sky-600"
              )}
              {metric(
                <AlertTriangle size={20} className="text-white" />,
                "Urgent Tickets",
                dashboard?.urgent_tickets ?? 0,
                "bg-rose-600"
              )}
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2 bg-gray-800 rounded-xl border border-gray-700 p-6">
                <h2 className="text-xl font-semibold mb-4">Today&apos;s Orders</h2>
                {dashboard?.recent_orders?.length ? (
                  <div className="space-y-4">
                    {dashboard.recent_orders.slice(0, 5).map((order, index) => (
                      <div
                        key={order.id || index}
                        className="rounded-xl border border-gray-700 p-4"
                      >
                        <div className="flex items-center justify-between gap-4">
                          <p className="font-semibold">Order #{order.id || order.order_number || `#${index + 1}`}</p>
                          <span className="text-sm text-gray-400">
                            {order.status || order.order_status || "N/A"}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400 mt-2">
                          {order.customer_name || order.customer || "Customer details unavailable"}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400">No recent orders available yet.</p>
                )}
              </div>

              <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                <h2 className="text-xl font-semibold mb-4">Quick Links</h2>
                <div className="space-y-3 text-gray-300">
                  <p>- Access inventory tasks</p>
                  <p>- Review shipping assignments</p>
                  <p>- Track customer support requests</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default StaffDashboard;
