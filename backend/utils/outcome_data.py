"""
Generate dummy outcome data for testing SOU
"""
import random
from uuid import uuid4
from datetime import datetime, timedelta
from typing import List

from algorithms.learning.models import (
    OutcomeRecord,
    OutcomeTimeframe,
    AdherenceLevel
)


def generate_dummy_outcomes(count: int = 100) -> List[OutcomeRecord]:
    """Generate dummy outcome records for testing"""

    outcomes = []

    for i in range(count):
        # Random user
        user_id = uuid4()

        # Random baseline (struggling to balanced)
        baseline_score = random.uniform(35, 70)

        # Random weak domains
        all_domains = ["physical", "emotional", "social", "cognitive", "spiritual"]
        weak_domains = random.sample(all_domains, random.randint(1, 3))

        baseline_domain_scores = {}
        for domain in all_domains:
            if domain in weak_domains:
                baseline_domain_scores[domain] = random.uniform(25, 50)
            else:
                baseline_domain_scores[domain] = random.uniform(60, 85)

        # Random interventions (1-3)
        num_interventions = random.randint(1, 3)
        recommended = [uuid4() for _ in range(num_interventions)]

        # Adherence
        adherence_pct = random.uniform(40, 95)
        if adherence_pct > 80:
            adherence_level = AdherenceLevel.HIGH
        elif adherence_pct > 50:
            adherence_level = AdherenceLevel.MEDIUM
        else:
            adherence_level = AdherenceLevel.LOW

        # Actually used (based on adherence)
        if adherence_level == AdherenceLevel.HIGH:
            actually_used = recommended
        elif adherence_level == AdherenceLevel.MEDIUM:
            actually_used = random.sample(recommended, max(1, len(recommended) - 1))
        else:
            actually_used = random.sample(recommended, 1)

        # Outcome depends on adherence
        if adherence_level == AdherenceLevel.HIGH:
            improvement = random.uniform(15, 40)  # Good improvement
        elif adherence_level == AdherenceLevel.MEDIUM:
            improvement = random.uniform(5, 25)  # Moderate
        else:
            improvement = random.uniform(-5, 15)  # Mixed results

        outcome_score = min(100, baseline_score + (baseline_score * improvement / 100))

        # Outcome domain scores
        outcome_domain_scores = {}
        domain_improvements = {}
        for domain in all_domains:
            domain_improvement = improvement + random.uniform(-5, 5)
            domain_improvements[domain] = domain_improvement
            outcome_domain_scores[domain] = min(100, baseline_domain_scores[domain] +
                                                (baseline_domain_scores[domain] * domain_improvement / 100))

        # Completion
        completed = adherence_level != AdherenceLevel.LOW and random.random() > 0.2

        # Satisfaction correlates with improvement
        if improvement > 25:
            satisfaction = random.randint(4, 5)
        elif improvement > 10:
            satisfaction = random.randint(3, 4)
        else:
            satisfaction = random.randint(1, 3)

        # Dates
        baseline_date = datetime.utcnow() - timedelta(weeks=random.randint(12, 52))
        outcome_date = baseline_date + timedelta(weeks=8)

        outcome = OutcomeRecord(
            user_id=user_id,
            baseline_sism_score=baseline_score,
            baseline_domain_scores=baseline_domain_scores,
            baseline_weak_domains=weak_domains,
            baseline_recorded_at=baseline_date,
            user_age=random.randint(25, 65),
            user_gender=random.choice(["male", "female", "other"]),
            primary_conditions=random.sample(["anxiety", "insomnia", "pain", "stress"], random.randint(1, 2)),
            primary_goals=["improve_wellbeing"],
            recommended_interventions=recommended,
            interventions_actually_used=actually_used,
            adherence_level=adherence_level,
            adherence_percentage=adherence_pct,
            practitioner_id=uuid4() if random.random() > 0.5 else None,
            practitioner_specialty="herbal_medicine" if random.random() > 0.5 else "acupuncture",
            sessions_completed=random.randint(4, 12) if completed else 0,
            outcome_sism_score=outcome_score,
            outcome_domain_scores=outcome_domain_scores,
            outcome_recorded_at=outcome_date,
            timeframe=OutcomeTimeframe.EIGHT_WEEKS,
            overall_improvement=improvement,
            domain_improvements=domain_improvements,
            user_satisfaction=satisfaction,
            would_recommend=satisfaction >= 4,
            reported_side_effects=[],
            completed_full_program=completed,
            dropout_reason=None if completed else "time_constraints",
            season=random.choice(["spring", "summer", "fall", "winter"]),
            cost_per_week=random.uniform(20, 80),
            time_per_week_minutes=random.randint(120, 480)
        )

        outcomes.append(outcome)

    return outcomes
