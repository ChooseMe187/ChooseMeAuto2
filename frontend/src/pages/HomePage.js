import React from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { homeCopy } from "../i18n/home";
import "../styles/home.css";

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

      {/* Quick Links */}
      <section className="cma-quick-links">
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
    </div>
  );
};

export default HomePage;
