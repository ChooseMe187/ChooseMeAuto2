import React, { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { testdriveCopy } from "../i18n/testdrive";
import { formsCopy } from "../i18n/forms";
import "../styles/forms.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const TestDrivePage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { lang } = useLanguage();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const formData = new FormData(e.target);
    const payload = {
      type: "test-drive",
      firstName: formData.get("firstName"),
      lastName: formData.get("lastName"),
      phone: formData.get("phone"),
      email: formData.get("email"),
      stockNumber: formData.get("stockNumber"),
      preferredDate: formData.get("preferredDate"),
      preferredTime: formData.get("preferredTime"),
      notes: formData.get("notes"),
      source: "test-drive-page",
    };

    try {
      const response = await fetch(`${API_BASE}/api/vehicle-leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to submit test drive request");
      }

      console.log("Test drive lead submitted:", payload);
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
        <h1>{testdriveCopy.pageTitle[lang]}</h1>
        <p>{testdriveCopy.pageSubtitle[lang]}</p>
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
              <label>{testdriveCopy.stockLabel[lang]}</label>
              <input
                name="stockNumber"
                type="text"
                placeholder={formsCopy.stockNumberPlaceholder[lang]}
                required
              />
            </div>

            <div className="cma-field-grid">
              <div className="cma-field-group">
                <label>{testdriveCopy.preferredDate[lang]}</label>
                <input name="preferredDate" type="date" required />
              </div>
              <div className="cma-field-group">
                <label>{testdriveCopy.preferredTime[lang]}</label>
                <select name="preferredTime" required>
                  <option value="">{testdriveCopy.selectTime[lang]}</option>
                  <option value="9:00 AM">9:00 AM</option>
                  <option value="10:00 AM">10:00 AM</option>
                  <option value="11:00 AM">11:00 AM</option>
                  <option value="12:00 PM">12:00 PM</option>
                  <option value="1:00 PM">1:00 PM</option>
                  <option value="2:00 PM">2:00 PM</option>
                  <option value="3:00 PM">3:00 PM</option>
                  <option value="4:00 PM">4:00 PM</option>
                  <option value="5:00 PM">5:00 PM</option>
                  <option value="6:00 PM">6:00 PM</option>
                </select>
              </div>
            </div>

            <div className="cma-field-group">
              <label>{testdriveCopy.additionalNotes[lang]}</label>
              <textarea
                name="notes"
                placeholder={testdriveCopy.notesPlaceholder[lang]}
              />
            </div>

            <button
              type="submit"
              className="cma-btn cma-btn-primary cma-btn-full"
              disabled={submitting}
            >
              {submitting ? formsCopy.submitting[lang] : testdriveCopy.submitBtn[lang]}
            </button>

            {submitted && (
              <p className="cma-success-text">
                {testdriveCopy.successMessage[lang]}
              </p>
            )}
          </form>
        </div>

        {/* RIGHT: Location Info + Contact */}
        <div className="cma-card cma-side-card">
          <h2>{testdriveCopy.visitTitle[lang]}</h2>
          <p>{testdriveCopy.visitDesc[lang]}</p>

          <div style={{ marginTop: "1.5rem", marginBottom: "1.5rem" }}>
            <p className="cma-contact-line">
              <strong>{formsCopy.addressLabel[lang]}:</strong>
              <br />
              Choose Me Auto
              <br />
              Renton, WA 98057
            </p>
          </div>

          <p className="cma-contact-note">
            {formsCopy.questionsPhone[lang]}
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

export default TestDrivePage;
