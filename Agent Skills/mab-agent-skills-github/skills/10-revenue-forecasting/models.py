"""
Skill 10: Revenue Forecasting & Pipeline Health Engine - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DealForecastInput(BaseModel):
    deal_id: str
    deal_size: float
    stage: str
    days_in_stage: int
    activity_level: float
    industry: Optional[str] = None
    rep_performance: float = 0.5
    engagement_score: float = 0.5
    competitor_presence: float = 0.0


class DealForecastResult(BaseModel):
    deal_id: str
    probability: float
    expected_close_date: str
    risk_factors: List[str]


class ForecastRequest(BaseModel):
    timeframe_days: int = 90
    deals: List[DealForecastInput]


class PipelineForecast(BaseModel):
    best_case: float
    likely: float
    worst_case: float
    confidence_interval: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class WebhookRequest(BaseModel):
    intent: str
    parameters: Dict[str, Any]
    user_id: str
    conversation_id: Optional[str] = None


class WebhookResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
