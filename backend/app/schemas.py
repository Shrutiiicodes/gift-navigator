"""Pydantic request/response models for the GIFT Navigator API."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---- /recommend ----
class RecommendRequest(BaseModel):
    entity_id: str = Field(..., description="Entity chosen in the wizard, e.g. 'aif'")
    investor_type: Optional[str] = Field(
        None, description="For AIF only: 'retail' or 'nonretail'"
    )


class EligibilityRule(BaseModel):
    rule: str
    source: str
    ref_url: Optional[str] = None
    value: Optional[str] = None  # human-readable resolved value, if any


class RecommendResponse(BaseModel):
    id: str
    name: str
    sub: str
    tag: str
    regulator: str
    what: str
    eligibility: list[EligibilityRule]
    timeline_label: str
    activities: list[str]


# ---- /tax/estimate ----
class TaxRequest(BaseModel):
    annual_income_usd: float = Field(..., ge=0)
    onshore_rate_pct: float = Field(..., ge=0, le=100)
    block_period_years: Optional[int] = Field(None, ge=1, le=40)
    advanced: bool = False
    surcharge_pct: Optional[float] = Field(None, ge=0, le=100)
    cess_pct: Optional[float] = Field(None, ge=0, le=100)
    mat_rate_pct: Optional[float] = Field(None, ge=0, le=100)
    apply_mat: bool = False

class TaxSeriesPoint(BaseModel):
    year: int
    phase: str
    onshore_cumulative: float
    ifsc_cumulative: float
    saving_cumulative: float

class TaxResponse(BaseModel):
    annual_income_usd: float
    onshore_rate_pct: float
    onshore_tax_annual: float
    ifsc_tax_annual: float
    annual_saving: float
    holiday_years: int
    holiday_total_saving: float
    block_period_years: int
    post_holiday_rate_pct: float
    block_total_saving: float
    disclaimer: str
    ifsc_post_holiday_annual: float
    advanced: bool
    surcharge_pct: float
    cess_pct: float
    mat_rate_pct: float
    apply_mat: bool
    series: list[TaxSeriesPoint]


# ---- /classify (free-text intake) ----
class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=2000)


class ClassifyResponse(BaseModel):
    entity_id: str
    confidence: float
    method: str  # "keyword" or "llm" or "fallback"
    matched_terms: list[str] = []
    note: Optional[str] = None


# ---- /feedback ----
class FeedbackRequest(BaseModel):
    entity_id: str
    helpful: bool
    comment: Optional[str] = Field(None, max_length=2000)


class FeedbackResponse(BaseModel):
    ok: bool
    feedback_id: int

# ---- /event (client-side funnel logging) ----
class EventRequest(BaseModel):
    kind: str = Field(..., max_length=40)
    entity_id: Optional[str] = None


class EventResponse(BaseModel):
    ok: bool