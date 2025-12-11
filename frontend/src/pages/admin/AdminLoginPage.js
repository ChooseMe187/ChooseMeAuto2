import React, { useState } from "react";
import { useAdminAuth } from "../../context/AdminAuthContext";
import "../../styles/admin.css";

const AdminLoginPage = () => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAdminAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const result = await login(password);

    if (!result.success) {
      setError(result.message || "Invalid password");
    }
    setLoading(false);
  };

  return (
    <div className="admin-login-page">
      <div className="admin-login-card">
        <div className="admin-login-header">
          <h1>Choose Me Auto</h1>
          <p>Admin Panel</p>
        </div>

        <form onSubmit={handleSubmit} className="admin-login-form">
          <div className="admin-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter admin password"
              required
              autoFocus
            />
          </div>

          {error && <p className="admin-error">{error}</p>}

          <button type="submit" disabled={loading} className="admin-btn-primary">
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="admin-login-hint">
          Contact your administrator if you don't have access.
        </p>
      </div>
    </div>
  );
};

export default AdminLoginPage;
