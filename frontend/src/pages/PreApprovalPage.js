import React, { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { preapprovalCopy } from "../i18n/preapproval";
import { formsCopy } from "../i18n/forms";
import "../styles/forms.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";
const GOOD_CHEV_URL = "https://www.goodchev.com/preapproved.aspx";

const PreApprovalPage = () => {
  const { lang } = useLanguage();
  
  // Form state
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    phone: "",
    email: "",
    stockNumber: "",
  });
  
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [canContinue, setCanContinue] = useState(false);

  // Validation helpers
  const isValidEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
  const isValidPhone = (v) => v.replace(/\D/g, "").length >= 10;

  const validate = () => {
    const e = {};
    if (!form.firstName.trim()) e.firstName = lang === "en" ? "First name is required." : "El nombre es requerido.";
    if (!form.lastName.trim()) e.lastName = lang === "en" ? "Last name is required." : "El apellido es requerido.";
    if (!isValidPhone(form.phone)) e.phone = lang === "en" ? "Enter a valid phone number (10+ digits)." : "Ingresa un número de teléfono válido (10+ dígitos).";
    if (!isValidEmail(form.email)) e.email = lang === "en" ? "Enter a valid email address." : "Ingresa un correo electrónico válido.";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleChange = (field) => (e) => {
    // Reset canContinue if user edits after submission
    setCanContinue(false);
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    // Clear field error on change
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setSubmitting(true);
    setErrors({});

    const payload = {
      type: "preapproval",
      firstName: form.firstName,
      lastName: form.lastName,
      phone: form.phone,
      email: form.email,
      stockNumber: form.stockNumber,
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
      setCanContinue(true);
      
    } catch (err) {
      console.error(err);
      setErrors((prev) => ({
        ...prev,
        form: lang === "en" 
          ? "Something went wrong. Please try again." 
          : "Algo salió mal. Por favor intenta de nuevo.",
      }));
      setCanContinue(false);
    } finally {
      setSubmitting(false);
    }
  };

  const handleContinueToGoodChev = () => {
    if (!canContinue) {
      setErrors((prev) => ({
        ...prev,
        form: lang === "en" 
          ? "Please complete and submit the form first." 
          : "Por favor completa y envía el formulario primero.",
      }));
      return;
    }
    window.open(GOOD_CHEV_URL, "_blank", "noopener,noreferrer");
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
          {errors.form && (
            <div className="cma-error-banner">{errors.form}</div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="cma-field-grid">
              <div className="cma-field-group">
                <label>{formsCopy.firstName[lang]} *</label>
                <input 
                  type="text" 
                  value={form.firstName}
                  onChange={handleChange("firstName")}
                  className={errors.firstName ? "cma-input-error" : ""}
                />
                {errors.firstName && <span className="cma-field-error">{errors.firstName}</span>}
              </div>
              <div className="cma-field-group">
                <label>{formsCopy.lastName[lang]} *</label>
                <input 
                  type="text" 
                  value={form.lastName}
                  onChange={handleChange("lastName")}
                  className={errors.lastName ? "cma-input-error" : ""}
                />
                {errors.lastName && <span className="cma-field-error">{errors.lastName}</span>}
              </div>
            </div>

            <div className="cma-field-group">
              <label>{formsCopy.phone[lang]} *</label>
              <input 
                type="tel" 
                value={form.phone}
                onChange={handleChange("phone")}
                placeholder="(555) 555-5555"
                className={errors.phone ? "cma-input-error" : ""}
              />
              {errors.phone && <span className="cma-field-error">{errors.phone}</span>}
            </div>

            <div className="cma-field-group">
              <label>{formsCopy.email[lang]} *</label>
              <input 
                type="email" 
                value={form.email}
                onChange={handleChange("email")}
                placeholder="you@example.com"
                className={errors.email ? "cma-input-error" : ""}
              />
              {errors.email && <span className="cma-field-error">{errors.email}</span>}
            </div>

            <div className="cma-field-group">
              <label>{preapprovalCopy.stockLabel[lang]}</label>
              <input
                type="text"
                value={form.stockNumber}
                onChange={handleChange("stockNumber")}
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

            {canContinue && (
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

          {/* Gated Button - Only clickable after form submission */}
          <button
            type="button"
            onClick={handleContinueToGoodChev}
            disabled={!canContinue}
            className={`cma-btn cma-btn-full ${canContinue ? "cma-btn-secondary" : "cma-btn-disabled"}`}
          >
            {preapprovalCopy.continueBtn[lang]}
          </button>
          
          {!canContinue && (
            <p className="cma-unlock-hint">
              {lang === "en" 
                ? "Submit your info above to unlock the secure credit application." 
                : "Envía tu información arriba para desbloquear la solicitud de crédito segura."}
            </p>
          )}

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
