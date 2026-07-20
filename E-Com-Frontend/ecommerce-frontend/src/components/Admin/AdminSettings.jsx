import React, { useState, useEffect } from "react";
import { Save, AlertCircle } from "lucide-react";
import axios from "axios";
import { BACKEND_URL } from "../../config";

function AdminSettings() {
  const [settings, setSettings] = useState({
    store_name: "E-Commerce Store",
    store_description: "Your awesome e-commerce platform",
    store_email: "support@ecommerce.com",
    store_phone: "+1-800-123-4567",
    currency: "USD",
    tax_rate: "10",
    shipping_cost: "10",
    min_order_amount: "0",
    maintenance_mode: false,
    allow_registration: true,
    require_email_verification: false,
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");


  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const accessToken = localStorage.getItem("access_token");
        const response = await axios.get(`${BACKEND_URL}/api/store/admin/settings/`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        setSettings(response.data);
      } catch (error) {
        console.error("Error fetching settings:", error);
      }
    };

    fetchSettings();
  }, [BACKEND_URL]);

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      const accessToken = localStorage.getItem("access_token");
      await axios.put(
        `${BACKEND_URL}/api/store/admin/settings/`,
        settings,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      setMessage("Settings saved successfully!");
      setTimeout(() => setMessage(""), 3000);
    } catch (error) {
      console.error("Error saving settings:", error);
      setMessage("Error saving settings");
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <h2 className="text-2xl font-bold">Admin Settings</h2>

      {/* Success Message */}
      {message && (
        <div className="bg-green-900 border border-green-600 text-green-100 px-4 py-3 rounded flex items-center space-x-2">
          <AlertCircle size={20} />
          <span>{message}</span>
        </div>
      )}

      {/* Settings Form */}
      <div className="space-y-8">
        {/* Store Information */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Store Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Store Name</label>
              <input
                type="text"
                value={settings.store_name}
                onChange={(e) =>
                  setSettings({ ...settings, store_name: e.target.value })
                }
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Store Description
              </label>
              <textarea
                value={settings.store_description}
                onChange={(e) =>
                  setSettings({ ...settings, store_description: e.target.value })
                }
                rows="3"
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Store Email</label>
                <input
                  type="email"
                  value={settings.store_email}
                  onChange={(e) =>
                    setSettings({ ...settings, store_email: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Store Phone</label>
                <input
                  type="tel"
                  value={settings.store_phone}
                  onChange={(e) =>
                    setSettings({ ...settings, store_phone: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Billing & Shipping */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Billing & Shipping</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Currency</label>
                <select
                  value={settings.currency}
                  onChange={(e) =>
                    setSettings({ ...settings, currency: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="INR">INR (₹)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Tax Rate (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={settings.tax_rate}
                  onChange={(e) =>
                    setSettings({ ...settings, tax_rate: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Shipping Cost</label>
                <input
                  type="number"
                  step="0.01"
                  value={settings.shipping_cost}
                  onChange={(e) =>
                    setSettings({ ...settings, shipping_cost: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Minimum Order Amount
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={settings.min_order_amount}
                  onChange={(e) =>
                    setSettings({ ...settings, min_order_amount: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Store Features */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Store Features</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 bg-gray-700 rounded">
              <input
                type="checkbox"
                checked={settings.maintenance_mode}
                onChange={(e) =>
                  setSettings({ ...settings, maintenance_mode: e.target.checked })
                }
                className="w-5 h-5 rounded bg-gray-600 border-gray-500"
              />
              <div>
                <label className="font-medium">Maintenance Mode</label>
                <p className="text-sm text-gray-400">
                  Disable store for maintenance
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4 p-4 bg-gray-700 rounded">
              <input
                type="checkbox"
                checked={settings.allow_registration}
                onChange={(e) =>
                  setSettings({ ...settings, allow_registration: e.target.checked })
                }
                className="w-5 h-5 rounded bg-gray-600 border-gray-500"
              />
              <div>
                <label className="font-medium">Allow User Registration</label>
                <p className="text-sm text-gray-400">
                  Allow new users to create accounts
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4 p-4 bg-gray-700 rounded">
              <input
                type="checkbox"
                checked={settings.require_email_verification}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    require_email_verification: e.target.checked,
                  })
                }
                className="w-5 h-5 rounded bg-gray-600 border-gray-500"
              />
              <div>
                <label className="font-medium">Require Email Verification</label>
                <p className="text-sm text-gray-400">
                  Users must verify email to register
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-red-900 bg-opacity-20 p-6 rounded-lg border border-red-700">
          <h3 className="text-lg font-semibold text-red-400 mb-4">Danger Zone</h3>
          <p className="text-gray-300 mb-4">
            These actions cannot be undone. Please proceed with caution.
          </p>
          <div className="space-y-2">
            <button className="w-full px-4 py-2 border border-red-600 text-red-400 rounded hover:bg-red-900 hover:bg-opacity-30 transition">
              Clear Cache
            </button>
            <button className="w-full px-4 py-2 border border-red-600 text-red-400 rounded hover:bg-red-900 hover:bg-opacity-30 transition">
              Reset Database
            </button>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSaveSettings}
          disabled={loading}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-2 rounded transition font-medium"
        >
          <Save size={20} />
          <span>{loading ? "Saving..." : "Save Settings"}</span>
        </button>
      </div>
    </div>
  );
}

export default AdminSettings;
