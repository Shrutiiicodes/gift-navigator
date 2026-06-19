import { useState } from "react";
import { api } from "./api/client.js";
import Wizard from "./components/Wizard.jsx";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import EntityCard from "./components/EntityCard.jsx";
import TaxCalculator from "./components/TaxCalculator.jsx";
import ComparisonTable from "./components/ComparisonTable.jsx";

function Feedback({ entityId }) {
  const [done, setDone] = useState(false);
  async function send(helpful) {
    try {
      await api.feedback(entityId, helpful, null);
      setDone(true);
    } catch (_) {
      setDone(true); // fail quietly in the UI
    }
  }
  if (done) return <div className="fb"><span className="done">Thanks — logged.</span></div>;
  return (
    <div className="fb">
      <span>Was this recommendation useful?</span>
      <button onClick={() => send(true)} style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
        <ThumbsUp size={14} style={{ strokeWidth: 2 }} /> Yes
      </button>
      <button onClick={() => send(false)} style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
        <ThumbsDown size={14} style={{ strokeWidth: 2 }} /> No
      </button>
    </div>
  );
}

export default function App() {
  const [started, setStarted] = useState(false);
  const [result, setResult] = useState(null);

  function start() {
    setStarted(true);
    setResult(null);
    setTimeout(
      () => document.querySelector(".tool")?.scrollIntoView({ behavior: "smooth" }),
      0
    );
  }

  function restart() {
    setResult(null);
    setTimeout(
      () => document.querySelector(".tool")?.scrollIntoView({ behavior: "smooth" }),
      0
    );
  }

  return (
    <>
      <header>
        <div className="wrap brand">
          <div className="mark">G</div>
          <div>
            <h1>GIFT Setup Navigator</h1>
            <p>IFSC entity finder &amp; tax estimator</p>
          </div>
        </div>
      </header>

      <section className="hero">
        <div className="wrap">
          <p className="eyebrow">India's International Financial Services Centre</p>
          <h2>Find the right way to set up in GIFT City — in under a minute.</h2>
          <p>
            Six entity structures, six rulebooks. Answer a few questions and get the
            structure that fits you, what you'd need to qualify, and how much tax you'd
            save versus staying onshore.
          </p>
          <button className="start-btn" onClick={start}>
            Start the navigator →
          </button>
        </div>
      </section>

      <section className="tool">
        <div className="wrap">
          <div className="panel">
            {!started && (
              <p className="state-msg">
                Tap <strong>Start the navigator</strong> above to begin.
              </p>
            )}
            {started && !result && <Wizard onResult={setResult} />}
            {result && (
              <div className="result">
                <EntityCard result={result} />
                <TaxCalculator />
                <Feedback entityId={result.id} />
                <div className="restart">
                  <button onClick={restart}>↺ Start over</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {result && <ComparisonTable />}

      <footer>
        <div className="wrap">
          Prototype for educational use · figures are indicative, not legal or tax
          advice · verify against current{" "}
          <a href="https://www.ifsca.gov.in" target="_blank" rel="noopener">
            IFSCA
          </a>{" "}
          circulars
        </div>
      </footer>
    </>
  );
}
