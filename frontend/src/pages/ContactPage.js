import React from "react";

const ContactPage = () => {
  return (
    <section style={{ padding: "2rem 0" }}>
      <h2 style={{ fontSize: "1.75rem", marginBottom: "1rem" }}>Contact Us</h2>
      <p style={{ marginBottom: "1.5rem", lineHeight: "1.6" }}>
        Plug in your contact form, phone number, and store address here.
      </p>
      
      <div style={{
        background: "#f3f4f6",
        padding: "2rem",
        borderRadius: "0.5rem",
        marginTop: "1.5rem"
      }}>
        <h3 style={{ marginBottom: "1rem" }}>Choose Me Auto - Renton</h3>
        <div style={{ lineHeight: "1.8" }}>
          <p><strong>Address:</strong> Renton, WA</p>
          <p><strong>Phone:</strong> (555) 123-4567</p>
          <p><strong>Email:</strong> info@choosemeauto.com</p>
          <p><strong>Hours:</strong> Mon-Sat 9AM-7PM, Sun 10AM-6PM</p>
        </div>
      </div>
    </section>
  );
};

export default ContactPage;