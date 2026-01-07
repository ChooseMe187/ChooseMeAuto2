import React, { useState, useRef } from "react";
import "../../styles/admin.css";

const AddVehicleForm = ({ token, onClose, onSuccess, editingVehicle }) => {
  const isEditing = !!editingVehicle;
  const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

  // Form state
  const [vin, setVin] = useState(editingVehicle?.vin || "");
  const [stockNumber, setStockNumber] = useState(editingVehicle?.stock_number || "");
  const [year, setYear] = useState(editingVehicle?.year?.toString() || "");
  const [make, setMake] = useState(editingVehicle?.make || "");
  const [model, setModel] = useState(editingVehicle?.model || "");
  const [trim, setTrim] = useState(editingVehicle?.trim || "");
  const [price, setPrice] = useState(editingVehicle?.price?.toString() || "");
  const [mileage, setMileage] = useState(editingVehicle?.mileage?.toString() || "");
  const [condition, setCondition] = useState(editingVehicle?.condition || "Used");
  const [bodyStyle, setBodyStyle] = useState(editingVehicle?.body_style || "");
  const [exteriorColor, setExteriorColor] = useState(editingVehicle?.exterior_color || "");
  const [interiorColor, setInteriorColor] = useState(editingVehicle?.interior_color || "");
  const [transmission, setTransmission] = useState(editingVehicle?.transmission || "");
  const [drivetrain, setDrivetrain] = useState(editingVehicle?.drivetrain || "");
  const [engine, setEngine] = useState(editingVehicle?.engine || "");
  
  // New fields
  const [carfaxUrl, setCarfaxUrl] = useState(editingVehicle?.carfax_url || "");
  const [windowStickerUrl, setWindowStickerUrl] = useState(editingVehicle?.window_sticker_url || "");
  const [callForAvailabilityEnabled, setCallForAvailabilityEnabled] = useState(
    editingVehicle?.call_for_availability_enabled || false
  );
  
  // Featured on Homepage
  const [isFeaturedHomepage, setIsFeaturedHomepage] = useState(
    editingVehicle?.is_featured_homepage || false
  );
  const [featuredRank, setFeaturedRank] = useState(
    editingVehicle?.featured_rank?.toString() || ""
  );

  const [files, setFiles] = useState([]);
  const [existingPhotos, setExistingPhotos] = useState(editingVehicle?.photo_urls || []);
  const [status, setStatus] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (!e.target.files) return;
    setFiles(Array.from(e.target.files));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus(null);
    setIsSaving(true);

    try {
      const payload = {
        vin,
        stock_number: stockNumber || null,
        year: parseInt(year),
        make,
        model,
        trim: trim || null,
        price: price ? parseFloat(price) : null,
        mileage: mileage ? parseInt(mileage) : null,
        condition,
        body_style: bodyStyle || null,
        exterior_color: exteriorColor || null,
        interior_color: interiorColor || null,
        transmission: transmission || null,
        drivetrain: drivetrain || null,
        engine: engine || null,
        carfax_url: carfaxUrl || null,
        window_sticker_url: windowStickerUrl || null,
        call_for_availability_enabled: callForAvailabilityEnabled,
        is_featured_homepage: isFeaturedHomepage,
        featured_rank: featuredRank ? parseInt(featuredRank) : null,
      };

      let vehicleId = editingVehicle?.id;

      if (isEditing) {
        // Update existing vehicle
        const response = await fetch(`${API_BASE}/api/admin/vehicles/${vehicleId}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "x-admin-token": token,
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          setStatus(data.detail || "Failed to update vehicle.");
          setIsSaving(false);
          return;
        }
      } else {
        // Create new vehicle
        const response = await fetch(`${API_BASE}/api/admin/vehicles`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-admin-token": token,
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          setStatus(data.detail || "Failed to create vehicle.");
          setIsSaving(false);
          return;
        }

        const vehicle = await response.json();
        vehicleId = vehicle.id;
      }

      // Upload photos if any
      if (files.length > 0 && vehicleId) {
        const formData = new FormData();
        files.forEach((file) => formData.append("files", file));

        const photoRes = await fetch(`${API_BASE}/api/admin/vehicles/${vehicleId}/photos`, {
          method: "POST",
          headers: { "x-admin-token": token },
          body: formData,
        });

        if (!photoRes.ok) {
          setStatus("Vehicle saved, but photo upload failed.");
          setIsSaving(false);
          onSuccess();
          return;
        }
      }

      setStatus(isEditing ? "Vehicle updated successfully!" : "Vehicle created successfully!");
      setIsSaving(false);
      
      // Call success callback after short delay
      setTimeout(() => onSuccess(), 1000);

    } catch (err) {
      console.error(err);
      setStatus("Something went wrong.");
      setIsSaving(false);
    }
  };

  return (
    <div className="admin-form-container">
      <div className="admin-form-header">
        <h2>{isEditing ? "Edit Vehicle" : "Add New Vehicle"}</h2>
        <button onClick={onClose} className="admin-close-btn">
          &times;
        </button>
      </div>

      <form onSubmit={handleSubmit} className="admin-form">
        {/* Section 1: Basics */}
        <div className="admin-form-section">
          <h3>Basic Information</h3>
          <div className="admin-form-grid-3">
            <div className="admin-field">
              <label>VIN *</label>
              <input
                value={vin}
                onChange={(e) => setVin(e.target.value)}
                required
                placeholder="17 character VIN"
              />
            </div>
            <div className="admin-field">
              <label>Stock #</label>
              <input
                value={stockNumber}
                onChange={(e) => setStockNumber(e.target.value)}
                placeholder="Auto-generated if empty"
              />
            </div>
            <div className="admin-field">
              <label>Condition *</label>
              <select value={condition} onChange={(e) => setCondition(e.target.value)}>
                <option value="Used">Used</option>
                <option value="New">New</option>
              </select>
            </div>
          </div>

          <div className="admin-form-grid-4">
            <div className="admin-field">
              <label>Year *</label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                required
                placeholder="2024"
                min="1900"
                max="2030"
              />
            </div>
            <div className="admin-field">
              <label>Make *</label>
              <input
                value={make}
                onChange={(e) => setMake(e.target.value)}
                required
                placeholder="Chevrolet"
              />
            </div>
            <div className="admin-field">
              <label>Model *</label>
              <input
                value={model}
                onChange={(e) => setModel(e.target.value)}
                required
                placeholder="Malibu"
              />
            </div>
            <div className="admin-field">
              <label>Trim</label>
              <input
                value={trim}
                onChange={(e) => setTrim(e.target.value)}
                placeholder="LT"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Pricing & Details */}
        <div className="admin-form-section">
          <h3>Pricing & Details</h3>
          <div className="admin-form-grid-4">
            <div className="admin-field">
              <label>Price ($)</label>
              <input
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="25000"
                min="0"
              />
            </div>
            <div className="admin-field">
              <label>Mileage</label>
              <input
                type="number"
                value={mileage}
                onChange={(e) => setMileage(e.target.value)}
                placeholder="35000"
                min="0"
              />
            </div>
            <div className="admin-field">
              <label>Body Style</label>
              <input
                value={bodyStyle}
                onChange={(e) => setBodyStyle(e.target.value)}
                placeholder="Sedan"
              />
            </div>
            <div className="admin-field">
              <label>Transmission</label>
              <input
                value={transmission}
                onChange={(e) => setTransmission(e.target.value)}
                placeholder="Automatic"
              />
            </div>
          </div>

          <div className="admin-form-grid-3">
            <div className="admin-field">
              <label>Exterior Color</label>
              <input
                value={exteriorColor}
                onChange={(e) => setExteriorColor(e.target.value)}
                placeholder="Black"
              />
            </div>
            <div className="admin-field">
              <label>Interior Color</label>
              <input
                value={interiorColor}
                onChange={(e) => setInteriorColor(e.target.value)}
                placeholder="Gray"
              />
            </div>
            <div className="admin-field">
              <label>Drivetrain</label>
              <input
                value={drivetrain}
                onChange={(e) => setDrivetrain(e.target.value)}
                placeholder="FWD"
              />
            </div>
          </div>

          <div className="admin-field">
            <label>Engine</label>
            <input
              value={engine}
              onChange={(e) => setEngine(e.target.value)}
              placeholder="1.5L Turbo 4-Cylinder"
            />
          </div>
        </div>

        {/* Section 3: Documents & CTAs */}
        <div className="admin-form-section">
          <h3>Documents & CTAs</h3>
          <div className="admin-form-grid-2">
            <div className="admin-field">
              <label>CARFAX URL</label>
              <input
                type="url"
                value={carfaxUrl}
                onChange={(e) => setCarfaxUrl(e.target.value)}
                placeholder="https://www.carfax.com/..."
              />
              <span className="admin-field-hint">Leave empty if not available</span>
            </div>
            <div className="admin-field">
              <label>Window Sticker URL (PDF)</label>
              <input
                type="url"
                value={windowStickerUrl}
                onChange={(e) => setWindowStickerUrl(e.target.value)}
                placeholder="https://..."
              />
              <span className="admin-field-hint">Allowed for New and Used vehicles</span>
            </div>
          </div>
          
          <div className="admin-field admin-toggle-field">
            <label className="admin-toggle-label">
              <input
                type="checkbox"
                checked={callForAvailabilityEnabled}
                onChange={(e) => setCallForAvailabilityEnabled(e.target.checked)}
              />
              <span className="admin-toggle-slider"></span>
              <span className="admin-toggle-text">Enable "Call for Availability" CTA</span>
            </label>
            <span className="admin-field-hint">When enabled, shows a prominent call-to-action on the vehicle detail page</span>
          </div>
        </div>

        {/* Section 4: Photos */}
        <div className="admin-form-section">
          <h3>Photos & Media</h3>
          
          {/* Existing Photos */}
          {existingPhotos.length > 0 && (
            <div className="admin-existing-photos">
              <label>Current Photos</label>
              <div className="admin-photo-grid">
                {existingPhotos.map((url, index) => (
                  <div key={index} className="admin-photo-item">
                    <img src={url} alt={`Photo ${index + 1}`} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload New Photos */}
          <div
            className="admin-dropzone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileChange}
              style={{ display: "none" }}
            />
            <div className="admin-dropzone-content">
              <span className="admin-dropzone-icon">📷</span>
              <p>Drag & drop photos here or click to browse</p>
              <p className="admin-dropzone-hint">Supports JPG, PNG, WebP</p>
            </div>
          </div>

          {files.length > 0 && (
            <div className="admin-selected-files">
              <p>{files.length} file(s) selected:</p>
              <ul>
                {files.map((file, i) => (
                  <li key={i}>{file.name}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="admin-form-actions">
          {status && (
            <p className={status.includes("success") ? "admin-success" : "admin-error"}>
              {status}
            </p>
          )}
          <div className="admin-form-buttons">
            <button type="button" onClick={onClose} className="admin-btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={isSaving} className="admin-btn-primary">
              {isSaving ? "Saving..." : isEditing ? "Update Vehicle" : "Save Vehicle"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default AddVehicleForm;
