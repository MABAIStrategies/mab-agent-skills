"""
Skill 02: Client Success Health Monitor & Churn Predictor
Main webhook handler
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Shared modules
import sys
sys.path.append('/app')
from shared.auth import get_current_user, require_roles
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository, PostgresRepository

# Skill-specific imports
from service import ClientHealthService
from models import (
    HealthScoreCalculation,
    ChurnPrediction,
    RetentionCampaignRequest,
    AccountHealthRecord
)

# Initialize
app = FastAPI(title="Client Health Monitor & Churn Predictor")
logger = get_logger(__name__, skill_name="client-health-monitor")
audit_logger = AuditLogger("client-health-monitor")

# Repositories
health_repo = FirestoreRepository("account_health")
account_repo = Firestore Repository("accounts")
intervention_repo = FirestoreRepository("interventions")

# Service
service = ClientHealthService()

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "skill": "client-health-monitor"}


@app.get("/ready")
async def readiness_check():
    """Readiness check"""
    try:
        _ = health_repo.list(limit=1)
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", error=e)
        raise HTTPException(status_code=503, detail="Service not ready")


# Main webhook endpoint
@app.post("/webhook")
async def handle_webhook(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Handle webhook from Google Antigravity
    
    Expected payload:
    {
        "intent": "calculate_health_score | get_at_risk_accounts | generate_retention_plan | predict_churn",
        "parameters": {...},
        "user_id": "user_id",
        "conversation_id": "conv_id"
    }
    """
    try:
        intent = request.get("intent")
        params = request.get("parameters", {})
        user_id = current_user.get("user_id")
        
        logger.info(
            f"Webhook received: {intent}",
            user_id=user_id,
            extra={"intent": intent, "params": params}
        )
        
        # Route to appropriate handler
        if intent == "calculate_health_score":
            return await calculate_health_score(params, user_id, background_tasks)
        elif intent == "get_at_risk_accounts":
            return await get_at_risk_accounts(params, user_id)
        elif intent == "generate_retention_plan":
            return await generate_retention_plan(params, user_id)
        elif intent == "predict_churn":
            return await predict_churn(params, user_id)
        elif intent == "get_health_report":
            return await get_health_report(params, user_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")
            
    except Exception as e:
        logger.error("Webhook processing failed", error=e, user_id=current_user.get("user_id"))
        raise HTTPException(status_code=500, detail=str(e))


async def calculate_health_score(
    params: Dict[str, Any],
    user_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Calculate health score for an account
    
    Params:
        account_id: Account to score (optional - if not provided, score all)
        force_refresh: Force recalculation even if recent score exists
    """
    account_id = params.get("account_id")
    force_refresh = params.get("force_refresh", False)
    
    if account_id:
        # Calculate for specific account
        health_record = await service.calculate_health_score(
            account_id=account_id,
            force_refresh=force_refresh
        )
        
        # Log audit
        audit_logger.log_action(
            action="CALCULATE",
            user_id=user_id,
            resource_type="health_score",
            resource_id=account_id
        )
        
        return {
            "success": True,
            "account_id": account_id,
            "health_score": health_record
        }
    else:
        # Schedule calculation for all accounts
        accounts = account_repo.list(
            filters=[("active", "==", True)],
            limit=1000
        )
        
        for account in accounts:
            background_tasks.add_task(
                service.calculate_health_score,
                account_id=account["id"]
            )
        
        return {
            "success": True,
            "message": f"Health score calculation scheduled for {len(accounts)} accounts"
        }


async def get_at_risk_accounts(
    params: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Get accounts at risk of churn
    
    Params:
        status: Filter by status (red | yellow | green)
        limit: Max results (default 50)
        sort_by: Sort field (default: health_score)
    """
    status = params.get("status")
    limit = params.get("limit", 50)
    sort_by = params.get("sort_by", "health_score")
    
    filters = []
    
    # Filter by status if provided
    if status:
        filters.append(("status", "==", status.lower()))
    else:
        # Default: show red and yellow only
        filters.append(("status", "in", ["red", "yellow"]))
    
    # Get at-risk accounts
    at_risk = health_repo.list(
        filters=filters,
        order_by=sort_by,
        limit=limit
    )
    
    # Enrich with account details
    enriched = []
    for health_record in at_risk:
        account = account_repo.get(health_record["account_id"])
        if account:
            enriched.append({
                **health_record,
                "account_name": account.get("name"),
                "csm_assigned": account.get("csm_assigned"),
                "mrr": account.get("mrr")
            })
    
    # Group by severity
    red_accounts = [a for a in enriched if a["status"] == "red"]
    yellow_accounts = [a for a in enriched if a["status"] == "yellow"]
    
    return {
        "success": True,
        "summary": {
            "total_at_risk": len(enriched),
            "red_count": len(red_accounts),
            "yellow_count": len(yellow_accounts)
        },
        "red_accounts": red_accounts,
        "yellow_accounts": yellow_accounts
    }


async def generate_retention_plan(
    params: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Generate personalized retention campaign
    
    Params:
        account_id: Account to create plan for
        campaign_type: email | call | executive_engagement
    """
    account_id = params.get("account_id")
    campaign_type = params.get("campaign_type", "email")
    
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")
    
    # Get account health data
    health_record = health_repo.get(f"health_{account_id}")
    if not health_record:
        raise HTTPException(status_code=404, detail="Account health data not found")
    
    # Get account details
    account = account_repo.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Generate campaign
    logger.info(f"Generating retention campaign for {account_id}", user_id=user_id)
    
    campaign = await service.generate_retention_campaign(
        account=account,
        health_record=health_record,
        campaign_type=campaign_type
    )
    
    # Save intervention record
    intervention_id = intervention_repo.create(
        f"intervention_{account_id}_{int(datetime.utcnow().timestamp())}",
        {
            "account_id": account_id,
            "type": "retention_campaign",
            "campaign_type": campaign_type,
            "campaign_content": campaign,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "executed": False
        }
    )
    
    # Log audit
    audit_logger.log_action(
        action="CREATE",
        user_id=user_id,
        resource_type="retention_campaign",
        resource_id=intervention_id["id"],
        details={"account_id": account_id}
    )
    
    return {
        "success": True,
        "account_id": account_id,
        "account_name": account.get("name"),
        "campaign": campaign,
        "intervention_id": intervention_id["id"]
    }


async def predict_churn(
    params: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Predict churn probability for an account
    
    Params:
        account_id: Account to predict
        prediction_window_days: Days into future (30, 60, or 90)
    """
    account_id = params.get("account_id")
    window_days = params.get("prediction_window_days", 30)
    
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")
    
    # Get prediction
    prediction = await service.predict_churn(
        account_id=account_id,
        window_days=window_days
    )
    
    return {
        "success": True,
        "account_id": account_id,
        "prediction": prediction
    }


async def get_health_report(
    params: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Get comprehensive health report
    
    Params:
        timeframe_days: Report period (default 30)
    """
    timeframe_days = params.get("timeframe_days", 30)
    
    # Get all health records
    all_health = health_repo.list(limit=10000)
    
    # Calculate aggregate metrics
    total_accounts = len(all_health)
    red_count = sum(1 for h in all_health if h.get("status") == "red")
    yellow_count = sum(1 for h in all_health if h.get("status") == "yellow")
    green_count = sum(1 for h in all_health if h.get("status") == "green")
    
    avg_health_score = sum(h.get("health_score", 0) for h in all_health) / total_accounts if total_accounts > 0 else 0
    
    # Get intervention history
    since_date = datetime.utcnow() - timedelta(days=timeframe_days)
    interventions = intervention_repo.list(
        filters=[("created_at", ">=", since_date)],
        limit=1000
    )
    
    # Calculate save rate
    executed_interventions = [i for i in interventions if i.get("executed")]
    successful_saves = [i for i in executed_interventions if i.get("outcome") == "saved"]
    save_rate = len(successful_saves) / len(executed_interventions) * 100 if executed_interventions else 0
    
    return {
        "success": True,
        "report": {
            "timeframe_days": timeframe_days,
            "total_accounts": total_accounts,
            "health_distribution": {
                "red": red_count,
                "yellow": yellow_count,
                "green": green_count
            },
            "average_health_score": round(avg_health_score, 2),
            "interventions": {
                "total": len(interventions),
                "executed": len(executed_interventions),
                "save_rate": round(save_rate, 2)
            },
            "top_risk_factors": await service.get_top_risk_factors(timeframe_days)
        }
    }


# Scheduled job endpoint
@app.post("/cron/calculate-all-scores")
@require_roles(["admin", "system"])
async def calculate_all_scores(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Scheduled job to calculate health scores for all accounts
    Called daily by Cloud Scheduler
    """
    logger.info("Starting scheduled health score calculation")
    
    # Get all active accounts
    accounts = account_repo.list(
        filters=[("active", "==", True)],
        limit=10000
    )
    
    # Schedule calculations
    for account in accounts:
        background_tasks.add_task(
            service.calculate_health_score,
            account_id=account["id"]
        )
    
    return {
        "success": True,
        "message": f"Scheduled health score calculation for {len(accounts)} accounts"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
