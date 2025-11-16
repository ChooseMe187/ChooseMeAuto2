import React from "react";
import { Link } from "react-router-dom";

const HomePage = () => {
  return (
    <section style={{ padding: "2rem 0" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>Welcome to Choose Me Auto</h1>
      <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
        We specialize in helping bad credit, no credit, and first-time buyers
        get into the vehicles they deserve.
      </p>
      <p style={{ lineHeight: "1.6" }}>
        Start with our <Link to="/preapproved" style={{ color: "#2563eb" }}>Pre-Approval</Link> or browse{" "}
        <Link to="/vehicles" style={{ color: "#2563eb" }}>All Inventory</Link>.
      </p>
    </section>
  );
};

export default HomePage;