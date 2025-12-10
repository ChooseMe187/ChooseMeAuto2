import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import "./../styles/navbar.css";

const NavBar = () => {
  const [open, setOpen] = useState(false);

  const toggleMenu = () => setOpen((prev) => !prev);
  const closeMenu = () => setOpen(false);

  const navLinks = [
    { to: "/", label: "Home", exact: true },
    { to: "/used", label: "Used" },
    { to: "/new", label: "New" },
    { to: "/preapproved", label: "Pre-Approved" },
    { to: "/test-drive", label: "Test Drive" },
    { to: "/contact", label: "Contact" },
  ];

  return (
    <header className="cma-navbar">
      <div className="cma-navbar-inner">
        {/* Left: Logo / Brand */}
        <div className="cma-navbar-brand">
          <Link to="/" onClick={closeMenu} className="cma-logo-link">
            <span className="cma-logo-main">Choose Me Auto</span>
            <span className="cma-logo-sub">Your Trusted Car Dealership</span>
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
            <span className="cma-credit-badge">✓ Bad Credit OK</span>
            <span className="cma-credit-badge">✓ No Credit OK</span>
          </div>
          
          <Link to="/preapproved" className="cma-cta-btn">
            Get Pre-Approved
          </Link>
        </nav>

        {/* Mobile: Credit Badges + Menu Button */}
        <div className="cma-mobile-right">
          <div className="cma-credit-badges-mobile">
            <span className="cma-credit-badge-mobile">✓ Bad Credit OK</span>
            <span className="cma-credit-badge-mobile">✓ No Credit OK</span>
          </div>
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
            Get Pre-Approved
          </Link>
        </nav>
      )}
    </header>
  );
};

export default NavBar;
