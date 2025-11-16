import React from "react";
import { Link } from "react-router-dom";

const UsedVehiclesPage = () => {
  return (
    <section style={{ padding: "2rem 0" }}>
      <h2 style={{ fontSize: "1.75rem", marginBottom: "1rem" }}>Used Vehicles</h2>
      <p style={{ lineHeight: "1.6" }}>
        Browse our full used inventory on the{" "}
        <Link to="/vehicles" style={{ color: "#2563eb" }}>inventory page</Link>. This tab exists so customers
        can quickly understand we have a strong used selection.
      </p>
    </section>
  );
};

export default UsedVehiclesPage;