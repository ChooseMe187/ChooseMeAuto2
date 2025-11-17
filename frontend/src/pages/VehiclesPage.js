import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const VehiclesPage = ({ initialFilters = {} }) => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [filters, setFilters] = useState({
    make: searchParams.get("make") || "",
    model: searchParams.get("model") || "",
    min_price: searchParams.get("min_price") || "",
    max_price: searchParams.get("max_price") || "",
    body_style: searchParams.get("body_style") || "",
    condition: searchParams.get("condition") || "",
    sort: searchParams.get("sort") || "",
    ...initialFilters,
  });

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);

      try {
        const qs = new URLSearchParams();
        if (filters.make) qs.set("make", filters.make);
        if (filters.model) qs.set("model", filters.model);
        if (filters.min_price) qs.set("min_price", filters.min_price);
        if (filters.max_price) qs.set("max_price", filters.max_price);
        if (filters.body_style) qs.set("body_style", filters.body_style);
        if (filters.condition) qs.set("condition", filters.condition);

        const url =
          `${API_BASE}/api/vehicles` +
          (qs.toString() ? `?${qs.toString()}` : "");

        const res = await fetch(url);
        if (!res.ok) {
          throw new Error(await res.text());
        }
        const data = await res.json();
        setVehicles(data);
      } catch (err) {
        console.error(err);
        setError("Unable to load inventory. Please try again.");
      } finally {
        setLoading(false);
      }
    }

    // Sync URL with filters
    const newParams = {};
    if (filters.make) newParams.make = filters.make;
    if (filters.model) newParams.model = filters.model;
    if (filters.min_price) newParams.min_price = filters.min_price;
    if (filters.max_price) newParams.max_price = filters.max_price;
    if (filters.body_style) newParams.body_style = filters.body_style;
    if (filters.condition) newParams.condition = filters.condition;
    if (filters.sort) newParams.sort = filters.sort;
    setSearchParams(newParams, { replace: true });

    load();
  }, [filters, setSearchParams, API_BASE]);

  const sortedVehicles = useMemo(() => {
    const arr = [...vehicles];
    switch (filters.sort) {
      case "price_asc":
        arr.sort((a, b) => (a.price ?? Infinity) - (b.price ?? Infinity));
        break;
      case "price_desc":
        arr.sort((a, b) => (b.price ?? -Infinity) - (a.price ?? -Infinity));
        break;
      case "year_desc":
        arr.sort((a, b) => (b.year ?? 0) - (a.year ?? 0));
        break;
      case "mileage_asc":
        arr.sort(
          (a, b) => (a.mileage ?? Infinity) - (b.mileage ?? Infinity)
        );
        break;
      case "mileage_desc":
        arr.sort(
          (a, b) => (b.mileage ?? -Infinity) - (a.mileage ?? -Infinity)
        );
        break;
      default:
        break;
    }
    return arr;
  }, [vehicles, filters.sort]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleReset = () => {
    setFilters({
      make: "",
      model: "",
      min_price: "",
      max_price: "",
      body_style: "",
      condition: "",
      sort: "",
    });
    navigate("/vehicles");
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <header className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              Choose Me Auto Inventory
            </h1>
            <p className="text-sm text-slate-600">
              {loading
                ? "Loading vehicles..."
                : `Showing ${sortedVehicles.length} vehicles in stock`}
            </p>
          </div>
        </header>

        {/* Condition filter indicator */}
        {filters.condition && (
          <div className="mb-3 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            Showing <strong>{filters.condition}</strong> vehicles only.
            <button
              onClick={() => setFilters({ ...filters, condition: "" })}
              className="ml-2 text-emerald-600 underline hover:text-emerald-700"
            >
              Clear filter
            </button>
          </div>
        )}

        {/* Filter + Sort */}
        <div className="mb-6 rounded-xl bg-white p-4 shadow-sm">
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
            <input
              name="make"
              placeholder="Make"
              value={filters.make}
              onChange={handleInputChange}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            <input
              name="model"
              placeholder="Model"
              value={filters.model}
              onChange={handleInputChange}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            <input
              name="min_price"
              placeholder="Min Price"
              value={filters.min_price}
              onChange={handleInputChange}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            <input
              name="max_price"
              placeholder="Max Price"
              value={filters.max_price}
              onChange={handleInputChange}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            <input
              name="body_style"
              placeholder="Body Style (SUV, Sedan...)"
              value={filters.body_style}
              onChange={handleInputChange}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            <select
              name="sort"
              value={filters.sort}
              onChange={handleInputChange}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            >
              <option value="">Sort: Default</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="year_desc">Year: Newest First</option>
              <option value="mileage_asc">Mileage: Low to High</option>
              <option value="mileage_desc">Mileage: High to Low</option>
            </select>
          </div>

          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={() => setFilters({ ...filters })}
              className="flex-1 rounded-lg bg-black px-3 py-2 text-sm font-semibold text-white"
            >
              Apply Filters
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700"
            >
              Reset
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Results */}
        {!loading && sortedVehicles.length === 0 ? (
          <div className="rounded-xl bg-white p-6 text-center text-sm text-slate-500 shadow-sm">
            No vehicles found. Try adjusting your filters.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {sortedVehicles.map((v) => (
              <div
                key={v.stock_id}
                className="group cursor-pointer rounded-xl bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                onClick={() =>
                  navigate(`/vehicle/${encodeURIComponent(v.stock_id)}`)
                }
              >
                {/* Vehicle Image */}
                {v.image_url || (v.image_urls && v.image_urls[0]) ? (
                  <img
                    src={v.image_url || v.image_urls[0]}
                    alt={`${v.year} ${v.make} ${v.model}`}
                    className="mb-3 h-40 w-full rounded-lg bg-slate-200 object-cover"
                    loading="lazy"
                    onError={(e) => {
                      e.currentTarget.style.display = "none";
                      e.currentTarget.nextElementSibling.style.display = "block";
                    }}
                  />
                ) : null}
                <div 
                  className="mb-3 h-40 w-full rounded-lg bg-slate-200" 
                  style={{ display: (v.image_url || (v.image_urls && v.image_urls[0])) ? 'none' : 'block' }}
                />

                <div className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                  {v.year} {v.make} {v.model}
                </div>
                <div className="mb-1 text-sm font-semibold text-slate-900">
                  {v.trim}
                </div>

                <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
                  <span>{v.body_style || "Vehicle"}</span>
                  <span>Stock #{v.stock_id}</span>
                </div>

                <div className="mb-2 flex items-center justify-between">
                  <span className="text-lg font-bold text-emerald-600">
                    {v.price
                      ? v.price.toLocaleString("en-US", {
                          style: "currency",
                          currency: "USD",
                          maximumFractionDigits: 0,
                        })
                      : "Call for price"}
                  </span>
                  <span className="text-xs text-slate-500">
                    {v.mileage
                      ? `${v.mileage.toLocaleString()} mi`
                      : "Miles N/A"}
                  </span>
                </div>

                <div className="mt-2 text-center">
                  <span className="inline-flex items-center justify-center rounded-full bg-black px-3 py-1 text-xs font-semibold text-white group-hover:bg-emerald-600">
                    View Details & Schedule
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VehiclesPage;
