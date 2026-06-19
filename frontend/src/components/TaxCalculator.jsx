import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { fmtUSD } from "../lib/format.js";

export default function TaxCalculator() {
  const [income, setIncome] = useState(2000000);
  const [rate, setRate] = useState(25);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    let cancelled = false;
    const t = setTimeout(() => {
      api
        .taxEstimate(Number(income) || 0, Number(rate))
        .then((r) => !cancelled && (setResult(r), setErr("")))
        .catch((e) => !cancelled && setErr(e.message));
    }, 120); // debounce
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [income, rate]);

  const onshore = result?.onshore_tax_annual || 0;
  const ifsc = result?.ifsc_tax_annual || 0;
  const max = Math.max(onshore, 1);

  return (
    <div className="calc">
      <h3>Estimate your tax saving</h3>
      <p className="hint">
        Compares tax onshore vs the GIFT IFSC tax holiday on eligible income.
      </p>

      <div className="field">
        <label htmlFor="inc">
          Expected annual eligible income <span>(USD)</span>
        </label>
        <div className="inrow">
          <span className="pfx">$</span>
          <input
            id="inc"
            type="number"
            min="0"
            step="50000"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
          />
        </div>
      </div>

      <div className="field">
        <label htmlFor="rate">
          Onshore tax rate you'd otherwise pay:{" "}
          <span className="rate-val">{rate}%</span>
        </label>
        <input
          id="rate"
          type="range"
          min="9"
          max="35"
          value={rate}
          onChange={(e) => setRate(e.target.value)}
        />
      </div>

      {err && <div className="error-msg">{err}</div>}

      {result && (
        <>
          <div className="readout">
            <div className="stat">
              <div className="k">Onshore tax / year</div>
              <div className="v">{fmtUSD(result.onshore_tax_annual)}</div>
            </div>
            <div className="stat win">
              <div className="k">Saving / year in IFSC</div>
              <div className="v">{fmtUSD(result.annual_saving)}</div>
            </div>
            <div className="stat win">
              <div className="k">{result.block_period_years}-yr block saving</div>
              <div className="v">{fmtUSD(result.block_total_saving)}</div>
            </div>
          </div>

          <div className="bars">
            <div className="bar-row">
              <div className="bl">Onshore / yr</div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: "100%", background: "var(--ink-soft)" }}
                >
                  {fmtUSD(onshore)}
                </div>
              </div>
            </div>
            <div className="bar-row">
              <div className="bl">GIFT IFSC / yr</div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: `${Math.max((ifsc / max) * 100, 2)}%`,
                    background: "var(--green)",
                    minWidth: "34px",
                  }}
                >
                  {fmtUSD(ifsc)}
                </div>
              </div>
            </div>
          </div>

          <p className="disclaimer">{result.disclaimer}</p>
        </>
      )}
    </div>
  );
}
