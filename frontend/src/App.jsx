import { useEffect, useState } from "react";
import { api } from "./api/client.js";
import Wizard from "./components/Wizard.jsx";
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
  if (state === "done") {
    return <div className="fb"><span className="done">Thanks, that's been recorded.</span></div>;
  }
  return (
    <div className="fb">
      <label htmlFor="fb-comment">Was this recommendation useful?</label>
      <div className="row">
        <input id="fb-comment" type="text" maxLength={2000} value={comment}
          placeholder="Anything missing or wrong? (optional)"
          onChange={(e) => setComment(e.target.value)} />
        <button className="btn plain" onClick={() => send(true)}>Yes</button>
        <button className="btn plain" onClick={() => send(false)}>No</button>
      </div>
      {state === "failed" && <p className="error-msg gap-top" role="alert">That didn't save. Please try again.</p>}
    </div>
  );
}

export default function App() {
  const [result, setResult] = useState(null);
  const [why, setWhy] = useState(null); // set when free-text routing chose the structure
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Top of the usage funnel. This first request also wakes the free-tier
  // backend, which sleeps when idle.
  useEffect(() => {
    api.event("start");
  }, []);

  function showResult(r, reason = null) {
    setResult(r);
    setWhy(reason);
    window.scrollTo(0, 0);
  }

  function restart() {
    setResult(null);
    window.scrollTo(0, 0);
  }

  return (
    <>
      <header className="top">
        <div className="wrap">
          <span className="site-name">GIFT Setup Navigator</span>
          <button className="linklike" onClick={() => setShowAnalytics((s) => !s)}>
            {showAnalytics ? "Back to the navigator" : "Usage stats"}
          </button>
        </div>
      </header>

      <main className="wrap">
        {showAnalytics ? (
          <AnalyticsPanel />
        ) : result ? (
          <>
            {why && (
              <p className="why">
                {why}{" "}
                <button className="linklike" onClick={restart}>
                  Not right? Choose from the list
                </button>
              </p>
            )}
            <EntityCard result={result} />
            <TaxCalculator entityId={result.id} />
            <ComparisonTable />
            <Feedback entityId={result.id} />
            <div className="restart">
              <button className="btn" onClick={restart}>Start again</button>
            </div>
          </>
        ) : (
          <>
            <div className="intro">
              <h1>Which GIFT City structure fits your business?</h1>
              <p>
                GIFT City is India's international financial services centre (IFSC). Each
                type of business there is licensed under a different set of IFSCA
                regulations. Pick what you plan to do and you'll see the entity type that
                applies, what you need to qualify, and a rough estimate of the tax saved
                compared with staying onshore.
              </p>
            </div>
            <Wizard onResult={showResult} />
          </>
        )}
      </main>

      <footer>
        <div className="wrap">
          A prototype for learning purposes. Figures are indicative and are not legal or
          tax advice. Check them against current{" "}
          <a href="https://www.ifsca.gov.in" target="_blank" rel="noopener noreferrer">IFSCA</a>{" "}
          circulars before relying on anything here. Built by{" "}
          <a href="https://github.com/Shrutiiicodes" target="_blank" rel="noopener noreferrer">Shrutiiicodes</a>
          {" "}(<a href="https://github.com/Shrutiiicodes/gift-navigator" target="_blank" rel="noopener noreferrer">source</a>).
        </div>
      </footer>
    </>
  );
}
