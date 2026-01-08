import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { vehicleDetailCopy } from "../i18n/vehicleDetail";
import CallForAvailabilityForm from "../components/CallForAvailabilityForm";
import { trackGetApprovedClick, trackHoldVehicleSubmit } from "../utils/analytics";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";
const DEALER_PHONE = "(206) 786-1751";
const GOOD_CHEV_CREDIT_URL = "https://www.goodchevrolet.com/finance/apply-for-financing.htm";

const VehicleDetailPage = () => {
  const { stock_id } = useParams();
  const navigate = useNavigate();
  const { lang } = useLanguage();

  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAvailabilityModal, setShowAvailabilityModal] = useState(false);
  const [showHoldModal, setShowHoldModal] = useState(false);

  useEffect(() => {
    if (!stock_id) return;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/api/vehicles/${stock_id}`);
        if (res.status === 404) {
          setError(vehicleDetailCopy.notAvailableDesc[lang]);
          setVehicle(null);
        } else if (!res.ok) {
          throw new Error(await res.text());
        } else {
          const data = await res.json();
          setVehicle(data);
        }
      } catch (err) {
        console.error(err);
        setError("Unable to load vehicle. Please try again.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [stock_id, lang]);

  // Detect mobile device
  const isMobile = typeof window !== "undefined" && window.innerWidth < 768;

  const handleCallClick = () => {
    if (isMobile) {
      window.location.href = `tel:${DEALER_PHONE.replace(/[^\d+]/g, "")}`;
    } else {
      setShowAvailabilityModal(true);
    }
  };

  // F1: Get Approved for THIS Vehicle - passes VIN info to credit app
  const handleGetApproved = () => {
    if (!vehicle) return;
    
    // Track get_approved_click event
    trackGetApprovedClick({
      vehicleId: vehicle.stock_id || stock_id,
      vin: vehicle.vin || '',
      sourcePage: 'vdp',
      ctaLocation: 'primary',
    });
    
    // Build URL with vehicle context
    const params = new URLSearchParams({
      vin: vehicle.vin || "",
      vehicle: `${vehicle.year} ${vehicle.make} ${vehicle.model}`,
      source: "vdp",
      stock: vehicle.stock_id || stock_id,
    });
    
    // Navigate to pre-approval page with vehicle context
    navigate(`/preapproved?${params.toString()}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p className="text-sm text-slate-600">{vehicleDetailCopy.loading[lang]}</p>
      </div>
    );
  }

  if (error || !vehicle) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="rounded-xl bg-white p-8 text-center shadow-sm">
          <h1 className="mb-2 text-2xl font-bold">{vehicleDetailCopy.notAvailable[lang]}</h1>
          <p className="mb-4 text-sm text-slate-600">
            {error || vehicleDetailCopy.notAvailableDesc[lang]}
          </p>
          <button
            onClick={() => navigate("/vehicles")}
            className="rounded-lg bg-black px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-600"
          >
            {vehicleDetailCopy.backToInventory[lang]}
          </button>
        </div>
      </div>
    );
  }

  const {
    year,
    make,
    model,
    trim,
    price,
    mileage,
    body_style,
    drivetrain,
    exterior_color,
    interior_color,
    vin,
    stock_id: sid,
    carfax_url,
    window_sticker_url,
    call_for_availability_enabled,
  } = vehicle;

  const vehicleTitle = `${year} ${make} ${model}`;

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-4 text-sm">
          <button
            onClick={() => navigate("/vehicles")}
            className="text-slate-500 hover:text-slate-800"
          >
            {vehicleDetailCopy.backToVehicles[lang]}
          </button>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Left: Image Gallery */}
          <div className="rounded-xl bg-white p-4 shadow-sm">
            {(() => {
              const allImages = [
                vehicle.image_url,
                ...(vehicle.image_urls || []),
                ...(vehicle.photo_urls || [])
              ].filter(Boolean);

              if (allImages.length > 0) {
                return (
                  <>
                    <img
                      src={allImages[0]}
                      alt={vehicleTitle}
                      className="mb-3 h-64 w-full rounded-lg bg-slate-200 object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />

                    {allImages.length > 1 && (
                      <div className="flex gap-2 overflow-x-auto">
                        {allImages.slice(1).map((img, idx) => (
                          <img
                            key={idx}
                            src={img}
                            alt={`${vehicleTitle} - ${idx + 2}`}
                            className="h-16 w-24 flex-shrink-0 rounded-md bg-slate-200 object-cover cursor-pointer hover:opacity-75 transition"
                            onError={(e) => {
                              e.currentTarget.style.display = "none";
                            }}
                          />
                        ))}
                      </div>
                    )}
                  </>
                );
              } else {
                return (
                  <>
                    <div className="mb-3 h-64 w-full rounded-lg bg-slate-200" />
                    <p className="text-xs text-slate-500">
                      {vehicleDetailCopy.photosComingSoon[lang]}
                    </p>
                  </>
                );
              }
            })()}
          </div>

          {/* Right: Info */}
          <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">{vehicleTitle}</h1>
              <p className="text-sm text-slate-600">{trim}</p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs uppercase text-slate-500">{vehicleDetailCopy.price[lang]}</div>
                <div className="text-2xl font-bold text-emerald-600">
                  {price
                    ? price.toLocaleString("en-US", {
                        style: "currency",
                        currency: "USD",
                        maximumFractionDigits: 0,
                      })
                    : vehicleDetailCopy.callForPrice[lang]}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">{vehicleDetailCopy.mileage[lang]}</div>
                <div className="text-base font-semibold text-slate-800">
                  {mileage
                    ? `${mileage.toLocaleString()} mi`
                    : vehicleDetailCopy.milesNA[lang]}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <div className="text-xs uppercase text-slate-500">
                  {vehicleDetailCopy.bodyStyle[lang]}
                </div>
                <div className="font-medium text-slate-800">
                  {body_style || vehicleDetailCopy.na[lang]}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">
                  {vehicleDetailCopy.drivetrain[lang]}
                </div>
                <div className="font-medium text-slate-800">
                  {drivetrain || vehicleDetailCopy.na[lang]}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">
                  {vehicleDetailCopy.exteriorColor[lang]}
                </div>
                <div className="font-medium text-slate-800">
                  {exterior_color || vehicleDetailCopy.na[lang]}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">
                  {vehicleDetailCopy.interiorColor[lang]}
                </div>
                <div className="font-medium text-slate-800">
                  {interior_color || vehicleDetailCopy.na[lang]}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs text-slate-500">
              <div>{vehicleDetailCopy.vin[lang]}: {vin}</div>
              <div>{vehicleDetailCopy.stockLabel[lang]} #: {sid}</div>
            </div>

            {/* Document Buttons */}
            <div className="flex flex-wrap gap-2">
              {window_sticker_url && (
                <a
                  href={window_sticker_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:border-emerald-500 hover:text-emerald-600 transition"
                >
                  <span>📄</span>
                  {vehicleDetailCopy.viewWindowSticker[lang]}
                </a>
              )}
              {carfax_url ? (
                <a
                  href={carfax_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:border-emerald-500 hover:text-emerald-600 transition"
                >
                  <span>🔍</span>
                  {vehicleDetailCopy.viewCarfax[lang]}
                </a>
              ) : (
                <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500">
                  <span>🔍</span>
                  {vehicleDetailCopy.carfaxOnRequest[lang]}
                </div>
              )}
            </div>

            {/* F1: VIN-Specific CTAs */}
            <div className="mt-4 space-y-3">
              {/* Primary CTA: Get Approved for THIS Vehicle */}
              <button 
                onClick={handleGetApproved}
                className="w-full rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-700 transition flex items-center justify-center gap-2"
              >
                <span>✓</span>
                {lang === "es" 
                  ? `Pre-Aprobación para ${year} ${make} ${model}`
                  : `Get Approved for This ${year} ${make} ${model}`
                }
              </button>

              {/* Secondary CTA: Hold This Vehicle */}
              <button 
                onClick={() => setShowHoldModal(true)}
                className="w-full rounded-lg bg-black px-4 py-3 text-sm font-semibold text-white hover:bg-slate-800 transition flex items-center justify-center gap-2"
              >
                <span>🔒</span>
                {lang === "es" ? "Reservar Este Vehículo" : "Hold This Vehicle"}
              </button>

              {/* Test Drive */}
              <button 
                onClick={() => navigate(`/test-drive?vehicle=${encodeURIComponent(vehicleTitle)}&vin=${vin}&stock=${sid}`)}
                className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-800 hover:border-emerald-500 transition"
              >
                {vehicleDetailCopy.scheduleTestDrive[lang]}
              </button>
              
              {/* Call for Availability - Conditional based on toggle */}
              {call_for_availability_enabled && (
                <>
                  {/* Mobile: Click-to-call */}
                  <a
                    href={`tel:${DEALER_PHONE.replace(/[^\d+]/g, "")}`}
                    className="flex w-full items-center justify-center gap-2 rounded-lg border border-emerald-500 px-4 py-3 text-sm font-semibold text-emerald-600 hover:bg-emerald-50 md:hidden"
                  >
                    <span>📞</span>
                    {vehicleDetailCopy.callNow[lang]}: {DEALER_PHONE}
                  </a>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Availability Modal */}
        {showAvailabilityModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="relative w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
              <button
                onClick={() => setShowAvailabilityModal(false)}
                className="absolute right-4 top-4 text-2xl text-slate-400 hover:text-slate-600"
              >
                &times;
              </button>
              <AvailabilityLeadForm 
                vehicle={vehicle} 
                onSuccess={() => setShowAvailabilityModal(false)} 
              />
            </div>
          </div>
        )}

        {/* F2: Hold Vehicle Modal */}
        {showHoldModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="relative w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
              <button
                onClick={() => setShowHoldModal(false)}
                className="absolute right-4 top-4 text-2xl text-slate-400 hover:text-slate-600"
              >
                &times;
              </button>
              <HoldVehicleForm 
                vehicle={vehicle} 
                onSuccess={() => setShowHoldModal(false)} 
              />
            </div>
          </div>
        )}

        {/* Inline Form (when toggle is off, show at bottom) */}
        {!call_for_availability_enabled && (
          <div id="call-for-availability" className="mt-6">
            <CallForAvailabilityForm vehicle={vehicle} />
          </div>
        )}
      </div>
    </div>
  );
};

