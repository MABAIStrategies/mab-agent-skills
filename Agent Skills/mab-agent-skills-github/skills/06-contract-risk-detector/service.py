"""
Skill 06: Contract Red Flag Detector & Risk Mitigator - Service Layer
"""

import re
from typing import Any, Dict, List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository

from models import ContractReviewRequest, ContractReview, ClauseFinding, RedlineRecommendation

logger = get_logger(__name__, skill_name="contract-risk-detector")

review_repo = FirestoreRepository("contract_reviews")
redline_repo = FirestoreRepository("contract_redlines")

RISK_PATTERNS = [
    {
        "clause_type": "Unlimited Liability",
        "pattern": r"unlimited liability|liability without limit",
        "risk_level": "high",
        "recommendation": "Cap liability to 12-24 months of fees paid.",
    },
    {
        "clause_type": "IP Ownership Reversion",
        "pattern": r"all intellectual property shall belong to client|assign all IP",
        "risk_level": "high",
        "recommendation": "Retain ownership of pre-existing IP and grant license only.",
    },
    {
        "clause_type": "Auto-Renewal",
        "pattern": r"automatic renewal|auto-renew",
        "risk_level": "medium",
        "recommendation": "Add 30-60 day notice requirement for termination.",
    },
    {
        "clause_type": "Net 60+ Payment",
        "pattern": r"net\s*(60|90|120)",
        "risk_level": "medium",
        "recommendation": "Negotiate payment terms to Net 30.",
    },
    {
        "clause_type": "Non-Compete Duration",
        "pattern": r"non-compete.*(18|24)\s*months",
        "risk_level": "high",
        "recommendation": "Limit non-compete to 12 months and narrow scope.",
    },
]


class ContractRiskService:
    """Analyze contracts for risky clauses."""

    def review_contract(self, request: ContractReviewRequest) -> ContractReview:
        findings = self._detect_findings(request.contract_text)
        risk_score = self._score_risk(findings)
        risk_level = self._risk_level(risk_score)

        review = ContractReview(
            contract_id=request.contract_id,
            risk_score=risk_score,
            risk_level=risk_level,
            findings=findings,
        )

        review_repo.create(request.contract_id, review.dict())
        logger.info("Contract review completed", extra={"contract_id": request.contract_id})

        return review

    def generate_redlines(self, review: ContractReview) -> RedlineRecommendation:
        redlines = [finding.recommendation for finding in review.findings]
        response = RedlineRecommendation(contract_id=review.contract_id, redlines=redlines)
        redline_repo.create(review.contract_id, response.dict())
        return response

    def build_review(self, record: Dict[str, Any]) -> ContractReview:
        """Rehydrate review from stored data."""
        return ContractReview(**record)

    def _detect_findings(self, contract_text: str) -> List[ClauseFinding]:
        findings = []
        for rule in RISK_PATTERNS:
            match = re.search(rule["pattern"], contract_text, re.IGNORECASE)
            if match:
                findings.append(
                    ClauseFinding(
                        clause_type=rule["clause_type"],
                        risk_level=rule["risk_level"],
                        excerpt=match.group(0),
                        recommendation=rule["recommendation"],
                    )
                )
        return findings

    def _score_risk(self, findings: List[ClauseFinding]) -> float:
        if not findings:
            return 0.0
        score = 0.0
        for finding in findings:
            if finding.risk_level == "high":
                score += 0.4
            elif finding.risk_level == "medium":
                score += 0.2
            else:
                score += 0.1
        return round(min(score, 1.0) * 100, 2)

    def _risk_level(self, risk_score: float) -> str:
        if risk_score >= 70:
            return "high"
        if risk_score >= 40:
            return "medium"
        return "low"
