import React, { useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { vehicleDetailCopy } from "../i18n/vehicleDetail";

const CallForAvailabilityForm = ({ vehicle }) => {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const { lang } = useLanguage();

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
        {vehicleDetailCopy.callForAvailability[lang]}
      </h2>
      <p className="mb-4 text-xs text-slate-600">
        {vehicleDetailCopy.formIntro[lang]}{" "}
        <span className="font-semibold">
          {vehicle.year} {vehicle.make} {vehicle.model}
        </span>{" "}
        ({vehicleDetailCopy.stockNumber[lang]}{vehicle.stock_id}).
      </p>

      <form onSubmit={handleSubmit} className="space-y-3 text-sm">
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">
              {vehicleDetailCopy.fullName[lang]} *
            </label>
            <input
              name="name"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder={vehicleDetailCopy.fullNamePlaceholder[lang]}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">
              {vehicleDetailCopy.mobileNumber[lang]} *
            </label>
            <input
              name="phone"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder={vehicleDetailCopy.mobilePlaceholder[lang]}
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-700">
            {vehicleDetailCopy.emailLabel[lang]}
          </label>
          <input
            name="email"
            type="email"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder={vehicleDetailCopy.emailPlaceholder[lang]}
          />
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-700">
            {vehicleDetailCopy.preferredContact[lang]}
          </label>
          <select
            name="contact_preference"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            defaultValue="text"
          >
            <option value="text">{vehicleDetailCopy.textMessage[lang]}</option>
            <option value="call">{vehicleDetailCopy.phoneCall[lang]}</option>
            <option value="email">{vehicleDetailCopy.email[lang]}</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-700">
            {vehicleDetailCopy.anythingElse[lang]}
          </label>
          <textarea
            name="message"
            rows={3}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder={vehicleDetailCopy.anythingPlaceholder[lang]}
          />
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        {status === "success" && (
          <div className="rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
            {vehicleDetailCopy.successMessage[lang]}
          </div>
        )}

        <button
          type="submit"
          disabled={status === "sending"}
          className="mt-1 w-full rounded-lg bg-black px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {status === "sending"
            ? vehicleDetailCopy.sending[lang]
            : vehicleDetailCopy.callForAvailability[lang]}
        </button>

        <p className="mt-1 text-[11px] leading-snug text-slate-500">
          {vehicleDetailCopy.disclaimer[lang]}
        </p>
      </form>
    </div>
  );
};

export default CallForAvailabilityForm;
