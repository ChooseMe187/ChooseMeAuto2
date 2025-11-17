import React, { useState } from "react";
import "../styles/forms.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const PreApprovalPage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

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
        <h1>Get Pre-Approved with Choose Me Auto</h1>
        <p>
          Step 1: Tell us how to reach you. Step 2: Complete the secure bank
          application. We'll help you every step of the way&mdash;even with bad
          credit, no credit, or first-time buying.
        </p>
      </div>

      <div className="cma-form-layout">
        {/* LEFT: FORM */}
        <div className="cma-card">
          <form onSubmit={handleSubmit}>
            <div className="cma-field-grid">
              <div className="cma-field-group">
                <label>First Name</label>
                <input name="firstName" type="text" required />
              </div>
              <div className="cma-field-group">
                <label>Last Name</label>
                <input name="lastName" type="text" required />
              </div>
            </div>

            <div className="cma-field-group">
              <label>Phone Number</label>
              <input name="phone" type="tel" required />
            </div>

            <div className="cma-field-group">
              <label>Email Address</label>
              <input name="email" type="email" required />
            </div>

            <div className="cma-field-group">
              <label>Stock Number (Vehicle You're Interested In)</label>
              <input
                name="stockNumber"
                type="text"
                placeholder="e.g. P57801"
              />
            </div>

            <button
              type="submit"
              className="cma-btn cma-btn-primary cma-btn-full"
              disabled={submitting}
            >
              {submitting ? "Submitting..." : "Submit Info First"}
            </button>

            {submitted && (
              <p className="cma-success-text">
                Thank you! We've received your info. Next, complete the secure
                pre-approval application so we can lock in terms for you.
              </p>
            )}
          </form>
        </div>

        {/* RIGHT: "Step 2" + GoodChev Link + Contact */}
        <div className="cma-card cma-side-card">
          <h2>Step 2: Complete the Secure Bank Application</h2>
          <p>
            After you submit your info, click below to finish the official
            pre-approval on Good Chevrolet&apos;s secure finance page.
          </p>

          <a
            href="https://www.goodchev.com/preapproved.aspx"
            target="_blank"
            rel="noreferrer"
            className="cma-btn cma-btn-secondary cma-btn-full"
          >
            Continue to Full Pre-Approval Application
          </a>

          <p className="cma-contact-note">
            Prefer to do this over the phone?
          </p>
          <p className="cma-contact-line">
            Call:{" "}
            <a href="tel:12067861751" className="cma-link-strong">
              (206) 786-1751
            </a>
          </p>
          <p className="cma-contact-line">
            Email:{" "}
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
