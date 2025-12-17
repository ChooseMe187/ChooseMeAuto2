import React, { useState, useEffect } from "react";
import { useAdminAuth } from "../../context/AdminAuthContext";
import "../../styles/admin.css";

const AdminLeadsPage = () => {
  const { token } = useAdminAuth();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ status: "", lead_type: "" });
  const [stats, setStats] = useState({ total: 0, new: 0, by_type: {} });
  
  // Notes modal state
  const [notesModal, setNotesModal] = useState({ open: false, lead: null });
  const [newNote, setNewNote] = useState("");
  const [addingNote, setAddingNote] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

  // Team members for assignment
  const teamMembers = ["Jay", "Sarah", "Mike", "Unassigned"];

  const fetchLeads = async () => {
    setLoading(true);
    try {
      let url = `${API_BASE}/api/leads`;
      const params = new URLSearchParams();
      if (filter.status) params.append("status", filter.status);
      if (filter.lead_type) params.append("lead_type", filter.lead_type);
      if (params.toString()) url += `?${params.toString()}`;

      const response = await fetch(url, {
        headers: { "x-admin-token": token },
      });
      if (response.ok) {
        const data = await response.json();
        setLeads(data);
      }
    } catch (error) {
      console.error("Error fetching leads:", error);
    }
    setLoading(false);
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/leads/stats/summary`, {
        headers: { "x-admin-token": token },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  useEffect(() => {
    fetchLeads();
    fetchStats();
  }, [token, filter]);

  const updateStatus = async (leadId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE}/api/leads/${leadId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "x-admin-token": token,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        fetchLeads();
        fetchStats();
      } else {
        alert("Failed to update status");
      }
    } catch (error) {
      console.error("Update error:", error);
    }
  };

  const assignLead = async (leadId, assignedTo) => {
    try {
      const response = await fetch(`${API_BASE}/api/leads/${leadId}/assign`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "x-admin-token": token,
        },
        body: JSON.stringify({ assigned_to: assignedTo === "Unassigned" ? null : assignedTo }),
      });

      if (response.ok) {
        fetchLeads();
      } else {
        alert("Failed to assign lead");
      }
    } catch (error) {
      console.error("Assignment error:", error);
    }
  };

  const addNote = async () => {
    if (!newNote.trim() || !notesModal.lead) return;
    
    setAddingNote(true);
    try {
      const response = await fetch(`${API_BASE}/api/leads/${notesModal.lead.id}/notes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-token": token,
        },
        body: JSON.stringify({ text: newNote, by: "admin" }),
      });

      if (response.ok) {
        setNewNote("");
        fetchLeads();
        // Refresh the modal with updated lead
        const updatedLead = leads.find(l => l.id === notesModal.lead.id);
        if (updatedLead) {
          // Re-fetch to get updated notes
          const res = await fetch(`${API_BASE}/api/leads/${notesModal.lead.id}`, {
            headers: { "x-admin-token": token },
          });
          if (res.ok) {
            const data = await res.json();
            setNotesModal({ open: true, lead: data });
          }
        }
      } else {
        alert("Failed to add note");
      }
    } catch (error) {
      console.error("Add note error:", error);
    }
    setAddingNote(false);
  };

  const deleteLead = async (leadId) => {
    if (!window.confirm("Are you sure you want to delete this lead?")) return;

    try {
      const response = await fetch(`${API_BASE}/api/leads/${leadId}`, {
        method: "DELETE",
        headers: { "x-admin-token": token },
      });

      if (response.ok) {
        fetchLeads();
        fetchStats();
      } else {
        alert("Failed to delete lead");
      }
    } catch (error) {
      console.error("Delete error:", error);
    }
  };

  const exportCSV = async () => {
    try {
      let url = `${API_BASE}/api/leads/export.csv`;
      const params = new URLSearchParams();
      if (filter.status) params.append("status", filter.status);
      if (filter.lead_type) params.append("lead_type", filter.lead_type);
      if (params.toString()) url += `?${params.toString()}`;

      const response = await fetch(url, {
        headers: { "x-admin-token": token },
      });

      if (response.ok) {
        const blob = await response.blob();
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "choosemeauto-leads.csv";
        a.click();
        URL.revokeObjectURL(a.href);
      } else {
        alert("Failed to export CSV");
      }
    } catch (error) {
      console.error("Export error:", error);
      alert("Error exporting CSV");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "—";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const formatNoteDate = (dateStr) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const getStatusBadgeClass = (status) => {
    const classes = {
      new: "admin-badge-new",
      contacted: "admin-badge-contacted",
      qualified: "admin-badge-qualified",
      converted: "admin-badge-converted",
      lost: "admin-badge-lost",
    };
    return classes[status] || "admin-badge-new";
  };

  const getLeadTypeBadgeClass = (type) => {
    const classes = {
      pre_approval: "admin-badge-preapproval",
      test_drive: "admin-badge-testdrive",
      contact: "admin-badge-contact",
      availability: "admin-badge-availability",
    };
    return classes[type] || "";
  };

  const formatLeadType = (type) => {
    const labels = {
      pre_approval: "Pre-Approval",
      test_drive: "Test Drive",
      contact: "Contact",
      availability: "Availability",
    };
    return labels[type] || type;
  };

  return (
    <div className="admin-leads-page">
      {/* Stats Cards */}
      <div className="admin-stats-row">
        <div className="admin-stat-card">
          <span className="admin-stat-value">{stats.total}</span>
          <span className="admin-stat-label">Total Leads</span>
        </div>
        <div className="admin-stat-card admin-stat-new">
          <span className="admin-stat-value">{stats.new}</span>
          <span className="admin-stat-label">New Leads</span>
        </div>
        <div className="admin-stat-card">
          <span className="admin-stat-value">{stats.by_type?.pre_approval || 0}</span>
          <span className="admin-stat-label">Pre-Approvals</span>
        </div>
        <div className="admin-stat-card">
          <span className="admin-stat-value">{stats.by_type?.test_drive || 0}</span>
          <span className="admin-stat-label">Test Drives</span>
        </div>
      </div>

      {/* Filters & Actions */}
      <div className="admin-filters">
        <select
          value={filter.status}
          onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          className="admin-filter-select"
        >
          <option value="">All Statuses</option>
          <option value="new">New</option>
          <option value="contacted">Contacted</option>
          <option value="qualified">Qualified</option>
          <option value="converted">Converted</option>
          <option value="lost">Lost</option>
        </select>

        <select
          value={filter.lead_type}
          onChange={(e) => setFilter({ ...filter, lead_type: e.target.value })}
          className="admin-filter-select"
        >
          <option value="">All Types</option>
          <option value="pre_approval">Pre-Approval</option>
          <option value="test_drive">Test Drive</option>
          <option value="contact">Contact</option>
          <option value="availability">Availability</option>
        </select>

        <button onClick={fetchLeads} className="admin-btn-secondary">
          Refresh
        </button>
        
        <button onClick={exportCSV} className="admin-btn-export">
          📥 Export CSV
        </button>
      </div>

      {/* Leads Table */}
      <div className="admin-table-container">
        {loading ? (
          <div className="admin-loading">Loading leads...</div>
        ) : leads.length === 0 ? (
          <div className="admin-empty">
            <p>No leads found.</p>
          </div>
        ) : (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Name</th>
                <th>Contact</th>
                <th>Vehicle</th>
                <th>Assigned To</th>
                <th>Notes</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id}>
                  <td className="admin-date-cell">
                    {formatDate(lead.created_at)}
                  </td>
                  <td>
                    <span className={`admin-type-badge ${getLeadTypeBadgeClass(lead.lead_type)}`}>
                      {formatLeadType(lead.lead_type)}
                    </span>
                  </td>
                  <td>
                    <div className="admin-lead-name">
                      <strong>{lead.first_name} {lead.last_name}</strong>
                    </div>
                  </td>
                  <td>
                    <div className="admin-lead-contact">
                      {lead.phone && <div>📞 {lead.phone}</div>}
                      {lead.email && <div>✉️ {lead.email}</div>}
                    </div>
                  </td>
                  <td>
                    {lead.stock_number && <div>Stock: {lead.stock_number}</div>}
                    {lead.vehicle_summary && <div className="admin-vehicle-summary">{lead.vehicle_summary}</div>}
                    {lead.preferred_date && <div>📅 {lead.preferred_date} {lead.preferred_time}</div>}
                  </td>
                  <td>
                    <select
                      value={lead.assigned_to || "Unassigned"}
                      onChange={(e) => assignLead(lead.id, e.target.value)}
                      className="admin-assign-select"
                    >
                      {teamMembers.map((member) => (
                        <option key={member} value={member}>{member}</option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <button
                      onClick={() => setNotesModal({ open: true, lead })}
                      className="admin-notes-btn"
                    >
                      📝 {lead.notes?.length || 0}
                    </button>
                  </td>
                  <td>
                    <select
                      value={lead.status}
                      onChange={(e) => updateStatus(lead.id, e.target.value)}
                      className={`admin-status-select ${getStatusBadgeClass(lead.status)}`}
                    >
                      <option value="new">New</option>
                      <option value="contacted">Contacted</option>
                      <option value="qualified">Qualified</option>
                      <option value="converted">Converted</option>
                      <option value="lost">Lost</option>
                    </select>
                  </td>
                  <td>
                    <button
                      onClick={() => deleteLead(lead.id)}
                      className="admin-btn-delete"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Notes Modal */}
      {notesModal.open && notesModal.lead && (
        <div className="admin-modal-overlay" onClick={() => setNotesModal({ open: false, lead: null })}>
          <div className="admin-modal admin-notes-modal" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h3>Notes for {notesModal.lead.first_name} {notesModal.lead.last_name}</h3>
              <button 
                className="admin-close-btn"
                onClick={() => setNotesModal({ open: false, lead: null })}
              >
                ×
              </button>
            </div>
            
            <div className="admin-notes-list">
              {notesModal.lead.notes?.length === 0 ? (
                <p className="admin-no-notes">No notes yet.</p>
              ) : (
                notesModal.lead.notes?.map((note, idx) => (
                  <div key={idx} className="admin-note-item">
                    <div className="admin-note-header">
                      <span className="admin-note-by">{note.by}</span>
                      <span className="admin-note-date">{formatNoteDate(note.at)}</span>
                    </div>
                    <p className="admin-note-text">{note.text}</p>
                  </div>
                ))
              )}
            </div>
            
            <div className="admin-add-note">
              <textarea
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Add a note..."
                rows={3}
              />
              <button 
                onClick={addNote} 
                disabled={addingNote || !newNote.trim()}
                className="admin-btn-primary"
              >
                {addingNote ? "Adding..." : "Add Note"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminLeadsPage;
