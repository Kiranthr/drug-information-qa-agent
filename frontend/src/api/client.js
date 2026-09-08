/**
 * API client communicating with FastAPI backend via /api/v1 endpoints.
 */

const API_BASE = '/api/v1';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchMedicines() {
  const res = await fetch(`${API_BASE}/medicines`);
  if (!res.ok) throw new Error(`Failed to fetch medicines: ${res.statusText}`);
  return res.json();
}

export async function fetchMedicine(id) {
  const res = await fetch(`${API_BASE}/medicines/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch medicine ${id}: ${res.statusText}`);
  return res.json();
}

export async function createMedicine(payload) {
  const res = await fetch(`${API_BASE}/medicines`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to create medicine');
  }
  return res.json();
}

export async function fetchDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.statusText}`);
  return res.json();
}

export async function uploadDocument(formData) {
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to upload PDF document');
  }
  return res.json();
}

export async function deleteDocument(docId, passcode) {
  const headers = {};
  if (passcode) {
    headers['X-Admin-Passcode'] = passcode;
  }
  const res = await fetch(`${API_BASE}/documents/${docId}`, {
    method: 'DELETE',
    headers,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to delete document');
  }
  return true;
}

export async function askQuestion({ question, medicineId = null, sessionId = null }) {
  const payload = {
    question,
    medicine_id: medicineId || undefined,
    session_id: sessionId || undefined,
  };
  const res = await fetch(`${API_BASE}/chat/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to get answer');
  }
  return res.json();
}

export async function fetchChatHistory(sessionId) {
  const res = await fetch(`${API_BASE}/chat/history/${sessionId}`);
  if (!res.ok) throw new Error(`Failed to fetch chat history: ${res.statusText}`);
  return res.json();
}

export async function fetchSafetyAuditLogs(limit = 50) {
  const res = await fetch(`${API_BASE}/safety/audit-logs?limit=${limit}`);
  if (!res.ok) throw new Error(`Failed to fetch safety audit logs: ${res.statusText}`);
  return res.json();
}
