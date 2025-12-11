import React, { useState, useEffect } from "react";
import { useAdminAuth } from "../../context/AdminAuthContext";
import AddVehicleForm from "../../components/admin/AddVehicleForm";
import VehicleTable from "../../components/admin/VehicleTable";
import "../../styles/admin.css";

const AdminVehiclesPage = () => {
  const { token, logout } = useAdminAuth();
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

  const fetchVehicles = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/admin/vehicles`, {
        headers: { "x-admin-token": token },
      });
      if (response.ok) {
        const data = await response.json();
        setVehicles(data);
      }
    } catch (error) {
      console.error("Error fetching vehicles:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchVehicles();
  }, [token]);

  const handleVehicleCreated = () => {
    setShowAddForm(false);
    fetchVehicles();
  };

  const handleDelete = async (vehicleId) => {
    if (!window.confirm("Are you sure you want to delete this vehicle?")) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/admin/vehicles/${vehicleId}`, {
        method: "DELETE",
        headers: { "x-admin-token": token },
      });

      if (response.ok) {
        fetchVehicles();
      } else {
        alert("Failed to delete vehicle");
      }
    } catch (error) {
      console.error("Delete error:", error);
      alert("Error deleting vehicle");
    }
  };

  const handleEdit = (vehicle) => {
    setEditingVehicle(vehicle);
    setShowAddForm(true);
  };

  return (
    <div className="admin-page">
      {/* Header */}
      <div className="admin-header">
        <div className="admin-header-left">
          <h1>Vehicle Inventory</h1>
          <span className="admin-vehicle-count">{vehicles.length} vehicles</span>
        </div>
        <div className="admin-header-right">
          <button
            onClick={() => {
              setEditingVehicle(null);
              setShowAddForm(true);
            }}
            className="admin-btn-primary"
          >
            + Add Vehicle
          </button>
          <button onClick={logout} className="admin-btn-secondary">
            Logout
          </button>
        </div>
      </div>

      {/* Add/Edit Vehicle Form */}
      {showAddForm && (
        <div className="admin-modal-overlay">
          <div className="admin-modal">
            <AddVehicleForm
              token={token}
              onClose={() => {
                setShowAddForm(false);
                setEditingVehicle(null);
              }}
              onSuccess={handleVehicleCreated}
              editingVehicle={editingVehicle}
            />
          </div>
        </div>
      )}

      {/* Vehicle Table */}
      <div className="admin-content">
        {loading ? (
          <div className="admin-loading">Loading vehicles...</div>
        ) : vehicles.length === 0 ? (
          <div className="admin-empty">
            <p>No vehicles in inventory yet.</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="admin-btn-primary"
            >
              Add Your First Vehicle
            </button>
          </div>
        ) : (
          <VehicleTable
            vehicles={vehicles}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}
      </div>
    </div>
  );
};

export default AdminVehiclesPage;
