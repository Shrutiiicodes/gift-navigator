import { useEffect, useState } from "react";
import { api, BASE } from "../api/client.js";
import FreeTextIntake from "./FreeTextIntake.jsx";

export default function Wizard({ onResult }) {
  const [options, setOptions] = useState(null);
  const [loadErr, setLoadErr] = useState("");
  const [entity, setEntity] = useState(null); // option awaiting its follow-up answer
  const [why, setWhy] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .entities()
      .then((d) => setOptions(d.options))
      .catch((e) => setLoadErr(e.message));
  }, []);

  async function recommend(entityId, investorType, reason) {
    setBusy(true);
    setErr("");
    try {
      onResult(await api.recommend(entityId, investorType), reason);
    } catch (e) {
      setErr(`That recommendation didn't load: ${e.message}`);
    } finally {
      setBusy(false);
    }
  }

  // `reason` is set when the free-text classifier (not the user) chose the entity.
  function pick(entityId, reason = null) {
    const option = options.find((o) => o.key === entityId);
    if (option?.branch) {
      setEntity(option);
      setWhy(reason);
      setErr("");
    } else {
      recommend(entityId, null, reason);
    }
  }

  if (loadErr) {
    return (
      <div className="error-msg">
        Can't reach the API at {BASE}. Start the backend, or check VITE_API_URL. ({loadErr})
      </div>
    );
  }

  if (!options) {
    return (
      <p className="state-msg" role="status">
        Loading. The server sleeps when it hasn't been used for a while, so the first
        load can take up to a minute.
      </p>
    );
  }

  if (entity) {
    const branch = entity.branch;
    return (
      <div>
        <button className="linklike back" onClick={() => setEntity(null)}>
          Back to all structures
        </button>
        <p className="label">{entity.name}</p>
        <h2 className="q">{branch.question}</h2>
        <p className="q-sub">{branch.sub}</p>
        {why && <p className="why">{why}</p>}
        <div className="opts">
          {branch.options.map((o) => (
            <button key={o.id} className="opt" disabled={busy}
              onClick={() => recommend(entity.key, o.id, why)}>
              <span className="ot">{o.label}</span>
              <span className="od">{o.detail}</span>
            </button>
          ))}
        </div>
        {err && <div className="error-msg">{err}</div>}
      </div>
    );
  }

  return (
    <div>
      <h2 className="q">What do you plan to do in GIFT City?</h2>
      <p className="q-sub">Pick the closest match.</p>
      <div className="opts">
        {options.map((o) => (
          <button key={o.key} className="opt" disabled={busy} onClick={() => pick(o.key)}>
            <span className="ot">{o.name}</span>
            <span className="od">{o.tag}</span>
          </button>
        ))}
      </div>
      {err && <div className="error-msg">{err}</div>}
      <FreeTextIntake onClassified={pick} disabled={busy} />
    </div>
  );
}
