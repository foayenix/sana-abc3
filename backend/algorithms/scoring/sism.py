"""
SISM - SANA Intake Scoring Model
Calculates baseline health score from multi-domain questionnaire data
"""
from typing import Dict, List
from uuid import UUID
import logging
from datetime import datetime

from .models import (
    QuestionnaireInput,
    QuestionResponse,
    SISMOutput,
    DomainScore,
    DomainWeights,
    SISMInput,
    DomainScoreOutput
)

logger = logging.getLogger(__name__)


class SISMAlgorithm:
    """
    SANA Intake Scoring Model (SISM)

    Transforms multi-domain wellness questionnaire responses into:
    - Overall health score (0-100)
    - Domain-specific scores
    - Identified improvement areas
    """

    def __init__(self, weights: DomainWeights = None):
        """
        Initialize SISM with optional custom domain weights

        Args:
            weights: Custom domain weights, defaults to standard weights
        """
        self.weights = weights or DomainWeights()
        self.weights.validate_sum()
        logger.info(f"SISM initialized with weights: {self.weights.model_dump()}")

    def normalize_score(self, raw_score: int, min_val: int = 0, max_val: int = 10) -> float:
        """
        Normalize a raw score to 0-100 scale

        Args:
            raw_score: Original score from questionnaire
            min_val: Minimum possible value
            max_val: Maximum possible value

        Returns:
            Normalized score (0-100)
        """
        if max_val == min_val:
            return 50.0  # Avoid division by zero

        normalized = ((raw_score - min_val) / (max_val - min_val)) * 100
        return round(normalized, 2)

    def calculate_domain_score(
        self,
        domain: str,
        responses: List[QuestionResponse]
    ) -> DomainScore:
        """
        Calculate score for a single domain

        Args:
            domain: Domain name (physical, emotional, etc.)
            responses: All question responses for this domain

        Returns:
            DomainScore object with calculations
        """
        if not responses:
            raise ValueError(f"No responses provided for domain: {domain}")

        # Normalize all scores
        normalized_scores = []
        question_ids = []

        for response in responses:
            normalized = self.normalize_score(response.raw_score)
            normalized_scores.append(normalized)
            question_ids.append(response.question_id)

        # Calculate average
        raw_average = sum(r.raw_score for r in responses) / len(responses)
        normalized_average = sum(normalized_scores) / len(normalized_scores)

        # Get weight for this domain
        weight = getattr(self.weights, domain)

        # Calculate contribution to overall score
        weighted_contribution = normalized_average * weight

        return DomainScore(
            domain=domain,
            raw_average=round(raw_average, 2),
            normalized_score=round(normalized_average, 2),
            weight=weight,
            weighted_contribution=round(weighted_contribution, 2),
            question_count=len(responses),
            questions_scored=question_ids
        )

    def identify_weak_domains(
        self,
        domain_scores: Dict[str, DomainScore],
        threshold: float = 60.0
    ) -> List[str]:
        """
        Identify domains that need improvement

        Args:
            domain_scores: Calculated domain scores
            threshold: Score below which a domain is considered weak

        Returns:
            List of weak domain names
        """
        weak = [
            domain for domain, score in domain_scores.items()
            if score.normalized_score < threshold
        ]
        return sorted(weak)  # Sort for consistency

    def calculate(self, questionnaire: QuestionnaireInput) -> SISMOutput:
        """
        Main calculation method - processes questionnaire and returns SISM output

        Args:
            questionnaire: Complete questionnaire input

        Returns:
            SISMOutput with all scores and metadata

        Raises:
            ValueError: If questionnaire is invalid or incomplete
        """
        logger.info(f"Calculating SISM for user: {questionnaire.user_id}")

        # Group responses by domain
        domain_responses: Dict[str, List[QuestionResponse]] = {}
        for response in questionnaire.responses:
            if response.domain not in domain_responses:
                domain_responses[response.domain] = []
            domain_responses[response.domain].append(response)

        # Calculate scores for each domain
        domain_scores: Dict[str, DomainScore] = {}
        for domain, responses in domain_responses.items():
            domain_scores[domain] = self.calculate_domain_score(domain, responses)

        # Calculate overall score (weighted sum of domain scores)
        overall_score = sum(
            score.weighted_contribution
            for score in domain_scores.values()
        )

        # Identify weak domains
        weak_domains = self.identify_weak_domains(domain_scores)

        # Build metadata
        calculation_metadata = {
            "weights_used": self.weights.model_dump(),
            "total_questions": len(questionnaire.responses),
            "domains_analyzed": list(domain_scores.keys()),
            "weak_domain_threshold": 60.0,
            "calculation_timestamp": datetime.utcnow().isoformat()
        }

        result = SISMOutput(
            user_id=questionnaire.user_id,
            overall_score=round(overall_score, 2),
            domain_scores=domain_scores,
            weak_domains=weak_domains,
            calculation_metadata=calculation_metadata,
            questionnaire_version=questionnaire.questionnaire_version,
            calculated_at=datetime.utcnow()
        )

        logger.info(
            f"SISM calculated for user {questionnaire.user_id}: "
            f"Overall={result.overall_score}, Weak domains={weak_domains}"
        )

        return result

    def recalculate_with_weights(
        self,
        questionnaire: QuestionnaireInput,
        new_weights: DomainWeights
    ) -> SISMOutput:
        """
        Recalculate score with different weights (for testing/optimization)

        Args:
            questionnaire: Original questionnaire input
            new_weights: New domain weights to use

        Returns:
            New SISMOutput with updated weights
        """
        old_weights = self.weights
        self.weights = new_weights
        self.weights.validate_sum()

        result = self.calculate(questionnaire)

        self.weights = old_weights  # Restore original weights
        return result


