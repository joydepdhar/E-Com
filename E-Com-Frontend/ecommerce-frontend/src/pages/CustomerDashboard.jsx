import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { AuthContext } from "./AuthContext";
import { ShoppingCart, CreditCard, Package, Clock } from "lucide-react";

import { BACKEND_URL } from "../config";

function CustomerDashboard() {
  const { user } = useContext(AuthContext);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCustomerDashboard();
  }, []);

  const fetchCustomerDashboard = async () => {
    try {
      const accessToken = localStorage.getItem("access_token");
      if (!accessToken) {
        setError("Missing authentication token.");
        setLoading(false);
        return;
      }

      const response = await axios.get(`${BACKEND_URL}/api/store/customer/dashboard/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      setDashboard(response.data);
    } catch (err) {
      console.error("Failed to load customer dashboard:", err);
      setError(
        err.response?.data?.detail || "Unable to load customer dashboard. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="rounded-3xl bg-gray-900 border border-gray-800 p-8 shadow-xl">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-sky-400">Customer Dashboard</p>
              <h1 className="text-3xl font-bold">Hello, {user?.username || "Customer"}</h1>
              <p className="mt-2 text-gray-400 max-w-2xl">
                Track your orders, payments, and recent activity in one place.
              </p>
            </div>
            <div className="rounded-3xl bg-slate-950 px-5 py-4 border border-gray-700 text-right">
              <p className="text-sm text-gray-400">Member since</p>
              <p className="text-lg font-semibold">{dashboard?.member_since || "N/A"}</p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="rounded-xl bg-gray-900 p-8 text-center">Loading your dashboard...</div>
        ) : error ? (
          <div className="rounded-xl bg-rose-900 p-8 text-center text-rose-100">{error}</div>
        ) : (
          <>
            <div className="grid gap-6 md:grid-cols-4">
              <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-400">Orders</span>
                  <ShoppingCart size={22} className="text-sky-400" />
                </div>
                <p className="text-3xl font-semibold">{dashboard?.total_orders ?? 0}</p>
              </div>

              <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-400">Pending Payment</span>
                  <CreditCard size={22} className="text-emerald-400" />
                </div>
                <p className="text-3xl font-semibold">{dashboard?.pending_payments ?? 0}</p>
              </div>

              <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-400">Cart Items</span>
                  <Package size={22} className="text-indigo-400" />
                </div>
                <p className="text-3xl font-semibold">{dashboard?.cart_items ?? 0}</p>
              </div>

              <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-400">Open Support</span>
                  <Clock size={22} className="text-amber-400" />
                </div>
                <p className="text-3xl font-semibold">{dashboard?.open_tickets ?? 0}</p>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2 bg-gray-800 rounded-xl border border-gray-700 p-6">
                <h2 className="text-xl font-semibold mb-4">Recent Orders</h2>
                {dashboard?.recent_orders?.length ? (
                  <div className="space-y-4">
                    {dashboard.recent_orders.slice(0, 5).map((order, index) => (
                      <div key={order.id || index} className="rounded-xl border border-gray-700 p-4">
                        <div className="flex items-center justify-between gap-4">
                          <p className="font-semibold">Order #{order.id || order.order_number || `#${index + 1}`}</p>
                          <span className="text-sm text-gray-400">{order.status || "Status unknown"}</span>
                        </div>
                        <p className="text-sm text-gray-400 mt-2">Total: {order.total || order.amount || "N/A"}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400">You don’t have any recent orders yet.</p>
                )}
              </div>
              <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                <div className="space-y-3 text-gray-300">
                  <p>- Go to Shop to add new products.</p>
                  <p>- Track your delivery status.</p>
                  <p>- Edit payment and shipping details.</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default CustomerDashboard;
