import React from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { homeCopy } from "../i18n/home";
import FeaturedVehicles from "../components/FeaturedVehicles";
import "../styles/home.css";
import "../styles/featured-vehicles.css";

const HomePage = () => {
  const { lang } = useLanguage();

  return (
    <div className="cma-home">
      {/* Hero Section */}
      <section className="cma-hero">
        <div className="cma-hero-inner">
          {/* Left: Main CTA */}
          <div className="cma-hero-left">
            <div className="cma-hero-badge">
              <span className="dot"></span>
              <span>{homeCopy.heroBadge[lang]}</span>
            </div>

            <h1 className="cma-hero-title">
              {homeCopy.heroTitle[lang]}
              <br />
              <span className="highlight">{homeCopy.heroTitleHighlight[lang]}</span>
            </h1>

            <p className="cma-hero-subtitle">
              {homeCopy.heroSubtitle[lang]}
            </p>

            <div className="cma-hero-ctas">
              <Link to="/preapproved" className="btn-primary">
                {homeCopy.ctaPrimary[lang]}
              </Link>
              <Link to="/vehicles" className="btn-secondary">
                {homeCopy.ctaSecondary[lang]}
              </Link>
            </div>

            <div className="cma-hero-meta">
              <span>✓ {homeCopy.badgeBadCredit[lang]}</span>
              <span>✓ {homeCopy.badgeNoCredit[lang]}</span>
              <span>✓ {homeCopy.badgeFirstTime[lang]}</span>
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
                {homeCopy.tagline[lang]}
              </p>

              <div className="cma-hero-stats">
                <div className="stat">
                  <span className="stat-label">{homeCopy.statsVehicles[lang]}</span>
                  <span className="stat-value">112+</span>
                </div>
                <div className="stat">
                  <span className="stat-label">{homeCopy.statsApproved[lang]}</span>
                  <span className="stat-value">98%</span>
                </div>
                <div className="stat">
                  <span className="stat-label">{homeCopy.statsRating[lang]}</span>
                  <span className="stat-value">4.8★</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Vehicles Section - NEW */}
      <FeaturedVehicles />

      {/* Quick Links */}
      <section className="cma-quick-links">
        <Link to="/new" className="quick-card">
          <span className="quick-label">{homeCopy.quickNew?.[lang] || "New Vehicles"}</span>
          <span className="quick-desc">
            {homeCopy.quickNewDesc?.[lang] || "Latest arrivals with full warranty"}
          </span>
        </Link>

        <Link to="/used" className="quick-card">
          <span className="quick-label">{homeCopy.quickUsed[lang]}</span>
          <span className="quick-desc">
            {homeCopy.quickUsedDesc[lang]}
          </span>
        </Link>

        <Link to="/preapproved" className="quick-card">
          <span className="quick-label">{homeCopy.quickPreApproved[lang]}</span>
          <span className="quick-desc">
            {homeCopy.quickPreApprovedDesc[lang]}
          </span>
        </Link>

        <Link to="/test-drive" className="quick-card">
          <span className="quick-label">{homeCopy.quickTestDrive[lang]}</span>
          <span className="quick-desc">
            {homeCopy.quickTestDriveDesc[lang]}
          </span>
        </Link>
      </section>

      {/* Trust Section - Customer Service Feel */}
      <section className="cma-trust-section">
        <div className="cma-trust-inner">
          <div className="cma-trust-content">
            <h2>{lang === "es" ? "¿Por Qué Elegirnos?" : "Why Choose Us?"}</h2>
            <ul className="cma-trust-list">
              <li>
                <span className="trust-icon">🤝</span>
                <div>
                  <strong>{lang === "es" ? "Servicio Personalizado" : "Personalized Service"}</strong>
                  <p>{lang === "es" ? "Nuestro equipo habla español e inglés" : "Our team speaks English and Spanish"}</p>
                </div>
              </li>
              <li>
                <span className="trust-icon">✅</span>
                <div>
                  <strong>{lang === "es" ? "Aprobación Garantizada" : "Guaranteed Approval"}</strong>
                  <p>{lang === "es" ? "Trabajamos con todo tipo de crédito" : "We work with all credit types"}</p>
                </div>
              </li>
              <li>
                <span className="trust-icon">💰</span>
                <div>
                  <strong>{lang === "es" ? "Precios Transparentes" : "Transparent Pricing"}</strong>
                  <p>{lang === "es" ? "Sin cargos ocultos ni sorpresas" : "No hidden fees or surprises"}</p>
                </div>
              </li>
              <li>
                <span className="trust-icon">🚗</span>
                <div>
                  <strong>{lang === "es" ? "Vehículos de Calidad" : "Quality Vehicles"}</strong>
                  <p>{lang === "es" ? "Todos inspeccionados y certificados" : "All inspected and certified"}</p>
                </div>
              </li>
            </ul>
          </div>
          <div className="cma-trust-image">
            <img 
              src="https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=600&q=80" 
              alt={lang === "es" ? "Equipo de ventas atendiendo cliente" : "Sales team helping customer"}
              loading="lazy"
            />
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
