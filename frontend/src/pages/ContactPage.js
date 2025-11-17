import React, { useState } from "react";
import "../styles/forms.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const ContactPage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

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
        <h1>Contact Choose Me Auto</h1>
        <p>
          Have a question? Interested in a specific vehicle? Fill out the form
          below and we'll get back to you as soon as possible.
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
              <label>Stock Number (Optional)</label>
              <input
                name="stockNumber"
                type="text"
                placeholder="e.g. P57801"
              />
            </div>

            <div className="cma-field-group">
              <label>Your Message</label>
              <textarea
                name="message"
                placeholder="Tell us how we can help you..."
                required
              />
            </div>

            <button
              type="submit"
              className="cma-btn cma-btn-primary cma-btn-full"
              disabled={submitting}
            >
              {submitting ? "Sending..." : "Send Message"}
            </button>

            {submitted && (
              <p className="cma-success-text">
                Thank you for contacting us! We've received your message and
                will respond within 24 hours.
              </p>
            )}
          </form>
        </div>

        {/* RIGHT: Contact Info */}
        <div className="cma-card cma-side-card">
          <h2>Choose Me Auto - Renton</h2>
          <p>
            Located at Good Chevrolet in Renton, Washington. We specialize in
            helping customers with bad credit, no credit, and first-time buyers.
          </p>

          <div style={{ marginTop: "1.5rem", marginBottom: "1.5rem" }}>
            <p className="cma-contact-line">
              <strong>Address:</strong>
              <br />
              Good Chevrolet Renton
              <br />
              Renton, WA 98057
            </p>
            <p className="cma-contact-line">
              <strong>Hours:</strong>
              <br />
              Monday - Saturday: 9:00 AM - 7:00 PM
              <br />
              Sunday: 10:00 AM - 6:00 PM
            </p>
          </div>

          <p className="cma-contact-note">Get in touch</p>
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

export default ContactPage;
