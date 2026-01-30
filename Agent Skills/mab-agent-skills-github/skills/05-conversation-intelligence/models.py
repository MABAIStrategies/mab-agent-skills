"""
Skill 05: Sales Conversation Intelligence Miner - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConversationAnalysisRequest(BaseModel):
    """Request to analyze a sales conversation"""

    call_id: str
    transcript: str
    participants: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ObjectionFinding(BaseModel):
    category: str
    excerpt: str
    confidence: float


class ConversationAnalysis(BaseModel):
    call_id: str
    talk_ratio_rep: float
    sentiment_score: float
    objection_findings: List[ObjectionFinding]
    value_prop_mentions: int
    next_steps_defined: bool
    score: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        extra = "ignore"


class CoachingTip(BaseModel):
    title: str
    recommendation: str
    impact: str


class CoachingResponse(BaseModel):
    call_id: str
    tips: List[CoachingTip]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


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
