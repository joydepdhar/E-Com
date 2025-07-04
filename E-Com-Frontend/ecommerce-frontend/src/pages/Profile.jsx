import React, { useContext, useEffect, useState } from "react";
import { AuthContext } from "../pages/AuthContext"; // Adjust path
import { useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = "https://e-com-fgbd.onrender.com";

function Profile() {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Redirect if not logged in
  useEffect(() => {
    if (!user) {
      navigate("/login");
    }
  }, [user, navigate]);

  // Fetch user profile from API
  useEffect(() => {
    if (!user) return;

    async function fetchProfile() {
      setLoading(true);
      setError(null);
      try {
        // Assuming your API requires Authorization header with Bearer token
        const token = localStorage.getItem("access_token");
        const response = await axios.get(`${BACKEND_URL}/api/user_app/profile/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setProfileData(response.data);
      } catch (err) {
        console.error("Failed to fetch profile:", err);
        setError("Failed to load profile data.");
      } finally {
        setLoading(false);
      }
    }

    fetchProfile();
  }, [user]);

  const editStyle =
    "ml-2 text-sm px-2 py-1 bg-[#38bdf8] text-[#0f172a] rounded hover:bg-[#7b2cbf] cursor-pointer";

  if (!user) return null; // Or loading spinner

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        Loading profile...
      </div>
    );

  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center text-red-500">
        {error}
      </div>
    );

  return (
    <div className="min-h-screen bg-[#0f172a] text-white flex flex-col items-center justify-center px-4 py-12">
      <div className="bg-[#1e293b] p-8 rounded-xl shadow-lg max-w-md w-full space-y-6">
        <h2 className="text-3xl font-bold text-center text-[#38bdf8]">
          My Profile
        </h2>

        <div className="flex justify-center">
          {profileData.profile_picture ? (
            <img
              src={profileData.profile_picture}
              alt={`${profileData.username} profile`}
              className="w-32 h-32 rounded-full object-cover border-4 border-[#38bdf8]"
            />
          ) : (
            <div className="w-32 h-32 rounded-full bg-gray-700 flex items-center justify-center text-4xl text-[#7b2cbf] font-bold">
              {profileData.username[0].toUpperCase()}
            </div>
          )}
        </div>

        <div>
          <p>
            <strong>Username:</strong> {profileData.username}
          </p>
          <p>
            <strong>Email:</strong> {profileData.email}
          </p>
          <p>
            <strong>Address:</strong> {profileData.address || "Not set"}
            <button
              className={editStyle}
              onClick={() => navigate("/edit-profile")}
              aria-label="Edit Address"
              title="Edit Address"
            >
              Edit
            </button>
          </p>
          <p>
            <strong>Phone:</strong> {profileData.phone || "Not set"}
            <button
              className={editStyle}
              onClick={() => navigate("/edit-profile")}
              aria-label="Edit Phone"
              title="Edit Phone"
            >
              Edit
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Profile;
