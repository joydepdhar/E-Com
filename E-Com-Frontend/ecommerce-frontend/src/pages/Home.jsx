import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

// Your backend URL here
const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

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
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-500 text-white">
      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center text-center px-6 py-20 max-w-7xl mx-auto">
        <h1 className="text-5xl md:text-7xl font-extrabold mb-4 animate-pulse drop-shadow-lg">
          Welcome to Joydep's E-Commerce
        </h1>
        <p className="text-xl md:text-2xl max-w-xl mb-8 drop-shadow-md">
          Discover the latest products, handpicked just for you.
        </p>
        <Link to="/products">
          <button className="px-8 py-3 bg-white text-indigo-700 font-bold rounded-full shadow-lg hover:bg-indigo-100 transition">
            Shop Now
          </button>
        </Link>
      </section>

      {/* Product Showcase */}
      <section className="bg-white text-gray-900 rounded-t-3xl py-12 px-6 max-w-7xl mx-auto shadow-lg -mt-20 relative z-10">
        <h2 className="text-3xl font-bold mb-8 text-center">Featured Products</h2>
        {loading ? (
          <p className="text-center text-gray-700">Loading products...</p>
        ) : products.length === 0 ? (
          <p className="text-center text-gray-700">No products found.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
            {products.map((product) => (
              <div
                key={product.id}
                className="border rounded-lg shadow-md p-4 hover:shadow-xl transition cursor-pointer"
              >
                <img
                  src={BACKEND_URL + product.image}
                  alt={product.name}
                  className="w-full h-48 object-contain mb-4"
                />
                <h3 className="text-xl font-semibold mb-2">{product.name}</h3>
                <p className="text-gray-700 mb-2">{product.description}</p>
                <p className="font-bold text-lg mb-2">${product.price}</p>
                <Link
                  to={`/products/${product.id}`}
                  className="text-indigo-600 hover:underline"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Feature Highlights */}
      <section className="max-w-7xl mx-auto px-6 py-16 flex flex-col md:flex-row justify-around text-white">
        <div className="flex flex-col items-center mb-10 md:mb-0">
          <svg
            className="w-16 h-16 mb-4 text-white"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 12h18M3 6h18M3 18h18" />
          </svg>
          <h4 className="text-xl font-semibold mb-2">Wide Selection</h4>
          <p className="max-w-xs text-center text-indigo-200">
            Shop from a diverse range of categories.
          </p>
        </div>
        <div className="flex flex-col items-center mb-10 md:mb-0">
          <svg
            className="w-16 h-16 mb-4 text-white"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
          <h4 className="text-xl font-semibold mb-2">Fast Delivery</h4>
          <p className="max-w-xs text-center text-indigo-200">
            Quick and reliable shipping on all orders.
          </p>
        </div>
        <div className="flex flex-col items-center">
          <svg
            className="w-16 h-16 mb-4 text-white"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M20 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M4 21v-2a4 4 0 0 1 3-3.87" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <h4 className="text-xl font-semibold mb-2">24/7 Support</h4>
          <p className="max-w-xs text-center text-indigo-200">
            We're here to help anytime you need us.
          </p>
        </div>
      </section>
    </div>
  );
}

export default Home;
