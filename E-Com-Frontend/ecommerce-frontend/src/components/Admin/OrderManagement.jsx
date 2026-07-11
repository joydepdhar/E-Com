import React, { useState, useEffect } from "react";
import { Eye, CheckCircle, Clock, XCircle, Search } from "lucide-react";
import axios from "axios";

function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [orderStatus, setOrderStatus] = useState("");

  const BACKEND_URL = "http://127.0.0.1:8000";
  const STATUS_OPTIONS = ["pending", "processing", "shipped", "delivered", "cancelled"];

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const accessToken = localStorage.getItem("access_token");
      const response = await axios.get(`${BACKEND_URL}/api/store/admin/orders/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setOrders(response.data);
    } catch (error) {
      console.error("Error fetching orders:", error);
    }
    setLoading(false);
  };

  const filteredOrders = orders.filter(
    (order) =>
      order.order_number?.includes(searchTerm) ||
      order.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.customer_email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewOrder = (order) => {
    setSelectedOrder(order);
    setOrderStatus(order.status);
    setShowModal(true);
  };

  const handleUpdateStatus = async () => {
    if (!selectedOrder) return;

    try {
      const accessToken = localStorage.getItem("access_token");
      await axios.patch(
        `${BACKEND_URL}/api/store/admin/orders/${selectedOrder.id}/`,
        { status: orderStatus },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      fetchOrders();
      setShowModal(false);
      setSelectedOrder(null);
    } catch (error) {
      console.error("Error updating order:", error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "pending":
        return <Clock className="text-yellow-400" size={18} />;
      case "processing":
        return <Clock className="text-blue-400" size={18} />;
      case "shipped":
        return <CheckCircle className="text-blue-400" size={18} />;
      case "delivered":
        return <CheckCircle className="text-green-400" size={18} />;
      case "cancelled":
        return <XCircle className="text-red-400" size={18} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "pending":
        return "bg-yellow-600 text-white";
      case "processing":
        return "bg-blue-600 text-white";
      case "shipped":
        return "bg-blue-600 text-white";
      case "delivered":
        return "bg-green-600 text-white";
      case "cancelled":
        return "bg-red-600 text-white";
      default:
        return "bg-gray-600 text-white";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <h2 className="text-2xl font-bold">Order Management</h2>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-3 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Search by order number, customer name, or email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
        />
      </div>

      {/* Orders Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-700 border-b border-gray-600">
                <th className="px-6 py-3 text-left text-sm font-semibold">Order ID</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Customer</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Items</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Amount</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Date</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-8 text-gray-400">
                    Loading orders...
                  </td>
                </tr>
              ) : filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-8 text-gray-400">
                    No orders found
                  </td>
                </tr>
              ) : (
                filteredOrders.map((order) => (
                  <tr key={order.id} className="border-b border-gray-700 hover:bg-gray-750">
                    <td className="px-6 py-4 font-semibold">{order.order_number}</td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium">{order.customer_name}</p>
                        <p className="text-sm text-gray-400">{order.customer_email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm">{order.items_count || 0} items</td>
                    <td className="px-6 py-4 font-semibold">
                      ${order.total_amount?.toFixed(2) || 0}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(order.status)}
                        <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(order.status)}`}>
                          {order.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {new Date(order.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleViewOrder(order)}
                        className="text-blue-400 hover:text-blue-300 transition flex items-center space-x-1"
                      >
                        <Eye size={18} />
                        <span>View</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Order Details Modal */}
      {showModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg max-w-2xl w-full border border-gray-700 max-h-screen overflow-y-auto">
            <h3 className="text-lg font-bold mb-4">Order Details</h3>

            <div className="space-y-4">
              {/* Order Info */}
              <div className="grid grid-cols-2 gap-4 pb-4 border-b border-gray-700">
                <div>
                  <p className="text-gray-400 text-sm">Order Number</p>
                  <p className="font-semibold">{selectedOrder.order_number}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Order Date</p>
                  <p className="font-semibold">
                    {new Date(selectedOrder.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Customer</p>
                  <p className="font-semibold">{selectedOrder.customer_name}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Email</p>
                  <p className="font-semibold">{selectedOrder.customer_email}</p>
                </div>
              </div>

              {/* Order Items */}
              <div>
                <h4 className="font-semibold mb-3">Items</h4>
                <div className="space-y-2 bg-gray-700 p-4 rounded">
                  {selectedOrder.items?.map((item, idx) => (
                    <div key={idx} className="flex justify-between border-b border-gray-600 pb-2">
                      <span>{item.product_name} x{item.quantity}</span>
                      <span>${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                  )) || <p className="text-gray-400">No items</p>}
                </div>
              </div>

              {/* Order Summary */}
              <div className="bg-gray-700 p-4 rounded space-y-2">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span>${(selectedOrder.total_amount * 0.9).toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tax</span>
                  <span>${(selectedOrder.total_amount * 0.1).toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold text-lg border-t border-gray-600 pt-2">
                  <span>Total</span>
                  <span>${selectedOrder.total_amount?.toFixed(2)}</span>
                </div>
              </div>

              {/* Status Update */}
              <div className="pb-4 border-b border-gray-700">
                <label className="block text-sm font-medium mb-2">Update Status</label>
                <select
                  value={orderStatus}
                  onChange={(e) => setOrderStatus(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                >
                  {STATUS_OPTIONS.map((status) => (
                    <option key={status} value={status}>
                      {status.charAt(0).toUpperCase() + status.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
                >
                  Close
                </button>
                <button
                  onClick={handleUpdateStatus}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition"
                >
                  Update Status
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OrderManagement;
