import { useEffect, useState } from "react";
import { api } from "./api/client.js";
import Wizard from "./components/Wizard.jsx";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import EntityCard from "./components/EntityCard.jsx";
import TaxCalculator from "./components/TaxCalculator.jsx";
import ComparisonTable from "./components/ComparisonTable.jsx";
import AnalyticsPanel from "./components/AnalyticsPanel.jsx";

function Feedback({ entityId }) {
  const [comment, setComment] = useState("");
  const [state, setState] = useState("idle"); // idle | done | failed
  async function send(helpful) {
    try {
      await api.feedback(entityId, helpful, comment.trim() || null);
      setState("done");
    } catch (_) {
      setState("failed");
    }
  }
  if (state === "done") return <div className="fb"><span className="done">Thanks — logged.</span></div>;
  return (
    <div className="fb">
      <label htmlFor="fb-comment">Was this recommendation useful?</label>
      <input id="fb-comment" type="text" maxLength={2000} value={comment}
        placeholder="Optional: what worked or what was missing?"
        onChange={(e) => setComment(e.target.value)} />
      <button className="btn-icon" onClick={() => send(true)}>
        <ThumbsUp size={14} strokeWidth={2} /> Yes
      </button>
      <button className="btn-icon" onClick={() => send(false)}>
        <ThumbsDown size={14} strokeWidth={2} /> No
      </button>
      {state === "failed" && <span role="alert">Couldn't save that — try again.</span>}
    </div>
  );
}

export default function App() {
  const [started, setStarted] = useState(false);
  const [result, setResult] = useState(null);
  const [why, setWhy] = useState(null); // set when free-text routing chose the structure
  const [showAnalytics, setShowAnalytics] = useState(false);

  // The free-tier backend sleeps when idle; start waking it as the page loads.
  useEffect(() => {
    api.health().catch(() => {});
  }, []);

  function showResult(r, reason = null) {
    setResult(r);
    setWhy(reason);
  }

  function start() {
    setStarted(true);
    setResult(null);
    api.event("start");
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
          <button className="nav-analytics" onClick={() => setShowAnalytics((s) => !s)}>
            {showAnalytics ? "← Back to tool" : "Usage ▦"}
          </button>
        </div>
      </header>

      {showAnalytics ? (
        <section className="tool">
          <div className="wrap">
            <div className="panel">
              <AnalyticsPanel />
            </div>
          </div>
        </section>
      ) : (
        <>

          <section className="hero">
            <div className="wrap">
              <p className="eyebrow">India's International Financial Services Centre</p>
              <h2>Find the right way to set up in GIFT City — in under a minute.</h2>
              <p>
                Every entity structure has its own rulebook. Answer a few questions and get
                the structure that fits you, what you'd need to qualify, and how much tax
                you'd save versus staying onshore.
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
                {started && !result && <Wizard onResult={showResult} />}
                {result && (
                  <div className="result">
                    {why && (
                      <p className="why">
                        Why this structure: {why}{" "}
                        <button className="linklike" onClick={restart}>
                          Not right? Choose manually
                        </button>
                      </p>
                    )}
                    <EntityCard result={result} />
                    <TaxCalculator entityId={result.id} />
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
        </>
      )}

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
