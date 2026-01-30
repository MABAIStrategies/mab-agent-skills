"""
Skill 03: Proposal Win-Loss Intelligence Analyzer - Service Layer
"""

import os
import uuid
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository
from shared.utils.llm import LLMClient

from models import DealRecord, WinLossAnalysis, PlaybookResponse, PlaybookRecommendation

logger = get_logger(__name__, skill_name="win-loss-analyzer")
llm = LLMClient("win-loss-analyzer")

analysis_repo = FirestoreRepository("win_loss_analyses")
playbook_repo = FirestoreRepository("win_loss_playbooks")


class WinLossAnalyzerService:
    """Service for analyzing win/loss data"""

    def analyze(self, deals: List[DealRecord], timeframe_days: int) -> WinLossAnalysis:
        """Analyze deal outcomes and generate aggregated insights."""
        if not deals:
            raise ValueError("No deals provided for analysis")

        wins = [deal for deal in deals if deal.outcome.lower() == "won"]
        losses = [deal for deal in deals if deal.outcome.lower() == "lost"]
        total_deals = len(deals)
        win_rate = round((len(wins) / total_deals) * 100, 2)
        avg_deal_size = round(sum(deal.amount for deal in deals) / total_deals, 2)

        by_competitor = self._count_by(deals, "competitor")
        by_industry = self._count_by(deals, "industry")
        by_stage = self._count_by(deals, "stage")
        top_objections = self._top_objections(deals)

        analysis_id = f"analysis_{uuid.uuid4().hex[:10]}"
        analysis = WinLossAnalysis(
            analysis_id=analysis_id,
            timeframe_days=timeframe_days,
            total_deals=total_deals,
            wins=len(wins),
            losses=len(losses),
            win_rate=win_rate,
            avg_deal_size=avg_deal_size,
            by_competitor=by_competitor,
            by_industry=by_industry,
            by_stage=by_stage,
            top_objections=top_objections,
            generated_at=datetime.utcnow(),
        )

        analysis_repo.create(analysis_id, analysis.dict())
        logger.info("Win-loss analysis created", extra={"analysis_id": analysis_id})

        return analysis

    def generate_playbook(self, analysis: WinLossAnalysis) -> PlaybookResponse:
        """Generate a sales playbook based on analysis."""
        summary = self._generate_summary(analysis)
        recommendations = self._generate_recommendations(analysis)

        playbook = PlaybookResponse(
            analysis_id=analysis.analysis_id,
            executive_summary=summary,
            recommendations=recommendations,
            generated_at=datetime.utcnow(),
        )

        playbook_repo.create(playbook.analysis_id, playbook.dict())
        logger.info("Playbook generated", extra={"analysis_id": playbook.analysis_id})

        return playbook

    def build_analysis(self, record: Dict[str, Any]) -> WinLossAnalysis:
        """Rehydrate a WinLossAnalysis from stored data."""
        return WinLossAnalysis(**record)

    def _count_by(self, deals: List[DealRecord], field: str) -> Dict[str, int]:
        values = [getattr(deal, field) for deal in deals if getattr(deal, field)]
        return dict(Counter(values))

    def _top_objections(self, deals: List[DealRecord], limit: int = 5) -> List[str]:
        objections = []
        for deal in deals:
            objections.extend(deal.objections)
        counts = Counter(objections)
        return [item for item, _ in counts.most_common(limit)]

    def _generate_summary(self, analysis: WinLossAnalysis) -> str:
        prompt = (
            "Summarize the win-loss analysis for executive review. "
            "Highlight win rate, biggest loss drivers, and top opportunity areas."
        )
        system_prompt = (
            "You are a sales operations strategist for MAB AI Strategies. "
            "Keep it concise, data-backed, and action-oriented."
        )

        if not os.getenv("ANTHROPIC_API_KEY"):
            return (
                f"Win rate sits at {analysis.win_rate}%. "
                "Focus on strengthening objection handling and improving differentiation in "
                "the most competitive industries."
            )

        return llm.generate(
            prompt=f"{prompt}\n\nAnalysis: {analysis.json()}" ,
            system_prompt=system_prompt,
            max_tokens=500,
        )

    def _generate_recommendations(self, analysis: WinLossAnalysis) -> List[PlaybookRecommendation]:
        if not os.getenv("ANTHROPIC_API_KEY"):
            return [
                PlaybookRecommendation(
                    headline="Tighten competitive positioning",
                    rationale="Losses cluster around key competitors.",
                    recommended_actions=[
                        "Refresh battlecards quarterly",
                        "Create objection scripts for top loss reasons",
                        "Run competitive demo training",
                    ],
                ),
                PlaybookRecommendation(
                    headline="Improve proposal momentum",
                    rationale="Stage analysis highlights slowdowns in mid-funnel.",
                    recommended_actions=[
                        "Introduce proposal checklists",
                        "Add exec sponsorship at proposal stage",
                        "Set 48-hour follow-up SLAs",
                    ],
                ),
            ]

        schema = {
            "recommendations": [
                {
                    "headline": "string",
                    "rationale": "string",
                    "recommended_actions": ["string"],
                }
            ]
        }
        response = llm.generate_structured(
            prompt=(
                "Generate 3 playbook recommendations based on the analysis. "
                "Focus on improving win rate and shortening sales cycles."
                f"\n\nAnalysis: {analysis.json()}"
            ),
            output_schema=schema,
            system_prompt="You are a sales enablement leader for MAB AI Strategies.",
        )

        recommendations = []
        for item in response.get("recommendations", []):
            recommendations.append(
                PlaybookRecommendation(
                    headline=item.get("headline", "Action"),
                    rationale=item.get("rationale", ""),
                    recommended_actions=item.get("recommended_actions", []),
                )
            )
        return recommendations
