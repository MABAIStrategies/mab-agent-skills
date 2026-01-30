"""
Skill 07: Upsell & Cross-Sell Opportunity Identifier - Service Layer
"""

import os
from typing import Any, Dict, List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository
from shared.utils.llm import LLMClient

from models import UpsellSignalRequest, UpsellOpportunity, UpsellProposal

logger = get_logger(__name__, skill_name="upsell-identifier")
llm = LLMClient("upsell-identifier")

opportunity_repo = FirestoreRepository("upsell_opportunities")
proposal_repo = FirestoreRepository("upsell_proposals")


class UpsellIdentifierService:
    """Identify and propose expansion opportunities."""

    def score_opportunity(self, signals: UpsellSignalRequest) -> UpsellOpportunity:
        score = (
            signals.utilization_rate * 0.30
            + signals.feature_request_quality * 0.25
            + signals.org_growth_rate * 0.20
            + signals.roi_achievement * 0.15
            + signals.executive_sponsorship * 0.10
        )
        score = round(score * 100, 2)
        recommended_tier = self._recommend_tier(score)
        key_signals = self._key_signals(signals)

        opportunity = UpsellOpportunity(
            account_id=signals.account_id,
            account_name=signals.account_name,
            expansion_score=score,
            recommended_tier=recommended_tier,
            key_signals=key_signals,
        )

        opportunity_repo.create(signals.account_id, opportunity.dict())
        logger.info("Upsell opportunity scored", extra={"account_id": signals.account_id})

        return opportunity

    def generate_proposal(self, opportunity: UpsellOpportunity) -> UpsellProposal:
        if os.getenv("ANTHROPIC_API_KEY"):
            summary = llm.generate(
                prompt=(
                    "Draft a concise upsell proposal summary for the account. "
                    f"Opportunity: {opportunity.json()}"
                ),
                system_prompt="You are a revenue strategist for MAB AI Strategies.",
                max_tokens=400,
            )
        else:
            summary = (
                f"{opportunity.account_name} shows strong expansion signals. "
                "Recommend upgrading to the next tier with a focus on ROI proof and executive visibility."
            )

        proposal = UpsellProposal(
            account_id=opportunity.account_id,
            proposal_summary=summary,
            expansion_tier=opportunity.recommended_tier,
            roi_projection="Projected 25-40% efficiency lift",
            timeline="Implementation in 4-6 weeks",
            pricing_note="Include a 10% loyalty discount for expansion",
        )

        proposal_repo.create(opportunity.account_id, proposal.dict())
        return proposal

    def build_opportunity(self, record: Dict[str, Any]) -> UpsellOpportunity:
        """Rehydrate opportunity from stored data."""
        return UpsellOpportunity(**record)

    def _recommend_tier(self, score: float) -> str:
        if score >= 80:
            return "Enterprise+"
        if score >= 60:
            return "Growth"
        return "Core"

    def _key_signals(self, signals: UpsellSignalRequest) -> List[str]:
        highlights = []
        if signals.utilization_rate >= 0.8:
            highlights.append("High utilization")
        if signals.feature_request_quality >= 0.7:
            highlights.append("Strong feature demand")
        if signals.org_growth_rate >= 0.6:
            highlights.append("Org growth")
        if signals.roi_achievement >= 0.7:
            highlights.append("ROI achieved")
        if signals.executive_sponsorship >= 0.6:
            highlights.append("Executive engagement")
        return highlights
