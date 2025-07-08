import React, { useEffect, useState } from "react";
import axios from "axios";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Review() {
  const [orders, setOrders] = useState([]);
  const [reviews, setReviews] = useState({});
  const [existingReviews, setExistingReviews] = useState({});
  const accessToken = localStorage.getItem("access_token");

  // Fetch orders on mount
  useEffect(() => {
    if (!accessToken) return;

    axios
      .get(`${BACKEND_URL}/api/store/orders/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => setOrders(res.data))
      .catch((err) => console.error("Failed to fetch orders", err));
  }, [accessToken]);

  // Extract unique purchased products from orders
  const purchasedProducts = Array.from(
    new Set(
      orders
        .flatMap((order) =>
          order.order_items ? order.order_items.map((item) => item.product) : []
        )
        .map((p) => JSON.stringify(p))
    )
  ).map((p) => JSON.parse(p));

  // Fetch existing reviews for each purchased product
  useEffect(() => {
    if (!accessToken || purchasedProducts.length === 0) return;

    purchasedProducts.forEach((product) => {
      axios
        .get(`${BACKEND_URL}/api/store/products/${product.id}/reviews/`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        })
        .then((res) => {
          setExistingReviews((prev) => ({
            ...prev,
            [product.id]: res.data,
          }));
        })
        .catch((err) =>
          console.error(`Failed to fetch reviews for product ${product.id}`, err)
        );
    });
  }, [purchasedProducts, accessToken]);

  // Find user's existing review for a product (assuming backend returns 'user' info with username)
  const getUserReview = (productId) => {
    const productReviews = existingReviews[productId] || [];
    // Ideally you would identify the current user's username or id.
    // For demo, assume backend returns user info and you can get current username from localStorage or token
    // But here we assume current user username is in localStorage:
    const currentUsername = localStorage.getItem("username"); // set this on login ideally

    return productReviews.find((rev) => rev.user?.username === currentUsername);
  };

  // Handle input changes for new or existing review (for update)
  const handleCommentChange = (productId, value) => {
    setReviews((prev) => ({
      ...prev,
      [productId]: {
        ...prev[productId],
        comment: value,
      },
    }));
  };

  const handleRatingChange = (productId, value) => {
    setReviews((prev) => ({
      ...prev,
      [productId]: {
        ...prev[productId],
        rating: value,
      },
    }));
  };

  // Submit new review or update existing review
  const handleSubmit = async (productId) => {
    const reviewData = reviews[productId] || {};
    const rating = reviewData.rating || 5;
    const comment = reviewData.comment || "";

    if (!comment.trim()) {
      alert("Please write a review comment.");
      return;
    }

    const userReview = getUserReview(productId);

    try {
      if (userReview) {
        // Update existing review (PUT or PATCH)
        await axios.put(
          `${BACKEND_URL}/api/store/products/${productId}/reviews/${userReview.id}/`,
          { rating, comment },
          { headers: { Authorization: `Bearer ${accessToken}` } }
        );
        alert("Review updated!");
      } else {
        // Create new review (POST)
        const response = await axios.post(
          `${BACKEND_URL}/api/store/products/${productId}/reviews/`,
          { rating, comment, product_id: productId },
          { headers: { Authorization: `Bearer ${accessToken}` } }
        );
        alert("Review submitted!");

        // Add the new review to existing reviews
        setExistingReviews((prev) => ({
          ...prev,
          [productId]: prev[productId]
            ? [...prev[productId], response.data]
            : [response.data],
        }));
      }

      // Clear input fields
      setReviews((prev) => ({
        ...prev,
        [productId]: { rating: 5, comment: "" },
      }));
    } catch (err) {
      console.error("Failed to submit or update review", err);
      alert("Failed to submit or update review.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-sky-400 mb-6 text-center">
          📝 Product Reviews
        </h1>

        {purchasedProducts.length === 0 ? (
          <p className="text-center text-gray-400">No purchased products found.</p>
        ) : (
          purchasedProducts.map((product) => {
            const userReview = getUserReview(product.id);

            // If user has reviewed, prefill form inputs with their review
            const productReview = reviews[product.id] || {
              rating: userReview?.rating || 5,
              comment: userReview?.comment || "",
            };

            return (
              <div
                key={product.id}
                className="bg-gray-800 p-4 rounded-xl shadow mb-8"
              >
                <h3 className="text-xl font-semibold text-yellow-300 mb-2">
                  {product.name}
                </h3>

                {/* Existing reviews */}
                <div className="mb-4 max-h-48 overflow-y-auto">
                  <h4 className="text-lg font-semibold mb-2">Previous Reviews:</h4>
                  {(existingReviews[product.id] || []).length === 0 ? (
                    <p className="text-gray-400">No reviews yet.</p>
                  ) : (
                    existingReviews[product.id].map((rev) => (
                      <div
                        key={rev.id}
                        className="border border-gray-700 p-2 rounded mb-2"
                      >
                        <p className="font-semibold text-yellow-400">
                          Rating: {rev.rating} ⭐
                        </p>
                        <p className="italic">"{rev.comment}"</p>
                        <p className="text-sm text-gray-500 mt-1">
                          By: {rev.user?.username || "Anonymous"}
                        </p>
                      </div>
                    ))
                  )}
                </div>

                {/* Review form */}
                <label className="block mt-2 text-sm font-semibold">Rating:</label>
                <select
                  value={productReview.rating}
                  onChange={(e) =>
                    handleRatingChange(product.id, parseInt(e.target.value, 10))
                  }
                  className="bg-gray-700 text-white rounded p-2 mt-1"
                >
                  {[1, 2, 3, 4, 5].map((star) => (
                    <option key={star} value={star}>
                      {star} Star{star > 1 ? "s" : ""}
                    </option>
                  ))}
                </select>

                <label className="block mt-4 text-sm font-semibold">Comment:</label>
                <textarea
                  value={productReview.comment}
                  onChange={(e) =>
                    handleCommentChange(product.id, e.target.value)
                  }
                  placeholder="Write your review..."
                  className="w-full mt-2 p-3 bg-gray-700 text-white rounded resize-none"
                  rows={4}
                />

                <button
                  onClick={() => handleSubmit(product.id)}
                  className="mt-4 bg-purple-700 hover:bg-purple-800 px-4 py-2 rounded text-white"
                >
                  {userReview ? "Update Review" : "Submit Review"}
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default Review;
