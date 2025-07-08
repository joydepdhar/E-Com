// src/pages/Shipping.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Shipping() {
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [country, setCountry] = useState("");

  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");
  const orderId = localStorage.getItem("order_id");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!orderId || !accessToken) {
      alert("Missing order or user information.");
      return;
    }

    try {
      await axios.post(
        `${BACKEND_URL}/api/store/orders/${orderId}/shipping/`,
        { address, city, postal_code: postalCode, country },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      alert("Shipping address added successfully.");
      navigate("/payment");
    } catch (err) {
      console.error("Error adding shipping:", err);
      alert("Failed to add shipping address.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white py-12 px-4">
      <div className="max-w-xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-yellow-400 mb-8">
          🚚 Shipping Details
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6 bg-gray-800 p-8 rounded-xl shadow">
          <div>
            <label className="block mb-1 font-semibold">Address</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded bg-gray-700 text-white"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block mb-1 font-semibold">City</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded bg-gray-700 text-white"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block mb-1 font-semibold">Postal Code</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded bg-gray-700 text-white"
              value={postalCode}
              onChange={(e) => setPostalCode(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block mb-1 font-semibold">Country</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded bg-gray-700 text-white"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-purple-700 hover:bg-purple-800 text-white font-bold py-2 rounded transition"
          >
            Continue to Payment
          </button>
        </form>
      </div>
    </div>
  );
}

export default Shipping;
