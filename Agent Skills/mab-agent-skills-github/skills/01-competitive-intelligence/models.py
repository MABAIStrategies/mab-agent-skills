"""
Skill 01: Competitive Intelligence - Data Models
Pydantic models for request/response validation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, validator


class CompetitorProfile(BaseModel):
    """Competitor profile data model"""
    id: str
    name: str
    website: HttpUrl
    linkedin_url: Optional[HttpUrl] = None
    monitored_pages: Dict[str, HttpUrl] = Field(default_factory=dict)
    alert_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "pricing_change_percent": 5.0,
            "content_change_percent": 10.0
        }
    )
    active: bool = True
    user_id: str
    last_crawled: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MonitoringRequest(BaseModel):
    """Request to monitor a new competitor"""
    company_name: str = Field(..., min_length=1, max_length=200)
    website_url: HttpUrl
    linkedin_url: Optional[HttpUrl] = None
    pages_to_monitor: Optional[Dict[str, HttpUrl]] = None
    alert_thresholds: Optional[Dict[str, float]] = None
    
    @validator('company_name')
    def validate_company_name(cls, v):
        # Remove any dangerous characters
        return v.strip()


class BattlecardRequest(BaseModel):
    """Request to generate competitive battlecard"""
    competitor_name: str = Field(..., min_length=1)
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on (pricing, features, etc.)"
    )


class IntelligenceEntry(BaseModel):
    """Competitive intelligence data model"""
    id: str
    competitor_id: str
    competitor_name: str
    type: str = Field(..., description="pricing_change | product_launch | content_update | hiring")
    page_type: str
    severity: str = Field(..., pattern="^(high|medium|low)$")
    summary: str
    details: Dict[str, Any]
    strategic_implications: str
    recommended_actions: List[str]
    detected_at: datetime
    alerted: bool = False
    notion_url: Optional[str] = None
    related_opportunities: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChangeDetection(BaseModel):
    """Detected change in competitor content"""
    page_type: str
    change_percent: float
    diff: str
    analysis: Dict[str, Any]
    severity: str
    detected_at: datetime


class CrawlResult(BaseModel):
    """Result of competitor crawl"""
    competitor_id: str
    crawled_at: datetime
    pages_crawled: List[str]
    changes_detected: List[ChangeDetection]
    errors: List[Dict[str, str]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Battlecard(BaseModel):
    """Generated competitive battlecard"""
    competitor_name: str
    executive_summary: str
    feature_comparison: Dict[str, Dict[str, str]]
    pricing_analysis: Dict[str, str]
    win_themes: List[str]
    objection_handling: Dict[str, str]
    recent_news: List[str]
    recommended_approach: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


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
