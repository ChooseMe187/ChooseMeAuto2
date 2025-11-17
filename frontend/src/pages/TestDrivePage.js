import React, { useState } from "react";
import "../styles/forms.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const TestDrivePage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

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
        <h1>Schedule a Test Drive</h1>
        <p>
          Experience your dream vehicle in person. Fill out the form below and
          we'll have it ready for you at our Renton location.
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
                required
              />
            </div>

            <div className="cma-field-grid">
              <div className="cma-field-group">
                <label>Preferred Date</label>
                <input name="preferredDate" type="date" required />
              </div>
              <div className="cma-field-group">
                <label>Preferred Time</label>
                <select name="preferredTime" required>
                  <option value="">Select time...</option>
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
              <label>Additional Notes (Optional)</label>
              <textarea
                name="notes"
                placeholder="Any specific questions or requirements?"
              />
            </div>

            <button
              type="submit"
              className="cma-btn cma-btn-primary cma-btn-full"
              disabled={submitting}
            >
              {submitting ? "Submitting..." : "Schedule Test Drive"}
            </button>

            {submitted && (
              <p className="cma-success-text">
                Thank you! We've received your test drive request. Our team will
                contact you shortly to confirm your appointment.
              </p>
            )}
          </form>
        </div>

        {/* RIGHT: Location Info + Contact */}
        <div className="cma-card cma-side-card">
          <h2>Visit Us in Renton</h2>
          <p>
            We're located at Good Chevrolet in Renton, Washington. Our friendly
            sales team is here to help you find the perfect vehicle.
          </p>

          <div style={{ marginTop: "1.5rem", marginBottom: "1.5rem" }}>
            <p className="cma-contact-line">
              <strong>Address:</strong>
              <br />
              Good Chevrolet Renton
              <br />
              Renton, WA 98057
            </p>
          </div>

          <p className="cma-contact-note">
            Questions? Prefer to schedule by phone?
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

export default TestDrivePage;
