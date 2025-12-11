import React from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { thankyouCopy } from "../i18n/thankyou";
import "../styles/forms.css";

const ThankYouPage = () => {
  const { lang } = useLanguage();

  return (
    <div className="cma-page">
      <div className="cma-page-header">
        <h1 style={{ color: "#22c55e" }}>
          {thankyouCopy.pageTitle[lang]} ✅
        </h1>
        <p>{thankyouCopy.pageSubtitle[lang]}</p>
      </div>

      <div className="cma-form-layout" style={{ maxWidth: "960px", margin: "0 auto" }}>
        {/* Main Content */}
        <div className="cma-card">
          <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#f9fafb" }}>
            {thankyouCopy.whatHappensNext[lang]}
          </h2>

          <div style={{ marginBottom: "1.5rem" }}>
            <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
              {thankyouCopy.behindScenes[lang]}
            </p>

            <ul style={{ listStyle: "none", padding: 0 }}>
              <li style={{ marginBottom: "1rem", paddingLeft: "2rem", position: "relative" }}>
                <span style={{ position: "absolute", left: 0, color: "#22c55e" }}>🔍</span>
                <strong>{thankyouCopy.step1[lang]}</strong>
              </li>
              <li style={{ marginBottom: "1rem", paddingLeft: "2rem", position: "relative" }}>
                <span style={{ position: "absolute", left: 0, color: "#22c55e" }}>🚗</span>
                <strong>{thankyouCopy.step2[lang]}</strong>
              </li>
              <li style={{ marginBottom: "1rem", paddingLeft: "2rem", position: "relative" }}>
                <span style={{ position: "absolute", left: 0, color: "#22c55e" }}>📅</span>
                <strong>{thankyouCopy.step3[lang]}</strong>
              </li>
            </ul>
          </div>

          <div
            style={{
              padding: "1.5rem",
              borderRadius: "0.75rem",
              background: "rgba(34, 197, 94, 0.1)",
              border: "1px solid rgba(34, 197, 94, 0.3)",
              marginBottom: "1.5rem",
            }}
          >
            <p style={{ marginBottom: "0.5rem", fontSize: "0.9rem" }}>
              <strong>{thankyouCopy.hearFromUs[lang]}</strong>
            </p>
            <p style={{ marginBottom: "0.25rem" }}>
              📞 {thankyouCopy.callOrTextFrom[lang]}{" "}
              <a href="tel:12067861751" style={{ color: "#22c55e", textDecoration: "none", fontWeight: "600" }}>
                (206) 786-1751
              </a>
            </p>
            <p style={{ marginBottom: 0 }}>
              📧 {thankyouCopy.emailFrom[lang]}{" "}
              <a
                href="mailto:jay.alfred@choosemeauto.com"
                style={{ color: "#22c55e", textDecoration: "none", fontWeight: "600" }}
              >
                jay.alfred@choosemeauto.com
              </a>
            </p>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "0.75rem", color: "#f9fafb" }}>
              {thankyouCopy.speedUp[lang]}
            </h3>
            <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
              {thankyouCopy.speedUpDesc[lang].split('"').map((part, i) => 
                i === 1 ? <strong key={i}>&quot;{part}&quot;</strong> : part
              )}
            </p>
            <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
              {thankyouCopy.speedUpDesc2[lang]}
            </p>
          </div>

          <div>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "0.75rem", color: "#f9fafb" }}>
              {thankyouCopy.stillBrowsing[lang]}
            </h3>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
              <Link to="/used" className="cma-btn cma-btn-secondary">
                {thankyouCopy.shopUsed[lang]}
              </Link>
              <Link to="/vehicles" className="cma-btn cma-btn-secondary">
                {thankyouCopy.viewAll[lang]}
              </Link>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="cma-card cma-side-card">
          <h2>{thankyouCopy.helpUsTitle[lang]}</h2>
          <p>{thankyouCopy.helpUsDesc[lang]}</p>

          <div style={{ marginTop: "1.5rem" }}>
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                {thankyouCopy.paymentRange[lang]}
              </label>
              <select
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "0.5rem",
                  border: "1px solid rgba(148, 163, 184, 0.5)",
                  background: "rgba(15, 23, 42, 0.7)",
                  color: "#f9fafb",
                }}
              >
                <option value="">{thankyouCopy.selectRange[lang]}</option>
                <option value="200-300">$200 - $300/mo</option>
                <option value="300-400">$300 - $400/mo</option>
                <option value="400-500">$400 - $500/mo</option>
                <option value="500+">$500+/mo</option>
              </select>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                {thankyouCopy.vehicleType[lang]}
              </label>
              <select
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "0.5rem",
                  border: "1px solid rgba(148, 163, 184, 0.5)",
                  background: "rgba(15, 23, 42, 0.7)",
                  color: "#f9fafb",
                }}
              >
                <option value="">{thankyouCopy.selectType[lang]}</option>
                <option value="SUV">SUV / Crossover</option>
                <option value="Sedan">Sedan</option>
                <option value="Truck">Truck</option>
                <option value="EV">Electric / Hybrid</option>
              </select>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                {thankyouCopy.tradeIn[lang]}
              </label>
              <select
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "0.5rem",
                  border: "1px solid rgba(148, 163, 184, 0.5)",
                  background: "rgba(15, 23, 42, 0.7)",
                  color: "#f9fafb",
                }}
              >
                <option value="">{thankyouCopy.selectOption[lang]}</option>
                <option value="yes">{thankyouCopy.yesTradeIn[lang]}</option>
                <option value="no">{thankyouCopy.noTradeIn[lang]}</option>
              </select>
            </div>

            <button
              className="cma-btn cma-btn-primary cma-btn-full"
              style={{ marginTop: "1rem" }}
              onClick={() => alert("This would submit the additional info to help customize your experience")}
            >
              {thankyouCopy.submitPrefs[lang]}
            </button>
          </div>

          <p className="cma-contact-note">{thankyouCopy.prefsHelp[lang]}</p>
        </div>
      </div>

      {/* Return Home Link */}
      <div style={{ textAlign: "center", marginTop: "2rem" }}>
        <Link
          to="/"
          style={{
            color: "#9ca3af",
            textDecoration: "none",
            fontSize: "0.9rem",
          }}
        >
          ← {thankyouCopy.backHome[lang]}
        </Link>
      </div>
    </div>
  );
};

export default ThankYouPage;
