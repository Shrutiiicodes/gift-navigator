export default function EntityCard({ result }) {
  return (
    <div className="cert">
      <div className="cert-top">
        <div className="cert-label">Recommended structure</div>
        <div className="cert-name">{result.name}</div>
        <span className="cert-tag">{result.tag}</span>
      </div>
      <div className="cert-body">
        <p className="cert-what">{result.what}</p>
        <div className="cert-grid">
          <div>
            <h4>What you'll need</h4>
            <ul>
              {result.eligibility.map((r, i) => (
                <li key={i}>
                  {r.rule}
                  {r.source && <span className="src">Source: {r.source}</span>}
                </li>
              ))}
            </ul>
            <h4 style={{ marginTop: "18px" }}>Indicative timeline</h4>
            <div className="timeline-chip">{result.timeline_label}</div>
          </div>
          <div>
            <h4>What you can do</h4>
            <ul>
              {result.activities.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
            <h4 style={{ marginTop: "18px" }}>Regulator</h4>
            <div className="timeline-chip">{result.regulator}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
