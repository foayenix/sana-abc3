"""
SANA Herb Index (SHI) Calculator

Calculates evidence-based credibility scores (0-100) for herbs and supplements
based on real-world outcome data.

Score Components:
- Evidence Volume: 0-25 points
- Efficacy: 0-40 points
- Safety: 0-20 points
- Data Quality: 0-15 points
"""
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np

from .models import (
    Herb,
    HerbUsage,
    HerbOutcome,
    HerbIndexScore,
    ConditionHerbEfficacy,
    EvidenceLevel,
    AdverseEventSeverity,
)


class HerbIndexCalculator:
    """Calculate SANA Herb Index (SHI) scores"""

    def __init__(self):
        # Evidence level thresholds
        self.VERY_HIGH_THRESHOLD = 85
        self.HIGH_THRESHOLD = 70
        self.MODERATE_THRESHOLD = 50
        self.LOW_THRESHOLD = 30

        # Minimum cases for reliability
        self.MIN_CASES_FOR_SCORE = 10
        self.MIN_CASES_FOR_CONDITION = 30

    def calculate_herb_index(
        self,
        herb: Herb,
        usage_data: List[HerbUsage],
        outcome_data: List[HerbOutcome],
    ) -> HerbIndexScore:
        """
        Calculate complete Herb Index Score for an herb

        Args:
            herb: Herb master record
            usage_data: List of usage records for this herb
            outcome_data: List of outcome measurements

        Returns:
            HerbIndexScore with all component scores
        """
        if len(usage_data) < self.MIN_CASES_FOR_SCORE:
            # Return minimal score for insufficient data
            return HerbIndexScore(
                herb_id=herb.herb_id,
                herb_name=herb.common_names[0] if herb.common_names else herb.botanical_name,
                botanical_name=herb.botanical_name,
                overall_score=0,
                evidence_volume_score=0,
                efficacy_score=0,
                safety_score=0,
                data_quality_score=0,
                total_cases=len(usage_data),
                unique_practitioners=0,
                unique_conditions=0,
                evidence_level=EvidenceLevel.INSUFFICIENT,
                confidence_interval=(0.0, 0.0),
            )

        # Calculate component scores
        evidence_score = self._calculate_evidence_volume(usage_data)
        efficacy_score = self._calculate_efficacy(outcome_data)
        safety_score = self._calculate_safety(outcome_data)
        quality_score = self._calculate_data_quality(usage_data, outcome_data)

        overall_score = int(evidence_score + efficacy_score + safety_score + quality_score)

        # Calculate metadata
        unique_practitioners = len(set(u.practitioner_id for u in usage_data))
        unique_conditions = len(set(u.primary_condition_id for u in usage_data if u.primary_condition_id))

        # Determine evidence level
        evidence_level = self._determine_evidence_level(overall_score, len(usage_data))

        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(outcome_data, overall_score)

        return HerbIndexScore(
            herb_id=herb.herb_id,
            herb_name=herb.common_names[0] if herb.common_names else herb.botanical_name,
            botanical_name=herb.botanical_name,
            overall_score=overall_score,
            evidence_volume_score=int(evidence_score),
            efficacy_score=int(efficacy_score),
            safety_score=int(safety_score),
            data_quality_score=int(quality_score),
            total_cases=len(usage_data),
            unique_practitioners=unique_practitioners,
            unique_conditions=unique_conditions,
            evidence_level=evidence_level,
            confidence_interval=confidence_interval,
        )

    def _calculate_evidence_volume(self, usage_data: List[HerbUsage]) -> float:
        """
        Calculate Evidence Volume Score (0-25 points)

        Formula:
        - Total instances: log10(n) * 5 (max 15 points)
        - Unique practitioners: sqrt(practitioners) * 0.8 (max 8 points)
        - Geographic diversity: unique_regions * 0.5 (max 2 points)
        """
        total_instances = len(usage_data)
        unique_practitioners = len(set(u.practitioner_id for u in usage_data))
        unique_regions = len(set(u.region for u in usage_data if u.region))

        # Instance score (logarithmic scale)
        instance_score = min(15, math.log10(max(1, total_instances)) * 5)

        # Practitioner diversity score
        practitioner_score = min(8, math.sqrt(unique_practitioners) * 0.8)

        # Geographic diversity score
        geographic_score = min(2, unique_regions * 0.5)

        return instance_score + practitioner_score + geographic_score

    def _calculate_efficacy(self, outcome_data: List[HerbOutcome]) -> float:
        """
        Calculate Efficacy Score (0-40 points)

        Formula:
        - Mean improvement: mean(improvement_pct) * 0.25 (max 20 points)
        - Effect size: cohens_d * 10 (max 15 points)
        - Consistency bonus: (1 - cv) * 5 (max 5 points)
        """
        if not outcome_data:
            return 0.0

        # Get improvement percentages
        improvements = [o.improvement_percentage for o in outcome_data if o.improvement_percentage is not None]

        if not improvements:
            return 0.0

        improvements = np.array(improvements)

        # Mean improvement score (max 20 points for 80% improvement)
        mean_improvement = np.mean(improvements)
        improvement_score = min(20, max(0, mean_improvement * 0.25))

        # Effect size (Cohen's d)
        baseline_scores = np.array([o.baseline_score for o in outcome_data])
        followup_scores = np.array([o.followup_score for o in outcome_data])
        cohens_d = self._calculate_cohens_d(baseline_scores, followup_scores)
        effect_score = min(15, cohens_d * 10)

        # Consistency (inverse of coefficient of variation)
        if np.mean(improvements) > 0:
            cv = np.std(improvements) / np.mean(improvements)
            consistency_score = min(5, max(0, (1 - cv) * 5))
        else:
            consistency_score = 0

        return improvement_score + effect_score + consistency_score

    def _calculate_safety(self, outcome_data: List[HerbOutcome]) -> float:
        """
        Calculate Safety Score (0-20 points)

        Formula:
        - Base score: 20 points
        - Adverse event penalty: -1 point per 1% of cases
        - Severity multiplier: 1x (mild), 2x (moderate), 3x (severe)
        - Dropout penalty: -5 points per 10% dropout rate
        """
        if not outcome_data:
            return 18.0  # Default high safety if no data

        total_cases = len(outcome_data)

        # Count adverse events by severity
        severity_weights = {
            AdverseEventSeverity.MILD: 1,
            AdverseEventSeverity.MODERATE: 2,
            AdverseEventSeverity.SEVERE: 3,
        }

        weighted_ae_count = 0
        for outcome in outcome_data:
            if outcome.adverse_events:
                weight = severity_weights.get(outcome.adverse_event_severity, 1)
                weighted_ae_count += weight

        weighted_ae_rate = weighted_ae_count / total_cases if total_cases > 0 else 0

        # Dropout rate
        dropout_count = sum(1 for o in outcome_data if o.discontinued)
        dropout_rate = dropout_count / total_cases if total_cases > 0 else 0

        # Calculate score
        score = 20 - (weighted_ae_rate * 100) - (dropout_rate * 50)
        return max(0, score)

    def _calculate_data_quality(
        self,
        usage_data: List[HerbUsage],
        outcome_data: List[HerbOutcome],
    ) -> float:
        """
        Calculate Data Quality Score (0-15 points)

        Formula:
        - Dosage completeness: pct_complete * 4 (max 4 points)
        - Outcome completeness: pct_complete * 6 (max 6 points)
        - Follow-up compliance: pct_complete * 5 (max 5 points)
        """
        # Dosage completeness
        dosage_complete = sum(
            1 for u in usage_data
            if u.dosage_amount is not None
            and u.dosage_unit is not None
            and u.frequency is not None
        ) / len(usage_data) if usage_data else 0

        # Outcome measurement completeness
        outcome_complete = sum(
            1 for o in outcome_data
            if o.baseline_score is not None and o.followup_score is not None
        ) / len(outcome_data) if outcome_data else 0

        # Follow-up compliance (at 4-week mark)
        followup_compliance = sum(
            1 for o in outcome_data if o.days_since_start >= 28
        ) / len(outcome_data) if outcome_data else 0

        score = (
            dosage_complete * 4 +
            outcome_complete * 6 +
            followup_compliance * 5
        )
        return min(15, score)

    def _calculate_cohens_d(
        self,
        baseline: np.ndarray,
        followup: np.ndarray,
    ) -> float:
        """Calculate Cohen's d effect size"""
        if len(baseline) == 0 or len(followup) == 0:
            return 0.0

        diff = baseline - followup  # Improvement = baseline - followup
        pooled_std = np.sqrt((np.var(baseline) + np.var(followup)) / 2)

        if pooled_std == 0:
            return 0.0

        return abs(np.mean(diff) / pooled_std)

    def _determine_evidence_level(self, overall_score: int, case_count: int) -> EvidenceLevel:
        """Determine evidence level based on score and sample size"""
        # Require minimum cases for higher evidence levels
        if case_count < 30:
            return EvidenceLevel.LOW if overall_score >= self.LOW_THRESHOLD else EvidenceLevel.INSUFFICIENT

        if overall_score >= self.VERY_HIGH_THRESHOLD and case_count >= 500:
            return EvidenceLevel.VERY_HIGH
        elif overall_score >= self.HIGH_THRESHOLD and case_count >= 100:
            return EvidenceLevel.HIGH
        elif overall_score >= self.MODERATE_THRESHOLD:
            return EvidenceLevel.MODERATE
        elif overall_score >= self.LOW_THRESHOLD:
            return EvidenceLevel.LOW
        else:
            return EvidenceLevel.INSUFFICIENT

    def _calculate_confidence_interval(
        self,
        outcome_data: List[HerbOutcome],
        point_estimate: float,
    ) -> Tuple[float, float]:
        """Calculate 95% confidence interval for score using bootstrap"""
        if not outcome_data:
            return (point_estimate, point_estimate)

        improvements = [o.improvement_percentage for o in outcome_data if o.improvement_percentage is not None]

        if len(improvements) < 10:
            # Too few samples for reliable bootstrap
            return (max(0, point_estimate - 10), min(100, point_estimate + 10))

        improvements = np.array(improvements)
        n = len(improvements)

        # Bootstrap confidence interval
        bootstrap_scores = []
        for _ in range(1000):
            sample = np.random.choice(improvements, size=n, replace=True)
            # Scale sample mean to approximate score contribution
            bootstrap_score = min(100, max(0, sample.mean() * 1.25))
            bootstrap_scores.append(bootstrap_score)

        ci_lower = float(np.percentile(bootstrap_scores, 2.5))
        ci_upper = float(np.percentile(bootstrap_scores, 97.5))

        return (ci_lower, ci_upper)

    def calculate_condition_efficacy(
        self,
        herb: Herb,
        condition_id: UUID,
        condition_name: str,
        outcome_data: List[HerbOutcome],
    ) -> Optional[ConditionHerbEfficacy]:
        """
        Calculate condition-specific efficacy for an herb

        Args:
            herb: Herb record
            condition_id: Condition UUID
            condition_name: Human-readable condition name
            outcome_data: Outcomes filtered for this condition

        Returns:
            ConditionHerbEfficacy or None if insufficient data
        """
        if len(outcome_data) < self.MIN_CASES_FOR_CONDITION:
            return None

        improvements = np.array([
            o.improvement_percentage for o in outcome_data
            if o.improvement_percentage is not None
        ])

        if len(improvements) == 0:
            return None

        # Calculate metrics
        mean_improvement = float(np.mean(improvements))
        median_improvement = float(np.median(improvements))
        std_deviation = float(np.std(improvements))

        # Effect size
        baseline_scores = np.array([o.baseline_score for o in outcome_data])
        followup_scores = np.array([o.followup_score for o in outcome_data])
        effect_size = self._calculate_cohens_d(baseline_scores, followup_scores)

        # Days to improvement (median)
        days_to_improvement = [
            o.days_since_start for o in outcome_data
            if o.improvement_percentage and o.improvement_percentage > 20
        ]
        median_days = int(np.median(days_to_improvement)) if days_to_improvement else None

        # Get primary outcome measure
        outcome_measures = [o.outcome_measure for o in outcome_data]
        primary_measure = max(set(outcome_measures), key=outcome_measures.count)

        return ConditionHerbEfficacy(
            herb_id=herb.herb_id,
            herb_name=herb.common_names[0] if herb.common_names else herb.botanical_name,
            condition_id=condition_id,
            condition_name=condition_name,
            mean_improvement=mean_improvement,
            median_improvement=median_improvement,
            std_deviation=std_deviation,
            effect_size=effect_size,
            sample_size=len(outcome_data),
            outcome_measure=primary_measure,
            median_days_to_improvement=median_days,
        )

    def rank_herbs_for_condition(
        self,
        condition_id: UUID,
        condition_name: str,
        herb_efficacies: List[ConditionHerbEfficacy],
        metric: str = "efficacy",
    ) -> List[ConditionHerbEfficacy]:
        """
        Rank herbs by effectiveness for a specific condition

        Args:
            condition_id: Condition to rank for
            condition_name: Human-readable condition name
            herb_efficacies: List of efficacy data for herbs
            metric: Ranking metric (efficacy, safety, effect_size)

        Returns:
            Sorted list of ConditionHerbEfficacy with ranks assigned
        """
        if metric == "efficacy":
            sorted_herbs = sorted(
                herb_efficacies,
                key=lambda x: x.mean_improvement,
                reverse=True
            )
        elif metric == "effect_size":
            sorted_herbs = sorted(
                herb_efficacies,
                key=lambda x: x.effect_size,
                reverse=True
            )
        else:
            # Default to mean improvement
            sorted_herbs = sorted(
                herb_efficacies,
                key=lambda x: x.mean_improvement,
                reverse=True
            )

        # Assign ranks
        for i, efficacy in enumerate(sorted_herbs):
            efficacy.rank = i + 1

        return sorted_herbs
