# GIFT Setup Navigator

A guided web tool that helps a founder, fund manager, or foreign firm answer three
questions about setting up in India's GIFT City IFSC:

1. **Which entity structure fits me?** (recommendation engine over IFSCA rules)
2. **What do I need to qualify?** (eligibility, capital thresholds, timeline, permitted activities — shown as a term-sheet card, with sources)
3. **How much tax would I save?** (estimator over the Section 80LA tax-holiday period)

It turns expensive, fragmented advisory into a self-serve flow.

## Architecture at a glance

```
React + Vite (frontend)  ──HTTP/JSON──>  FastAPI (backend)
                                          ├─ rules_engine   (answers -> entity)
                                          ├─ tax_engine     (saving math)
                                          ├─ classifier     (free-text -> entity; keyword + LLM fallback)
                                          ├─ logging_store  (SQLite events + feedback)
                                          └─ data/*.json    (cited source of truth)
```

The regulation lives as **structured, cited data** (`backend/app/data/entities.json`,
`tax_rules.json`), not hard-coded strings — so every figure is auditable and updating a
threshold is a one-file edit. See `docs/architecture.md` and `docs/sources.md`.

## Run it locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API now at http://localhost:8000  (docs at /docs)
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env          # VITE_API_URL=http://localhost:8000
npm run dev
# App now at http://localhost:5173
```

## Prove it works

```bash
cd backend
python -m pytest -q            # 22 unit tests across both engines
python -m eval.run_eval        # classifier accuracy by path + difficulty, confusion matrix
```

The eval prints overall accuracy plus a breakdown by **resolution path** (keyword vs
fallback vs LLM) and by **case difficulty** (easy vs hard) over a 53-case expert-validated
golden set, with a confusion matrix and the escalation rate. Reporting the keyword and
escalation paths separately is what quantifies the value of the LLM fallback rather than
assuming it.

## Features

- **Guided wizard + free-text intake** — pick an activity, or describe the business in
  plain English (keyword match with confidence-gated LLM fallback).
- **Term-sheet result card** — eligibility, capital thresholds, timeline and activities,
  each rule shown with its source.
- **Tax estimator** — adjustable block period (10–25 years) with a year-by-year cumulative
  savings chart, and an **advanced mode** that adds surcharge, cess and minimum alternate
  tax to narrow the gap to a filing-grade estimate.
- **Usage analytics** — a funnel view (`Usage` in the header) showing which structures are
  most queried and where users abandon the flow.

## Deploy

- **Backend → Render** (free tier): new Web Service from this repo, root directory
  `backend/`, build `pip install -r requirements.txt`, start
  `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set `FRONTEND_ORIGIN` to your frontend
  URL, and `ANTHROPIC_API_KEY` only if you want the LLM free-text fallback.
- **Frontend → Vercel / Netlify**: root directory `frontend/`, build `npm run build`,
  output `dist`. Set `VITE_API_URL` to the Render URL.

Free-tier backends sleep after inactivity — hit `/health` once before a live demo.

## Optional: LLM free-text intake

The free-text box ("describe your business in your own words") uses keyword matching
first and only escalates to an LLM when keyword confidence is below a threshold
(`classifier.CONFIDENCE_THRESHOLD`). With no `ANTHROPIC_API_KEY` set, it runs purely on
keywords and falls back to a safe default. Uncomment `anthropic` in `requirements.txt`
to enable the LLM path.

## Disclaimer

Figures are **indicative** and were coded for a prototype. Verify every threshold against
the current IFSCA circulars and the latest Finance Act before any real use. This is not
legal or tax advice.
