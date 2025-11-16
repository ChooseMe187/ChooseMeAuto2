import React from "react";

const TestDrivePage = () => {
  return (
    <section style={{ padding: "2rem 0" }}>
      <h2 style={{ fontSize: "1.75rem", marginBottom: "1rem" }}>Schedule a Test Drive</h2>
      <p style={{ marginBottom: "1.5rem", lineHeight: "1.6" }}>
        This can later be tied to a real scheduling form. For now, it gives
        customers a clear next step after browsing inventory.
      </p>
      
      <div style={{
        background: "#f3f4f6",
        padding: "2rem",
        borderRadius: "0.5rem",
        marginTop: "1.5rem"
      }}>
        <h3 style={{ marginBottom: "1rem" }}>Ready to Test Drive?</h3>
        <p style={{ lineHeight: "1.6", marginBottom: "1rem" }}>
          Schedule a test drive for any vehicle in our inventory. We'll have it ready for you!
        </p>
        <ul style={{ lineHeight: "1.8", paddingLeft: "1.5rem" }}>
          <li>Browse our <a href="/vehicles" style={{ color: "#2563eb" }}>inventory</a></li>
          <li>Call us at (555) 123-4567</li>
          <li>Or visit us in Renton, WA</li>
        </ul>
      </div>
    </section>
  );
};

export default TestDrivePage;