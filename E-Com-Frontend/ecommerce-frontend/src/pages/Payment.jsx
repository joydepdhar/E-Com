import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Payment() {
  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");
  const orderId = localStorage.getItem("order_id");
  const totalPrice = localStorage.getItem("total_price");

  const [paymentMethod, setPaymentMethod] = useState("Stripe"); // Default payment method
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

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/store/orders/${orderId}/payment/`,
        {
          payment_method: paymentMethod,
          payment_id: `TXN_${Date.now()}`, // Dummy transaction id
          amount: totalPrice,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      alert("Payment successful! You can now review your products.");
      setLoading(false);

      // Redirect to review page after payment success
      navigate("/review");
    } catch (err) {
      console.error("Payment failed:", err);
      setError(
        err.response?.data?.error ||
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
            <option value="Stripe">Stripe</option>
            <option value="PayPal">PayPal</option>
            <option value="CashOnDelivery">Cash on Delivery</option>
          </select>

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
