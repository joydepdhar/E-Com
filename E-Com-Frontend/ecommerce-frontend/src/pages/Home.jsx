import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Home() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
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

    axios
      .get(`${BACKEND_URL}/api/store/categories/`)
      .then((res) => {
        setCategories(res.data);
      })
      .catch((err) => {
        console.error("Error fetching categories:", err);
      });
  }, []);

  return (
    <div className="min-h-screen bg-white text-gray-800">
      {/* Hero Section */}
      <section className="text-center px-6 py-20 max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold mb-4">Welcome to Joydep's E-Commerce</h1>
        <p className="text-lg mb-6">Explore our latest collections and exclusive deals</p>
        <Link to="/products">
          <button className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 transition">
            Shop Now
          </button>
        </Link>
      </section>

      {/* Category Section */}
      <section className="bg-gray-50 py-6 px-4 max-w-7xl mx-auto rounded-md shadow-sm">
        <h2 className="text-2xl font-semibold mb-4">Browse by Category</h2>
        <div className="flex flex-wrap gap-4">
          {categories.length > 0 ? (
            categories.map((cat) => (
              <span
                key={cat.id}
                className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium"
              >
                {cat.name}
              </span>
            ))
          ) : (
            <p>No categories found.</p>
          )}
        </div>
      </section>

      {/* Product Showcase */}
      <section className="py-10 px-6 max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold mb-6 text-center">Featured Products</h2>
        {loading ? (
          <p className="text-center text-gray-500">Loading products...</p>
        ) : products.length === 0 ? (
          <p className="text-center text-gray-500">No products found.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {products.map((product) => (
              <div
                key={product.id}
                className="border rounded-md shadow-sm hover:shadow-lg p-4 transition"
              >
                <img
                  src={BACKEND_URL + product.image}
                  alt={product.name}
                  className="w-full h-48 object-contain mb-4"
                />
                <h3 className="text-xl font-semibold">{product.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{product.description}</p>
                <p className="font-bold text-lg text-blue-600 mb-2">${product.price}</p>
                <Link
                  to={`/products/${product.id}`}
                  className="text-blue-500 hover:underline text-sm"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Features */}
      <section className="bg-gray-100 py-12 mt-10">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 px-6 text-center">
          <div>
            <h4 className="text-lg font-semibold mb-2">🛍️ Wide Selection</h4>
            <p className="text-gray-600">Find electronics, clothing, accessories and more.</p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-2">🚀 Fast Delivery</h4>
            <p className="text-gray-600">Get your orders delivered quickly and reliably.</p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-2">📞 24/7 Support</h4>
            <p className="text-gray-600">We’re always here to help you with your orders.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
