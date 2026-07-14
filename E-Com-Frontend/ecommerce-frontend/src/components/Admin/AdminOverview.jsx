import React, { useState, useEffect } from "react";
import { TrendingUp, DollarSign, Users, Package, ArrowUp, ArrowDown, ShoppingCart } from "lucide-react";
import axios from "axios";

function AdminOverview({ stats }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardStats, setDashboardStats] = useState({
    totalUsers: 0,
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    monthlyRevenue: 0,
    activeUsers: 0,
    pendingOrders: 0,
  });

  const [recentOrders, setRecentOrders] = useState([]);

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const accessToken = localStorage.getItem("access_token");
      if (!accessToken) {
        setError("Your session has expired. Please log in again.");
        return;
      }

      const response = await axios.get(`${BACKEND_URL}/api/store/admin/dashboard/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
        timeout: 10000,
      });

      const totals = response.data?.totals || {};
      setDashboardStats({
        totalUsers: totals.customers || 0,
        totalProducts: totals.products || 0,
        totalOrders: totals.orders || 0,
        totalRevenue: Number(totals.revenue) || 0,
        monthlyRevenue: 0,
        activeUsers: totals.customers || 0,
        pendingOrders: totals.pending_orders || 0,
      });
      setRecentOrders(response.data?.recent_orders || []);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setError(
        error.code === "ECONNABORTED"
          ? "Dashboard request timed out. Check that the backend is running."
          : error.response?.data?.detail || "Unable to load dashboard data."
      );
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, label, value, change, positive }) => (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm mb-2">{label}</p>
          <p className="text-3xl font-bold">{value}</p>
          <div className="flex items-center mt-2 text-sm">
            {positive ? (
              <ArrowUp size={16} className="text-green-500 mr-1" />
            ) : (
              <ArrowDown size={16} className="text-red-500 mr-1" />
            )}
            <span className={positive ? "text-green-500" : "text-red-500"}>
              {change}%
            </span>
            <span className="text-gray-400 ml-1">vs last month</span>
          </div>
        </div>
        <div className="bg-blue-600 p-4 rounded-lg">
          <Icon size={32} className="text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {loading && (
        <div className="rounded-lg border border-blue-700 bg-blue-950 p-4 text-blue-100">
          Loading dashboard data...
        </div>
      )}
      {error && (
        <div className="rounded-lg border border-red-700 bg-red-950 p-4 text-red-100">
          {error}
        </div>
      )}
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Users}
          label="Total Users"
          value={dashboardStats.totalUsers}
          change="12"
          positive={true}
        />
        <StatCard
          icon={Package}
          label="Total Products"
          value={dashboardStats.totalProducts}
          change="8"
          positive={true}
        />
        <StatCard
          icon={ShoppingCart}
          label="Total Orders"
          value={dashboardStats.totalOrders}
          change="15"
          positive={true}
        />
        <StatCard
          icon={DollarSign}
          label="Total Revenue"
          value={`$${dashboardStats.totalRevenue?.toLocaleString() || 0}`}
          change="20"
          positive={true}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Monthly Revenue</h3>
          <div className="h-64 flex items-end justify-around space-x-2">
            {[65, 59, 80, 81, 56, 55, 70, 85, 72, 88, 95, 100].map((value, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center">
                <div
                  className="w-full bg-blue-600 rounded-t"
                  style={{ height: `${value * 2}px` }}
                ></div>
                <span className="text-xs text-gray-400 mt-2">
                  {["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"][idx]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-gray-700">
              <span className="text-gray-400">Active Users</span>
              <span className="font-semibold">{dashboardStats.activeUsers}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-gray-700">
              <span className="text-gray-400">Pending Orders</span>
              <span className="font-semibold">{dashboardStats.pendingOrders}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-gray-700">
              <span className="text-gray-400">Monthly Revenue</span>
              <span className="font-semibold">${dashboardStats.monthlyRevenue?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between items-center py-3">
              <span className="text-gray-400">Conversion Rate</span>
              <span className="font-semibold">3.24%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminOverview;
