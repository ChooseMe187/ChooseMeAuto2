import React, { useState, useRef } from "react";
import "../../styles/admin.css";

const MAX_FILE_SIZE_MB = 8;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];

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
  
  // Document fields
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

  // Photo state - now supports images[] array format
  const [files, setFiles] = useState([]);
  const [existingImages, setExistingImages] = useState(
    editingVehicle?.images || editingVehicle?.photo_urls?.map((url, i) => ({
      url,
      is_primary: i === 0,
      upload_id: `legacy-${i}`,
    })) || []
  );
  const [uploadProgress, setUploadProgress] = useState(null);
  const [status, setStatus] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef(null);

  // Validate files before adding
  const validateFiles = (fileList) => {
    const errors = [];
    const validFiles = [];

    for (const file of fileList) {
      // Check type
      if (!ALLOWED_TYPES.includes(file.type)) {
        errors.push(`${file.name}: Invalid type. Use JPG, PNG, or WebP.`);
        continue;
      }

      // Check size
      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > MAX_FILE_SIZE_MB) {
        errors.push(`${file.name}: Too large (${sizeMB.toFixed(1)}MB). Max ${MAX_FILE_SIZE_MB}MB.`);
        continue;
      }

      validFiles.push(file);
    }

    if (errors.length > 0) {
      setStatus(`⚠️ ${errors.join(' ')}`);
    }

    return validFiles;
  };

  const handleFileChange = (e) => {
    if (!e.target.files) return;
    const validFiles = validateFiles(Array.from(e.target.files));
    setFiles((prev) => [...prev, ...validFiles]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const validFiles = validateFiles(Array.from(e.dataTransfer.files));
      setFiles((prev) => [...prev, ...validFiles]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const removeSelectedFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const deleteExistingPhoto = async (imageIndex) => {
    if (!editingVehicle?.id) return;
    
    try {
      const res = await fetch(
        `${API_BASE}/api/admin/vehicles/${editingVehicle.id}/photos/${imageIndex}`,
        {
          method: "DELETE",
          headers: { "x-admin-token": token },
        }
      );
      
      if (res.ok) {
        const data = await res.json();
        setExistingImages(data.images || []);
        setStatus("✅ Photo deleted");
      } else {
        setStatus("❌ Failed to delete photo");
      }
    } catch (err) {
      setStatus("❌ Error deleting photo");
    }
  };

  const setPrimaryPhoto = async (imageIndex) => {
    if (!editingVehicle?.id) return;
    
    try {
      const res = await fetch(
        `${API_BASE}/api/admin/vehicles/${editingVehicle.id}/photos/${imageIndex}/primary`,
        {
          method: "PATCH",
          headers: { "x-admin-token": token },
        }
      );
      
      if (res.ok) {
        const data = await res.json();
        setExistingImages(data.images || []);
        setStatus("✅ Primary photo updated");
      } else {
        setStatus("❌ Failed to set primary photo");
      }
    } catch (err) {
      setStatus("❌ Error setting primary photo");
    }
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
          setStatus(`❌ ${data.detail || "Failed to update vehicle."}`);
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
          setStatus(`❌ ${data.detail || "Failed to create vehicle."}`);
          setIsSaving(false);
          return;
        }

        const vehicle = await response.json();
        vehicleId = vehicle.id;
      }

      // Upload photos if any
      if (files.length > 0 && vehicleId) {
        setUploadProgress(`Uploading ${files.length} photo(s)...`);
        
        const formData = new FormData();
        files.forEach((file) => formData.append("files", file));

        const photoRes = await fetch(`${API_BASE}/api/admin/vehicles/${vehicleId}/photos`, {
          method: "POST",
          headers: { "x-admin-token": token },
          body: formData,
        });

        if (!photoRes.ok) {
          const errorData = await photoRes.json().catch(() => ({}));
          setStatus(`⚠️ Vehicle saved, but photo upload failed: ${errorData.detail?.message || 'Unknown error'}`);
          setUploadProgress(null);
          setIsSaving(false);
          onSuccess();
          return;
        }

        const photoData = await photoRes.json();
        setUploadProgress(null);
        
        if (photoData.errors?.length > 0) {
          setStatus(`⚠️ ${photoData.message}. Some files had errors.`);
        }
      }

      setStatus(isEditing ? "✅ Vehicle updated successfully!" : "✅ Vehicle created successfully!");
      setIsSaving(false);
      
      // Call success callback after short delay
      setTimeout(() => onSuccess(), 1000);

    } catch (err) {
      console.error(err);
      setStatus("❌ Something went wrong. Please try again.");
      setUploadProgress(null);
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

        {/* Section 4: Homepage Featured */}
        <div className="admin-form-section">
          <h3>Homepage Feature</h3>
          <div className="admin-field admin-toggle-field">
            <label className="admin-toggle-label">
              <input
                type="checkbox"
                checked={isFeaturedHomepage}
                onChange={(e) => setIsFeaturedHomepage(e.target.checked)}
              />
              <span className="admin-toggle-slider"></span>
              <span className="admin-toggle-text">Feature on Homepage</span>
            </label>
            <span className="admin-field-hint">Display this vehicle in the Featured Vehicles section on the homepage</span>
          </div>
          
          {isFeaturedHomepage && (
            <div className="admin-field" style={{ marginTop: "1rem" }}>
              <label>Display Order (Optional)</label>
              <input
                type="number"
                value={featuredRank}
                onChange={(e) => setFeaturedRank(e.target.value)}
                placeholder="1, 2, 3... (lower = first)"
                min="1"
                max="99"
                style={{ maxWidth: "200px" }}
              />
              <span className="admin-field-hint">Lower numbers appear first. Leave empty for default ordering.</span>
            </div>
          )}
        </div>

        {/* Section 5: Photos */}
        <div className="admin-form-section">
          <h3>Photos & Media</h3>
          <p className="admin-field-hint" style={{ marginBottom: "1rem" }}>
            Supported formats: JPG, PNG, WebP (max {MAX_FILE_SIZE_MB}MB each). 
            Images are automatically optimized for web display.
          </p>
          
          {/* Existing Photos */}
          {existingImages.length > 0 && (
            <div className="admin-existing-photos">
              <label>Current Photos ({existingImages.length})</label>
              <div className="admin-photo-grid">
                {existingImages.map((img, index) => {
                  const url = typeof img === 'string' ? img : img.url;
                  const isPrimary = typeof img === 'object' && img.is_primary;
                  
                  return (
                    <div key={index} className={`admin-photo-item ${isPrimary ? 'is-primary' : ''}`}>
                      <img src={url} alt={`Photo ${index + 1}`} />
                      {isPrimary && <span className="primary-badge">Primary</span>}
                      <div className="admin-photo-actions">
                        {!isPrimary && (
                          <button
                            type="button"
                            className="photo-action-btn"
                            onClick={() => setPrimaryPhoto(index)}
                            title="Set as primary"
                          >
                            ⭐
                          </button>
                        )}
                        <button
                          type="button"
                          className="photo-action-btn delete"
                          onClick={() => deleteExistingPhoto(index)}
                          title="Delete photo"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  );
                })}
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
              accept="image/jpeg,image/png,image/webp,image/gif"
              multiple
              onChange={handleFileChange}
              style={{ display: "none" }}
            />
            <div className="admin-dropzone-content">
              <span className="admin-dropzone-icon">📷</span>
              <p>Drag & drop photos here or click to browse</p>
              <p className="admin-dropzone-hint">
                JPG, PNG, WebP • Max {MAX_FILE_SIZE_MB}MB each
              </p>
            </div>
          </div>

          {files.length > 0 && (
            <div className="admin-selected-files">
              <p><strong>{files.length} file(s) ready to upload:</strong></p>
              <ul>
                {files.map((file, i) => (
                  <li key={i}>
                    {file.name} ({(file.size / (1024 * 1024)).toFixed(2)}MB)
                    <button
                      type="button"
                      className="remove-file-btn"
                      onClick={() => removeSelectedFile(i)}
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="admin-form-actions">
          {uploadProgress && (
            <p className="admin-progress">{uploadProgress}</p>
          )}
          {status && (
            <p className={status.includes("✅") ? "admin-success" : status.includes("⚠️") ? "admin-warning" : "admin-error"}>
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
