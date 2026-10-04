import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function AnalyticsPanel() {
    const [data, setData] = useState(null);
    const [err, setErr] = useState("");

    useEffect(() => {
        api
            .analytics()
            .then(setData)
            .catch((e) => setErr(e.message));
    }, []);

    if (err) return <div className="error-msg">The usage data didn't load: {err}</div>;
    if (!data) return <p className="state-msg">Loading usage data…</p>;

    const maxQ = Math.max(1, ...data.most_queried.map((m) => m.count));
    const maxF = Math.max(1, ...data.funnel.map((f) => f.count));

    return (
        <div className="analytics">
            <h2>How the navigator is being used</h2>
            <p className="state-msg">
                Visits are counted once per browser tab and carry no personal data.
            </p>

            <h3>Structures recommended most often</h3>
            {data.most_queried.length === 0 ? (
                <p className="state-msg">No recommendations logged yet.</p>
            ) : (
                <div className="abars">
                    {data.most_queried.map((m) => (
                        <div className="abar-row" key={m.entity_id}>
                            <div className="abar-label">{m.name}</div>
                            <div className="abar-track">
                                <div className="abar-fill"
                                    style={{ width: `${(m.count / maxQ) * 100}%` }}>
                                    {m.count}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <h3>How far visits get</h3>
            <div className="funnel">
                {data.funnel.map((f) => (
                    <div className="funnel-row" key={f.stage}>
                        <div className="funnel-label">{f.label}</div>
                        <div className="funnel-track">
                            <div className="funnel-fill"
                                style={{ width: `${(f.count / maxF) * 100}%` }}>
                                {f.count}
                            </div>
                        </div>
                        <div className="funnel-drop">
                            {f.drop_from_prev_pct === null
                                ? ""
                                : f.drop_from_prev_pct === 0
                                ? "0%"
                                : `−${f.drop_from_prev_pct}%`}
                        </div>
                    </div>
                ))}
            </div>
            <p className="state-msg gap-top">
                The percentage is the share of visits lost since the previous step.
                {data.feedback.total > 0 &&
                    ` ${data.feedback.helpful} of ${data.feedback.total} feedback responses said the recommendation was useful.`}
            </p>
        </div>
    );
}
