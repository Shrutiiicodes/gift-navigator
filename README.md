# GIFT Setup Navigator

Find the right way to set up in **GIFT City** — India's International Financial Services Centre (IFSC) — in under a minute. Answer a few questions and get a recommended entity structure, what you'd need to qualify, and an estimate of how much tax you'd save versus staying onshore.

**Live demo:** [gift-navigator.vercel.app](https://gift-navigator.vercel.app/)
**API:** [gift-navigator-api.onrender.com](https://gift-navigator-api.onrender.com/)

> ⚠️ The backend runs on a free tier that sleeps when idle, so the **first request after a while may take 30–50 seconds** to wake up. Give it a moment on first load.

> ⚠️ Prototype for educational use. All figures are **indicative**, not legal or tax advice — verify against current [IFSCA](https://www.ifsca.gov.in) circulars and the latest Finance Act.

---

## What it does

- **Guided wizard** — pick your structure and investor type, get a tailored recommendation with eligibility requirements and key benefits.
- **Tax estimator** — compare onshore vs IFSC tax over a configurable block period.
  - *Simple mode:* headline rate comparison with cumulative savings.
  - *Advanced mode:* layers in surcharge, cess, and optional MAT (minimum alternate tax), with a year-by-year cumulative chart.
- **Comparison table** — side-by-side view across the available structures and hubs.
- **Free-text intake** — describe your situation in plain language and get classified to a structure. A hybrid classifier scores keywords first (fast, free, deterministic) and only escalates to a Groq-hosted LLM when keyword confidence is low.
- **Usage analytics** — a built-in funnel (start → recommend → tax view → feedback) with step-over-step drop-off, plus a "most queried" breakdown.
- **Feedback loop** — thumbs up/down on each recommendation, logged for review.

---

## Tech stack

**Frontend** — React + Vite, [lucide-react](https://lucide.dev) icons, inline-SVG charts (no charting dependency).
**Backend** — FastAPI + Pydantic, SQLite for event/feedback logging, pytest for tests.
**LLM fallback** — [Groq](https://groq.com) (`openai/gpt-oss-20b`) for free-text classification when keyword confidence is low. The app works fully without it via keyword matching.
---

## Running locally

You'll need **Python 3.12** and **Node 18+**. Use two terminals.

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API comes up at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`, health check at `/health`.

### Frontend

```bash
cd frontend
npm install

# point the frontend at your local API
cp .env.example .env        # then ensure VITE_API_URL=http://localhost:8000

npm run dev
```

App runs at `http://localhost:5173`.

### Tests & evaluation

```bash
cd backend
python -m pytest -q          # unit tests
python -m eval.run_eval      # classifier accuracy against golden cases
```

---

## API reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/entities` | Wizard step-1 options |
| `POST` | `/recommend` | Recommend a structure for an entity + investor type |
| `POST` | `/tax/estimate` | Tax comparison (simple or advanced mode) with cumulative series |
| `GET` | `/tax/rules` | Tax parameters and comparison hubs |
| `POST` | `/classify` | Classify free-text into a structure |
| `POST` | `/feedback` | Log thumbs up/down on a recommendation |
| `POST` | `/event` | Log a client-side funnel event |
| `GET` | `/analytics` | Usage funnel + most-queried structures |
| `GET` | `/stats` | Aggregate logging stats |

Full schemas are visible in the live Swagger UI at [`/docs`](https://gift-navigator-api.onrender.com/docs).

---

## Project structure

```
gift-navigator/
├── backend/
│   ├── main.py                 # FastAPI app + routes
│   ├── app/
│   │   ├── rules_engine.py     # entity recommendation logic
│   │   ├── tax_engine.py       # simple + advanced tax estimation
│   │   ├── classifier.py       # free-text → structure (keyword + LLM fallback)
│   │   ├── logging_store.py    # SQLite events, feedback, analytics
│   │   ├── schemas.py          # Pydantic request/response models
│   │   └── data/               # entities.json, tax_rules.json
│   ├── eval/                   # golden cases + accuracy harness
│   └── tests/                  # pytest suite
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── api/client.js
│       ├── components/         # Wizard, TaxCalculator, CumulativeChart,
│       │                       # AnalyticsPanel, ComparisonTable, EntityCard…
│       └── styles/tokens.css
└── docs/                       # architecture + sources notes
```

---

## Deployment

The live demo is split across two free hosts:

- **Frontend → Vercel.** Root directory `frontend`, framework auto-detected as Vite. Set `VITE_API_URL` (no trailing slash) to the backend URL. Vite bakes env vars in at build time, so changing it requires a redeploy.
- **Backend → Render.** Root directory `backend`, Python pinned to **3.12** (via `PYTHON_VERSION` or `backend/.python-version` — 3.14 lacks prebuilt `pydantic-core` wheels). Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set `FRONTEND_ORIGIN` to your Vercel URL to lock down CORS (defaults to `*`). Set `GROQ_API_KEY` to enable the LLM free-text fallback (falls back to keyword-only if unset).

> The free Render disk is ephemeral, so SQLite analytics/feedback reset on restart — fine for a demo. For durable data, attach a persistent disk or swap to a hosted Postgres.

---

## License

Educational prototype. Not affiliated with IFSCA or any government body. Figures are illustrative and must not be relied upon for actual structuring or tax decisions.