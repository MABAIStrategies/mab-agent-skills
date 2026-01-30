"""
Skill 09: Portfolio Showcase & Demo Environment Generator
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import DemoRequest
from service import DemoGeneratorService

app = FastAPI(title="Portfolio Showcase & Demo Environment Generator")
logger = get_logger(__name__, skill_name="demo-generator")
audit_logger = AuditLogger("demo-generator")

env_repo = FirestoreRepository("demo_environments")
service = DemoGeneratorService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "demo-generator"}


@app.get("/ready")
async def readiness_check():
    try:
        _ = env_repo.list(limit=1)
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
        "intent": "generate_demo | list_catalog | get_demo",
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

        if intent == "generate_demo":
            return await generate_demo(params, user_id)
        if intent == "list_catalog":
            return await list_catalog()
        if intent == "get_demo":
            return await get_demo(params)

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def generate_demo(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = DemoRequest(**params)
    environment = service.generate_demo(payload)

    audit_logger.log_action(
        action="GENERATE",
        user_id=user_id,
        resource_type="demo_environment",
        resource_id=environment.environment_id,
    )

    return {"success": True, "environment": environment.dict()}


async def list_catalog() -> Dict[str, Any]:
    catalog = [item.dict() for item in service.list_catalog()]
    return {"success": True, "catalog": catalog}


async def get_demo(params: Dict[str, Any]) -> Dict[str, Any]:
    environment_id = params.get("environment_id")
    if not environment_id:
        raise HTTPException(status_code=400, detail="environment_id is required")

    environment = env_repo.get(environment_id)
    if not environment:
        raise HTTPException(status_code=404, detail="Demo environment not found")

    return {"success": True, "environment": environment}
