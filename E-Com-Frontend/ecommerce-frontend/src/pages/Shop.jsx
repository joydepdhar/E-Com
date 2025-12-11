import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com/api/store";

function Shop() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${BACKEND_URL}/products/`)
      .then((res) => {
        setProducts(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching products:", err);
        setLoading(false);
      });

    axios
      .get(`${BACKEND_URL}/categories/`)
      .then((res) => setCategories(res.data))
      .catch((err) => console.error("Error fetching categories:", err));
  }, []);

  const getImageUrl = (imagePath) => {
    return imagePath || "/fallback.png";
  };

  const filteredProducts =
    selectedCategory === "All"
      ? products
      : products.filter((p) => p.category?.name === selectedCategory);

  const handleAddToCart = async (productId, productName) => {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      navigate("/login");
      return;
    }

    console.log("Adding to cart productId:", productId); // Debug

    try {
      await axios.post(
        `${BACKEND_URL}/cart/`,
        {
          product_id: productId,
          quantity: 1,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      alert(`"${productName}" added to cart!`);
    } catch (error) {
      console.error("Error adding to cart:", error.response || error);
      if (error.response && error.response.status === 401) {
        // Unauthorized, token might be invalid/expired
        alert("Session expired. Please login again.");
        localStorage.removeItem("access_token");
        navigate("/login");
      } else if (error.response && error.response.data.error) {
        alert(`Failed to add product: ${error.response.data.error}`);
      } else {
        alert("Failed to add product to cart. Try again.");
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0f172a] via-[#1e293b] to-[#1e1b4b] text-[#f1f5f9]">
      <section className="py-12 px-4 max-w-7xl mx-auto">
        <h2 className="text-3xl sm:text-4xl font-extrabold mb-6 text-center text-[#38bdf8]">
          🗂 Categories
        </h2>
        <div className="flex flex-wrap justify-center gap-3 mb-6">
          <button
            onClick={() => setSelectedCategory("All")}
            className={`px-4 py-2 rounded-full text-sm font-semibold border transition-all shadow ${
              selectedCategory === "All"
                ? "bg-[#facc15] text-[#1e1b4b]"
                : "bg-white text-[#7b2cbf] border-[#7b2cbf] hover:bg-[#facc15] hover:text-[#1e1b4b]"
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.name)}
              className={`px-4 py-2 rounded-full text-sm font-semibold border transition-all shadow ${
                selectedCategory === cat.name
                  ? "bg-[#facc15] text-[#1e1b4b]"
                  : "bg-white text-[#7b2cbf] border-[#7b2cbf] hover:bg-[#facc15] hover:text-[#1e1b4b]"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </section>

      <section className="py-16 px-4 max-w-7xl mx-auto">
        <h2 className="text-3xl sm:text-4xl font-extrabold mb-8 text-center text-[#38bdf8]">
          🌟 Featured Products
        </h2>
        {loading ? (
          <p className="text-center text-[#7b2cbf] animate-pulse">Loading...</p>
        ) : filteredProducts.length === 0 ? (
          <p className="text-center text-gray-400">No products found.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className="bg-[#f1f5f9] rounded-2xl shadow-lg hover:shadow-2xl transition duration-300 overflow-hidden flex flex-col group"
              >
                <img
                  src={getImageUrl(product.image)}
                  alt={product.name}
                  className="w-full h-56 object-contain bg-[#e2e8f0] p-6 group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "/fallback.png";
                  }}
                />
                <div className="p-5 flex-grow flex flex-col text-[#0f172a]">
                  <h3 className="text-xl font-bold mb-1 truncate">{product.name}</h3>
                  <p className="text-sm mb-3 text-gray-600 line-clamp-2 flex-grow">
                    {product.description}
                  </p>
                  <p className="text-[#7b2cbf] font-bold text-lg mb-3">${product.price}</p>
                  <button
                    onClick={() => handleAddToCart(product.id, product.name)}
                    className="bg-[#7b2cbf] text-white font-semibold py-2 rounded hover:bg-[#6d28d9] transition"
                  >
                    Add to Cart
                  </button>
                  <Link
                    to={`/products/${product.id}`}
                    className="text-sm text-[#7b2cbf] mt-2 hover:underline"
                  >
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Shop;
