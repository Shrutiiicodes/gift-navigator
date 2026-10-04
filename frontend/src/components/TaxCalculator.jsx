import { useEffect, useRef, useState } from "react";
import { api } from "../api/client.js";
import { fmtUSD } from "../lib/format.js";
import CumulativeChart from "./CumulativeChart.jsx";

// Loads the tax parameters once so bounds and defaults come from tax_rules.json,
// not from copies in this file.
export default function TaxCalculator({ entityId }) {
  const [rules, setRules] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.taxRules().then(setRules).catch((e) => setErr(e.message));
  }, []);

  if (err) return <div className="error-msg">The tax estimator didn't load: {err}</div>;
  if (!rules) return <p className="state-msg">Loading tax estimator…</p>;
  return <Calculator rules={rules} entityId={entityId} />;
}

function PctField({ id, label, hint, value, onChange }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{hint}</span></label>
      <div className="inrow">
        <input id={id} type="number" min="0" max="100" step="1" value={value}
          onChange={(e) => onChange(e.target.value)} />
        <span className="pfx sfx">%</span>
      </div>
    </div>
  );
}

function Calculator({ rules, entityId }) {
  const rateBounds = rules.onshore_rate_bounds_pct;
  const blockBounds = rules.block_period_bounds_years;
  const adv = rules.advanced_defaults;
  const s80 = rules.section_80la;

  const [income, setIncome] = useState(2000000);
  const [rate, setRate] = useState(rules.onshore_default_rate_pct);
  const [block, setBlock] = useState(s80.block_period_years);
  const [advanced, setAdvanced] = useState(false);
  const [surcharge, setSurcharge] = useState(adv.surcharge_pct);
  const [cess, setCess] = useState(adv.cess_pct);
  const [mat, setMat] = useState(adv.mat_rate_pct);
  const [applyMat, setApplyMat] = useState(true);
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");

  // Funnel stage "tax_view": the user actually touched the estimator, logged
  // once per recommendation (this component remounts for each new result).
  const logged = useRef(false);
  function logUse() {
    if (logged.current) return;
    logged.current = true;
    api.event("tax_view", entityId);
  }

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
    <div className="calc" onChange={logUse}>
      <h2>Estimated tax saving</h2>
      <p className="hint">
        Tax on eligible income if the business stayed onshore, against the same income
        under the GIFT IFSC tax holiday, added up over the block period.
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
        <input id="rate" type="range" min={rateBounds.min} max={rateBounds.max} value={rate}
          onChange={(e) => setRate(e.target.value)} />
      </div>

      <div className="field">
        <label htmlFor="block">
          Block period to model: <span className="rate-val">{block} years</span>{" "}
          <span>({s80.holiday_years}-year holiday + concessional tail)</span>
        </label>
        <input id="block" type="range" min={blockBounds.min} max={blockBounds.max} value={block}
          onChange={(e) => setBlock(e.target.value)} />
      </div>

      <div className="adv-toggle">
        <label>
          <input type="checkbox" checked={advanced}
            onChange={(e) => setAdvanced(e.target.checked)} />
          Include surcharge, cess and minimum alternate tax (MAT)
        </label>
      </div>

      {advanced && (
        <div className="adv-grid">
          <PctField id="sur" label="Surcharge" hint="(% of tax)"
            value={surcharge} onChange={setSurcharge} />
          <PctField id="cess" label="Cess" hint="(% of tax+surcharge)"
            value={cess} onChange={setCess} />
          <PctField id="mat" label="MAT rate" hint="(on book profit)"
            value={mat} onChange={setMat} />
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
            <div className="stat">
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

          <h3 className="chart-title">Cumulative saving over the block period</h3>
          <CumulativeChart series={result.series} holidayYears={result.holiday_years} />

          <p className="disclaimer">{result.disclaimer}</p>
        </>
      )}
    </div>
  );
}