# Legacy calculator for backwards compatibility
class SISMCalculator:
    """SANA Intake Scoring Model calculator (legacy)."""

    DEFAULT_WEIGHTS = {
        "physical": 0.25,
        "emotional": 0.25,
        "social": 0.15,
        "cognitive": 0.20,
        "spiritual": 0.15
    }

    def __init__(self, domain_weights: Dict[str, float] = None):
        self.domain_weights = domain_weights or self.DEFAULT_WEIGHTS
        self._validate_weights()

    def _validate_weights(self):
        total = sum(self.domain_weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Domain weights must sum to 1.0, got {total}")

    def calculate_domain_score(self, responses: Dict[str, int]) -> float:
        if not responses:
            return 0.0
        return sum(responses.values()) / len(responses)

    def calculate(self, input_data: SISMInput):
        domain_scores = {}
        domain_outputs = []

        for domain, responses in input_data.domain_responses.items():
            score = self.calculate_domain_score(responses)
            domain_scores[domain] = score
            domain_outputs.append(DomainScoreOutput(
                domain=domain,
                score=score,
                weight=self.domain_weights.get(domain, 0.0)
            ))

        overall_score = sum(
            score * self.domain_weights.get(domain, 0.0)
            for domain, score in domain_scores.items()
        )

        from .models import SISMOutput as LegacySISMOutput
        # Return simple dict-based output for legacy compatibility
        return {
            "user_id": str(input_data.user_id),
            "overall_score": overall_score,
            "domain_scores": domain_outputs,
            "metadata": {"weights_used": self.domain_weights}
        }


# Convenience function for direct calculation
def calculate_sism_score(
    user_id: UUID,
    domain_responses: Dict[str, Dict[str, int]],
    weights: Dict[str, float] = None
) -> SISMOutput:
    """
    Calculate SISM score for a user (legacy interface).

    Args:
        user_id: User identifier
        domain_responses: Responses organized by domain
        weights: Optional custom domain weights

    Returns:
        Complete SISM output
    """
    # Convert legacy format to new format
    responses = []
    for domain, questions in domain_responses.items():
        for question_id, score in questions.items():
            # Convert 0-100 scale to 0-10 scale for compatibility
            raw_score = min(10, max(0, score // 10))
            responses.append(QuestionResponse(
                question_id=question_id,
                domain=domain,
                raw_score=raw_score
            ))

    questionnaire = QuestionnaireInput(
        user_id=user_id,
        responses=responses
    )

    # Create weights if provided
    domain_weights = None
    if weights:
        domain_weights = DomainWeights(**weights)

    calculator = SISMAlgorithm(domain_weights)
    return calculator.calculate(questionnaire)
