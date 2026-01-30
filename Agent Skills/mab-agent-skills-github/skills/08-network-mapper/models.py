"""
Skill 08: Strategic Network Relationship Mapper - Data Models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NetworkNode(BaseModel):
    node_id: str
    name: str
    node_type: str = Field(..., description="person | company | industry | role")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NetworkEdge(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    strength: float


class NetworkMapRequest(BaseModel):
    map_id: str
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    owner_id: str


class IntroPathRequest(BaseModel):
    map_id: str
    start_id: str
    target_id: str


class IntroPathResponse(BaseModel):
    map_id: str
    path: List[str]
    confidence: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class RelationshipScoreRequest(BaseModel):
    interaction_frequency: float
    recency: float
    influence_level: float
    accessibility: float


class RelationshipScore(BaseModel):
    score: float
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
