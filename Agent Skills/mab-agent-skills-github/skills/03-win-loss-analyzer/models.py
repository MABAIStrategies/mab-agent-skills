"""
Skill 03: Proposal Win-Loss Intelligence Analyzer - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DealRecord(BaseModel):
    """Normalized deal record for analysis"""

    id: str
    account_name: str
    stage: str
    outcome: str = Field(..., description="won | lost | open")
    amount: float
    industry: Optional[str] = None
    competitor: Optional[str] = None
    objections: List[str] = Field(default_factory=list)
    demo_score: Optional[float] = None
    proposal_version: Optional[str] = None
    closed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WinLossAnalysis(BaseModel):
    """Aggregated win-loss insights"""

    analysis_id: str
    timeframe_days: int
    total_deals: int
    wins: int
    losses: int
    win_rate: float
    avg_deal_size: float
    by_competitor: Dict[str, int]
    by_industry: Dict[str, int]
    by_stage: Dict[str, int]
    top_objections: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "ignore"


class PlaybookRecommendation(BaseModel):
    """Generated recommendations from analysis"""

    headline: str
    rationale: str
    recommended_actions: List[str]


class PlaybookResponse(BaseModel):
    """Sales playbook output"""

    analysis_id: str
    executive_summary: str
    recommendations: List[PlaybookRecommendation]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class WinLossRequest(BaseModel):
    """Request payload for win-loss analysis"""

    timeframe_days: int = 90
    deals: List[DealRecord]


class WebhookRequest(BaseModel):
    """Standard webhook request format"""

    intent: str
    parameters: Dict[str, Any]
    user_id: str
    conversation_id: Optional[str] = None


class WebhookResponse(BaseModel):
    """Standard webhook response format"""

    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
