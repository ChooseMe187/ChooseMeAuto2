import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import CallForAvailabilityForm from "../components/CallForAvailabilityForm";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const VehicleDetailPage = () => {
  const { stock_id } = useParams();
  const navigate = useNavigate();

  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!stock_id) return;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/api/vehicles/${stock_id}`);
        if (res.status === 404) {
          setError("Vehicle not found.");
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
  }, [stock_id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p className="text-sm text-slate-600">Loading vehicle...</p>
      </div>
    );
  }

  if (error || !vehicle) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="rounded-xl bg-white p-8 text-center shadow-sm">
          <h1 className="mb-2 text-2xl font-bold">Vehicle not available</h1>
          <p className="mb-4 text-sm text-slate-600">
            {error ||
              "This vehicle may have been sold or is no longer in our active inventory."}
          </p>
          <button
            onClick={() => navigate("/vehicles")}
            className="rounded-lg bg-black px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-600"
          >
            Back to Inventory
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
  } = vehicle;

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-4 text-sm">
          <button
            onClick={() => navigate("/vehicles")}
            className="text-slate-500 hover:text-slate-800"
          >
            ← Back to all vehicles
          </button>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Left: Image Gallery */}
          <div className="rounded-xl bg-white p-4 shadow-sm">
            {(() => {
              const allImages = [
                vehicle.image_url,
                ...(vehicle.image_urls || [])
              ].filter(Boolean);

              if (allImages.length > 0) {
                return (
                  <>
                    <img
                      src={allImages[0]}
                      alt={`${year} ${make} ${model}`}
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
                            alt={`${year} ${make} ${model} - ${idx + 2}`}
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
                      Photos coming soon. This vehicle currently has no images in the
                      inventory file.
                    </p>
                  </>
                );
              }
            })()}
          </div>

          {/* Right: Info */}
          <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                {year} {make} {model}
              </h1>
              <p className="text-sm text-slate-600">{trim}</p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs uppercase text-slate-500">Price</div>
                <div className="text-2xl font-bold text-emerald-600">
                  {price
                    ? price.toLocaleString("en-US", {
                        style: "currency",
                        currency: "USD",
                        maximumFractionDigits: 0,
                      })
                    : "Call for price"}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">Mileage</div>
                <div className="text-base font-semibold text-slate-800">
                  {mileage
                    ? `${mileage.toLocaleString()} mi`
                    : "Miles N/A"}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <div className="text-xs uppercase text-slate-500">
                  Body Style
                </div>
                <div className="font-medium text-slate-800">
                  {body_style || "N/A"}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">
                  Drivetrain
                </div>
                <div className="font-medium text-slate-800">
                  {drivetrain || "N/A"}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">
                  Exterior Color
                </div>
                <div className="font-medium text-slate-800">
                  {exterior_color || "N/A"}
                </div>
              </div>
              <div>
                <div className="text-xs uppercase text-slate-500">
                  Interior Color
                </div>
                <div className="font-medium text-slate-800">
                  {interior_color || "N/A"}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs text-slate-500">
              <div>VIN: {vin}</div>
              <div>Stock #: {sid}</div>
            </div>

            <div className="mt-4 space-y-2">
              <button className="w-full rounded-lg bg-black px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-600">
                Schedule Test Drive
              </button>
              <a
                href="#call-for-availability"
                className="flex w-full items-center justify-center rounded-lg border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-800 hover:border-emerald-500"
              >
                Call For Availability & Price
              </a>
            </div>
          </div>
        </div>

        <div id="call-for-availability">
          <CallForAvailabilityForm vehicle={vehicle} />
        </div>
      </div>
    </div>
  );
};

export default VehicleDetailPage;
