import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { fmtUSD } from "../lib/format.js";
import CumulativeChart from "./CumulativeChart.jsx";

export default function TaxCalculator() {
  const [income, setIncome] = useState(2000000);
  const [rate, setRate] = useState(25);
  const [block, setBlock] = useState(25);
  const [advanced, setAdvanced] = useState(false);
  const [surcharge, setSurcharge] = useState(12);
  const [cess, setCess] = useState(4);
  const [mat, setMat] = useState(9);
  const [applyMat, setApplyMat] = useState(true);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    let cancelled = false;
    const t = setTimeout(() => {
      const params = {
        annual_income_usd: Number(income) || 0,
        onshore_rate_pct: Number(rate),
        block_period_years: Number(block),
        advanced,
      };
      if (advanced) {
        params.surcharge_pct = Number(surcharge);
        params.cess_pct = Number(cess);
        params.mat_rate_pct = Number(mat);
        params.apply_mat = applyMat;
      }
      api
        .taxEstimate(params)
        .then((r) => !cancelled && (setResult(r), setErr("")))
        .catch((e) => !cancelled && setErr(e.message));
    }, 140);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [income, rate, block, advanced, surcharge, cess, mat, applyMat]);

  return (
    <div className="calc">
      <h3>Estimate your tax saving</h3>
      <p className="hint">
        Compares tax onshore vs the GIFT IFSC tax holiday on eligible income, projected
        across the block period.
      </p>

      <div className="field">
        <label htmlFor="inc">
          Expected annual eligible income <span>(USD)</span>
        </label>
        <div className="inrow">
          <span className="pfx">$</span>
          <input id="inc" type="number" min="0" step="50000" value={income}
            onChange={(e) => setIncome(e.target.value)} />
        </div>
      </div>

      <div className="field">
        <label htmlFor="rate">
          Onshore tax rate you'd otherwise pay: <span className="rate-val">{rate}%</span>
        </label>
        <input id="rate" type="range" min="9" max="35" value={rate}
          onChange={(e) => setRate(e.target.value)} />
      </div>

      <div className="field">
        <label htmlFor="block">
          Block period to model: <span className="rate-val">{block} years</span>{" "}
          <span>(10-year holiday + concessional tail)</span>
        </label>
        <input id="block" type="range" min="10" max="25" value={block}
          onChange={(e) => setBlock(e.target.value)} />
      </div>

      <div className="adv-toggle">
        <label>
          <input type="checkbox" checked={advanced}
            onChange={(e) => setAdvanced(e.target.checked)} />
          Advanced: add surcharge, cess &amp; minimum alternate tax (MAT)
        </label>
      </div>

      {advanced && (
        <div className="adv-grid">
          <div className="field">
            <label htmlFor="sur">Surcharge <span>(% of tax)</span></label>
            <div className="inrow">
              <input id="sur" type="number" min="0" step="1" value={surcharge}
                onChange={(e) => setSurcharge(e.target.value)} />
              <span className="pfx" style={{ borderLeft: "1px solid var(--line)", borderRight: "none" }}>%</span>
            </div>
          </div>
          <div className="field">
            <label htmlFor="cess">Cess <span>(% of tax+surcharge)</span></label>
            <div className="inrow">
              <input id="cess" type="number" min="0" step="1" value={cess}
                onChange={(e) => setCess(e.target.value)} />
              <span className="pfx" style={{ borderLeft: "1px solid var(--line)", borderRight: "none" }}>%</span>
            </div>
          </div>
          <div className="field">
            <label htmlFor="mat">MAT rate <span>(on book profit)</span></label>
            <div className="inrow">
              <input id="mat" type="number" min="0" step="1" value={mat}
                onChange={(e) => setMat(e.target.value)} />
              <span className="pfx" style={{ borderLeft: "1px solid var(--line)", borderRight: "none" }}>%</span>
            </div>
          </div>
          <div className="field adv-check">
            <label>
              <input type="checkbox" checked={applyMat}
                onChange={(e) => setApplyMat(e.target.checked)} />
              Apply MAT during the holiday
            </label>
          </div>
        </div>
      )}

      {err && <div className="error-msg">{err}</div>}

      {result && (
        <>
          <div className="readout">
            <div className="stat">
              <div className="k">Onshore tax / year</div>
              <div className="v">{fmtUSD(result.onshore_tax_annual)}</div>
            </div>
            <div className="stat win">
              <div className="k">
                IFSC tax / year {result.apply_mat ? "(MAT)" : ""}
              </div>
              <div className="v">{fmtUSD(result.ifsc_tax_annual)}</div>
            </div>
            <div className="stat win">
              <div className="k">{result.block_period_years}-yr block saving</div>
              <div className="v">{fmtUSD(result.block_total_saving)}</div>
            </div>
          </div>

          <h4 className="chart-title">Cumulative saving across the block</h4>
          <CumulativeChart series={result.series} holidayYears={result.holiday_years} />

          <p className="disclaimer">{result.disclaimer}</p>
        </>
      )}
    </div>
  );
}
