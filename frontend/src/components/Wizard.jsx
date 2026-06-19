import { useEffect, useState } from "react";
import { api } from "../api/client.js";
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
  HelpCircle
};

function OptionIcon({ name }) {
  const Icon = iconMap[name] || HelpCircle;
  return <Icon size={20} style={{ strokeWidth: 2, verticalAlign: "middle" }} />;
}


export default function Wizard({ onResult }) {
  const [options, setOptions] = useState([]);
  const [loadErr, setLoadErr] = useState("");
  const [step, setStep] = useState(1);
  const [entity, setEntity] = useState(null);

  useEffect(() => {
    api
      .entities()
      .then((d) => setOptions(d.options))
      .catch((e) => setLoadErr(e.message));
  }, []);

  async function pick(entityId) {
    if (entityId === "aif") {
      setEntity(entityId);
      setStep(2);
    } else {
      const result = await api.recommend(entityId, null);
      onResult(result);
    }
  }

  async function pickInvestor(investorType) {
    const result = await api.recommend(entity, investorType);
    onResult(result);
  }

  if (loadErr) {
    return (
      <div className="error-msg">
        Couldn't reach the API at {import.meta.env.VITE_API_URL || "localhost:8000"}.
        Start the backend, or check VITE_API_URL. ({loadErr})
      </div>
    );
  }

  if (step === 2) {
    return (
      <div>
        <div className="step-meta">
          <span>Step 2 of 2</span>
          <span>Investor type</span>
        </div>
        <div className="progress">
          <i style={{ width: "100%" }} />
        </div>
        <h3 className="q">Who can invest in your fund?</h3>
        <p className="q-sub">This sets the minimum net worth your FME needs.</p>
        <div className="opts">
          <button className="opt" onClick={() => pickInvestor("nonretail")}>
            <span className="ic"><Handshake size={20} style={{ strokeWidth: 2 }} /></span>
            <span>
              <span className="ot">Accredited / institutional only</span>
              <span className="od">Non-retail — net worth from USD 500k</span>
            </span>
          </button>
          <button className="opt" onClick={() => pickInvestor("retail")}>
            <span className="ic"><Users size={20} style={{ strokeWidth: 2 }} /></span>
            <span>
              <span className="ot">Open to retail investors</span>
              <span className="od">Retail — net worth USD 3M</span>
            </span>
          </button>
        </div>
        <button className="back" onClick={() => setStep(1)} style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
          <ArrowLeft size={14} /> Back
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="step-meta">
        <span>Step 1 of 2</span>
        <span>Choose your activity</span>
      </div>
      <div className="progress">
        <i style={{ width: "50%" }} />
      </div>
      <h3 className="q">What do you mainly want to do in GIFT City?</h3>
      <p className="q-sub">Pick the activity closest to your business.</p>
      <div className="opts">
        {options.map((o) => (
          <button key={o.key} className="opt" onClick={() => pick(o.key)}>
            <span className="ic"><OptionIcon name={o.icon} /></span>
            <span>
              <span className="ot">{o.name}</span>
              <span className="od">{o.tag}</span>
            </span>
          </button>
        ))}
      </div>
      <FreeTextIntake onClassified={pick} />
    </div>
  );
}
