"""
Skill 04: Omnichannel Content Repurposing Engine - Service Layer
"""

import os
import uuid
from typing import List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository
from shared.utils.llm import LLMClient

from models import ContentSource, RepurposeRequest, RepurposedAsset, RepurposeBatch

logger = get_logger(__name__, skill_name="content-repurposing")
llm = LLMClient("content-repurposing")

batch_repo = FirestoreRepository("content_batches")


class ContentRepurposingService:
    """Service to transform content across channels"""

    def repurpose(self, request: RepurposeRequest) -> RepurposeBatch:
        batch_id = f"batch_{uuid.uuid4().hex[:10]}"

        if os.getenv("ANTHROPIC_API_KEY"):
            assets = self._generate_with_llm(request)
        else:
            assets = self._generate_fallback(request)

        batch = RepurposeBatch(
            batch_id=batch_id,
            source_id=request.source.source_id,
            assets=assets,
            status="complete",
        )

        batch_repo.create(batch_id, batch.dict())
        logger.info("Repurpose batch created", extra={"batch_id": batch_id})

        return batch

    def _generate_with_llm(self, request: RepurposeRequest) -> List[RepurposedAsset]:
        schema = {
            "assets": [
                {
                    "platform": "string",
                    "format": "string",
                    "headline": "string",
                    "body": "string",
                    "hashtags": ["string"],
                    "call_to_action": "string",
                }
            ]
        }
        prompt = (
            "Repurpose the following content into platform-specific assets. "
            f"Targets: {', '.join(request.target_platforms)}. "
            f"Tone: {request.tone}. Include CTA: {request.include_cta}.\n\n"
            f"Title: {request.source.title}\n\n"
            f"Body: {request.source.body}"
        )
        response = llm.generate_structured(
            prompt=prompt,
            output_schema=schema,
            system_prompt=(
                "You are a content strategist for MAB AI Strategies. "
                "Return concise, high-engagement assets optimized for each platform."
            ),
        )

        assets = []
        for item in response.get("assets", []):
            assets.append(
                RepurposedAsset(
                    platform=item.get("platform", "unknown"),
                    format=item.get("format", "post"),
                    headline=item.get("headline", ""),
                    body=item.get("body", ""),
                    hashtags=item.get("hashtags", []),
                    call_to_action=item.get("call_to_action"),
                )
            )
        return assets

    def _generate_fallback(self, request: RepurposeRequest) -> List[RepurposedAsset]:
        assets = []
        for platform in request.target_platforms:
            assets.append(
                RepurposedAsset(
                    platform=platform,
                    format="post",
                    headline=f"{request.source.title} ({platform})",
                    body=request.source.body[:280],
                    hashtags=["#MABAI", "#AI"],
                    call_to_action="Book a strategy call" if request.include_cta else None,
                )
            )
        return assets
