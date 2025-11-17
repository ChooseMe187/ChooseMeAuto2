import React from "react";
import { Link } from "react-router-dom";
import "../styles/forms.css";

const ThankYouPage = () => {
  return (
    <div className="cma-page">
      <div className="cma-page-header">
        <h1 style={{ color: "#22c55e" }}>
          You're All Set — We're Working on Your Approval ✅
        </h1>
        <p>
          Thanks for completing your secure pre-approval. Now we match you with
          the right vehicles and the right lender.
        </p>
      </div>

      <div className="cma-form-layout" style={{ maxWidth: "960px", margin: "0 auto" }}>
        {/* Main Content */}
        <div className="cma-card">
          <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#f9fafb" }}>
            What Happens Next
          </h2>

          <div style={{ marginBottom: "1.5rem" }}>
            <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
              Here's what we're doing behind the scenes:
            </p>

            <ul style={{ listStyle: "none", padding: 0 }}>
              <li style={{ marginBottom: "1rem", paddingLeft: "2rem", position: "relative" }}>
                <span style={{ position: "absolute", left: 0, color: "#22c55e" }}>🔍</span>
                <strong>Reviewing your approval</strong> with our lending partners
              </li>
              <li style={{ marginBottom: "1rem", paddingLeft: "2rem", position: "relative" }}>
                <span style={{ position: "absolute", left: 0, color: "#22c55e" }}>🚗</span>
                <strong>Matching you with vehicles</strong> that fit your budget and credit
                profile
              </li>
              <li style={{ marginBottom: "1rem", paddingLeft: "2rem", position: "relative" }}>
                <span style={{ position: "absolute", left: 0, color: "#22c55e" }}>📅</span>
                <strong>Preparing options</strong> so your time at the dealership is fast and
                focused, not all-day
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
              <strong>You'll hear from us within the next business day:</strong>
            </p>
            <p style={{ marginBottom: "0.25rem" }}>
              📞 Call or text from:{" "}
              <a href="tel:12067861751" style={{ color: "#22c55e", textDecoration: "none", fontWeight: "600" }}>
                (206) 786-1751
              </a>
            </p>
            <p style={{ marginBottom: 0 }}>
              📧 Email from:{" "}
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
              Want to Speed Things Up Even More?
            </h3>
            <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
              Call or text{" "}
              <a href="tel:12067861751" style={{ color: "#38bdf8", textDecoration: "none", fontWeight: "600" }}>
                (206) 786-1751
              </a>{" "}
              and mention you <strong>"Already Completed the Pre-Approval"</strong>.
            </p>
            <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
              We'll pull your file and give you a quick overview of what you qualify for
              and which vehicles make the most sense.
            </p>
          </div>

          <div>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "0.75rem", color: "#f9fafb" }}>
              Still Browsing? Check Out Our Inventory
            </h3>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
              <Link to="/used" className="cma-btn cma-btn-secondary">
                Shop Used Inventory
              </Link>
              <Link to="/vehicles" className="cma-btn cma-btn-secondary">
                View All Vehicles
              </Link>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="cma-card cma-side-card">
          <h2>Help Us Help You</h2>
          <p>Share a few more details so we can prepare the best options for you:</p>

          <div style={{ marginTop: "1.5rem" }}>
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                Preferred payment range:
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
                <option value="">Select range...</option>
                <option value="200-300">$200 - $300/mo</option>
                <option value="300-400">$300 - $400/mo</option>
                <option value="400-500">$400 - $500/mo</option>
                <option value="500+">$500+/mo</option>
              </select>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                Preferred vehicle type:
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
                <option value="">Select type...</option>
                <option value="SUV">SUV / Crossover</option>
                <option value="Sedan">Sedan</option>
                <option value="Truck">Truck</option>
                <option value="EV">Electric / Hybrid</option>
              </select>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                Do you have a trade-in?
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
                <option value="">Select...</option>
                <option value="yes">Yes, I have a trade-in</option>
                <option value="no">No trade-in</option>
              </select>
            </div>

            <button
              className="cma-btn cma-btn-primary cma-btn-full"
              style={{ marginTop: "1rem" }}
              onClick={() => alert("This would submit the additional info to help customize your experience")}
            >
              Submit Preferences
            </button>
          </div>

          <p className="cma-contact-note">This information helps us prepare better options for you.</p>
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
          ← Back to Home
        </Link>
      </div>
    </div>
  );
};

export default ThankYouPage;
