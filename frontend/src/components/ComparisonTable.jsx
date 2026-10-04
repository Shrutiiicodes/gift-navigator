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
      <h2>GIFT City next to Dubai and Singapore</h2>
      <p className="sub">
        An indicative comparison with the two hubs it most often competes with for
        India-linked financial business.
      </p>
      <div className="table-scroll">
        <table className="ctable">
          <thead>
            <tr>
              <th scope="col">Factor</th>
              <th scope="col">GIFT City IFSC</th>
              <th scope="col">Dubai (DIFC)</th>
              <th scope="col">Singapore</th>
            </tr>
          </thead>
          <tbody>
            {hubs.map((h, i) => (
              <tr key={i}>
                <th scope="row">{h.factor}</th>
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
