import React, { useState, useEffect } from "react";
import { useAdminAuth } from "../../context/AdminAuthContext";
import "../../styles/admin.css";

const AdminLeadsPage = () => {
  const { token } = useAdminAuth();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ status: "", lead_type: "" });
  const [stats, setStats] = useState({ total: 0, new: 0, by_type: {} });

  const API_BASE = process.env.REACT_APP_BACKEND_URL || "";

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

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
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

      {/* Filters */}
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
    </div>
  );
};

export default AdminLeadsPage;
