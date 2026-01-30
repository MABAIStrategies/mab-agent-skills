"""
Skill 10: Revenue Forecasting & Pipeline Health Engine
Main webhook handler
"""

from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Depends

import sys
sys.path.append('/app')
from shared.auth import get_current_user
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

from models import ForecastRequest
from service import RevenueForecastService

app = FastAPI(title="Revenue Forecasting & Pipeline Health Engine")
logger = get_logger(__name__, skill_name="revenue-forecasting")
audit_logger = AuditLogger("revenue-forecasting")

forecast_repo = FirestoreRepository("revenue_forecasts")
service = RevenueForecastService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "skill": "revenue-forecasting"}


@app.get("/ready")
async def readiness_check():
    try:
        _ = forecast_repo.list(limit=1)
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
        "intent": "forecast_pipeline | score_deals",
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

        if intent == "forecast_pipeline":
            return await forecast_pipeline(params, user_id)
        if intent == "score_deals":
            return await score_deals(params, user_id)

        raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")

    except Exception as exc:
        logger.error("Webhook processing failed", error=exc)
        raise HTTPException(status_code=500, detail=str(exc))


async def forecast_pipeline(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = ForecastRequest(**params)
    forecast = service.forecast_pipeline(payload)

    audit_logger.log_action(
        action="FORECAST",
        user_id=user_id,
        resource_type="pipeline_forecast",
        resource_id=user_id,
    )

    return {"success": True, "forecast": forecast.dict()}


async def score_deals(params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    payload = ForecastRequest(**params)
    results = service.score_deals(payload.deals)

    audit_logger.log_action(
        action="SCORE",
        user_id=user_id,
        resource_type="deal_forecast",
        resource_id=user_id,
    )

    return {"success": True, "deals": [result.dict() for result in results]}
