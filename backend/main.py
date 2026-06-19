"""GIFT Setup Navigator API.

Run locally:  uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import classifier, logging_store, rules_engine, tax_engine
from app.schemas import (
    ClassifyRequest,
    ClassifyResponse,
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


@app.on_event("startup")
def _startup() -> None:
    logging_store.init_db()


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
    logging_store.log_event("recommend", req.entity_id, {"investor_type": req.investor_type})
    return RecommendResponse(**result)


@app.post("/tax/estimate", response_model=TaxResponse)
def tax_estimate(req: TaxRequest) -> TaxResponse:
    try:
        result = tax_engine.estimate(req.annual_income_usd, req.onshore_rate_pct)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return TaxResponse(**result)


@app.get("/tax/rules")
def tax_rules() -> dict:
    """Expose the tax parameters + comparison hubs (for the comparison table)."""
    return tax_engine.load_tax_rules()


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    result = classifier.classify(req.text)
    logging_store.log_event("classify", result["entity_id"], {"method": result["method"]})
    return ClassifyResponse(**result)


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest) -> FeedbackResponse:
    fid = logging_store.log_feedback(req.entity_id, req.helpful, req.comment)
    return FeedbackResponse(ok=True, feedback_id=fid)


@app.get("/stats")
def stats() -> dict:
    return logging_store.stats()
