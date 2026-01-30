"""
Skill 04: Omnichannel Content Repurposing Engine
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import RepurposeRequest
from service import ContentRepurposingService

app = FastAPI(title="Omnichannel Content Repurposing Engine")
logger = get_logger(__name__, skill_name="content-repurposing")
audit_logger = AuditLogger("content-repurposing")

batch_repo = FirestoreRepository("content_batches")
service = ContentRepurposingService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "content-repurposing"}


@app.get("/ready")
async def readiness_check():
    try:
        _ = batch_repo.list(limit=1)
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
        "intent": "repurpose_content | get_batch | list_batches",
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

        if intent == "repurpose_content":
            return await repurpose_content(params, user_id)
        if intent == "get_batch":
            return await get_batch(params)
        if intent == "list_batches":
            return await list_batches(params)

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def repurpose_content(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = RepurposeRequest(**params)
    batch = service.repurpose(payload)

    audit_logger.log_action(
        action="REPURPOSE",
        user_id=user_id,
        resource_type="content_batch",
        resource_id=batch.batch_id,
    )

    return {"success": True, "batch": batch.dict()}


async def get_batch(params: Dict[str, Any]) -> Dict[str, Any]:
    batch_id = params.get("batch_id")
    if not batch_id:
        raise HTTPException(status_code=400, detail="batch_id is required")

    batch = batch_repo.get(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return {"success": True, "batch": batch}


async def list_batches(params: Dict[str, Any]) -> Dict[str, Any]:
    limit = params.get("limit", 20)
    batches = batch_repo.list(order_by="-generated_at", limit=limit)
    return {"success": True, "batches": batches}
