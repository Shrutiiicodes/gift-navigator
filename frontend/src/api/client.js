export const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Anonymous per-tab id so the usage funnel counts sessions, not clicks.
// No personal data; gone when the tab closes.
function sessionId() {
  try {
    let id = sessionStorage.getItem("gift_sid");
    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem("gift_sid", id);
    }
    return id;
  } catch (_) {
    return null; // storage blocked - the backend counts the row on its own
  }
}

async function call(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch (_) {
      /* keep default */
    }
    throw new Error(detail);
  }
  return res.json();
}

const post = (path, body) =>
  call(path, { method: "POST", body: JSON.stringify(body) });

export const api = {
  health: () => call("/health"),
  entities: () => call("/entities"),
  recommend: (entity_id, investor_type) =>
    post("/recommend", { entity_id, investor_type, session_id: sessionId() }),
  taxEstimate: (params) => post("/tax/estimate", params),
  taxRules: () => call("/tax/rules"),
  classify: (text) => post("/classify", { text, session_id: sessionId() }),
  feedback: (entity_id, helpful, comment) =>
    post("/feedback", { entity_id, helpful, comment, session_id: sessionId() }),
  event: (kind, entity_id = null) =>
    post("/event", { kind, entity_id, session_id: sessionId() }).catch(() => {}), // fire-and-forget; never block the UI
  analytics: () => call("/analytics"),
};
