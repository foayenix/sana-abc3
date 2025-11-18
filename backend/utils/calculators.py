"""
Score calculators for SANA Algorithms Suite.
"""

from typing import Dict, List
import numpy as np


def calculate_weighted_average(
    values: Dict[str, float],
    weights: Dict[str, float]
) -> float:
    """
    Calculate weighted average of values.

    Args:
        values: Dictionary of values
        weights: Dictionary of weights (should sum to 1.0)

    Returns:
        Weighted average
    """
    total = 0.0
    for key, value in values.items():
        weight = weights.get(key, 0.0)
        total += value * weight
    return total


def calculate_percentile(value: float, distribution: List[float]) -> float:
    """
    Calculate percentile of a value within a distribution.

    Args:
        value: Value to find percentile for
        distribution: Reference distribution

    Returns:
        Percentile (0-100)
    """
    if not distribution:
        return 50.0

    arr = np.array(distribution)
    return float(np.sum(arr < value) / len(arr) * 100)


def calculate_trend(
    values: List[float],
    timestamps: List[int] = None
) -> str:
    """
    Calculate trend direction from a series of values.

    Args:
        values: Series of values
        timestamps: Optional timestamps

    Returns:
        Trend direction: 'improving', 'stable', 'declining'
    """
    if len(values) < 2:
        return "stable"

    # Simple linear regression
    x = np.arange(len(values)) if timestamps is None else np.array(timestamps)
    y = np.array(values)

    # Calculate slope
    n = len(values)
    slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / \
            (n * np.sum(x ** 2) - np.sum(x) ** 2)

    if slope > 0.5:
        return "improving"
    elif slope < -0.5:
        return "declining"
    else:
        return "stable"


def calculate_confidence_interval(
    values: List[float],
    confidence: float = 0.95
) -> tuple:
    """
    Calculate confidence interval for a set of values.

    Args:
        values: Sample values
        confidence: Confidence level

    Returns:
        Tuple of (lower, upper) bounds
    """
    if not values:
        return (0.0, 0.0)

    arr = np.array(values)
    mean = np.mean(arr)
    std = np.std(arr)
    n = len(arr)

    # Z-score for confidence level
    z = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%

    margin = z * (std / np.sqrt(n))
    return (mean - margin, mean + margin)
