"""
Skill 07: Upsell & Cross-Sell Opportunity Identifier
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import UpsellSignalRequest
from service import UpsellIdentifierService

app = FastAPI(title="Upsell & Cross-Sell Opportunity Identifier")
logger = get_logger(__name__, skill_name="upsell-identifier")
audit_logger = AuditLogger("upsell-identifier")

opportunity_repo = FirestoreRepository("upsell_opportunities")

service = UpsellIdentifierService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "upsell-identifier"}


@app.get("/ready")
async def readiness_check():
    try:
        _ = opportunity_repo.list(limit=1)
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
        "intent": "score_opportunity | generate_proposal | get_opportunity",
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

        if intent == "score_opportunity":
            return await score_opportunity(params, user_id)
        if intent == "generate_proposal":
            return await generate_proposal(params, user_id)
        if intent == "get_opportunity":
            return await get_opportunity(params)

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def score_opportunity(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = UpsellSignalRequest(**params)
    opportunity = service.score_opportunity(payload)

    audit_logger.log_action(
        action="SCORE",
        user_id=user_id,
        resource_type="upsell_opportunity",
        resource_id=payload.account_id,
    )

    return {"success": True, "opportunity": opportunity.dict()}


async def generate_proposal(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    account_id = params.get("account_id")
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")

    opportunity_record = opportunity_repo.get(account_id)
    if not opportunity_record:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    opportunity = service.build_opportunity(opportunity_record)
    proposal = service.generate_proposal(opportunity)

    audit_logger.log_action(
        action="PROPOSE",
        user_id=user_id,
        resource_type="upsell_proposal",
        resource_id=account_id,
    )

    return {"success": True, "proposal": proposal.dict()}


async def get_opportunity(params: Dict[str, Any]) -> Dict[str, Any]:
    account_id = params.get("account_id")
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")

    opportunity = opportunity_repo.get(account_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return {"success": True, "opportunity": opportunity}
