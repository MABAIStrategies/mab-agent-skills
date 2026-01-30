"""
Skill 08: Strategic Network Relationship Mapper
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import NetworkMapRequest, IntroPathRequest, RelationshipScoreRequest
from service import NetworkMapperService

app = FastAPI(title="Strategic Network Relationship Mapper")
logger = get_logger(__name__, skill_name="network-mapper")
audit_logger = AuditLogger("network-mapper")

map_repo = FirestoreRepository("network_maps")
service = NetworkMapperService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "network-mapper"}


@app.get("/ready")
async def readiness_check():
    try:
        _ = map_repo.list(limit=1)
        return {"status": "ready"}
    except Exception as exc:
        logger.error("Readiness check failed", error=exc)
        raise HTTPException(status_code=503, detail="Service not ready")


@app.post("/webhook")
async def handle_webhook(
    request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
):
    """
    Expected payload:
    {
        "intent": "store_network | find_intro_path | score_relationship",
        "parameters": {...},
        "user_id": "user_id",
        "conversation_id": "conv_id"
    }
    """
    try:
        intent = request.get("intent")
        params = request.get("parameters", {})
        user_id = current_user.get("user_id")

        logger.info("Webhook received", extra={"intent": intent, "user_id": user_id})

        if intent == "store_network":
            return await store_network(params, user_id)
        if intent == "find_intro_path":
            return await find_intro_path(params, user_id)
        if intent == "score_relationship":
            return await score_relationship(params, user_id)

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def store_network(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = NetworkMapRequest(**params)
    result = service.store_map(payload)

    audit_logger.log_action(
        action="STORE",
        user_id=user_id,
        resource_type="network_map",
        resource_id=payload.map_id,
    )

    return {"success": True, "result": result}


async def find_intro_path(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = IntroPathRequest(**params)
    result = service.find_intro_path(payload)

    audit_logger.log_action(
        action="PATHFIND",
        user_id=user_id,
        resource_type="network_map",
        resource_id=payload.map_id,
    )

    return {"success": True, "path": result.dict()}


async def score_relationship(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = RelationshipScoreRequest(**params)
    result = service.score_relationship(payload)

    audit_logger.log_action(
        action="SCORE",
        user_id=user_id,
        resource_type="relationship_score",
        resource_id=user_id,
    )

    return {"success": True, "score": result.dict()}
