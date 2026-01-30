"""
Skill 09: Portfolio Showcase & Demo Environment Generator - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DemoRequest(BaseModel):
    industry: str
    pain_points: List[str]
    company_size: str
    requested_agents: Optional[List[str]] = None


class DemoCatalogItem(BaseModel):
    demo_id: str
    name: str
    industry: str
    use_case: str
    description: str


class DemoEnvironment(BaseModel):
    environment_id: str
    industry: str
    selected_demos: List[DemoCatalogItem]
    demo_url: str
    expires_at: datetime
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
