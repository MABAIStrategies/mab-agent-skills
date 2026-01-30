"""
Skill 03: Proposal Win-Loss Intelligence Analyzer
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import WinLossRequest
from service import WinLossAnalyzerService

app = FastAPI(title="Proposal Win-Loss Intelligence Analyzer")
logger = get_logger(__name__, skill_name="win-loss-analyzer")
audit_logger = AuditLogger("win-loss-analyzer")

analysis_repo = FirestoreRepository("win_loss_analyses")

service = WinLossAnalyzerService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "win-loss-analyzer"}


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
        "intent": "analyze_win_loss | generate_playbook | get_latest_analysis",
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

        if intent == "analyze_win_loss":
            return await analyze_win_loss(params, user_id)
        if intent == "generate_playbook":
            return await generate_playbook(params, user_id)
        if intent == "get_latest_analysis":
            return await get_latest_analysis()

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def analyze_win_loss(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Analyze win-loss data provided in the request."""
    payload = WinLossRequest(**params)
    analysis = service.analyze(payload.deals, payload.timeframe_days)

    audit_logger.log_action(
        action="ANALYZE",
        user_id=user_id,
        resource_type="win_loss_analysis",
        resource_id=analysis.analysis_id,
    )

    return {"success": True, "analysis": analysis.dict()}


async def generate_playbook(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    analysis_id = params.get("analysis_id")
    if not analysis_id:
        raise HTTPException(status_code=400, detail="analysis_id is required")

    analysis_record = analysis_repo.get(analysis_id)
    if not analysis_record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = service.build_analysis(analysis_record)
    playbook = service.generate_playbook(analysis)

    audit_logger.log_action(
        action="GENERATE_PLAYBOOK",
        user_id=user_id,
        resource_type="win_loss_playbook",
        resource_id=analysis_id,
    )

    return {"success": True, "playbook": playbook.dict()}


async def get_latest_analysis() -> Dict[str, Any]:
    latest = analysis_repo.list(order_by="-generated_at", limit=1)
    if not latest:
        return {"success": True, "analysis": None}

    return {"success": True, "analysis": latest[0]}
