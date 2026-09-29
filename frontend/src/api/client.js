import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// Attach JWT token automatically
client.interceptors.request.use((config) => {
  const stored = localStorage.getItem("nexusUser");
  if (stored) {
    try {
      const user = JSON.parse(stored);
      if (user.access_token || user.token) {
        config.headers.Authorization = `Bearer ${user.access_token || user.token}`;
      }
    } catch (e) {
      // ignore
    }
  }
  return config;
});

export const api = {
  // Auth
  login: (username, password) => client.post("/api/auth/login", { username, password }).then((r) => r.data),
  logout: () => client.post("/api/auth/logout").then((r) => r.data),
  getMe: () => client.get("/api/auth/me").then((r) => r.data),

  // Summary & Health
  getSummary: () => client.get("/api/summary").then((r) => r.data),
  getHealth: () => client.get("/api/health").then((r) => r.data),

  // Cases
  getCases: () => client.get("/api/cases").then((r) => r.data),
  getCase: (id) => client.get(`/api/cases/${id}`).then((r) => r.data),

  // Complaints
  getComplaints: (params) => client.get("/api/complaints/", { params }).then((r) => r.data),
  getComplaint: (id) => client.get(`/api/complaints/${id}`).then((r) => r.data),
  createComplaint: (data) => client.post("/api/complaints/", data).then((r) => r.data),

  // Spatio-Temporal Prediction
  predictCashout: (complaintId, topK = 5) =>
    client.post("/api/predictions/predict", { complaint_id: complaintId, top_k: topK }).then((r) => r.data),
  getLatestPredictions: (limit = 15) =>
    client.get("/api/predictions/latest", { params: { limit } }).then((r) => r.data),
  getComplaintPredictions: (complaintId) =>
    client.get(`/api/predictions/${complaintId}`).then((r) => r.data),

  // GIS Heatmap
  getHeatmapData: (params) => client.get("/api/heatmap/", { params }).then((r) => r.data),

  // Financial Money-Flow & UPI Fraud Tracing
  getMoneyFlow: (complaintId) => client.get(`/api/financial/flow/${complaintId}`).then((r) => r.data),
  getUpiTrace: (query) => client.get(`/api/financial/upi-trace/${query}`).then((r) => r.data),

  // Alerts
  getAlerts: (params) => client.get("/api/alerts/", { params }).then((r) => r.data),
  updateAlertStatus: (alertId, status, assignedTo) =>
    client.patch(`/api/alerts/${alertId}/status`, { status, assigned_to: assignedTo }).then((r) => r.data),

  // Evidence
  getEvidence: (caseId) => client.get("/api/evidence", { params: { case_id: caseId } }).then((r) => r.data),

  // Grounded RAG Assistant
  askRag: (caseId, question) =>
    client.post("/api/rag/ask", { case_id: caseId, question }).then((r) => r.data),

  // Model Performance Evaluation
  getModelMetrics: () => client.get("/api/model/metrics").then((r) => r.data),

  // Audit Logs
  getAuditLogs: (caseId) => client.get("/api/audit", { params: { case_id: caseId } }).then((r) => r.data),

  // Users & RBAC
  getUsers: () => client.get("/api/users/").then((r) => r.data),
};

export default api;
