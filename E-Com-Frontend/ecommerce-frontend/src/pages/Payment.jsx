import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

import { BACKEND_URL } from "../config";

function Payment() {
  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");
  const orderId = localStorage.getItem("order_id");
  const totalPrice = localStorage.getItem("total_price");

  const [paymentMethod, setPaymentMethod] = useState("Cash on Delivery");
  const [paymentId, setPaymentId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!accessToken || !orderId) {
      // If user not authenticated or no order info, redirect to cart
      navigate("/cart");
    }
  }, [accessToken, orderId, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const isCod = paymentMethod === "Cash on Delivery" || paymentMethod === "COD";
    const payload = { payment_method: paymentMethod };

    if (!isCod) {
      if (!paymentId.trim()) {
        setError("Payment reference is required for gateway payments.");
        setLoading(false);
        return;
      }
      payload.payment_id = paymentId.trim();
    }

    try {
      await axios.post(
        `${BACKEND_URL}/api/store/orders/${orderId}/payment/`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        }
      );

      alert("Payment submitted successfully! You can now review your products.");
      setLoading(false);

      // Redirect to review page after payment success
      navigate("/review");
    } catch (err) {
      console.error("Payment failed:", err);
      setError(
        err.response?.data?.message ||
          err.response?.data?.errors?.payment_id?.[0] ||
          err.response?.data?.errors?.payment_method?.[0] ||
          "Payment failed. Please try again or contact support."
      );
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white py-12 px-4 flex justify-center items-center">
      <div className="max-w-md w-full bg-gray-800 p-8 rounded-xl shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-center text-sky-400">
          Payment for Order #{orderId}
        </h2>

        <p className="mb-4 text-yellow-400 font-semibold text-lg">
          Total Amount: ${parseFloat(totalPrice).toFixed(2)}
        </p>

        {error && (
          <p className="mb-4 text-red-500 font-semibold text-center">{error}</p>
        )}

        <form onSubmit={handleSubmit}>
          <label className="block mb-2" htmlFor="paymentMethod">
            Payment Method
          </label>
          <select
            id="paymentMethod"
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
            className="w-full mb-6 p-2 rounded bg-gray-700 text-white"
          >
            <option value="Cash on Delivery">Cash on Delivery</option>
            <option value="COD">Cash on Delivery (Explicit)</option>
            <option value="TestGateway">TestGateway</option>
          </select>

          {!["Cash on Delivery", "COD"].includes(paymentMethod) && (
            <div className="mb-6">
              <label className="block mb-2" htmlFor="paymentId">
                Payment Reference
              </label>
              <input
                id="paymentId"
                type="text"
                value={paymentId}
                onChange={(e) => setPaymentId(e.target.value)}
                className="w-full p-2 rounded bg-gray-700 text-white"
                placeholder="Enter payment reference"
                required
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-700 hover:bg-purple-800 py-3 rounded font-bold text-white transition"
          >
            {loading ? "Processing..." : "Make Payment"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Payment;
