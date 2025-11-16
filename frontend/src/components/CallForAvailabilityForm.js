import React, { useState } from "react";

const CallForAvailabilityForm = ({ vehicle }) => {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    setError(null);

    const formData = new FormData(e.currentTarget);
    const payload = {
      name: formData.get("name"),
      phone: formData.get("phone"),
      email: formData.get("email"),
      contact_preference: formData.get("contact_preference"),
      message: formData.get("message"),
      stock_id: vehicle.stock_id,
      vin: vehicle.vin,
      vehicle_summary: `${vehicle.year} ${vehicle.make} ${vehicle.model} ${vehicle.trim}`,
    };

    try {
      const API_BASE = process.env.REACT_APP_BACKEND_URL || "";
      
      const res = await fetch(`${API_BASE}/api/vehicle-leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || "Failed to submit lead");
      }

      await res.json(); // Lead response from backend

      setStatus("success");
      e.target.reset();
    } catch (err) {
      console.error("Lead submission error:", err);
      setError("Something went wrong. Please try again.");
      setStatus("error");
    }
  };

  return (
    <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4">
      <h2 className="mb-2 text-sm font-semibold text-slate-900">
        Call For Availability & Price
      </h2>
      <p className="mb-4 text-xs text-slate-600">
        Tell us how to reach you and we'll confirm availability, pricing, and
        payments on this{" "}
        <span className="font-semibold">
          {vehicle.year} {vehicle.make} {vehicle.model}
        </span>{" "}
        (Stock #{vehicle.stock_id}).
      </p>

      <form onSubmit={handleSubmit} className="space-y-3 text-sm">
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">
              Full Name *
            </label>
            <input
              name="name"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder="First and last name"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">
              Mobile Number *
            </label>
            <input
              name="phone"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder="(555) 555-5555"
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-700">
            Email
          </label>
          <input
            name="email"
            type="email"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-700">
            Preferred Contact
          </label>
          <select
            name="contact_preference"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            defaultValue="text"
          >
            <option value="text">Text Message</option>
            <option value="call">Phone Call</option>
            <option value="email">Email</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-700">
            Anything we should know?
          </label>
          <textarea
            name="message"
            rows={3}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Tell us about your budget, trade-in, timeline, etc."
          />
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        {status === "success" && (
          <div className="rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
            Thank you! A Choose Me Auto specialist will reach out shortly with
            availability and pricing.
          </div>
        )}

        <button
          type="submit"
          disabled={status === "sending"}
          className="mt-1 w-full rounded-lg bg-black px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {status === "sending"
            ? "Sending..."
            : "Call For Availability & Price"}
        </button>

        <p className="mt-1 text-[11px] leading-snug text-slate-500">
          By submitting, you agree to be contacted by phone, text, or email. No
          spam. No pressure.
        </p>
      </form>
    </div>
  );
};

export default CallForAvailabilityForm;
