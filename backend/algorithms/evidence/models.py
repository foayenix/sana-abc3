"""
Pydantic models for evidence algorithms.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID


class InterventionScore(BaseModel):
    """Scored intervention recommendation."""
    intervention_id: UUID
    name: str
    score: float
    evidence_rating: str
    relevance_factors: List[str]


class EvidenceInput(BaseModel):
    """Input model for evidence engine."""
    user_id: UUID
    health_goals: List[str]
    domain_scores: Dict[str, float]
    contraindications: List[str] = []


class EvidenceOutput(BaseModel):
    """Output model for evidence engine."""
    user_id: UUID
    recommendations: List[InterventionScore]
    evidence_summary: Dict
    confidence_level: float


class GraphNode(BaseModel):
    """Node in the health graph."""
    id: str
    type: str  # intervention, condition, symptom, etc.
    name: str
    properties: Dict = {}


class GraphEdge(BaseModel):
    """Edge in the health graph."""
    source_id: str
    target_id: str
    relationship: str  # treats, causes, prevents, etc.
    properties: Dict = {}


class GraphQuery(BaseModel):
    """Query for the health graph."""
    node_type: Optional[str] = None
    relationship: Optional[str] = None
    properties: Dict = {}


class GraphResult(BaseModel):
    """Result from health graph query."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict = {}
