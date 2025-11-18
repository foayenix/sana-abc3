"""
Data normalizers for SANA Algorithms Suite.
"""

from typing import Dict, List
import numpy as np


def normalize_score(value: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Normalize a score to 0-100 range.

    Args:
        value: Value to normalize
        min_val: Original minimum
        max_val: Original maximum

    Returns:
        Normalized score (0-100)
    """
    if max_val == min_val:
        return 50.0
    return ((value - min_val) / (max_val - min_val)) * 100


def normalize_scores_zscore(scores: List[float]) -> List[float]:
    """
    Normalize scores using z-score normalization.

    Args:
        scores: List of scores

    Returns:
        Z-score normalized values
    """
    if not scores:
        return []

    arr = np.array(scores)
    mean = np.mean(arr)
    std = np.std(arr)

    if std == 0:
        return [0.0] * len(scores)

    return ((arr - mean) / std).tolist()


def normalize_domain_scores(
    domain_scores: Dict[str, float],
    population_stats: Dict[str, Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Normalize domain scores relative to population.

    Args:
        domain_scores: Raw domain scores
        population_stats: Population mean/std per domain

    Returns:
        Normalized domain scores
    """
    if not population_stats:
        return domain_scores

    normalized = {}
    for domain, score in domain_scores.items():
        if domain in population_stats:
            mean = population_stats[domain].get("mean", 50)
            std = population_stats[domain].get("std", 15)
            if std > 0:
                z_score = (score - mean) / std
                # Convert to 0-100 scale (assuming z-scores -3 to 3)
                normalized[domain] = normalize_score(z_score, -3, 3)
            else:
                normalized[domain] = score
        else:
            normalized[domain] = score

    return normalized
