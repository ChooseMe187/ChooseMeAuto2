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
            <span className="cma-logo-sub">Bad Credit • No Credit • First-Time</span>
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
          <Link to="/preapproved" className="cma-cta-btn">
            Get Pre-Approved
          </Link>
        </nav>

        {/* Mobile Menu Button */}
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
