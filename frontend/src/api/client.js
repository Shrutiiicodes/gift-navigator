const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function call(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch (_) {
      /* keep default */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  health: () => call("/health"),
  entities: () => call("/entities"),
  recommend: (entity_id, investor_type) =>
    call("/recommend", {
      method: "POST",
      body: JSON.stringify({ entity_id, investor_type }),
    }),
  taxEstimate: (annual_income_usd, onshore_rate_pct) =>
    call("/tax/estimate", {
      method: "POST",
      body: JSON.stringify({ annual_income_usd, onshore_rate_pct }),
    }),
  taxRules: () => call("/tax/rules"),
  classify: (text) =>
    call("/classify", { method: "POST", body: JSON.stringify({ text }) }),
  feedback: (entity_id, helpful, comment) =>
    call("/feedback", {
      method: "POST",
      body: JSON.stringify({ entity_id, helpful, comment }),
    }),
};
