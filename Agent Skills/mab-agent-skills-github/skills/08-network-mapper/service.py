"""
Skill 08: Strategic Network Relationship Mapper - Service Layer
"""

from collections import deque
from typing import Dict, List

import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository

from models import (
    NetworkMapRequest,
    IntroPathRequest,
    IntroPathResponse,
    RelationshipScoreRequest,
    RelationshipScore,
)

logger = get_logger(__name__, skill_name="network-mapper")

map_repo = FirestoreRepository("network_maps")


class NetworkMapperService:
    """Service for mapping and querying relationship graphs."""

    def store_map(self, request: NetworkMapRequest) -> Dict[str, str]:
        map_repo.create(request.map_id, request.dict())
        logger.info("Network map stored", extra={"map_id": request.map_id})
        return {"map_id": request.map_id, "status": "stored"}

    def find_intro_path(self, request: IntroPathRequest) -> IntroPathResponse:
        network_map = map_repo.get(request.map_id)
        if not network_map:
            raise ValueError("Network map not found")

        adjacency = self._build_adjacency(network_map.get("edges", []))
        path = self._bfs(adjacency, request.start_id, request.target_id)

        confidence = round(0.9 if path else 0.2, 2)
        return IntroPathResponse(map_id=request.map_id, path=path or [], confidence=confidence)

    def score_relationship(self, request: RelationshipScoreRequest) -> RelationshipScore:
        score = (
            request.interaction_frequency * 0.35
            + request.recency * 0.30
            + request.influence_level * 0.20
            + request.accessibility * 0.15
        )
        return RelationshipScore(score=round(score, 2))

    def _build_adjacency(self, edges: List[Dict]) -> Dict[str, List[str]]:
        adjacency: Dict[str, List[str]] = {}
        for edge in edges:
            adjacency.setdefault(edge["source_id"], []).append(edge["target_id"])
            adjacency.setdefault(edge["target_id"], []).append(edge["source_id"])
        return adjacency

    def _bfs(self, adjacency: Dict[str, List[str]], start: str, target: str) -> List[str]:
        if start == target:
            return [start]
        visited = set([start])
        queue = deque([[start]])
        while queue:
            path = queue.popleft()
            node = path[-1]
            for neighbor in adjacency.get(node, []):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                new_path = path + [neighbor]
                if neighbor == target:
                    return new_path
                queue.append(new_path)
        return []
