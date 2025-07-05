import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com/api/store";
const GITHUB_IMAGE_BASE =
  "https://raw.githubusercontent.com/joydepdhar/E-Com/master/E-Com/media/product_images/";

function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();

  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }

    axios
      .get(`${BACKEND_URL}/cart/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => {
        const data = res.data;
        // Your API returns cart object with items array
        if (data && Array.isArray(data.items)) {
          setCartItems(data.items);
        } else if (Array.isArray(data)) {
          setCartItems(data);
        } else {
          setCartItems([]);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching cart:", err);
        setErrorMsg("Failed to load cart. Please try again.");
        setCartItems([]);
        setLoading(false);
      });
  }, [navigate, accessToken]);

  const getImageUrl = (imagePath) => {
    if (!imagePath) return "/fallback.png";
    const fileName = imagePath.split("/").pop();
    return `${GITHUB_IMAGE_BASE}${fileName}`;
  };

  const getTotal = () =>
    cartItems.reduce(
      (acc, item) => acc + item.product.price * item.quantity,
      0
    );

  const handleRemoveItem = async (itemId) => {
    if (!window.confirm("Remove this item from cart?")) return;

    try {
      await axios.delete(`${BACKEND_URL}/cart/remove/${itemId}/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setCartItems((prev) => prev.filter((item) => item.id !== itemId));
    } catch (error) {
      console.error("Failed to remove item:", error);
      alert("Could not remove item. Please try again.");
    }
  };

  const handleCheckout = () => {
    alert("Checkout is not implemented yet.");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center bg-[#0f172a] text-[#f1f5f9]">
        <p className="animate-pulse text-[#7b2cbf]">Loading your cart...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-[#38bdf8] mb-8">
          🛒 Your Shopping Cart
        </h1>

        {errorMsg && (
          <p className="text-red-500 text-center mb-4">{errorMsg}</p>
        )}

        {cartItems.length === 0 ? (
          <div className="text-center text-gray-300">
            <p>Your cart is empty.</p>
            <Link to="/shop" className="text-[#38bdf8] hover:underline">
              Continue shopping
            </Link>
          </div>
        ) : (
          <>
            <div className="space-y-6">
              {cartItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center bg-[#1e293b] rounded-xl shadow p-4 gap-4"
                >
                  <img
                    src={getImageUrl(item.product.image)}
                    alt={item.product.name}
                    className="w-24 h-24 object-contain bg-[#e2e8f0] p-2 rounded"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "/fallback.png";
                    }}
                  />
                  <div className="flex-grow">
                    <h3 className="text-lg font-semibold">{item.product.name}</h3>
                    <p className="text-sm text-gray-400">
                      Quantity: {item.quantity}
                    </p>
                    <p className="text-sm text-gray-400">
                      Price: ${item.product.price.toFixed(2)}
                    </p>
                  </div>
                  <div className="text-right font-bold text-[#facc15]">
                    ${(item.product.price * item.quantity).toFixed(2)}
                  </div>
                  <button
                    onClick={() => handleRemoveItem(item.id)}
                    className="ml-4 text-red-500 hover:text-red-700 font-semibold"
                    title="Remove item"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-8 text-right">
              <p className="text-xl font-bold mb-4">
                Total:{" "}
                <span className="text-[#facc15]">${getTotal().toFixed(2)}</span>
              </p>
              <button
                onClick={handleCheckout}
                className="bg-[#7b2cbf] text-white px-6 py-2 rounded hover:bg-[#6d28d9] transition"
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
