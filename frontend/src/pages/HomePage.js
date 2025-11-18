import React from "react";
import { Link } from "react-router-dom";
import "../styles/home.css";

const HomePage = () => {
  return (
    <div className="cma-home">
      {/* Hero Section */}
      <section className="cma-hero">
        <div className="cma-hero-inner">
          {/* Left: Main CTA */}
          <div className="cma-hero-left">
            <div className="cma-hero-badge">
              <span className="dot"></span>
              <span>Approved in Minutes | Aprobación en Minutos</span>
            </div>

            <h1 className="cma-hero-title">
              Get the <span className="highlight">Car You Deserve</span>,
              <br />
              Regardless of Credit
            </h1>
            <h2 className="cma-hero-title-es" style={{ fontSize: "1.5rem", marginTop: "0.5rem", opacity: 0.9 }}>
              Obtén el auto que mereces, sin importar tu historial de crédito
            </h2>

            <p className="cma-hero-subtitle">
              Bad credit? No credit? First-time buyer? No problem. We specialize in
              helping everyone drive away happy.
            </p>
            <p className="cma-hero-subtitle-es" style={{ fontSize: "0.9rem", marginTop: "0.5rem", opacity: 0.85 }}>
              ¿Crédito malo? ¿Sin crédito? ¿Primera vez comprando? No hay problema.
              Nos especializamos en ayudar a todos a irse felices con su auto.
            </p>

            <div className="cma-hero-ctas">
              <Link to="/preapproved" className="btn-primary">
                Get Pre-Approved in Minutes
              </Link>
              <Link to="/vehicles" className="btn-secondary">
                Browse All Inventory
              </Link>
            </div>

            <div className="cma-hero-meta">
              <span>✓ Bad Credit OK</span>
              <span>✓ No Credit OK</span>
              <span>✓ First-Time Buyers Welcome</span>
            </div>
          </div>

          {/* Right: Logo Card */}
          <div className="cma-hero-right">
            <div className="cma-hero-card">
              <img
                src="/chooseme-logo.svg"
                alt="Choose Me Auto"
                className="cma-logo"
              />
              <p className="cma-hero-tagline">
                Your trusted partner in auto financing
              </p>

              <div className="cma-hero-stats">
                <div className="stat">
                  <span className="stat-label">Vehicles</span>
                  <span className="stat-value">112+</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Approved</span>
                  <span className="stat-value">98%</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Rating</span>
                  <span className="stat-value">4.8★</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="cma-quick-links">
        <Link to="/used" className="quick-card">
          <span className="quick-label">Shop Used Vehicles</span>
          <span className="quick-desc">
            Browse our selection of quality pre-owned cars, trucks, and SUVs
          </span>
        </Link>

        <Link to="/new" className="quick-card">
          <span className="quick-label">Shop New Vehicles</span>
          <span className="quick-desc">
            Explore the latest models with full manufacturer warranties
          </span>
        </Link>

        <Link to="/test-drive" className="quick-card">
          <span className="quick-label">Schedule Test Drive</span>
          <span className="quick-desc">
            Experience your dream vehicle in person — book online today
          </span>
        </Link>
      </section>
    </div>
  );
};

export default HomePage;
