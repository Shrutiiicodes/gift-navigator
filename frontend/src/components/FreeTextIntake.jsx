import { useState } from "react";
import { api } from "../api/client.js";

export default function FreeTextIntake({ onClassified, disabled }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");

  async function submit() {
    if (text.trim().length < 2) return;
    setBusy(true);
    setNote("");
    try {
      const result = await api.classify(text);
      if (!result.entity_id) {
        setNote("No clear match for that. Pick the closest option from the list above.");
        return;
      }
      const why =
        result.method === "llm"
          ? "Suggested from your description by the language-model fallback."
          : `Suggested because your description mentions: ${result.matched_terms.join(", ")}.` +
            (result.note ? " This is a weak match, so check it fits." : "");
      onClassified(result.entity_id, why);
    } catch (e) {
      setNote(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="intake">
      <label htmlFor="intake">Not sure? Describe the business in a sentence or two</label>
      <textarea
        id="intake"
        value={text}
        placeholder="For example: we want to raise a venture capital fund that invests in Indian startups"
        onChange={(e) => setText(e.target.value)}
      />
      <div className="row">
        <button className="btn" onClick={submit}
          disabled={disabled || busy || text.trim().length < 2}>
          {busy ? "Checking…" : "Suggest a structure"}
        </button>
        {note && <span className="note" role="status">{note}</span>}
      </div>
    </div>
  );
}
