import React from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { homeCopy } from "../i18n/home";
import FeaturedVehicles from "../components/FeaturedVehicles";
import "../styles/home.css";
import "../styles/featured-vehicles.css";

// Multicultural dealership imagery (Unsplash/Pexels - commercially licensed)
const TRUST_IMAGES = {
  hero: "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&q=80",
  consultation: "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=600&q=80",
  handshake: "https://images.unsplash.com/photo-1686771416282-3888ddaf249b?w=600&q=80",
  showroom: "https://images.pexels.com/photos/2127039/pexels-photo-2127039.jpeg?auto=compress&cs=tinysrgb&w=600",
  team: "https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=600",
  customer: "https://images.pexels.com/photos/7144191/pexels-photo-7144191.jpeg?auto=compress&cs=tinysrgb&w=600",
};

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

      {/* Featured Vehicles Section */}
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

      {/* Trust Section - Customer Service Feel with Multicultural Imagery */}
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
              src={TRUST_IMAGES.consultation}
              alt={lang === "es" ? "Consultor de ventas con cliente" : "Sales consultant with customer"}
              loading="lazy"
            />
          </div>
        </div>
      </section>

      {/* Team & Service Section - Multicultural */}
      <section className="cma-team-section">
        <div className="cma-team-inner">
          <h2>{lang === "es" ? "Nuestro Compromiso" : "Our Commitment"}</h2>
          <p className="cma-team-subtitle">
            {lang === "es" 
              ? "Un equipo dedicado a hacer realidad tus sueños de conducir"
              : "A dedicated team committed to making your driving dreams come true"
            }
          </p>
          
          <div className="cma-team-gallery">
            <div className="team-image-card">
              <img 
                src={TRUST_IMAGES.handshake}
                alt={lang === "es" ? "Apretón de manos cerrando trato" : "Handshake closing deal"}
                loading="lazy"
              />
              <span className="team-image-label">
                {lang === "es" ? "Atención Personalizada" : "Personal Attention"}
              </span>
            </div>
            <div className="team-image-card">
              <img 
                src={TRUST_IMAGES.team}
                alt={lang === "es" ? "Equipo profesional" : "Professional team"}
                loading="lazy"
              />
              <span className="team-image-label">
                {lang === "es" ? "Equipo Profesional" : "Professional Team"}
              </span>
            </div>
            <div className="team-image-card">
              <img 
                src={TRUST_IMAGES.customer}
                alt={lang === "es" ? "Clientes satisfechos" : "Satisfied customers"}
                loading="lazy"
              />
              <span className="team-image-label">
                {lang === "es" ? "Clientes Felices" : "Happy Customers"}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action Banner */}
      <section className="cma-cta-banner">
        <div className="cma-cta-inner">
          <div className="cta-content">
            <h2>
              {lang === "es" 
                ? "¿Listo para Conducir Tu Nuevo Auto?"
                : "Ready to Drive Your New Car?"
              }
            </h2>
            <p>
              {lang === "es"
                ? "Pre-aprobación en minutos. Sin afectar tu crédito."
                : "Pre-approval in minutes. No impact to your credit."
              }
            </p>
          </div>
          <div className="cta-buttons">
            <Link to="/preapproved" className="btn-primary-light">
              {lang === "es" ? "Comenzar Ahora" : "Get Started"}
            </Link>
            <a href="tel:+12067861751" className="btn-call">
              📞 (206) 786-1751
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
