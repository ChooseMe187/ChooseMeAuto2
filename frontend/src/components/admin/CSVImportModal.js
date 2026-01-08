import React, { useState, useRef } from "react";
import "../../styles/admin.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

const CSVImportModal = ({ token, onClose, onSuccess }) => {
  const [step, setStep] = useState("upload"); // upload, preview, importing, complete
  const [file, setFile] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Handle file selection
  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
        setError("Please select a CSV file");
        return;
      }
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError("File too large. Maximum size is 5MB");
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  // Preview CSV (dry run)
  const handlePreview = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch(`${API_BASE}/api/admin/vehicles/import-csv?dry_run=true`, {
        method: "POST",
        headers: { "x-admin-token": token },
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || "Failed to preview CSV");
      }
      
      setPreviewData(data);
      setStep("preview");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Execute import
  const handleImport = async () => {
    if (!file) return;
    
    setStep("importing");
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch(`${API_BASE}/api/admin/vehicles/import-csv?dry_run=false`, {
        method: "POST",
        headers: { "x-admin-token": token },
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || "Import failed");
      }
      
      setImportResult(data);
      setStep("complete");
    } catch (err) {
      setError(err.message);
      setStep("preview");
    } finally {
      setLoading(false);
    }
  };

  // Download template
  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/vehicles/csv-template`, {
        headers: { "x-admin-token": token },
      });
      
      if (!response.ok) {
        throw new Error("Failed to download template");
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "vehicle_import_template.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  };

  // Reset and close
  const handleComplete = () => {
    onSuccess?.();
    onClose();
  };

  return (
    <div className="csv-import-modal">
      <div className="csv-import-header">
        <h2>
          {step === "upload" && "Import Vehicles from CSV"}
          {step === "preview" && "Preview Import"}
          {step === "importing" && "Importing..."}
          {step === "complete" && "Import Complete"}
        </h2>
        <button className="csv-close-btn" onClick={onClose}>&times;</button>
      </div>

      <div className="csv-import-body">
        {/* Step 1: Upload */}
        {step === "upload" && (
          <div className="csv-upload-step">
            <div className="csv-template-section">
              <p>Need a template? Download our CSV template with all supported columns.</p>
              <button 
                type="button"
                className="csv-template-btn"
                onClick={handleDownloadTemplate}
              >
                📥 Download CSV Template
              </button>
            </div>

            <div className="csv-dropzone" onClick={() => fileInputRef.current?.click()}>
              <input
                type="file"
                ref={fileInputRef}
                accept=".csv"
                onChange={handleFileSelect}
                style={{ display: "none" }}
              />
              {file ? (
                <div className="csv-file-selected">
                  <span className="csv-file-icon">📄</span>
                  <span className="csv-file-name">{file.name}</span>
                  <span className="csv-file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                </div>
              ) : (
                <div className="csv-dropzone-placeholder">
                  <span className="csv-upload-icon">📁</span>
                  <span>Click to select CSV file</span>
                  <span className="csv-hint">Maximum 5MB</span>
                </div>
              )}
            </div>

            {error && <div className="csv-error">{error}</div>}

            <div className="csv-required-fields">
              <h4>Required Columns:</h4>
              <ul>
                <li><code>vin</code> - 17-character Vehicle Identification Number</li>
                <li><code>year</code> - Vehicle year (e.g., 2024)</li>
                <li><code>make</code> - Manufacturer (e.g., Honda)</li>
                <li><code>model</code> - Model name (e.g., Accord)</li>
                <li><code>price</code> - Price in dollars (e.g., 32500)</li>
              </ul>
            </div>

            <div className="csv-actions">
              <button 
                type="button"
                className="admin-btn-secondary" 
                onClick={onClose}
              >
                Cancel
              </button>
              <button
                type="button"
                className="admin-btn-primary"
                onClick={handlePreview}
                disabled={!file || loading}
              >
                {loading ? "Validating..." : "Preview Import"}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Preview */}
        {step === "preview" && previewData && (
          <div className="csv-preview-step">
            {/* Summary Cards */}
            <div className="csv-summary-cards">
              <div className="csv-summary-card csv-card-create">
                <span className="csv-card-icon">✅</span>
                <span className="csv-card-count">{previewData.counts.to_create}</span>
                <span className="csv-card-label">New vehicles to create</span>
              </div>
              <div className="csv-summary-card csv-card-update">
                <span className="csv-card-icon">🔁</span>
                <span className="csv-card-count">{previewData.counts.to_update}</span>
                <span className="csv-card-label">Existing vehicles to update</span>
              </div>
              <div className="csv-summary-card csv-card-skip">
                <span className="csv-card-icon">❌</span>
                <span className="csv-card-count">{previewData.counts.skipped}</span>
                <span className="csv-card-label">Rows skipped (errors)</span>
              </div>
            </div>

            {/* Preview Table */}
            {previewData.preview.length > 0 && (
              <div className="csv-preview-table-container">
                <h4>Preview (first {previewData.preview.length} rows)</h4>
                <table className="csv-preview-table">
                  <thead>
                    <tr>
                      <th>Row</th>
                      <th>Action</th>
                      <th>VIN</th>
                      <th>Vehicle</th>
                      <th>Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.preview.map((row, idx) => (
                      <tr key={idx} className={`csv-row-${row.action}`}>
                        <td>{row.row}</td>
                        <td>
                          <span className={`csv-action-badge csv-action-${row.action}`}>
                            {row.action === "create" ? "✅ New" : "🔁 Update"}
                          </span>
                        </td>
                        <td><code>{row.vin}</code></td>
                        <td>{row.vehicle}</td>
                        <td>{row.price ? `$${row.price.toLocaleString()}` : "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Errors */}
            {previewData.errors.length > 0 && (
              <div className="csv-errors-section">
                <h4>⚠️ Validation Errors ({previewData.errors.length})</h4>
                <div className="csv-errors-list">
                  {previewData.errors.slice(0, 10).map((err, idx) => (
                    <div key={idx} className="csv-error-item">{err}</div>
                  ))}
                  {previewData.errors.length > 10 && (
                    <div className="csv-error-more">
                      ...and {previewData.errors.length - 10} more errors
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Skipped Rows */}
            {previewData.skipped_rows.length > 0 && (
              <div className="csv-skipped-section">
                <h4>Skipped Rows</h4>
                <div className="csv-skipped-list">
                  {previewData.skipped_rows.slice(0, 5).map((row, idx) => (
                    <div key={idx} className="csv-skipped-item">
                      <strong>Row {row.row} (VIN: {row.vin}):</strong>
                      <ul>
                        {row.reasons.map((reason, i) => (
                          <li key={i}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && <div className="csv-error">{error}</div>}

            <div className="csv-actions">
              <button 
                type="button"
                className="admin-btn-secondary" 
                onClick={() => {
                  setStep("upload");
                  setPreviewData(null);
                }}
              >
                ← Back
              </button>
              <button
                type="button"
                className="admin-btn-primary"
                onClick={handleImport}
                disabled={previewData.counts.valid_rows === 0}
              >
                Import {previewData.counts.valid_rows} Vehicles
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Importing */}
        {step === "importing" && (
          <div className="csv-importing-step">
            <div className="csv-spinner"></div>
            <p>Importing vehicles... Please wait.</p>
          </div>
        )}

        {/* Step 4: Complete */}
        {step === "complete" && importResult && (
          <div className="csv-complete-step">
            <div className="csv-complete-icon">✅</div>
            <h3>Import Complete!</h3>
            
            <div className="csv-result-summary">
              <div className="csv-result-item">
                <span className="csv-result-count">{importResult.counts.created}</span>
                <span className="csv-result-label">vehicles created</span>
              </div>
              <div className="csv-result-item">
                <span className="csv-result-count">{importResult.counts.updated}</span>
                <span className="csv-result-label">vehicles updated</span>
              </div>
              {importResult.counts.skipped > 0 && (
                <div className="csv-result-item csv-result-skipped">
                  <span className="csv-result-count">{importResult.counts.skipped}</span>
                  <span className="csv-result-label">rows skipped</span>
                </div>
              )}
            </div>

            {importResult.errors.length > 0 && (
              <div className="csv-result-errors">
                <p>⚠️ Some rows had errors:</p>
                <ul>
                  {importResult.errors.slice(0, 5).map((err, idx) => (
                    <li key={idx}>{err}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="csv-actions">
              <button
                type="button"
                className="admin-btn-primary"
                onClick={handleComplete}
              >
                Done
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CSVImportModal;
