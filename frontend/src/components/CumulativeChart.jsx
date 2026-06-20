import { fmtUSD } from "../lib/format.js";

/**
 * Cumulative-savings area chart over the block period.
 * Pure inline SVG so we add no chart dependency to the bundle.
 * Shades the holiday years vs the concessional tail differently.
 */
export default function CumulativeChart({ series, holidayYears }) {
    if (!series || series.length === 0) return null;

    const W = 640;
    const H = 200;
    const padL = 56;
    const padR = 14;
    const padT = 14;
    const padB = 28;
    const innerW = W - padL - padR;
    const innerH = H - padT - padB;

    const maxVal = Math.max(...series.map((p) => p.saving_cumulative), 1);
    const n = series.length;

    const x = (i) => padL + (n === 1 ? 0 : (i / (n - 1)) * innerW);
    const y = (v) => padT + innerH - (v / maxVal) * innerH;

    const pts = series.map((p, i) => `${x(i)},${y(p.saving_cumulative)}`);
    const linePath = "M" + pts.join(" L");
    const areaPath =
        `M${x(0)},${y(0)} L` + pts.join(" L") + ` L${x(n - 1)},${y(0)} Z`;

    // Boundary between holiday and concessional phases.
    const holidayIdx = Math.min(holidayYears, n) - 1;
    const boundaryX = x(holidayIdx);

    // Y gridlines at 0, 25, 50, 75, 100%.
    const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => ({
        v: maxVal * f,
        yy: y(maxVal * f),
    }));

    return (
        <div className="chart">
            <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
                aria-label="Cumulative tax saving over the block period">
                {/* gridlines + y labels */}
                {ticks.map((t, i) => (
                    <g key={i}>
                        <line x1={padL} y1={t.yy} x2={W - padR} y2={t.yy}
                            stroke="var(--line)" strokeWidth="1" />
                        <text x={padL - 8} y={t.yy + 4} textAnchor="end"
                            fontFamily="var(--mono)" fontSize="10" fill="var(--muted)">
                            {fmtUSD(t.v)}
                        </text>
                    </g>
                ))}

                {/* holiday phase shading */}
                <rect x={padL} y={padT} width={boundaryX - padL} height={innerH}
                    fill="var(--saffron)" opacity="0.07" />
                <line x1={boundaryX} y1={padT} x2={boundaryX} y2={padT + innerH}
                    stroke="var(--saffron-deep)" strokeWidth="1" strokeDasharray="4 3" />
                <text x={boundaryX} y={padT + innerH + 18} textAnchor="middle"
                    fontFamily="var(--mono)" fontSize="10" fill="var(--saffron-deep)">
                    holiday ends (yr {holidayYears})
                </text>

                {/* area + line */}
                <path d={areaPath} fill="var(--green)" opacity="0.12" />
                <path d={linePath} fill="none" stroke="var(--green)" strokeWidth="2.5" />

                {/* end marker */}
                <circle cx={x(n - 1)} cy={y(series[n - 1].saving_cumulative)} r="4"
                    fill="var(--green)" />

                {/* x-axis end labels */}
                <text x={padL} y={H - 8} textAnchor="start"
                    fontFamily="var(--mono)" fontSize="10" fill="var(--muted)">yr 1</text>
                <text x={W - padR} y={H - 8} textAnchor="end"
                    fontFamily="var(--mono)" fontSize="10" fill="var(--muted)">yr {n}</text>
            </svg>
            <p className="chart-cap">
                Cumulative saving reaches <strong>{fmtUSD(series[n - 1].saving_cumulative)}</strong> over {n} years.
            </p>
        </div>
    );
}