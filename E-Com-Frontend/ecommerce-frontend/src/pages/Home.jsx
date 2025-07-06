import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";
const GITHUB_IMAGE_BASE =
  "https://raw.githubusercontent.com/joydepdhar/E-Com/master/E-Com/media/product_images/";

function Home() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${BACKEND_URL}/api/store/products/`)
      .then((res) => {
        setProducts(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching products:", err);
        setLoading(false);
      });

    axios
      .get(`${BACKEND_URL}/api/store/categories/`)
      .then((res) => setCategories(res.data))
      .catch((err) => console.error("Error fetching categories:", err));
  }, []);

  // Fixed image URL logic:
  const getImageUrl = (imagePath) => {
    if (!imagePath) return "/fallback.png";
    if (imagePath.startsWith("http://") || imagePath.startsWith("https://")) {
      return imagePath;
    }
    const fileName = imagePath.split("/").pop();
    return `${GITHUB_IMAGE_BASE}${fileName}`;
  };

  const handleAddToCart = (product) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    axios
      .post(
        `${BACKEND_URL}/api/store/cart/`,
        { product_id: product.id, quantity: 1 },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      .then(() => {
        alert(`✅ "${product.name}" added to cart`);
      })
      .catch((err) => {
        console.error("Failed to add to cart:", err);
        alert("Something went wrong. Please try again.");
      });
  };

  const filteredProducts =
    selectedCategory === "All"
      ? products
      : products.filter((p) => p.category?.name === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0f172a] via-[#1e293b] to-[#1e1b4b] text-[#f1f5f9]">
      {/* Hero Section */}
      <section className="text-center py-20 px-4 shadow-inner bg-[#0f172a]">
        <h1 className="text-4xl sm:text-5xl font-bold mb-2 text-white">
          Welcome to
        </h1>
        <h1
          className="text-4xl sm:text-5xl font-extrabold mb-6 bg-clip-text text-transparent"
          style={{
            backgroundImage: "linear-gradient(to right, #7b2cbf, #38bdf8, #f1f5f9)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Aura<span style={{ color: "#f1f5f9" }}>Arcade</span>
        </h1>
        <p className="text-md sm:text-lg mb-6 max-w-xl mx-auto font-medium text-[#f1f5f9cc]">
          Dive into a vibrant shopping experience where fun meets fashion.
        </p>
        <Link to="/products">
          <button className="px-8 py-3 bg-[#f1f5f9] text-[#0f172a] font-bold rounded-full shadow-lg hover:bg-[#7b2cbf] hover:text-white transition transform hover:scale-105">
            🛍️ Shop Now
          </button>
        </Link>
      </section>

      {/* Categories Section */}
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

      {/* Products Section */}
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
                    onClick={() => handleAddToCart(product)}
                    className="bg-[#7b2cbf] text-white font-semibold py-2 rounded hover:bg-[#6d28d9] transition"
                  >
                    Add to Cart
                  </button>
                  <Link
                    to={`/products/${product.id}`}
                    className="text-sm text-[#7b2cbf] mt-2 hover:underline"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Highlights Section */}
      <section className="bg-[#1e1b4b] py-20 px-6 text-white">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-10 text-center">
          <div className="bg-[#0f172a] p-6 rounded-xl shadow hover:shadow-2xl transition">
            <h4 className="text-lg font-bold mb-2 text-[#38bdf8]">🎮 Arcade Experience</h4>
            <p className="text-[#f1f5f9cc]">
              Turn your shopping into a playful adventure full of surprises.
            </p>
          </div>
          <div className="bg-[#0f172a] p-6 rounded-xl shadow hover:shadow-2xl transition">
            <h4 className="text-lg font-bold mb-2 text-[#38bdf8]">⚡ Lightning Delivery</h4>
            <p className="text-[#f1f5f9cc]">We race to your door with express shipping on every order.</p>
          </div>
          <div className="bg-[#0f172a] p-6 rounded-xl shadow hover:shadow-2xl transition">
            <h4 className="text-lg font-bold mb-2 text-[#38bdf8]">💬 Always-On Support</h4>
            <p className="text-[#f1f5f9cc]">
              Friendly customer service, anytime you need it — day or night.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
