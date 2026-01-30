"""
Skill 10: Revenue Forecasting & Pipeline Health Engine - Service Layer
"""

from datetime import datetime, timedelta
from typing import List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository

from models import DealForecastInput, DealForecastResult, ForecastRequest, PipelineForecast

logger = get_logger(__name__, skill_name="revenue-forecasting")

forecast_repo = FirestoreRepository("revenue_forecasts")

STAGE_WEIGHTS = {
    "qualification": 0.2,
    "discovery": 0.3,
    "proposal": 0.6,
    "negotiation": 0.8,
    "closed": 1.0,
}


class RevenueForecastService:
    """Forecast revenue and detect pipeline risks."""

    def forecast_pipeline(self, request: ForecastRequest) -> PipelineForecast:
        results = [self._score_deal(deal) for deal in request.deals]
        best_case = sum(deal.deal_size for deal in request.deals if deal.deal_id)
        likely = sum(deal.deal_size * result.probability for deal, result in zip(request.deals, results))
        worst_case = sum(deal.deal_size * max(result.probability - 0.2, 0) for deal, result in zip(request.deals, results))
        confidence_interval = round(min(max(likely / max(best_case, 1), 0.1), 0.95), 2)

        forecast = PipelineForecast(
            best_case=round(best_case, 2),
            likely=round(likely, 2),
            worst_case=round(worst_case, 2),
            confidence_interval=confidence_interval,
        )

        forecast_repo.create(f"forecast_{datetime.utcnow().isoformat()}", forecast.dict())
        logger.info("Pipeline forecast generated", extra={"best_case": forecast.best_case})

        return forecast

    def score_deals(self, deals: List[DealForecastInput]) -> List[DealForecastResult]:
        return [self._score_deal(deal) for deal in deals]

    def _score_deal(self, deal: DealForecastInput) -> DealForecastResult:
        stage_weight = STAGE_WEIGHTS.get(deal.stage.lower(), 0.4)
        probability = (
            stage_weight * 0.35
            + deal.activity_level * 0.2
            + deal.engagement_score * 0.2
            + deal.rep_performance * 0.15
            + (1 - deal.competitor_presence) * 0.1
        )
        probability = round(min(max(probability, 0.05), 0.95), 2)

        risk_factors = []
        if deal.days_in_stage > 30:
            risk_factors.append("Extended time in stage")
        if deal.activity_level < 0.4:
            risk_factors.append("Low activity level")
        if deal.competitor_presence > 0.5:
            risk_factors.append("Competitor presence detected")

        expected_close = (datetime.utcnow() + timedelta(days=max(7, 45 - deal.days_in_stage))).date()

        return DealForecastResult(
            deal_id=deal.deal_id,
            probability=probability,
            expected_close_date=expected_close.isoformat(),
            risk_factors=risk_factors,
        )
