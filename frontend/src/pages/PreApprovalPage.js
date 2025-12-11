import React, { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { preapprovalCopy } from "../i18n/preapproval";
import { formsCopy } from "../i18n/forms";
import "../styles/forms.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const PreApprovalPage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { lang } = useLanguage();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const formData = new FormData(e.target);
    const payload = {
      type: "preapproval",
      firstName: formData.get("firstName"),
      lastName: formData.get("lastName"),
      phone: formData.get("phone"),
      email: formData.get("email"),
      stockNumber: formData.get("stockNumber"),
      source: "preapproved-page",
    };

    try {
      const response = await fetch(`${API_BASE}/api/vehicle-leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to submit lead");
      }

      console.log("Preapproval lead submitted:", payload);
      setSubmitted(true);
      e.target.reset();
    } catch (err) {
      console.error(err);
      alert("Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="cma-page cma-form-page">
      <div className="cma-page-header">
        <h1>{preapprovalCopy.pageTitle[lang]}</h1>
        <p>{preapprovalCopy.pageSubtitle[lang]}</p>
      </div>

      <div className="cma-form-layout">
        {/* LEFT: FORM */}
        <div className="cma-card">
          <form onSubmit={handleSubmit}>
            <div className="cma-field-grid">
              <div className="cma-field-group">
                <label>{formsCopy.firstName[lang]}</label>
                <input name="firstName" type="text" required />
              </div>
              <div className="cma-field-group">
                <label>{formsCopy.lastName[lang]}</label>
                <input name="lastName" type="text" required />
              </div>
            </div>

            <div className="cma-field-group">
              <label>{formsCopy.phone[lang]}</label>
              <input name="phone" type="tel" required />
            </div>

            <div className="cma-field-group">
              <label>{formsCopy.email[lang]}</label>
              <input name="email" type="email" required />
            </div>

            <div className="cma-field-group">
              <label>{preapprovalCopy.stockLabel[lang]}</label>
              <input
                name="stockNumber"
                type="text"
                placeholder={formsCopy.stockNumberPlaceholder[lang]}
              />
            </div>

            <button
              type="submit"
              className="cma-btn cma-btn-primary cma-btn-full"
              disabled={submitting}
            >
              {submitting ? formsCopy.submitting[lang] : preapprovalCopy.submitBtn[lang]}
            </button>

            {submitted && (
              <p className="cma-success-text">
                {preapprovalCopy.successMessage[lang]}
              </p>
            )}
          </form>
        </div>

        {/* RIGHT: "Step 2" + GoodChev Link + Contact */}
        <div className="cma-card cma-side-card">
          {/* Credit OK Banner */}
          <div className="cma-credit-banner">
            <span>✓ {preapprovalCopy.creditBadge1[lang]}</span>
            <span>·</span>
            <span>✓ {preapprovalCopy.creditBadge2[lang]}</span>
            <span>·</span>
            <span>✓ {preapprovalCopy.creditBadge3[lang]}</span>
          </div>
          
          <h2>{preapprovalCopy.step2Title[lang]}</h2>
          <p>{preapprovalCopy.step2Desc[lang]}</p>

          <a
            href="https://www.goodchev.com/preapproved.aspx"
            target="_blank"
            rel="noreferrer"
            className="cma-btn cma-btn-secondary cma-btn-full"
          >
            {preapprovalCopy.continueBtn[lang]}
          </a>

          <p className="cma-contact-note">
            {formsCopy.preferPhone[lang]}
          </p>
          <p className="cma-contact-line">
            {formsCopy.callLabel[lang]}:{" "}
            <a href="tel:12067861751" className="cma-link-strong">
              (206) 786-1751
            </a>
          </p>
          <p className="cma-contact-line">
            {formsCopy.emailLabel[lang]}:{" "}
            <a
              href="mailto:jay.alfred@choosemeauto.com"
              className="cma-link-strong"
            >
              jay.alfred@choosemeauto.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PreApprovalPage;
