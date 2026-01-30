"""
Skill 05: Sales Conversation Intelligence Miner
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import ConversationAnalysisRequest
from service import ConversationIntelligenceService

app = FastAPI(title="Sales Conversation Intelligence Miner")
logger = get_logger(__name__, skill_name="conversation-intelligence")
audit_logger = AuditLogger("conversation-intelligence")

analysis_repo = FirestoreRepository("conversation_analyses")

service = ConversationIntelligenceService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "conversation-intelligence"}


@app.get("/ready")
async def readiness_check():
    try:
        _ = analysis_repo.list(limit=1)
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
        "intent": "analyze_conversation | generate_coaching | get_analysis",
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

        if intent == "analyze_conversation":
            return await analyze_conversation(params, user_id)
        if intent == "generate_coaching":
            return await generate_coaching(params, user_id)
        if intent == "get_analysis":
            return await get_analysis(params)

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def analyze_conversation(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = ConversationAnalysisRequest(**params)
    analysis = service.analyze(payload)

    audit_logger.log_action(
        action="ANALYZE",
        user_id=user_id,
        resource_type="conversation_analysis",
        resource_id=payload.call_id,
    )

    return {"success": True, "analysis": analysis.dict()}


async def generate_coaching(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    call_id = params.get("call_id")
    if not call_id:
        raise HTTPException(status_code=400, detail="call_id is required")

    analysis_record = analysis_repo.get(call_id)
    if not analysis_record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = service.build_analysis(analysis_record)
    coaching = service.generate_coaching(analysis)

    audit_logger.log_action(
        action="COACH",
        user_id=user_id,
        resource_type="conversation_coaching",
        resource_id=call_id,
    )

    return {"success": True, "coaching": coaching.dict()}


async def get_analysis(params: Dict[str, Any]) -> Dict[str, Any]:
    call_id = params.get("call_id")
    if not call_id:
        raise HTTPException(status_code=400, detail="call_id is required")

    analysis = analysis_repo.get(call_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {"success": True, "analysis": analysis}