// Availability Lead Form Component (for modal popup)
const AvailabilityLeadForm = ({ vehicle, onSuccess }) => {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const { lang } = useLanguage();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    setError(null);

    const formData = new FormData(e.currentTarget);
    const payload = {
      lead_type: "availability",
      first_name: formData.get("first_name"),
      last_name: formData.get("last_name"),
      phone: formData.get("phone"),
      email: formData.get("email"),
      message: formData.get("message"),
      vehicle_id: vehicle.stock_id || vehicle.id,
      vin: vehicle.vin,
      vehicle_summary: `${vehicle.year} ${vehicle.make} ${vehicle.model}`,
      source: "vdp_availability",
    };

    try {
      const res = await fetch(`${API_BASE}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("Failed to submit");
      }

      setStatus("success");
      setTimeout(() => {
        onSuccess?.();
      }, 2000);
    } catch (err) {
      console.error(err);
      setError(lang === "es" ? "Error al enviar. Intenta de nuevo." : "Something went wrong. Please try again.");
      setStatus("error");
    }
  };

  return (
    <div>
      <h2 className="mb-2 text-lg font-bold text-slate-900">
        {vehicleDetailCopy.requestAvailability[lang]}
      </h2>
      <p className="mb-4 text-sm text-slate-600">
        {vehicle.year} {vehicle.make} {vehicle.model} {vehicle.trim}
      </p>

      {status === "success" ? (
        <div className="rounded-lg bg-emerald-50 p-4 text-center text-emerald-700">
          {vehicleDetailCopy.successMessage[lang]}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">
                {lang === "es" ? "Nombre" : "First Name"} *
              </label>
              <input
                name="first_name"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">
                {lang === "es" ? "Apellido" : "Last Name"} *
              </label>
              <input
                name="last_name"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">
              {vehicleDetailCopy.mobileNumber[lang]} *
            </label>
            <input
              name="phone"
              type="tel"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder={vehicleDetailCopy.mobilePlaceholder[lang]}
            />
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
              {vehicleDetailCopy.anythingElse[lang]}
            </label>
            <textarea
              name="message"
              rows={2}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>

          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={status === "sending"}
            className="w-full rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            {status === "sending" ? vehicleDetailCopy.sending[lang] : vehicleDetailCopy.requestAvailability[lang]}
          </button>
        </form>
      )}
    </div>
  );
};

// F2: Hold Vehicle Form Component
const HoldVehicleForm = ({ vehicle, onSuccess }) => {
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const { lang } = useLanguage();

  const copy = {
    title: { en: "Hold This Vehicle", es: "Reservar Este Vehículo" },
    subtitle: { en: "Reserve this vehicle for review. Our team will reach out within 24 hours.", es: "Reserva este vehículo para revisión. Nuestro equipo te contactará en 24 horas." },
    firstName: { en: "First Name", es: "Nombre" },
    lastName: { en: "Last Name", es: "Apellido" },
    phone: { en: "Phone", es: "Teléfono" },
    email: { en: "Email", es: "Correo" },
    message: { en: "Message (optional)", es: "Mensaje (opcional)" },
    messagePlaceholder: { en: "Any questions or notes...", es: "Preguntas o notas..." },
    submit: { en: "Reserve for Review", es: "Reservar para Revisión" },
    sending: { en: "Sending...", es: "Enviando..." },
    success: { en: "✅ Vehicle reserved! We'll contact you within 24 hours.", es: "✅ ¡Vehículo reservado! Te contactaremos en 24 horas." },
    error: { en: "Something went wrong. Please try again.", es: "Error al enviar. Intenta de nuevo." },
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    setError(null);

    const formData = new FormData(e.currentTarget);
    const payload = {
      lead_type: "hold",
      first_name: formData.get("first_name"),
      last_name: formData.get("last_name"),
      phone: formData.get("phone"),
      email: formData.get("email"),
      message: formData.get("message") || "Vehicle hold request",
      vehicle_id: vehicle.stock_id || vehicle.id,
      vin: vehicle.vin,
      vehicle_summary: `${vehicle.year} ${vehicle.make} ${vehicle.model}`,
      source: "vdp_hold",
    };

    try {
      const res = await fetch(`${API_BASE}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error("Failed to submit");
      }

      setStatus("success");
      setTimeout(() => {
        onSuccess?.();
      }, 3000);
    } catch (err) {
      console.error(err);
      setError(copy.error[lang]);
      setStatus("error");
    }
  };

  return (
    <div>
      <h2 className="mb-1 text-lg font-bold text-slate-900 flex items-center gap-2">
        <span>🔒</span>
        {copy.title[lang]}
      </h2>
      <p className="mb-3 text-sm text-slate-600">
        {vehicle.year} {vehicle.make} {vehicle.model} {vehicle.trim}
      </p>
      <p className="mb-4 text-xs text-slate-500 bg-slate-50 p-2 rounded">
        {copy.subtitle[lang]}
      </p>

      {status === "success" ? (
        <div className="rounded-lg bg-emerald-50 p-4 text-center text-emerald-700">
          {copy.success[lang]}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">
                {copy.firstName[lang]} *
              </label>
              <input
                name="first_name"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">
                {copy.lastName[lang]} *
              </label>
              <input
                name="last_name"
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">
              {copy.phone[lang]} *
            </label>
            <input
              name="phone"
              type="tel"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder="(555) 123-4567"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">
              {copy.email[lang]}
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
              {copy.message[lang]}
            </label>
            <textarea
              name="message"
              rows={2}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder={copy.messagePlaceholder[lang]}
            />
          </div>

          {error && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={status === "sending"}
            className="w-full rounded-lg bg-black px-4 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {status === "sending" ? copy.sending[lang] : copy.submit[lang]}
          </button>
        </form>
      )}
    </div>
  );
};

export default VehicleDetailPage;
