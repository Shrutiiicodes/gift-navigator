export default function EntityCard({ result }) {
  return (
    <section className="rec">
      <p className="label">Recommended structure</p>
      <h2>{result.name}</h2>
      <p className="rec-meta">
        {result.tag} · Regulated by {result.regulator} · Typical setup time{" "}
        {result.timeline_label}
      </p>
      <p className="rec-what">{result.what}</p>

      <div className="rec-grid">
        <div>
          <h3>What you'll need</h3>
          <ul>
            {result.eligibility.map((r, i) => (
              <li key={i}>
                {r.rule}
                {r.source && (
                  <span className="src">
                    {r.ref_url ? (
                      <a href={r.ref_url} target="_blank" rel="noopener noreferrer">
                        {r.source}
                      </a>
                    ) : (
                      r.source
                    )}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3>What you can do</h3>
          <ul>
            {result.activities.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      </div>

      {result.last_reviewed && (
        <p className="reviewed">
          Figures are indicative and were last reviewed on {result.last_reviewed}. Follow
          the source links for the current position.
        </p>
      )}
    </section>
  );
}
