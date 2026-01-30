"""
Skill 04: Omnichannel Content Repurposing Engine - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContentSource(BaseModel):
    """Original content input"""

    source_id: str
    source_type: str = Field(..., description="webinar | blog | podcast | case_study | video")
    title: str
    body: str
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RepurposeRequest(BaseModel):
    """Request to repurpose content"""

    source: ContentSource
    target_platforms: List[str]
    tone: str = "professional"
    include_cta: bool = True


class RepurposedAsset(BaseModel):
    """Generated asset for a platform"""

    platform: str
    format: str
    headline: str
    body: str
    hashtags: List[str] = Field(default_factory=list)
    call_to_action: Optional[str] = None


class RepurposeBatch(BaseModel):
    """Batch of repurposed content"""

    batch_id: str
    source_id: str
    assets: List[RepurposedAsset]
    status: str = "complete"
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
