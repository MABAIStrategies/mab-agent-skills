"""
Skill 09: Portfolio Showcase & Demo Environment Generator - Service Layer
"""

import uuid
from datetime import datetime, timedelta
from typing import List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository

from models import DemoRequest, DemoCatalogItem, DemoEnvironment

logger = get_logger(__name__, skill_name="demo-generator")

env_repo = FirestoreRepository("demo_environments")

DEMO_CATALOG = [
    DemoCatalogItem(
        demo_id="health-intake",
        name="Patient Intake Automation",
        industry="Healthcare",
        use_case="Onboarding",
        description="Automate patient intake workflows with compliance checks.",
    ),
    DemoCatalogItem(
        demo_id="telecom-sales",
        name="Telecom Sales Ops",
        industry="Telecom",
        use_case="Sales Ops",
        description="Pipeline automation and deal acceleration dashboards.",
    ),
    DemoCatalogItem(
        demo_id="finance-invoice",
        name="Invoice Processing",
        industry="Finance",
        use_case="Operations",
        description="Automated invoice reconciliation and anomaly detection.",
    ),
    DemoCatalogItem(
        demo_id="manufacturing-supply",
        name="Supply Chain Optimization",
        industry="Manufacturing",
        use_case="Operations",
        description="Predictive supply chain insights and automation.",
    ),
]


class DemoGeneratorService:
    """Service to generate demo environments."""

    def generate_demo(self, request: DemoRequest) -> DemoEnvironment:
        selected = self._select_demos(request)
        environment_id = f"demo_{uuid.uuid4().hex[:8]}"
        demo_url = f"https://demo.mabstrategies.com/{environment_id}"
        expires_at = datetime.utcnow() + timedelta(days=7)

        environment = DemoEnvironment(
            environment_id=environment_id,
            industry=request.industry,
            selected_demos=selected,
            demo_url=demo_url,
            expires_at=expires_at,
        )

        env_repo.create(environment_id, environment.dict())
        logger.info("Demo environment created", extra={"environment_id": environment_id})

        return environment

    def list_catalog(self) -> List[DemoCatalogItem]:
        return DEMO_CATALOG

    def _select_demos(self, request: DemoRequest) -> List[DemoCatalogItem]:
        matches = [demo for demo in DEMO_CATALOG if demo.industry.lower() == request.industry.lower()]
        if matches:
            return matches[:3]
        return DEMO_CATALOG[:3]
