"""
SANA Health Graph - Knowledge base for CAM interventions
A structured ontology + knowledge base linking domains, conditions,
interventions, evidence, and contraindications
"""
from typing import List, Dict, Set, Optional, Tuple
from uuid import UUID
import logging
from collections import defaultdict

from .models import (
    Intervention,
    Domain,
    EvidenceStrength,
    Contraindication,
    ContraindicationType,
    HealthGraphNode,
    HealthGraphEdge,
    GraphQuery,
    GraphQueryResult
)

logger = logging.getLogger(__name__)

class HealthGraph:
    """
    SANA Health Graph - Knowledge base for evidence-based CAM interventions

    This graph structure enables:
    - Finding interventions for specific conditions/domains
    - Checking safety and contraindications
    - Retrieving evidence-based protocols
    - Reasoning about optimal treatment paths
    """

    def __init__(self):
        """Initialize empty health graph"""
        # Storage
        self.interventions: Dict[UUID, Intervention] = {}
        self.nodes: Dict[UUID, HealthGraphNode] = {}
        self.edges: List[HealthGraphEdge] = []

        # Indexes for fast lookup
        self._domain_to_interventions: Dict[Domain, Set[UUID]] = defaultdict(set)
        self._condition_to_interventions: Dict[str, Set[UUID]] = defaultdict(set)
        self._category_to_interventions: Dict[str, Set[UUID]] = defaultdict(set)
        self._evidence_strength_index: Dict[EvidenceStrength, Set[UUID]] = defaultdict(set)

        logger.info("Health graph initialized")

    def add_intervention(self, intervention: Intervention) -> UUID:
        """
        Add an intervention to the graph

        Args:
            intervention: Intervention object with full metadata

        Returns:
            UUID of added intervention
        """
        self.interventions[intervention.id] = intervention

        # Update indexes
        for domain in intervention.target_domains:
            self._domain_to_interventions[domain].add(intervention.id)

        for condition in intervention.target_conditions:
            self._condition_to_interventions[condition.lower()].add(intervention.id)

        self._category_to_interventions[intervention.category].add(intervention.id)
        self._evidence_strength_index[intervention.evidence_strength].add(intervention.id)

        logger.debug(f"Added intervention: {intervention.name} ({intervention.id})")
        return intervention.id

    def get_intervention(self, intervention_id: UUID) -> Optional[Intervention]:
        """Get intervention by ID"""
        return self.interventions.get(intervention_id)

    def find_interventions_for_domain(
        self,
        domain: Domain,
        min_evidence_strength: EvidenceStrength = EvidenceStrength.WEAK,
        user_conditions: Set[str] = None,
        user_medications: Set[str] = None
    ) -> List[Intervention]:
        """
        Find all interventions targeting a specific domain

        Args:
            domain: Target domain
            min_evidence_strength: Minimum acceptable evidence quality
            user_conditions: User's conditions for safety checking
            user_medications: User's medications for interaction checking

        Returns:
            List of safe, evidence-based interventions
        """
        user_conditions = user_conditions or set()
        user_medications = user_medications or set()

        # Get interventions for domain
        intervention_ids = self._domain_to_interventions.get(domain, set())

        # Filter by evidence strength
        evidence_strengths = self._get_evidence_strengths_at_least(min_evidence_strength)
        valid_evidence_ids = set()
        for strength in evidence_strengths:
            valid_evidence_ids.update(self._evidence_strength_index.get(strength, set()))

        filtered_ids = intervention_ids.intersection(valid_evidence_ids)

        # Get intervention objects and check safety
        safe_interventions = []
        for intervention_id in filtered_ids:
            intervention = self.interventions[intervention_id]
            is_safe, warnings = intervention.is_safe_for_user(user_conditions, user_medications)

            if is_safe:
                safe_interventions.append(intervention)
            elif warnings:
                logger.warning(
                    f"Intervention {intervention.name} has warnings for user: {warnings}"
                )

        # Sort by evidence strength (strong first)
        return sorted(
            safe_interventions,
            key=lambda x: self._evidence_strength_score(x.evidence_strength),
            reverse=True
        )

    def find_interventions_for_condition(
        self,
        condition: str,
        min_evidence_strength: EvidenceStrength = EvidenceStrength.WEAK,
        user_conditions: Set[str] = None,
        user_medications: Set[str] = None
    ) -> List[Intervention]:
        """
        Find all interventions for a specific condition

        Args:
            condition: Target condition (e.g., "insomnia", "anxiety")
            min_evidence_strength: Minimum acceptable evidence quality
            user_conditions: User's conditions for safety checking
            user_medications: User's medications for interaction checking

        Returns:
            List of safe, evidence-based interventions
        """
        user_conditions = user_conditions or set()
        user_medications = user_medications or set()

        # Get interventions for condition
        intervention_ids = self._condition_to_interventions.get(condition.lower(), set())

        # Filter by evidence strength
        evidence_strengths = self._get_evidence_strengths_at_least(min_evidence_strength)
        valid_evidence_ids = set()
        for strength in evidence_strengths:
            valid_evidence_ids.update(self._evidence_strength_index.get(strength, set()))

        filtered_ids = intervention_ids.intersection(valid_evidence_ids)

        # Get intervention objects and check safety
        safe_interventions = []
        for intervention_id in filtered_ids:
            intervention = self.interventions[intervention_id]
            is_safe, warnings = intervention.is_safe_for_user(user_conditions, user_medications)

            if is_safe:
                safe_interventions.append(intervention)

        return sorted(
            safe_interventions,
            key=lambda x: self._evidence_strength_score(x.evidence_strength),
            reverse=True
        )

    def find_interventions_for_weak_domains(
        self,
        weak_domains: List[str],
        min_evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE,
        user_conditions: Set[str] = None,
        user_medications: Set[str] = None,
        max_results: int = 5
    ) -> Dict[str, List[Intervention]]:
        """
        Find interventions for multiple weak domains (from SISM output)

        Args:
            weak_domains: List of weak domain names from SISM
            min_evidence_strength: Minimum evidence quality
            user_conditions: User's conditions for safety
            user_medications: User's medications for interactions
            max_results: Maximum interventions per domain

        Returns:
            Dict mapping domain name to list of interventions
        """
        results = {}

        for domain_name in weak_domains:
            try:
                domain = Domain(domain_name.lower())
                interventions = self.find_interventions_for_domain(
                    domain,
                    min_evidence_strength,
                    user_conditions,
                    user_medications
                )
                results[domain_name] = interventions[:max_results]
            except ValueError:
                logger.warning(f"Invalid domain name: {domain_name}")
                results[domain_name] = []

        return results

    def get_contraindications_for_user(
        self,
        intervention_id: UUID,
        user_conditions: Set[str],
        user_medications: Set[str]
    ) -> Tuple[bool, List[str]]:
        """
        Check if intervention is safe for user

        Args:
            intervention_id: Intervention to check
            user_conditions: User's conditions
            user_medications: User's medications

        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        intervention = self.get_intervention(intervention_id)
        if not intervention:
            return False, ["Intervention not found"]

        return intervention.is_safe_for_user(user_conditions, user_medications)

    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        return {
            "total_interventions": len(self.interventions),
            "interventions_by_domain": {
                domain.value: len(interventions)
                for domain, interventions in self._domain_to_interventions.items()
            },
            "interventions_by_evidence": {
                strength.value: len(interventions)
                for strength, interventions in self._evidence_strength_index.items()
            },
            "total_conditions_covered": len(self._condition_to_interventions),
            "interventions_by_category": {
                str(category): len(interventions)
                for category, interventions in self._category_to_interventions.items()
            }
        }

    def _get_evidence_strengths_at_least(
        self,
        min_strength: EvidenceStrength
    ) -> List[EvidenceStrength]:
        """Get all evidence strengths at or above minimum"""
        strength_order = [
            EvidenceStrength.STRONG,
            EvidenceStrength.MODERATE,
            EvidenceStrength.WEAK,
            EvidenceStrength.INSUFFICIENT,
            EvidenceStrength.CONFLICTING
        ]

        try:
            min_index = strength_order.index(min_strength)
            return strength_order[:min_index + 1]
        except ValueError:
            return [EvidenceStrength.STRONG]

    def _evidence_strength_score(self, strength: EvidenceStrength) -> int:
        """Convert evidence strength to numeric score for sorting"""
        scores = {
            EvidenceStrength.STRONG: 4,
            EvidenceStrength.MODERATE: 3,
            EvidenceStrength.WEAK: 2,
            EvidenceStrength.INSUFFICIENT: 1,
            EvidenceStrength.CONFLICTING: 0
        }
        return scores.get(strength, 0)


# Legacy class for backwards compatibility
class SANAHealthGraph(HealthGraph):
    """Legacy class name - use HealthGraph instead"""
    pass


# Singleton instance
health_graph = HealthGraph()
