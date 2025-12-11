import React from "react";
import "../../styles/admin.css";

const VehicleTable = ({ vehicles, onEdit, onDelete }) => {
  const formatPrice = (price) => {
    if (!price) return "—";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatMileage = (mileage) => {
    if (!mileage) return "—";
    return new Intl.NumberFormat("en-US").format(mileage) + " mi";
  };

  return (
    <div className="admin-table-container">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Photo</th>
            <th>Vehicle</th>
            <th>Stock #</th>
            <th>VIN</th>
            <th>Price</th>
            <th>Mileage</th>
            <th>Condition</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {vehicles.map((vehicle) => (
            <tr key={vehicle.id}>
              <td className="admin-table-photo">
                {vehicle.photo_urls?.length > 0 ? (
                  <img
                    src={vehicle.photo_urls[0]}
                    alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                  />
                ) : (
                  <div className="admin-no-photo">No Photo</div>
                )}
              </td>
              <td>
                <div className="admin-vehicle-info">
                  <strong>
                    {vehicle.year} {vehicle.make} {vehicle.model}
                  </strong>
                  {vehicle.trim && <span className="admin-trim">{vehicle.trim}</span>}
                </div>
              </td>
              <td>{vehicle.stock_number || "—"}</td>
              <td className="admin-vin">{vehicle.vin}</td>
              <td>{formatPrice(vehicle.price)}</td>
              <td>{formatMileage(vehicle.mileage)}</td>
              <td>
                <span
                  className={`admin-condition-badge ${
                    vehicle.condition === "New" ? "admin-badge-new" : "admin-badge-used"
                  }`}
                >
                  {vehicle.condition}
                </span>
              </td>
              <td>
                <div className="admin-actions">
                  <button
                    onClick={() => onEdit(vehicle)}
                    className="admin-btn-edit"
                    title="Edit"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => onDelete(vehicle.id)}
                    className="admin-btn-delete"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default VehicleTable;
