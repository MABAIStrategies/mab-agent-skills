"""
Skill 05: Sales Conversation Intelligence Miner - Service Layer
"""

import os
import re
from typing import Any, Dict, List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository
from shared.utils.llm import LLMClient

from models import (
    ConversationAnalysisRequest,
    ConversationAnalysis,
    ObjectionFinding,
    CoachingResponse,
    CoachingTip,
)

logger = get_logger(__name__, skill_name="conversation-intelligence")
llm = LLMClient("conversation-intelligence")

analysis_repo = FirestoreRepository("conversation_analyses")
coaching_repo = FirestoreRepository("conversation_coaching")

OBJECTION_KEYWORDS = {
    "pricing": ["price", "cost", "budget", "expensive"],
    "timing": ["timeline", "later", "next quarter"],
    "authority": ["need approval", "committee", "decision"],
    "fit": ["not a fit", "missing", "doesn't"],
}

POSITIVE_WORDS = {"great", "love", "excited", "interested", "awesome"}
NEGATIVE_WORDS = {"concern", "issue", "problem", "hesitant", "worried"}


class ConversationIntelligenceService:
    """Analyze sales conversations for coaching insights."""

    def analyze(self, request: ConversationAnalysisRequest) -> ConversationAnalysis:
        talk_ratio_rep = self._calculate_talk_ratio(request.transcript)
        sentiment_score = self._calculate_sentiment(request.transcript)
        objection_findings = self._extract_objections(request.transcript)
        value_prop_mentions = self._count_value_prop_mentions(request.transcript)
        next_steps_defined = self._detect_next_steps(request.transcript)

        score = round(
            (self._score_talk_ratio(talk_ratio_rep) * 0.2)
            + (self._score_objections(objection_findings) * 0.25)
            + (self._score_value_prop(value_prop_mentions) * 0.2)
            + (self._score_next_steps(next_steps_defined) * 0.15)
            + (self._score_sentiment(sentiment_score) * 0.2),
            2,
        )

        analysis = ConversationAnalysis(
            call_id=request.call_id,
            talk_ratio_rep=talk_ratio_rep,
            sentiment_score=sentiment_score,
            objection_findings=objection_findings,
            value_prop_mentions=value_prop_mentions,
            next_steps_defined=next_steps_defined,
            score=score,
        )

        analysis_repo.create(request.call_id, analysis.dict())
        logger.info("Conversation analysis created", extra={"call_id": request.call_id})
        return analysis

    def build_analysis(self, record: Dict[str, Any]) -> ConversationAnalysis:
        """Rehydrate analysis from stored data."""
        return ConversationAnalysis(**record)

    def generate_coaching(self, analysis: ConversationAnalysis) -> CoachingResponse:
        if os.getenv("ANTHROPIC_API_KEY"):
            return self._generate_with_llm(analysis)

        tips = [
            CoachingTip(
                title="Balance talk time",
                recommendation="Aim for a 40/60 rep-to-prospect talk ratio.",
                impact="Higher engagement and stronger discovery.",
            ),
            CoachingTip(
                title="Clarify next steps",
                recommendation="Always confirm timelines and owners before ending the call.",
                impact="Prevents deals from stalling.",
            ),
        ]
        response = CoachingResponse(call_id=analysis.call_id, tips=tips)
        coaching_repo.create(analysis.call_id, response.dict())
        return response

    def _generate_with_llm(self, analysis: ConversationAnalysis) -> CoachingResponse:
        schema = {
            "tips": [
                {
                    "title": "string",
                    "recommendation": "string",
                    "impact": "string",
                }
            ]
        }
        response = llm.generate_structured(
            prompt=(
                "Provide 3 coaching tips based on this sales call analysis. "
                f"Analysis: {analysis.json()}"
            ),
            output_schema=schema,
            system_prompt="You are a sales coach for MAB AI Strategies.",
        )

        tips = [
            CoachingTip(
                title=item.get("title", "Coaching Tip"),
                recommendation=item.get("recommendation", ""),
                impact=item.get("impact", ""),
            )
            for item in response.get("tips", [])
        ]

        coaching = CoachingResponse(call_id=analysis.call_id, tips=tips)
        coaching_repo.create(analysis.call_id, coaching.dict())
        return coaching

    def _calculate_talk_ratio(self, transcript: str) -> float:
        rep_lines = len(re.findall(r"^(rep|sales):", transcript, flags=re.MULTILINE | re.IGNORECASE))
        prospect_lines = len(
            re.findall(r"^(prospect|client|buyer):", transcript, flags=re.MULTILINE | re.IGNORECASE)
        )
        total = rep_lines + prospect_lines
        if total == 0:
            return 0.5
        return round(rep_lines / total, 2)

    def _calculate_sentiment(self, transcript: str) -> float:
        words = re.findall(r"\w+", transcript.lower())
        positive = sum(1 for word in words if word in POSITIVE_WORDS)
        negative = sum(1 for word in words if word in NEGATIVE_WORDS)
        if positive + negative == 0:
            return 0.5
        return round(positive / (positive + negative), 2)

    def _extract_objections(self, transcript: str) -> List[ObjectionFinding]:
        findings = []
        lower_text = transcript.lower()
        for category, keywords in OBJECTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lower_text:
                    findings.append(
                        ObjectionFinding(
                            category=category,
                            excerpt=keyword,
                            confidence=0.7,
                        )
                    )
                    break
        return findings

    def _count_value_prop_mentions(self, transcript: str) -> int:
        return len(re.findall(r"roi|value|impact|outcome", transcript, flags=re.IGNORECASE))

    def _detect_next_steps(self, transcript: str) -> bool:
        return bool(re.search(r"next steps|follow up|schedule|timeline", transcript, re.IGNORECASE))

    def _score_talk_ratio(self, ratio: float) -> float:
        if 0.35 <= ratio <= 0.55:
            return 1.0
        return 0.6

    def _score_objections(self, objections: List[ObjectionFinding]) -> float:
        return 1.0 if objections else 0.7

    def _score_value_prop(self, mentions: int) -> float:
        return 1.0 if mentions >= 2 else 0.6

    def _score_next_steps(self, defined: bool) -> float:
        return 1.0 if defined else 0.5

    def _score_sentiment(self, sentiment: float) -> float:
        return 1.0 if sentiment >= 0.6 else 0.6
