"""
Skill 01: Competitive Intelligence War Room
Main webhook handler
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

# Shared modules
import sys
sys.path.append('/app')
from shared.auth import get_current_user, require_roles, verify_webhook_signature
from shared.logging import get_logger, AuditLogger
from shared.database import FirestoreRepository

# Skill-specific imports
from service import CompetitorMonitorService
from models import (
    CompetitorProfile,
    MonitoringRequest,
    BattlecardRequest,
    IntelligenceEntry
)

# Initialize
app = FastAPI(title="Competitive Intelligence War Room")
logger = get_logger(__name__, skill_name="competitive-intelligence")
audit_logger = AuditLogger("competitive-intelligence")
competitor_repo = FirestoreRepository("competitors")
intel_repo = FirestoreRepository("intelligence")
service = CompetitorMonitorService()

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "skill": "competitive-intelligence"}


@app.get("/ready")
async def readiness_check():
    """Readiness check"""
    # Check dependencies
    try:
        _ = competitor_repo.list(limit=1)
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
        "intent": "monitor_competitor | generate_battlecard | get_intelligence",
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
        if intent == "monitor_competitor":
            return await monitor_competitor(params, user_id, background_tasks)
        elif intent == "generate_battlecard":
            return await generate_battlecard(params, user_id)
        elif intent == "get_intelligence":
            return await get_intelligence(params, user_id)
        elif intent == "list_competitors":
            return await list_competitors(user_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown intent: {intent}")
            
    except Exception as e:
        logger.error("Webhook processing failed", error=e, user_id=current_user.get("user_id"))
        raise HTTPException(status_code=500, detail=str(e))


async def monitor_competitor(
    params: Dict[str, Any],
    user_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Register a competitor for monitoring
    
    Params:
        company_name: Competitor name
        website_url: Main website
        linkedin_url: LinkedIn company page
        pages_to_monitor: Dict of page types to URLs
        alert_thresholds: Custom thresholds
    """
    company_name = params.get("company_name")
    website_url = params.get("website_url")
    
    if not company_name or not website_url:
        raise HTTPException(
            status_code=400,
            detail="company_name and website_url are required"
        )
    
    # Create competitor profile
    competitor_data = {
        "name": company_name,
        "website": website_url,
        "linkedin_url": params.get("linkedin_url"),
        "monitored_pages": params.get("pages_to_monitor", {
            "pricing": f"{website_url}/pricing",
            "products": f"{website_url}/products",
            "about": f"{website_url}/about"
        }),
        "alert_thresholds": params.get("alert_thresholds", {
            "pricing_change_percent": 5,
            "content_change_percent": 10
        }),
        "active": True,
        "user_id": user_id
    }
    
    # Save to Firestore
    competitor_id = f"comp_{company_name.lower().replace(' ', '_')}_{user_id[:8]}"
    competitor = competitor_repo.create(competitor_id, competitor_data)
    
    # Log audit trail
    audit_logger.log_action(
        action="CREATE",
        user_id=user_id,
        resource_type="competitor",
        resource_id=competitor_id,
        details={"company_name": company_name}
    )
    
    # Schedule initial crawl in background
    background_tasks.add_task(
        service.crawl_competitor,
        competitor_id=competitor_id,
        is_initial=True
    )
    
    return {
        "success": True,
        "competitor_id": competitor_id,
        "message": f"Now monitoring {company_name}. Initial crawl scheduled.",
        "competitor": competitor
    }


async def generate_battlecard(
    params: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Generate competitive battlecard
    
    Params:
        competitor_name: Competitor to compare against
        focus_areas: Optional list of focus areas
    """
    competitor_name = params.get("competitor_name")
    
    if not competitor_name:
        raise HTTPException(status_code=400, detail="competitor_name is required")
    
    # Find competitor
    competitors = competitor_repo.list(
        filters=[("name", "==", competitor_name)],
        limit=1
    )
    
    if not competitors:
        raise HTTPException(
            status_code=404,
            detail=f"Competitor '{competitor_name}' not found. Register them first."
        )
    
    competitor = competitors[0]
    
    # Generate battlecard
    logger.info(f"Generating battlecard for {competitor_name}", user_id=user_id)
    
    battlecard = await service.generate_battlecard(
        competitor_id=competitor['id'],
        focus_areas=params.get("focus_areas")
    )
    
    # Log audit
    audit_logger.log_action(
        action="READ",
        user_id=user_id,
        resource_type="battlecard",
        resource_id=competitor['id'],
        details={"competitor": competitor_name}
    )
    
    return {
        "success": True,
        "battlecard": battlecard,
        "competitor": competitor_name,
        "generated_at": datetime.utcnow().isoformat()
    }


async def get_intelligence(
    params: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Get competitive intelligence entries
    
    Params:
        competitor_name: Filter by competitor (optional)
        since_date: Get entries since date (optional)
        severity: Filter by severity (optional)
        limit: Max results (default 20)
    """
    filters = []
    
    # Filter by competitor
    if params.get("competitor_name"):
        competitors = competitor_repo.list(
            filters=[("name", "==", params["competitor_name"])],
            limit=1
        )
        if competitors:
            filters.append(("competitor_id", "==", competitors[0]['id']))
    
    # Filter by severity
    if params.get("severity"):
        filters.append(("severity", "==", params["severity"]))
    
    # Get intelligence entries
    entries = intel_repo.list(
        filters=filters,
        order_by="-detected_at",
        limit=params.get("limit", 20)
    )
    
    return {
        "success": True,
        "count": len(entries),
        "intelligence": entries
    }


async def list_competitors(user_id: str) -> Dict[str, Any]:
    """List all registered competitors"""
    competitors = competitor_repo.list(
        filters=[("user_id", "==", user_id), ("active", "==", True)],
        order_by="name",
        limit=100
    )
    
    return {
        "success": True,
        "count": len(competitors),
        "competitors": competitors
    }


# Scheduled job endpoint (called by Cloud Scheduler)
@app.post("/cron/crawl-all")
@require_roles(["admin", "system"])
async def crawl_all_competitors(
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Scheduled job to crawl all active competitors
    Called daily by Cloud Scheduler
    """
    logger.info("Starting scheduled crawl of all competitors")
    
    # Get all active competitors
    competitors = competitor_repo.list(
        filters=[("active", "==", True)],
        limit=1000
    )
    
    # Schedule crawls
    for competitor in competitors:
        background_tasks.add_task(
            service.crawl_competitor,
            competitor_id=competitor['id'],
            is_initial=False
        )
    
    return {
        "success": True,
        "message": f"Scheduled crawls for {len(competitors)} competitors"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
