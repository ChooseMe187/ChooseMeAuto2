import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { navbarCopy } from "../i18n/navbar";
import LanguageToggle from "./LanguageToggle";
import "./../styles/navbar.css";

const NavBar = () => {
  const [open, setOpen] = useState(false);
  const { lang, toggleLang } = useLanguage();

  const toggleMenu = () => setOpen((prev) => !prev);
  const closeMenu = () => setOpen(false);

  const navLinks = [
    { to: "/", label: navbarCopy.home[lang], exact: true },
    { to: "/used", label: navbarCopy.used[lang] },
    { to: "/preapproved", label: navbarCopy.preApproved[lang] },
    { to: "/test-drive", label: navbarCopy.testDrive[lang] },
    { to: "/contact", label: navbarCopy.contact[lang] },
  ];

  return (
    <header className="cma-navbar">
      <div className="cma-navbar-inner">
        {/* Left: Logo / Brand */}
        <div className="cma-navbar-brand">
          <Link to="/" onClick={closeMenu} className="cma-logo-link">
            <span className="cma-logo-main">Choose Me Auto</span>
            <span className="cma-logo-sub">{navbarCopy.tagline[lang]}</span>
          </Link>
        </div>

        {/* Desktop Nav */}
        <nav className="cma-nav-links-desktop">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.exact}
              className={({ isActive }) =>
                "cma-nav-link" + (isActive ? " cma-nav-link-active" : "")
              }
            >
              {link.label}
            </NavLink>
          ))}
          
          {/* Credit OK Badges */}
          <div className="cma-credit-badges">
            <span className="cma-credit-badge">✓ {navbarCopy.badCreditOK[lang]}</span>
            <span className="cma-credit-badge">✓ {navbarCopy.noCreditOK[lang]}</span>
          </div>
          
          {/* Language Toggle */}
          <LanguageToggle />
          
          <Link to="/preapproved" className="cma-cta-btn">
            {navbarCopy.getPreApproved[lang]}
          </Link>
        </nav>

        {/* Mobile: Credit Badges + Language Toggle + Menu Button */}
        <div className="cma-mobile-right">
          <div className="cma-credit-badges-mobile">
            <span className="cma-credit-badge-mobile">✓ {navbarCopy.badCreditOK[lang]}</span>
            <span className="cma-credit-badge-mobile">✓ {navbarCopy.noCreditOK[lang]}</span>
          </div>
          <button
            onClick={toggleLang}
            className="cma-lang-toggle-mobile"
            aria-label="Toggle language"
          >
            {lang === "en" ? "ES" : "EN"}
          </button>
          <button
            className="cma-burger-btn"
            onClick={toggleMenu}
            aria-label="Toggle navigation"
          >
            <span className="cma-burger-line" />
            <span className="cma-burger-line" />
            <span className="cma-burger-line" />
          </button>
        </div>
      </div>

      {/* Mobile Nav Panel */}
      {open && (
        <nav className="cma-nav-links-mobile">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.exact}
              onClick={closeMenu}
              className={({ isActive }) =>
                "cma-nav-link-mobile" + (isActive ? " cma-nav-link-mobile-active" : "")
              }
            >
              {link.label}
            </NavLink>
          ))}
          <Link to="/preapproved" onClick={closeMenu} className="cma-cta-btn-mobile">
            {navbarCopy.getPreApproved[lang]}
          </Link>
        </nav>
      )}
    </header>
  );
};

export default NavBar;
