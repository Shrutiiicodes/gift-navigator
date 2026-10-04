from __future__ import annotations

import os
import secrets
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import classifier, logging_store, rules_engine, tax_engine
from app.schemas import (
    ClassifyRequest,
    ClassifyResponse,
    EventRequest,
    EventResponse,
    FeedbackRequest,
    FeedbackResponse,
    RecommendRequest,
    RecommendResponse,
    TaxRequest,
    TaxResponse,
)

app = FastAPI(
    title="GIFT Setup Navigator API",
    version="1.0.0",
    description="Recommends a GIFT IFSC entity structure and estimates tax savings.",
)

# CORS - set FRONTEND_ORIGIN in production (e.g. https://gift-navigator.vercel.app)
_origins = os.environ.get("FRONTEND_ORIGIN", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/entities")
def entities() -> dict[str, list]:
    """Wizard step-1 options, served from the data layer."""
    return {"options": rules_engine.wizard_options()}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest) -> RecommendResponse:
    try:
        result = rules_engine.recommend(req.entity_id, req.investor_type)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown entity '{req.entity_id}'")
    logging_store.log_event(
        "recommend", req.entity_id, {"investor_type": req.investor_type}, req.session_id
    )
    return RecommendResponse(**result)


@app.post("/tax/estimate", response_model=TaxResponse)
def tax_estimate(req: TaxRequest) -> TaxResponse:
    try:
        result = tax_engine.estimate(
            req.annual_income_usd,
            req.onshore_rate_pct,
            block_period_years=req.block_period_years,
            advanced=req.advanced,
            surcharge_pct=req.surcharge_pct,
            cess_pct=req.cess_pct,
            mat_rate_pct=req.mat_rate_pct,
            apply_mat=req.apply_mat,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return TaxResponse(**result)


@app.post("/event", response_model=EventResponse)
def event(req: EventRequest) -> EventResponse:
    """Client-side funnel events ('start', 'tax_view')."""
    logging_store.log_event(req.kind, req.entity_id, session_id=req.session_id)
    return EventResponse(ok=True)


@app.get("/analytics")
def analytics() -> dict:
    """Most-queried structures, feedback totals, and the per-session funnel."""
    data = logging_store.analytics()
    entities = rules_engine.load_entities()
    for row in data["most_queried"]:
        row["name"] = entities.get(row["entity_id"], {}).get("name", row["entity_id"])
    return data


@app.get("/export")
def export(x_admin_token: Optional[str] = Header(None)) -> dict:
    """Raw events + feedback (includes free-text comments). Disabled unless
    ADMIN_TOKEN is set; callers must send it as the X-Admin-Token header."""
    token = os.environ.get("ADMIN_TOKEN")
    if not token:
        raise HTTPException(status_code=404, detail="Export is not enabled")
    if not secrets.compare_digest((x_admin_token or "").encode(), token.encode()):
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return logging_store.export()


@app.get("/tax/rules")
def tax_rules() -> dict:
    """Expose the tax parameters + comparison hubs (for the comparison table)."""
    return tax_engine.load_tax_rules()


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    result = classifier.classify(req.text)
    logging_store.log_event(
        "classify", result["entity_id"], {"method": result["method"]}, req.session_id
    )
    return ClassifyResponse(**result)


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest) -> FeedbackResponse:
    fid = logging_store.log_feedback(
        req.entity_id, req.helpful, req.comment, req.session_id
    )
    return FeedbackResponse(ok=True, feedback_id=fid)
