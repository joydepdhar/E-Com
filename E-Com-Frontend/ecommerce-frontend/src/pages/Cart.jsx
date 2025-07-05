import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }

    axios
      .get(`${BACKEND_URL}/api/store/cart/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      .then((res) => {
        setCart(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching cart:", err);
        setLoading(false);
      });
  }, [navigate, accessToken]);

  const handleRemove = (itemId) => {
    axios
      .delete(`${BACKEND_URL}/api/store/cart/remove/${itemId}/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      .then(() => {
        setCart((prev) => ({
          ...prev,
          items: prev.items.filter((item) => item.id !== itemId),
        }));
      })
      .catch((err) => console.error("Error removing item:", err));
  };

  const getTotal = () =>
    cart?.items?.reduce(
      (acc, item) => acc + parseFloat(item.product.price) * item.quantity,
      0
    ) || 0;

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center bg-gray-900 text-white">
        <p className="animate-pulse">Loading your cart...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-sky-400 mb-8">
          🛒 Your Shopping Cart
        </h1>

        {!cart?.items?.length ? (
          <div className="text-center text-gray-300">
            <p>Your cart is empty.</p>
            <Link to="/shop" className="text-sky-400 hover:underline">
              Continue shopping
            </Link>
          </div>
        ) : (
          <>
            <div className="space-y-6">
              {cart.items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center bg-gray-800 rounded-xl shadow p-4 gap-4"
                >
                  <img
                    src={item.product.image || "/fallback.png"}
                    alt={item.product.name}
                    className="w-24 h-24 object-cover bg-slate-200 p-2 rounded"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "/fallback.png";
                    }}
                  />
                  <div className="flex-grow">
                    <h3 className="text-lg font-semibold">
                      {item.product.name}
                    </h3>
                    <p className="text-sm text-gray-400">
                      Quantity: {item.quantity}
                    </p>
                    <p className="text-sm text-gray-400">
                      Price: ${parseFloat(item.product.price).toFixed(2)}
                    </p>
                  </div>
                  <div className="text-right font-bold text-yellow-400">
                    $
                    {(
                      parseFloat(item.product.price) * item.quantity
                    ).toFixed(2)}
                    <button
                      onClick={() => handleRemove(item.id)}
                      className="ml-4 text-red-500 hover:underline text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 text-right">
              <p className="text-xl font-bold mb-4">
                Total:{" "}
                <span className="text-yellow-400">
                  ${getTotal().toFixed(2)}
                </span>
              </p>
              <button
                onClick={() => alert("Checkout coming soon!")}
                className="bg-purple-700 text-white px-6 py-2 rounded hover:bg-purple-800 transition"
              >
                Proceed to Checkout
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Cart;
