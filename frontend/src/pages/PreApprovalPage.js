import React from "react";

const PreApprovalPage = () => {
  return (
    <section style={{ padding: "2rem 0" }}>
      <h2 style={{ fontSize: "1.75rem", marginBottom: "1rem" }}>Get Pre-Approved</h2>
      <p style={{ marginBottom: "1rem", lineHeight: "1.6" }}>
        Drop your finance application link or embedded form here (Good
        Chevrolet / lender portal). This is the core CTA for bad-credit and
        first-time buyers.
      </p>
      <div style={{
        background: "#f3f4f6",
        padding: "2rem",
        borderRadius: "0.5rem",
        marginTop: "1.5rem"
      }}>
        <h3 style={{ marginBottom: "1rem" }}>Why Get Pre-Approved?</h3>
        <ul style={{ lineHeight: "1.8", paddingLeft: "1.5rem" }}>
          <li>Know your budget before you shop</li>
          <li>Faster approval process</li>
          <li>Better negotiating power</li>
          <li>Bad credit? No credit? We can help!</li>
        </ul>
      </div>
    </section>
  );
};

export default PreApprovalPage;