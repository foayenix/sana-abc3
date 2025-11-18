"""
Data models for SANA Health Graph
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Set
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime

class EvidenceStrength(str, Enum):
    """Evidence quality ratings based on WHO/Cochrane standards"""
    STRONG = "strong"              # Multiple high-quality RCTs, meta-analyses
    MODERATE = "moderate"          # Some RCTs, systematic reviews
    WEAK = "weak"                  # Observational studies, case reports
    INSUFFICIENT = "insufficient"  # No quality studies, traditional use only
    CONFLICTING = "conflicting"    # Mixed results across studies

class InterventionCategory(str, Enum):
    """Types of CAM interventions"""
    HERBAL = "herbal"
    NUTRITION = "nutrition"
    MOVEMENT = "movement"
    MIND_BODY = "mind_body"
    ENERGY_WORK = "energy_work"
    MANUAL_THERAPY = "manual_therapy"
    LIFESTYLE = "lifestyle"

class Domain(str, Enum):
    """Wellness domains from SISM"""
    PHYSICAL = "physical"
    EMOTIONAL = "emotional"
    SOCIAL = "social"
    COGNITIVE = "cognitive"
    SPIRITUAL = "spiritual"

class ContraindicationType(str, Enum):
    """Types of contraindications"""
    ABSOLUTE = "absolute"  # Never use (e.g., pregnancy + certain herbs)
    RELATIVE = "relative"  # Use with caution
    INTERACTION = "interaction"  # Drug-herb interactions

class EvidenceSource(BaseModel):
    """Scientific evidence source"""
    id: UUID = Field(default_factory=uuid4)
    source_type: str  # "WHO", "NCCIH", "Cochrane", "PubMed"
    citation: str
    year: int
    url: Optional[str] = None
    summary: str

class DosageProtocol(BaseModel):
    """Dosage and duration guidelines"""
    id: UUID = Field(default_factory=uuid4)
    intervention_id: UUID
    min_dose: Optional[float] = None
    max_dose: Optional[float] = None
    dose_unit: Optional[str] = None  # "mg", "ml", "minutes", "sessions"
    frequency_per_day: Optional[int] = None
    frequency_per_week: Optional[int] = None
    min_duration_weeks: Optional[int] = None
    max_duration_weeks: Optional[int] = None
    instructions: str  # "Take with food", "Before bedtime", etc.

    def get_display_string(self) -> str:
        """Generate human-readable dosage string"""
        parts = []

        if self.min_dose and self.max_dose:
            parts.append(f"{self.min_dose}-{self.max_dose}{self.dose_unit}")
        elif self.min_dose:
            parts.append(f"{self.min_dose}+ {self.dose_unit}")

        if self.frequency_per_day:
            parts.append(f"{self.frequency_per_day}x/day")
        elif self.frequency_per_week:
            parts.append(f"{self.frequency_per_week}x/week")

        if self.min_duration_weeks and self.max_duration_weeks:
            parts.append(f"for {self.min_duration_weeks}-{self.max_duration_weeks} weeks")

        return ", ".join(parts)

class Contraindication(BaseModel):
    """Contraindication or interaction warning"""
    id: UUID = Field(default_factory=uuid4)
    intervention_id: UUID
    contraindication_type: ContraindicationType
    condition: str  # "pregnancy", "hypertension", "diabetes", etc.
    medication_class: Optional[str] = None  # For drug interactions
    severity: str  # "critical", "serious", "moderate", "minor"
    description: str
    source: Optional[str] = None

class ExpectedOutcome(BaseModel):
    """Expected timeline for results"""
    intervention_id: UUID
    condition: str
    typical_timeline_weeks: int
    outcome_description: str
    success_rate_percentage: Optional[float] = None

class Intervention(BaseModel):
    """CAM intervention with full metadata"""
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: InterventionCategory
    description: str

    # Target domains and conditions
    target_domains: List[Domain]
    target_conditions: List[str]  # "insomnia", "anxiety", "low_energy", etc.

    # Evidence
    evidence_strength: EvidenceStrength
    evidence_sources: List[EvidenceSource] = []

    # Safety
    contraindications: List[Contraindication] = []

    # Protocols
    dosage_protocols: List[DosageProtocol] = []

    # Outcomes
    expected_outcomes: List[ExpectedOutcome] = []

    # Practical info
    typical_duration_minutes: Optional[int] = None
    cost_estimate_min: Optional[float] = None
    cost_estimate_max: Optional[float] = None
    requires_practitioner: bool = False

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def is_safe_for_user(self, user_conditions: Set[str], user_medications: Set[str]) -> tuple[bool, List[str]]:
        """
        Check if intervention is safe for user

        Args:
            user_conditions: Set of user's conditions (e.g., {"pregnancy", "hypertension"})
            user_medications: Set of user's medication classes (e.g., {"antidepressants", "blood_thinners"})

        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        warnings = []

        for contra in self.contraindications:
            # Check conditions
            if contra.condition.lower() in {c.lower() for c in user_conditions}:
                if contra.contraindication_type == ContraindicationType.ABSOLUTE:
                    return False, [f"ABSOLUTE contraindication: {contra.description}"]
                else:
                    warnings.append(f"{contra.severity.upper()}: {contra.description}")

            # Check medication interactions
            if contra.medication_class and contra.medication_class.lower() in {m.lower() for m in user_medications}:
                if contra.severity == "critical":
                    return False, [f"CRITICAL drug interaction: {contra.description}"]
                else:
                    warnings.append(f"Drug interaction ({contra.severity}): {contra.description}")

        return len(warnings) == 0, warnings

class HealthGraphNode(BaseModel):
    """Generic node in the health graph"""
    id: UUID = Field(default_factory=uuid4)
    node_type: str  # "domain", "condition", "intervention", "evidence"
    name: str
    properties: Dict = {}

class HealthGraphEdge(BaseModel):
    """Relationship between nodes"""
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    target_id: UUID
    relationship_type: str  # "affects", "treats", "contraindicates", "supports"
    properties: Dict = {}
    weight: float = 1.0  # Relationship strength

class GraphQuery(BaseModel):
    """Query parameters for graph traversal"""
    start_node_id: Optional[UUID] = None
    node_type: Optional[str] = None
    relationship_type: Optional[str] = None
    filters: Dict = {}
    max_depth: int = 3

class GraphQueryResult(BaseModel):
    """Result from graph query"""
    nodes: List[HealthGraphNode]
    edges: List[HealthGraphEdge]
    paths: List[List[UUID]] = []  # Paths from start to end nodes
    metadata: Dict = {}


# Legacy models for backwards compatibility
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
