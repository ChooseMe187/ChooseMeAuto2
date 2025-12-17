import React, { useState } from "react";
import { useAdminAuth, AdminAuthProvider } from "../../context/AdminAuthContext";
import AdminLoginPage from "./AdminLoginPage";
import AdminVehiclesPage from "./AdminVehiclesPage";
import AdminLeadsPage from "./AdminLeadsPage";
import "../../styles/admin.css";

const AdminLayoutInner = () => {
  const { isAuthenticated, loading, logout } = useAdminAuth();
  const [activeTab, setActiveTab] = useState("leads"); // Default to leads

  if (loading) {
    return (
      <div className="admin-page">
        <div className="admin-loading">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AdminLoginPage />;
  }

  return (
    <div className="admin-page">
      {/* Admin Header with Navigation */}
      <div className="admin-header">
        <div className="admin-header-left">
          <h1>Choose Me Auto</h1>
          <span className="admin-header-subtitle">Admin Panel</span>
        </div>
        
        <div className="admin-nav-tabs">
          <button
            className={`admin-nav-tab ${activeTab === "leads" ? "active" : ""}`}
            onClick={() => setActiveTab("leads")}
          >
            📩 Leads
          </button>
          <button
            className={`admin-nav-tab ${activeTab === "vehicles" ? "active" : ""}`}
            onClick={() => setActiveTab("vehicles")}
          >
            🚗 Vehicles
          </button>
        </div>

        <div className="admin-header-right">
          <button onClick={logout} className="admin-btn-secondary">
            Logout
          </button>
        </div>
      </div>

      {/* Content based on active tab */}
      <div className="admin-content">
        {activeTab === "leads" && <AdminLeadsPage />}
        {activeTab === "vehicles" && <AdminVehiclesPage />}
      </div>
    </div>
  );
};

const AdminLayout = () => {
  return (
    <AdminAuthProvider>
      <AdminLayoutInner />
    </AdminAuthProvider>
  );
};

export default AdminLayout;
