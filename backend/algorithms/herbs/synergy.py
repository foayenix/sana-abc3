"""
Herb Synergy Detection Algorithm

Identifies herb combinations with synergistic effects using
association rule mining and outcome analysis.
"""
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np

from .models import (
    HerbUsage,
    HerbOutcome,
    HerbCombination,
)


class SynergyDetector:
    """Detect herb combinations with synergistic effects"""

    def __init__(self):
        self.MIN_SUPPORT = 0.05  # Minimum 5% of sessions
        self.MIN_LIFT = 1.2  # Minimum lift for synergy
        self.MIN_SAMPLE_SIZE = 30  # Minimum cases for reliable analysis
        self.SYNERGY_THRESHOLD = 70  # Minimum score to consider high synergy

    def find_synergistic_combinations(
        self,
        usage_data: List[HerbUsage],
        outcome_data: List[HerbOutcome],
        herb_names: Dict[UUID, str],
        condition_id: Optional[UUID] = None,
        min_synergy_score: int = 70,
        limit: int = 20,
    ) -> List[HerbCombination]:
        """
        Find herb combinations with synergistic effects

        Args:
            usage_data: All herb usage records
            outcome_data: All outcome measurements
            herb_names: Mapping of herb_id to name
            condition_id: Optional filter by condition
            min_synergy_score: Minimum synergy score to include
            limit: Maximum results to return

        Returns:
            List of HerbCombination objects sorted by synergy score
        """
        # Filter by condition if specified
        if condition_id:
            usage_data = [u for u in usage_data if u.primary_condition_id == condition_id]

        if len(usage_data) < self.MIN_SAMPLE_SIZE:
            return []

        # Group usage by session
        session_herbs = self._group_by_session(usage_data)

        # Find frequent itemsets (herb combinations)
        frequent_combos = self._find_frequent_combinations(session_herbs)

        # Calculate synergy for each combination
        synergies = []
        for herb_ids in frequent_combos:
            combo_outcomes = self._get_combination_outcomes(
                herb_ids, usage_data, outcome_data
            )

            if len(combo_outcomes) < self.MIN_SAMPLE_SIZE:
                continue

            # Calculate synergy metrics
            synergy_data = self._calculate_synergy_score(
                herb_ids,
                combo_outcomes,
                usage_data,
                outcome_data,
                herb_names,
            )

            if synergy_data and synergy_data.synergy_score >= min_synergy_score:
                synergies.append(synergy_data)

        # Sort by synergy score and limit
        synergies.sort(key=lambda x: x.synergy_score, reverse=True)
        return synergies[:limit]

    def _group_by_session(
        self,
        usage_data: List[HerbUsage],
    ) -> Dict[UUID, List[UUID]]:
        """Group herb usage by session"""
        session_herbs = defaultdict(list)
        for usage in usage_data:
            session_herbs[usage.session_id].append(usage.herb_id)
        return dict(session_herbs)

    def _find_frequent_combinations(
        self,
        session_herbs: Dict[UUID, List[UUID]],
        max_combo_size: int = 4,
    ) -> List[Tuple[UUID, ...]]:
        """
        Find frequent herb combinations using Apriori-like algorithm

        Args:
            session_herbs: Mapping of session_id to herb_ids
            max_combo_size: Maximum herbs in a combination

        Returns:
            List of herb_id tuples representing frequent combinations
        """
        total_sessions = len(session_herbs)
        min_support_count = int(total_sessions * self.MIN_SUPPORT)

        # Count individual herbs
        herb_counts = defaultdict(int)
        for herbs in session_herbs.values():
            for herb in set(herbs):  # Dedupe within session
                herb_counts[herb] += 1

        # Get frequent single herbs
        frequent_herbs = [
            herb for herb, count in herb_counts.items()
            if count >= min_support_count
        ]

        frequent_combos = []

        # Find frequent pairs, triples, etc.
        for combo_size in range(2, max_combo_size + 1):
            for combo in combinations(frequent_herbs, combo_size):
                combo_set = set(combo)
                count = sum(
                    1 for herbs in session_herbs.values()
                    if combo_set.issubset(set(herbs))
                )

                if count >= min_support_count:
                    frequent_combos.append(combo)

        return frequent_combos

    def _get_combination_outcomes(
        self,
        herb_ids: Tuple[UUID, ...],
        usage_data: List[HerbUsage],
        outcome_data: List[HerbOutcome],
    ) -> List[HerbOutcome]:
        """Get outcomes for sessions using all herbs in combination"""
        # Find sessions with all herbs
        session_herbs = self._group_by_session(usage_data)
        herb_set = set(herb_ids)

        matching_sessions = [
            session_id for session_id, herbs in session_herbs.items()
            if herb_set.issubset(set(herbs))
        ]

        # Get usage_ids for these sessions
        usage_ids = set()
        for usage in usage_data:
            if usage.session_id in matching_sessions:
                usage_ids.add(usage.usage_id)

        # Get outcomes for these usages
        return [o for o in outcome_data if o.usage_id in usage_ids]

    def _get_individual_improvement(
        self,
        herb_id: UUID,
        usage_data: List[HerbUsage],
        outcome_data: List[HerbOutcome],
    ) -> float:
        """Calculate mean improvement for a single herb"""
        # Get usage_ids for this herb
        usage_ids = {u.usage_id for u in usage_data if u.herb_id == herb_id}

        # Get outcomes
        improvements = [
            o.improvement_percentage for o in outcome_data
            if o.usage_id in usage_ids and o.improvement_percentage is not None
        ]

        return np.mean(improvements) if improvements else 0.0

    def _calculate_synergy_score(
        self,
        herb_ids: Tuple[UUID, ...],
        combo_outcomes: List[HerbOutcome],
        usage_data: List[HerbUsage],
        outcome_data: List[HerbOutcome],
        herb_names: Dict[UUID, str],
    ) -> Optional[HerbCombination]:
        """
        Calculate synergy score for a herb combination

        Synergy = (combo improvement - expected individual improvement) * boost factor
        """
        if not combo_outcomes:
            return None

        # Combination improvement
        combo_improvements = [
            o.improvement_percentage for o in combo_outcomes
            if o.improvement_percentage is not None
        ]

        if not combo_improvements:
            return None

        combo_mean = np.mean(combo_improvements)

        # Individual herb improvements
        individual_improvements = [
            self._get_individual_improvement(herb_id, usage_data, outcome_data)
            for herb_id in herb_ids
        ]

        # Expected improvement (average of individuals)
        expected_improvement = np.mean(individual_improvements)

        # Synergy boost
        synergy_boost = combo_mean - expected_improvement

        # Calculate lift (association rule metric)
        # Lift > 1 indicates positive association
        lift = combo_mean / expected_improvement if expected_improvement > 0 else 1.0

        # Synergy score (0-100)
        # Base 50, plus boost scaled
        synergy_score = min(100, max(0, int(50 + synergy_boost)))

        # Calculate optimal dosages (simplified - use mean dosages from successful cases)
        optimal_dosages = self._calculate_optimal_dosages(
            herb_ids, usage_data, combo_outcomes, herb_names
        )

        # Get condition info
        condition_ids = [u.primary_condition_id for u in usage_data if u.primary_condition_id]
        primary_condition = max(set(condition_ids), key=condition_ids.count) if condition_ids else None

        return HerbCombination(
            herb_ids=list(herb_ids),
            herb_names=[herb_names.get(h, str(h)) for h in herb_ids],
            condition_id=primary_condition,
            synergy_score=synergy_score,
            mean_improvement=float(combo_mean),
            expected_improvement=float(expected_improvement),
            synergy_boost=float(synergy_boost),
            optimal_dosages=optimal_dosages,
            sample_size=len(combo_outcomes),
            lift=float(lift),
        )

    def _calculate_optimal_dosages(
        self,
        herb_ids: Tuple[UUID, ...],
        usage_data: List[HerbUsage],
        combo_outcomes: List[HerbOutcome],
        herb_names: Dict[UUID, str],
    ) -> Dict[str, float]:
        """
        Calculate optimal dosages based on successful outcomes

        Uses mean dosages from top 25% of outcomes
        """
        # Get usage_ids with good outcomes
        good_outcome_ids = set()
        improvements = [o.improvement_percentage for o in combo_outcomes if o.improvement_percentage]
        if improvements:
            threshold = np.percentile(improvements, 75)
            good_outcome_ids = {
                o.usage_id for o in combo_outcomes
                if o.improvement_percentage and o.improvement_percentage >= threshold
            }

        # Calculate mean dosages for each herb in successful cases
        optimal = {}
        for herb_id in herb_ids:
            dosages = [
                u.dosage_amount for u in usage_data
                if u.herb_id == herb_id
                and u.usage_id in good_outcome_ids
                and u.dosage_amount is not None
            ]

            herb_name = herb_names.get(herb_id, str(herb_id))
            optimal[herb_name] = float(np.mean(dosages)) if dosages else 0.0

        return optimal

    def calculate_combination_protocol(
        self,
        herb_ids: List[UUID],
        usage_data: List[HerbUsage],
        outcome_data: List[HerbOutcome],
        herb_names: Dict[UUID, str],
    ) -> Dict:
        """
        Generate detailed protocol for a herb combination

        Returns:
            Protocol with timing, dosages, duration, expected outcomes
        """
        combo_outcomes = self._get_combination_outcomes(
            tuple(herb_ids), usage_data, outcome_data
        )

        if not combo_outcomes:
            return {}

        # Get usage patterns
        combo_usages = [
            u for u in usage_data
            if u.herb_id in herb_ids
        ]

        # Analyze timing
        frequencies = [u.frequency for u in combo_usages if u.frequency]
        primary_frequency = max(set(frequencies), key=frequencies.count) if frequencies else "daily"

        # Analyze duration
        durations = [u.duration_days for u in combo_usages if u.duration_days]
        median_duration = int(np.median(durations)) if durations else 28

        # Analyze days to improvement
        days_to_improve = [
            o.days_since_start for o in combo_outcomes
            if o.improvement_percentage and o.improvement_percentage > 20
        ]
        median_days = int(np.median(days_to_improve)) if days_to_improve else 14

        # Calculate optimal dosages
        optimal_dosages = self._calculate_optimal_dosages(
            tuple(herb_ids), usage_data, combo_outcomes, herb_names
        )

        # Expected improvement
        improvements = [o.improvement_percentage for o in combo_outcomes if o.improvement_percentage]
        expected_improvement = np.mean(improvements) if improvements else 0

        return {
            "herbs": [herb_names.get(h, str(h)) for h in herb_ids],
            "dosages": optimal_dosages,
            "frequency": primary_frequency,
            "duration_days": median_duration,
            "expected_improvement_pct": float(expected_improvement),
            "typical_days_to_improvement": median_days,
            "sample_size": len(combo_outcomes),
            "confidence": "high" if len(combo_outcomes) >= 100 else "moderate" if len(combo_outcomes) >= 30 else "low",
        }
