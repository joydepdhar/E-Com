// src/pages/Order.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Order() {
  const [message, setMessage] = useState("");
  const [orderId, setOrderId] = useState(null);
  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");

  const handlePlaceOrder = async () => {
    try {
      const res = await axios.post(`${BACKEND_URL}/api/store/orders/create/`, {}, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      setMessage(res.data.message);
      setOrderId(res.data.order_id);
    } catch (err) {
      console.error("Order placement failed:", err);
      setMessage("Failed to place order");
    }
  };

  useEffect(() => {
    if (!accessToken) navigate("/login");
  }, [accessToken, navigate]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-2xl mb-4 font-bold">📦 Order</h1>
      <button
        onClick={handlePlaceOrder}
        className="bg-purple-700 px-6 py-2 rounded hover:bg-purple-800"
      >
        Place Order
      </button>

      {message && <p className="mt-4">{message}</p>}
      {orderId && (
        <button
          onClick={() => navigate(`/shipping/${orderId}`)}
          className="mt-4 underline text-sky-400"
        >
          Go to Shipping →
        </button>
      )}
    </div>
  );
}

export default Order;
