# Architecture

## Why this shape

The recommendation logic *is* encoded regulation; the tax piece is pure arithmetic; and
the project needs to survive "so how does it actually work?" scrutiny. So:

- It is **not** a pure static page (too thin to defend as a build).
- It does **not** bolt on a database for its own sake (CRUD padding signals nothing).
- It splits a **React frontend** from a **FastAPI backend** that houses the rules engine,
  tax engine, optional LLM intake, and usage/feedback logging.

## Components

### Data layer — `backend/app/data/`
The single source of truth.

- `entities.json` — one record per IFSC structure: eligibility rules (each with a
  `source` and `ref_url`), capital/net-worth values, timeline, permitted activities,
  keyword list for the classifier, and any decision branches (e.g. AIF retail vs
  non-retail net worth).
- `tax_rules.json` — holiday length, block period, post-holiday concessional rate,
  Section 80LA reference, onshore-rate bounds, and the hub-comparison data.

Updating a threshold is a one-file edit with a citation — no code change.

### Rules engine — `rules_engine.py`
Pure functions. Loads + caches the entity data, resolves branch-dependent values
(e.g. picks the right net-worth figure for retail vs non-retail), and returns a
recommendation payload. No web-framework imports, so it is unit-testable and reused
directly by the eval harness.

### Tax engine — `tax_engine.py`
Pure functions. Computes onshore tax, IFSC tax (zero during the holiday), annual saving,
holiday-period saving, and full-block saving including the concessional tail. Validates
inputs. Deliberately ignores MAT, surcharge, GST and entity-specific rules — stated as a
limitation.

### Classifier — `classifier.py`
Hybrid free-text intake. Deterministic keyword scoring runs first; the LLM is called only
when keyword confidence is below `CONFIDENCE_THRESHOLD`. Common case is free, fast and
explainable; LLM cost/latency is bounded. The gating itself is a measurable design choice.

### Logging store — `logging_store.py`
SQLite. Logs every recommendation event and any user feedback. Tables are created lazily
on first use, so the store is robust regardless of launch method. The event log doubles
as a usage dataset for evaluation.

### API — `main.py`
FastAPI. Thin routing layer over the engines, with CORS, input validation via Pydantic
schemas, and a `/stats` endpoint that aggregates the logs.

## Request flow

1. Wizard answer → `POST /recommend` → `rules_engine` → resolved entity + cited rules.
2. Tax inputs → `POST /tax/estimate` → `tax_engine` → annual + block savings.
3. Free-text → `POST /classify` → `classifier` → entity id + method + confidence.
4. Every recommendation + feedback → `logging_store` (SQLite).

## Endpoints

| Method | Path             | Purpose                                  |
|--------|------------------|------------------------------------------|
| GET    | `/health`        | Liveness check                           |
| GET    | `/entities`      | Wizard step-1 options                    |
| POST   | `/recommend`     | Resolve a chosen entity                  |
| POST   | `/tax/estimate`  | Tax-saving estimate                      |
| GET    | `/tax/rules`     | Tax parameters + hub comparison          |
| POST   | `/classify`      | Free-text → entity                       |
| POST   | `/feedback`      | Log a thumbs up/down                     |
| GET    | `/stats`         | Aggregated usage + feedback              |

## Evaluation strategy

1. **Unit tests** — deterministic correctness of both engines, including edge cases.
2. **Golden-set validation** — `eval/golden_cases.json` + `eval/run_eval.py` produce an
   accuracy figure and confusion matrix over expert-validated scenarios.
3. **Source traceability** — every output figure traces to `docs/sources.md`.
4. **Usability testing** — task-based sessions with 5–8 participants; responses logged
   via `/feedback`. Standard SUS + task completion + time-on-task.
5. **Tax-model validation** — hand-calculated cases checked against engine output.
