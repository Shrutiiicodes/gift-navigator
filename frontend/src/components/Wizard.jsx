import { useEffect, useState } from "react";
import { api, BASE } from "../api/client.js";
import FreeTextIntake from "./FreeTextIntake.jsx";
import {
  TrendingUp,
  Landmark,
  Puzzle,
  Plane,
  Shield,
  Zap,
  LineChart,
  HelpCircle,
  Users,
  Handshake,
  ArrowLeft
} from "lucide-react";

const iconMap = {
  TrendingUp,
  Landmark,
  Puzzle,
  Plane,
  Shield,
  Zap,
  LineChart,
  HelpCircle,
  // branch option ids
  retail: Users,
  nonretail: Handshake
};

function OptionIcon({ name }) {
  const Icon = iconMap[name] || HelpCircle;
  return <Icon size={20} strokeWidth={2} />;
}


export default function Wizard({ onResult }) {
  const [options, setOptions] = useState(null);
  const [loadErr, setLoadErr] = useState("");
  const [entity, setEntity] = useState(null); // option awaiting its branch answer
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
      setErr(`Couldn't load that recommendation: ${e.message}`);
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
        Couldn't reach the API at {BASE}. Start the backend, or check VITE_API_URL. ({loadErr})
      </div>
    );
  }

  if (!options) {
    return (
      <p className="state-msg" role="status">
        Waking the server — on the free tier this can take up to a minute…
      </p>
    );
  }

  if (entity) {
    const branch = entity.branch;
    return (
      <div>
        <div className="step-meta">
          <span>Step 2 of 2</span>
          <span>{entity.name}</span>
        </div>
        <div className="progress">
          <i style={{ width: "100%" }} />
        </div>
        <h3 className="q">{branch.question}</h3>
        <p className="q-sub">{branch.sub}</p>
        {why && <p className="why">{why}</p>}
        <div className="opts">
          {branch.options.map((o) => (
            <button key={o.id} className="opt" disabled={busy}
              onClick={() => recommend(entity.key, o.id, why)}>
              <span className="ic"><OptionIcon name={o.id} /></span>
              <span>
                <span className="ot">{o.label}</span>
                <span className="od">{o.detail}</span>
              </span>
            </button>
          ))}
        </div>
        {err && <div className="error-msg">{err}</div>}
        <button className="back btn-icon" onClick={() => setEntity(null)}>
          <ArrowLeft size={14} /> Back
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="step-meta">
        <span>Step 1</span>
        <span>Choose your activity</span>
      </div>
      <div className="progress">
        <i style={{ width: "50%" }} />
      </div>
      <h3 className="q">What do you mainly want to do in GIFT City?</h3>
      <p className="q-sub">Pick the activity closest to your business.</p>
      <div className="opts">
        {options.map((o) => (
          <button key={o.key} className="opt" disabled={busy} onClick={() => pick(o.key)}>
            <span className="ic"><OptionIcon name={o.icon} /></span>
            <span>
              <span className="ot">{o.name}</span>
              <span className="od">{o.tag}</span>
            </span>
          </button>
        ))}
      </div>
      {err && <div className="error-msg">{err}</div>}
      <FreeTextIntake onClassified={pick} disabled={busy} />
    </div>
  );
}
