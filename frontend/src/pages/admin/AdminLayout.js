import React from "react";
import { Navigate } from "react-router-dom";
import { useAdminAuth, AdminAuthProvider } from "../../context/AdminAuthContext";
import AdminLoginPage from "./AdminLoginPage";
import AdminVehiclesPage from "./AdminVehiclesPage";

const AdminLayoutInner = () => {
  const { isAuthenticated, loading } = useAdminAuth();

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

  return <AdminVehiclesPage />;
};

const AdminLayout = () => {
  return (
    <AdminAuthProvider>
      <AdminLayoutInner />
    </AdminAuthProvider>
  );
};

export default AdminLayout;
