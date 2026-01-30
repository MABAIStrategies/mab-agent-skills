"""
Skill 07: Upsell & Cross-Sell Opportunity Identifier - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UpsellSignalRequest(BaseModel):
    """Signals used to evaluate expansion opportunities"""

    account_id: str
    account_name: str
    utilization_rate: float
    feature_request_quality: float
    org_growth_rate: float
    roi_achievement: float
    executive_sponsorship: float
    notes: Optional[str] = None


class UpsellOpportunity(BaseModel):
    account_id: str
    account_name: str
    expansion_score: float
    recommended_tier: str
    key_signals: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "ignore"


class UpsellProposal(BaseModel):
    account_id: str
    proposal_summary: str
    expansion_tier: str
    roi_projection: str
    timeline: str
    pricing_note: str
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
