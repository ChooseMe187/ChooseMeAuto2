import React, { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { contactCopy } from "../i18n/contact";
import { formsCopy } from "../i18n/forms";
import "../styles/forms.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const ContactPage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { lang } = useLanguage();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const formData = new FormData(e.target);
    const payload = {
      type: "contact",
      firstName: formData.get("firstName"),
      lastName: formData.get("lastName"),
      phone: formData.get("phone"),
      email: formData.get("email"),
      stockNumber: formData.get("stockNumber"),
      message: formData.get("message"),
      source: "contact-page",
    };

    try {
      const response = await fetch(`${API_BASE}/api/vehicle-leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to submit contact form");
      }

      console.log("Contact lead submitted:", payload);
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
        <h1>{contactCopy.pageTitle[lang]}</h1>
        <p>{contactCopy.pageSubtitle[lang]}</p>
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
              <label>{formsCopy.stockNumberOptional[lang]}</label>
              <input
                name="stockNumber"
                type="text"
                placeholder={formsCopy.stockNumberPlaceholder[lang]}
              />
            </div>

            <div className="cma-field-group">
              <label>{contactCopy.messageLabel[lang]}</label>
              <textarea
                name="message"
                placeholder={contactCopy.messagePlaceholder[lang]}
                required
              />
            </div>

            <button
              type="submit"
              className="cma-btn cma-btn-primary cma-btn-full"
              disabled={submitting}
            >
              {submitting ? formsCopy.sending[lang] : contactCopy.submitBtn[lang]}
            </button>

            {submitted && (
              <p className="cma-success-text">
                {contactCopy.successMessage[lang]}
              </p>
            )}
          </form>
        </div>

        {/* RIGHT: Contact Info */}
        <div className="cma-card cma-side-card">
          <h2>{contactCopy.sideTitle[lang]}</h2>
          <p>{contactCopy.sideDesc[lang]}</p>

          <div style={{ marginTop: "1.5rem", marginBottom: "1.5rem" }}>
            <p className="cma-contact-line">
              <strong>{formsCopy.addressLabel[lang]}:</strong>
              <br />
              Good Chevrolet Renton
              <br />
              Renton, WA 98057
            </p>
            <p className="cma-contact-line">
              <strong>{formsCopy.hoursLabel[lang]}:</strong>
              <br />
              {contactCopy.hours[lang].split('\n').map((line, i) => (
                <span key={i}>{line}<br /></span>
              ))}
            </p>
          </div>

          <p className="cma-contact-note">{formsCopy.getInTouch[lang]}</p>
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

export default ContactPage;
