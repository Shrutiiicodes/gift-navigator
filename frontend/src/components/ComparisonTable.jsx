import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function ComparisonTable() {
  const [hubs, setHubs] = useState([]);

  useEffect(() => {
    api
      .taxRules()
      .then((d) => setHubs(d.comparison_hubs || []))
      .catch(() => setHubs([]));
  }, []);

  if (!hubs.length) return null;

  return (
    <section className="compare">
      <div className="wrap">
        <h3>How GIFT City stacks up</h3>
        <p className="sub">
          Indicative snapshot against the hubs it competes with for India-linked
          financial business.
        </p>
        <table className="ctable">
          <thead>
            <tr>
              <th>Factor</th>
              <th className="gift">GIFT City IFSC</th>
              <th>Dubai (DIFC)</th>
              <th>Singapore</th>
            </tr>
          </thead>
          <tbody>
            {hubs.map((h, i) => (
              <tr key={i}>
                <td>{h.factor}</td>
                <td className="gift">{h.gift}</td>
                <td>{h.dubai}</td>
                <td>{h.singapore}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
