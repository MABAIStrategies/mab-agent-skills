"""
Skill 06: Contract Red Flag Detector & Risk Mitigator
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import ContractReviewRequest
from service import ContractRiskService

app = FastAPI(title="Contract Red Flag Detector & Risk Mitigator")
logger = get_logger(__name__, skill_name="contract-risk-detector")
audit_logger = AuditLogger("contract-risk-detector")

review_repo = FirestoreRepository("contract_reviews")
service = ContractRiskService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "contract-risk-detector"}


@app.get("/ready")
async def readiness_check():
    try:
        _ = review_repo.list(limit=1)
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
        "intent": "review_contract | generate_redlines | get_review",
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

        if intent == "review_contract":
            return await review_contract(params, user_id)
        if intent == "generate_redlines":
            return await generate_redlines(params, user_id)
        if intent == "get_review":
            return await get_review(params)

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def review_contract(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = ContractReviewRequest(**params)
    review = service.review_contract(payload)

    audit_logger.log_action(
        action="REVIEW",
        user_id=user_id,
        resource_type="contract_review",
        resource_id=payload.contract_id,
    )

    return {"success": True, "review": review.dict()}


async def generate_redlines(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    contract_id = params.get("contract_id")
    if not contract_id:
        raise HTTPException(status_code=400, detail="contract_id is required")

    review_record = review_repo.get(contract_id)
    if not review_record:
        raise HTTPException(status_code=404, detail="Review not found")

    review = service.build_review(review_record)
    redlines = service.generate_redlines(review)

    audit_logger.log_action(
        action="REDLINE",
        user_id=user_id,
        resource_type="contract_redlines",
        resource_id=contract_id,
    )

    return {"success": True, "redlines": redlines.dict()}


async def get_review(params: Dict[str, Any]) -> Dict[str, Any]:
    contract_id = params.get("contract_id")
    if not contract_id:
        raise HTTPException(status_code=400, detail="contract_id is required")

    review = review_repo.get(contract_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return {"success": True, "review": review}
