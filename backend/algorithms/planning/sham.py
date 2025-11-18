"""
SHAM - SANA Habit & Activity Model
Generates personalized daily/weekly wellness plans using SISM scores and Health Graph
"""
from typing import List, Dict, Optional
from uuid import UUID
import logging
from datetime import datetime
import random

from algorithms.scoring.sism import SISMAlgorithm
from algorithms.scoring.models import SISMOutput
from algorithms.evidence.health_graph import HealthGraph
from algorithms.evidence.models import Intervention, EvidenceStrength, Domain

from .models import (
    UserConstraints,
    UserGoals,
    SHAMOutput,
    WeeklySchedule,
    DailySchedule,
    ScheduledActivity,
    InterventionScore,
    TimeOfDay,
    DayOfWeek,
    HabitInput,
    HabitOutput
)

logger = logging.getLogger(__name__)

class SHAMAlgorithm:
    """
    SANA Habit & Activity Model (SHAM)

    Creates personalized wellness plans by:
    1. Analyzing SISM scores to find gaps
    2. Querying Health Graph for evidence-based interventions
    3. Optimizing selection within user constraints
    4. Generating realistic daily/weekly timetables
    """

    def __init__(
        self,
        health_graph: HealthGraph,
        sism: Optional[SISMAlgorithm] = None
    ):
        """
        Initialize SHAM

        Args:
            health_graph: SANA Health Graph instance with interventions
            sism: SISM algorithm instance (optional, for integrated flow)
        """
        self.health_graph = health_graph
        self.sism = sism or SISMAlgorithm()
        logger.info("SHAM initialized")

    def generate_plan(
        self,
        user_id: UUID,
        sism_output: SISMOutput,
        constraints: UserConstraints,
        goals: Optional[UserGoals] = None
    ) -> SHAMOutput:
        """
        Main method: Generate complete personalized wellness plan

        Args:
            user_id: User UUID
            sism_output: User's SISM health scores
            constraints: User's time/budget/availability constraints
            goals: Optional specific goals

        Returns:
            Complete SHAMOutput with weekly schedule and recommendations
        """
        logger.info(f"Generating SHAM plan for user {user_id}")

        # Step 1: Identify target domains (weak domains from SISM)
        target_domains = sism_output.weak_domains
        if not target_domains:
            # If no weak domains, focus on maintaining high scores
            target_domains = self._get_domains_for_maintenance(sism_output)

        logger.info(f"Target domains: {target_domains}")

        # Step 2: Get candidate interventions from Health Graph
        candidate_interventions = self._get_candidate_interventions(
            target_domains,
            constraints.medical_conditions,
            constraints.medications,
            goals
        )

        logger.info(f"Found {len(candidate_interventions)} candidate interventions")

        # Step 3: Score each intervention
        scored_interventions = self._score_interventions(
            candidate_interventions,
            sism_output,
            constraints
        )

        # Step 4: Select optimal set (constraint-aware optimization)
        selected_interventions = self._select_interventions(
            scored_interventions,
            constraints
        )

        logger.info(f"Selected {len(selected_interventions)} interventions for plan")

        # Step 5: Generate weekly schedule
        weekly_schedule = self._generate_weekly_schedule(
            user_id,
            selected_interventions,
            constraints,
            sism_output
        )

        # Step 6: Generate recommendations and insights
        priority_interventions = self._identify_priority_interventions(selected_interventions)
        quick_wins = self._identify_quick_wins(selected_interventions)
        expected_improvements = self._calculate_expected_improvements(
            selected_interventions,
            target_domains
        )
        timeline_expectations = self._calculate_timeline_expectations(selected_interventions)

        # Step 7: Build output
        output = SHAMOutput(
            user_id=user_id,
            weekly_schedule=weekly_schedule,
            priority_interventions=priority_interventions,
            quick_wins=quick_wins,
            expected_improvements=expected_improvements,
            timeline_expectations=timeline_expectations,
            fits_time_budget=weekly_schedule.total_time_minutes_per_week <= constraints.time_available_minutes_per_week,
            fits_cost_budget=weekly_schedule.total_cost_pounds_per_week <= constraints.budget_pounds_per_week,
            constraints_used=constraints,
            sism_input_id=sism_output.id
        )

        logger.info(
            f"SHAM plan generated: {weekly_schedule.total_activities} activities, "
            f"{weekly_schedule.total_time_minutes_per_week} min/week, "
            f"£{weekly_schedule.total_cost_pounds_per_week}/week"
        )

        return output

    def _get_domains_for_maintenance(self, sism_output: SISMOutput) -> List[str]:
        """Get domains to maintain when no weak domains exist"""
        # Return domains with highest scores (to maintain them)
        sorted_domains = sorted(
            sism_output.domain_scores.items(),
            key=lambda x: x[1].normalized_score,
            reverse=True
        )
        return [domain for domain, _ in sorted_domains[:2]]  # Top 2 domains

    def _get_candidate_interventions(
        self,
        target_domains: List[str],
        medical_conditions: List[str],
        medications: List[str],
        goals: Optional[UserGoals]
    ) -> List[Intervention]:
        """Get safe interventions from Health Graph for target domains"""
        all_interventions = []

        for domain_name in target_domains:
            try:
                domain = Domain(domain_name.lower())
                interventions = self.health_graph.find_interventions_for_domain(
                    domain,
                    min_evidence_strength=EvidenceStrength.WEAK,  # Include all with some evidence
                    user_conditions=set(medical_conditions),
                    user_medications=set(medications)
                )
                all_interventions.extend(interventions)
            except ValueError:
                logger.warning(f"Invalid domain: {domain_name}")

        # Remove duplicates (interventions can target multiple domains)
        seen = set()
        unique_interventions = []
        for intervention in all_interventions:
            if intervention.id not in seen:
                seen.add(intervention.id)
                unique_interventions.append(intervention)

        return unique_interventions

    def _score_interventions(
        self,
        interventions: List[Intervention],
        sism_output: SISMOutput,
        constraints: UserConstraints
    ) -> List[InterventionScore]:
        """Score each intervention based on multiple factors"""
        scored = []

        for intervention in interventions:
            # Evidence score (0-100)
            evidence_score = self._calculate_evidence_score(intervention.evidence_strength)

            # Domain gap score (how much this helps weak domains)
            domain_gap_score = self._calculate_domain_gap_score(
                intervention,
                sism_output
            )

            # Time efficiency (benefit per minute)
            duration = intervention.typical_duration_minutes or 30  # Default 30 min
            time_efficiency = (evidence_score + domain_gap_score) / 2 / duration * 100

            # Cost efficiency (benefit per pound)
            avg_cost = ((intervention.cost_estimate_min or 0) + (intervention.cost_estimate_max or 0)) / 2
            if avg_cost > 0:
                cost_efficiency = (evidence_score + domain_gap_score) / 2 / avg_cost * 10
            else:
                cost_efficiency = 100  # Free interventions get max score

            # Apply preference modifiers
            if intervention.category.value in constraints.preferred_categories:
                evidence_score *= 1.2  # 20% boost
            if intervention.category.value in constraints.disliked_categories:
                evidence_score *= 0.5  # 50% penalty

            scored_intervention = InterventionScore(
                intervention_id=intervention.id,
                intervention_name=intervention.name,
                evidence_score=min(100, evidence_score),
                domain_gap_score=domain_gap_score,
                time_efficiency_score=min(100, time_efficiency),
                cost_efficiency_score=min(100, cost_efficiency),
                total_score=0,  # Will be calculated
                duration_minutes=duration,
                cost_pounds=avg_cost,
                target_domains=[d.value for d in intervention.target_domains]
            )

            # Calculate total score
            scored_intervention.total_score = scored_intervention.calculate_total_score()
            scored.append(scored_intervention)

        return sorted(scored, key=lambda x: x.total_score, reverse=True)

    def _calculate_evidence_score(self, strength: EvidenceStrength) -> float:
        """Convert evidence strength to numeric score"""
        scores = {
            EvidenceStrength.STRONG: 100,
            EvidenceStrength.MODERATE: 75,
            EvidenceStrength.WEAK: 50,
            EvidenceStrength.INSUFFICIENT: 25,
            EvidenceStrength.CONFLICTING: 10
        }
        return scores.get(strength, 25)

    def _calculate_domain_gap_score(
        self,
        intervention: Intervention,
        sism_output: SISMOutput
    ) -> float:
        """Calculate how much this intervention helps with user's gaps"""
        gap_score = 0
        domains_helped = 0

        for domain in intervention.target_domains:
            domain_name = domain.value
            if domain_name in sism_output.domain_scores:
                domain_score = sism_output.domain_scores[domain_name].normalized_score
                # Higher gap (lower score) = higher benefit potential
                gap = 100 - domain_score
                gap_score += gap
                domains_helped += 1

        if domains_helped > 0:
            return gap_score / domains_helped
        return 0

    def _select_interventions(
        self,
        scored_interventions: List[InterventionScore],
        constraints: UserConstraints
    ) -> List[InterventionScore]:
        """
        Select optimal set of interventions using greedy knapsack approach

        Maximize: total_score
        Subject to: time budget, cost budget, domain balance
        """
        selected = []
        time_used = 0
        cost_used = 0.0
        domains_covered = set()

        # Greedy selection: pick highest-scoring interventions that fit
        for intervention in scored_interventions:
            # Check time constraint
            if time_used + intervention.duration_minutes > constraints.time_available_minutes_per_day * 7:
                continue

            # Check cost constraint
            if cost_used + intervention.cost_pounds > constraints.budget_pounds_per_week:
                continue

            # Add intervention
            selected.append(intervention)
            time_used += intervention.duration_minutes
            cost_used += intervention.cost_pounds
            domains_covered.update(intervention.target_domains)

            # Stop when we have enough (aim for 5-10 activities per week)
            if len(selected) >= 10:
                break

        # Ensure minimum variety (at least 3 different activities if possible)
        if len(selected) < 3 and len(scored_interventions) >= 3:
            selected = scored_interventions[:3]

        return selected

    def _generate_weekly_schedule(
        self,
        user_id: UUID,
        interventions: List[InterventionScore],
        constraints: UserConstraints,
        sism_output: SISMOutput
    ) -> WeeklySchedule:
        """Generate complete weekly schedule with activities distributed across days"""
        daily_schedules = {}

        # Distribute activities across available days
        available_days = constraints.available_days
        activities_per_day = self._distribute_activities(interventions, available_days)

        total_time = 0
        total_cost = 0.0
        total_activities = 0
        domains_addressed = {}
        evidence_distribution = {}

        for day in DayOfWeek:
            if day not in available_days:
                # Create empty schedule for unavailable days
                daily_schedules[day] = DailySchedule(
                    day=day,
                    activities=[],
                    total_time_minutes=0,
                    total_cost_pounds=0.0
                )
                continue

            day_activities = activities_per_day.get(day, [])
            scheduled_activities = []
            day_time = 0
            day_cost = 0.0

            for intervention_score in day_activities:
                # Get full intervention details
                intervention = self.health_graph.get_intervention(intervention_score.intervention_id)
                if not intervention:
                    continue

                # Determine time of day based on intervention type
                time_of_day = self._determine_time_slot(intervention, constraints)

                # Get dosage info if available
                dosage_info = None
                if intervention.dosage_protocols:
                    protocol = intervention.dosage_protocols[0]
                    dosage_info = protocol.get_display_string()

                activity = ScheduledActivity(
                    intervention_id=intervention.id,
                    intervention_name=intervention.name,
                    category=intervention.category.value,
                    day_of_week=day,
                    time_of_day=time_of_day,
                    duration_minutes=intervention_score.duration_minutes,
                    instructions=intervention.description,
                    dosage_info=dosage_info,
                    target_domains=[d.value for d in intervention.target_domains],
                    evidence_strength=intervention.evidence_strength.value,
                    expected_benefit_score=intervention_score.total_score,
                    cost_pounds=intervention_score.cost_pounds
                )

                scheduled_activities.append(activity)
                day_time += activity.duration_minutes
                day_cost += activity.cost_pounds

                # Track domains and evidence
                for domain in activity.target_domains:
                    domains_addressed[domain] = domains_addressed.get(domain, 0) + 1
                evidence_distribution[activity.evidence_strength] = \
                    evidence_distribution.get(activity.evidence_strength, 0) + 1

            daily_schedules[day] = DailySchedule(
                day=day,
                activities=scheduled_activities,
                total_time_minutes=day_time,
                total_cost_pounds=day_cost
            )

            total_time += day_time
            total_cost += day_cost
            total_activities += len(scheduled_activities)

        return WeeklySchedule(
            user_id=user_id,
            week_start_date=datetime.utcnow(),
            daily_schedules=daily_schedules,
            total_activities=total_activities,
            total_time_minutes_per_week=total_time,
            total_cost_pounds_per_week=total_cost,
            domains_addressed=domains_addressed,
            evidence_distribution=evidence_distribution,
            sism_score_at_creation=sism_output.overall_score,
            weak_domains_at_creation=sism_output.weak_domains
        )

    def _distribute_activities(
        self,
        interventions: List[InterventionScore],
        available_days: List[DayOfWeek]
    ) -> Dict[DayOfWeek, List[InterventionScore]]:
        """Distribute activities across the week"""
        distribution = {day: [] for day in available_days}

        if not available_days:
            return distribution

        # Simple round-robin distribution
        for i, intervention in enumerate(interventions):
            day = available_days[i % len(available_days)]
            distribution[day].append(intervention)

        return distribution

    def _determine_time_slot(
        self,
        intervention: Intervention,
        constraints: UserConstraints
    ) -> TimeOfDay:
        """Determine best time of day for intervention based on type"""
        category = intervention.category.value

        # Default time slot preferences by category
        preferences = {
            "movement": [TimeOfDay.MORNING, TimeOfDay.AFTERNOON],
            "mind_body": [TimeOfDay.MORNING, TimeOfDay.EVENING],
            "herbal": [TimeOfDay.MORNING, TimeOfDay.EVENING],
            "nutrition": [TimeOfDay.MORNING, TimeOfDay.MIDDAY, TimeOfDay.EVENING],
            "energy_work": [TimeOfDay.AFTERNOON, TimeOfDay.EVENING],
        }

        preferred_times = preferences.get(category, [TimeOfDay.MORNING])

        # Filter by user availability
        available_times = []
        if constraints.available_morning and TimeOfDay.MORNING in preferred_times:
            available_times.append(TimeOfDay.MORNING)
        if constraints.available_midday and TimeOfDay.MIDDAY in preferred_times:
            available_times.append(TimeOfDay.MIDDAY)
        if constraints.available_afternoon and TimeOfDay.AFTERNOON in preferred_times:
            available_times.append(TimeOfDay.AFTERNOON)
        if constraints.available_evening and TimeOfDay.EVENING in preferred_times:
            available_times.append(TimeOfDay.EVENING)

        if available_times:
            return random.choice(available_times)

        # Fallback to any available time
        if constraints.available_morning:
            return TimeOfDay.MORNING
        if constraints.available_evening:
            return TimeOfDay.EVENING
        return TimeOfDay.AFTERNOON

    def _identify_priority_interventions(
        self,
        interventions: List[InterventionScore]
    ) -> List[str]:
        """Identify top 3-5 priority interventions"""
        sorted_interventions = sorted(
            interventions,
            key=lambda x: x.total_score,
            reverse=True
        )
        return [i.intervention_name for i in sorted_interventions[:5]]

    def _identify_quick_wins(
        self,
        interventions: List[InterventionScore]
    ) -> List[str]:
        """Identify low-effort, high-impact activities"""
        quick_wins = []
        for intervention in interventions:
            # Quick win: < 20 minutes, high score (>70)
            if intervention.duration_minutes <= 20 and intervention.total_score >= 70:
                quick_wins.append(intervention.intervention_name)
        return quick_wins[:3]  # Top 3

    def _calculate_expected_improvements(
        self,
        interventions: List[InterventionScore],
        target_domains: List[str]
    ) -> Dict[str, str]:
        """Calculate expected improvements by domain"""
        improvements = {}
        for domain in target_domains:
            # Find interventions targeting this domain
            domain_interventions = [
                i for i in interventions
                if domain in i.target_domains
            ]
            if domain_interventions:
                improvements[domain] = f"Expected improvement through {len(domain_interventions)} interventions"
        return improvements

    def _calculate_timeline_expectations(
        self,
        interventions: List[InterventionScore]
    ) -> Dict[str, int]:
        """Calculate expected timeline to results for each intervention"""
        timelines = {}
        for intervention in interventions:
            # Get full intervention to access expected outcomes
            full_intervention = self.health_graph.get_intervention(intervention.intervention_id)
            if full_intervention and full_intervention.expected_outcomes:
                avg_timeline = sum(
                    outcome.typical_timeline_weeks
                    for outcome in full_intervention.expected_outcomes
                ) / len(full_intervention.expected_outcomes)
                timelines[intervention.intervention_name] = int(avg_timeline)
        return timelines


# Legacy class for backwards compatibility
class SHAMPlanner:
    """Legacy class - use SHAMAlgorithm instead"""

    def __init__(self):
        pass

    def generate_plan(self, input_data: HabitInput) -> HabitOutput:
        return HabitOutput(
            user_id=input_data.user_id,
            daily_plan=[],
            weekly_summary={},
            adherence_prediction=0.0
        )
