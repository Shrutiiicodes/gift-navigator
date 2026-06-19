import { useState } from "react";
import { api } from "../api/client.js";

export default function FreeTextIntake({ onClassified }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");

  async function submit() {
    if (text.trim().length < 2) return;
    setBusy(true);
    setNote("");
    try {
      const result = await api.classify(text);
      setNote(
        `Routed to "${result.entity_id}" via ${result.method}` +
          (result.confidence ? ` (confidence ${result.confidence})` : "")
      );
      onClassified(result.entity_id);
    } catch (e) {
      setNote(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="intake">
      <label htmlFor="intake">Or describe your business in your own words</label>
      <textarea
        id="intake"
        value={text}
        placeholder="e.g. We want to raise a venture capital fund investing in Indian startups"
        onChange={(e) => setText(e.target.value)}
      />
      <div className="row">
        <button onClick={submit} disabled={busy || text.trim().length < 2}>
          {busy ? "Routing…" : "Route me →"}
        </button>
        {note && <span className="note">{note}</span>}
      </div>
    </div>
  );
}
