"""
Input validators for SANA Algorithms Suite.
"""

from typing import Dict, List
from uuid import UUID


def validate_domain_responses(
    responses: Dict[str, Dict[str, int]],
    required_domains: List[str] = None
) -> bool:
    """
    Validate domain response structure and values.

    Args:
        responses: Domain responses to validate
        required_domains: Required domain names

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    required = required_domains or [
        "physical", "emotional", "social", "cognitive", "spiritual"
    ]

    for domain in required:
        if domain not in responses:
            raise ValueError(f"Missing required domain: {domain}")

        for question_id, score in responses[domain].items():
            if not isinstance(score, (int, float)):
                raise ValueError(
                    f"Invalid score type for {domain}/{question_id}: {type(score)}"
                )
            if score < 0 or score > 100:
                raise ValueError(
                    f"Score out of range for {domain}/{question_id}: {score}"
                )

    return True


def validate_weights(weights: Dict[str, float]) -> bool:
    """
    Validate domain weights sum to 1.0.

    Args:
        weights: Domain weights

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    total = sum(weights.values())
    if abs(total - 1.0) > 0.001:
        raise ValueError(f"Weights must sum to 1.0, got {total}")
    return True


def validate_uuid(value: str) -> UUID:
    """
    Validate and convert string to UUID.

    Args:
        value: String to convert

    Returns:
        UUID object

    Raises:
        ValueError: If invalid UUID
    """
    try:
        return UUID(value)
    except Exception:
        raise ValueError(f"Invalid UUID: {value}")
