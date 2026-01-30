"""
Skill 06: Contract Red Flag Detector & Risk Mitigator - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContractReviewRequest(BaseModel):
    """Request payload for contract review"""

    contract_id: str
    contract_title: Optional[str] = None
    contract_text: str
    counterparty: Optional[str] = None


class ClauseFinding(BaseModel):
    clause_type: str
    risk_level: str
    excerpt: str
    recommendation: str


class ContractReview(BaseModel):
    contract_id: str
    risk_score: float
    risk_level: str
    findings: List[ClauseFinding]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "ignore"


class RedlineRecommendation(BaseModel):
    contract_id: str
    redlines: List[str]
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
