"""
SISM - SANA Intake Scoring Model

Calculates baseline health scores across five domains:
- Physical
- Emotional
- Social
- Cognitive
- Spiritual

This model processes questionnaire responses to generate a comprehensive
health assessment that serves as the foundation for personalized recommendations.
"""

from typing import Dict, List
from uuid import UUID

from .models import SISMInput, SISMOutput, DomainScoreOutput


class SISMCalculator:
    """SANA Intake Scoring Model calculator."""

    # Default domain weights
    DEFAULT_WEIGHTS = {
        "physical": 0.25,
        "emotional": 0.25,
        "social": 0.15,
        "cognitive": 0.20,
        "spiritual": 0.15
    }

    def __init__(self, domain_weights: Dict[str, float] = None):
        """
        Initialize the SISM calculator.

        Args:
            domain_weights: Custom weights for each domain (must sum to 1.0)
        """
        self.domain_weights = domain_weights or self.DEFAULT_WEIGHTS
        self._validate_weights()

    def _validate_weights(self):
        """Validate that domain weights sum to 1.0."""
        total = sum(self.domain_weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Domain weights must sum to 1.0, got {total}")

    def calculate_domain_score(self, responses: Dict[str, int]) -> float:
        """
        Calculate the score for a single domain.

        Args:
            responses: Dictionary mapping question IDs to scores (0-100)

        Returns:
            Normalized domain score (0-100)
        """
        if not responses:
            return 0.0
        return sum(responses.values()) / len(responses)

    def calculate(self, input_data: SISMInput) -> SISMOutput:
        """
        Calculate the complete SISM health score.

        Args:
            input_data: SISM input containing all domain responses

        Returns:
            Complete SISM output with domain and overall scores
        """
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

        # Calculate weighted overall score
        overall_score = sum(
            score * self.domain_weights.get(domain, 0.0)
            for domain, score in domain_scores.items()
        )

        return SISMOutput(
            user_id=input_data.user_id,
            overall_score=overall_score,
            domain_scores=domain_outputs,
            metadata={"weights_used": self.domain_weights}
        )


# Convenience function for direct calculation
def calculate_sism_score(
    user_id: UUID,
    domain_responses: Dict[str, Dict[str, int]],
    weights: Dict[str, float] = None
) -> SISMOutput:
    """
    Calculate SISM score for a user.

    Args:
        user_id: User identifier
        domain_responses: Responses organized by domain
        weights: Optional custom domain weights

    Returns:
        Complete SISM output
    """
    calculator = SISMCalculator(weights)
    input_data = SISMInput(user_id=user_id, domain_responses=domain_responses)
    return calculator.calculate(input_data)
