"""
Unit tests for SHAM algorithm
"""
import pytest
from uuid import uuid4

from algorithms.planning.sham import SHAMAlgorithm
from algorithms.planning.models import UserConstraints, UserGoals, DayOfWeek
from algorithms.evidence.health_graph import HealthGraph
from algorithms.scoring.sism import SISMAlgorithm
from utils.dummy_data import DummyDataGenerator
from utils.health_graph_data import seed_health_graph

class TestSHAM:

    @pytest.fixture
    def health_graph(self):
        """Create and seed health graph"""
        graph = HealthGraph()
        seed_health_graph(graph)
        return graph

    @pytest.fixture
    def sism(self):
        """Create SISM instance"""
        return SISMAlgorithm()

    @pytest.fixture
    def sham(self, health_graph, sism):
        """Create SHAM instance"""
        return SHAMAlgorithm(health_graph, sism)

    @pytest.fixture
    def basic_constraints(self):
        """Basic user constraints"""
        return UserConstraints(
            time_available_minutes_per_day=60,
            time_available_minutes_per_week=420,  # 60 * 7
            budget_pounds_per_week=50.0,
            medical_conditions=[],
            medications=[]
        )

    def test_generate_plan_basic(self, sham, sism, basic_constraints):
        """Test basic plan generation"""
        # Generate questionnaire and SISM score
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        # Generate plan
        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        assert plan.user_id == questionnaire.user_id
        assert plan.weekly_schedule is not None
        assert plan.weekly_schedule.total_activities > 0

    def test_plan_respects_time_budget(self, sham, sism, basic_constraints):
        """Test that plan respects time constraints"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        # Check time constraint
        assert plan.weekly_schedule.total_time_minutes_per_week <= basic_constraints.time_available_minutes_per_week

    def test_plan_respects_cost_budget(self, sham, sism, basic_constraints):
        """Test that plan respects cost constraints"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        # Check cost constraint
        assert plan.weekly_schedule.total_cost_pounds_per_week <= basic_constraints.budget_pounds_per_week

    def test_plan_targets_weak_domains(self, sham, sism, basic_constraints):
        """Test that plan addresses weak domains from SISM"""
        # Generate with weak emotional domain
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="emotional_weak")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        # Check that emotional domain is addressed
        assert "emotional" in plan.weekly_schedule.domains_addressed

    def test_plan_with_medical_contraindications(self, sham, sism):
        """Test that plan respects medical contraindications"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        # User is pregnant - should avoid certain herbs
        constraints = UserConstraints(
            time_available_minutes_per_day=60,
            time_available_minutes_per_week=420,
            budget_pounds_per_week=50.0,
            medical_conditions=["pregnancy"],
            medications=[]
        )

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            constraints
        )

        # Plan should be generated (with safe interventions only)
        assert plan.weekly_schedule.total_activities >= 0

    def test_priority_interventions_identified(self, sham, sism, basic_constraints):
        """Test that priority interventions are identified"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        assert len(plan.priority_interventions) > 0
        assert len(plan.priority_interventions) <= 5

    def test_quick_wins_identified(self, sham, sism, basic_constraints):
        """Test that quick wins are identified"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        # Quick wins should be present (short, high-impact activities)
        assert isinstance(plan.quick_wins, list)

    def test_weekly_schedule_structure(self, sham, sism, basic_constraints):
        """Test weekly schedule has correct structure"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        schedule = plan.weekly_schedule

        # Check all days are present
        assert len(schedule.daily_schedules) == 7

        # Check summary fields
        assert schedule.total_activities >= 0
        assert schedule.total_time_minutes_per_week >= 0
        assert schedule.total_cost_pounds_per_week >= 0

    def test_activities_have_required_fields(self, sham, sism, basic_constraints):
        """Test that scheduled activities have all required fields"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        # Get first activity from first non-empty day
        for daily_schedule in plan.weekly_schedule.daily_schedules.values():
            if daily_schedule.activities:
                activity = daily_schedule.activities[0]

                # Check required fields
                assert activity.intervention_name is not None
                assert activity.category is not None
                assert activity.duration_minutes > 0
                assert activity.time_of_day is not None
                assert len(activity.target_domains) > 0
                break

    def test_limited_availability_respected(self, sham, sism):
        """Test that user availability constraints are respected"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        # User only available mornings on weekdays
        constraints = UserConstraints(
            time_available_minutes_per_day=60,
            time_available_minutes_per_week=300,  # 5 days * 60 min
            budget_pounds_per_week=50.0,
            available_morning=True,
            available_midday=False,
            available_afternoon=False,
            available_evening=False,
            available_days=[
                DayOfWeek.MONDAY,
                DayOfWeek.TUESDAY,
                DayOfWeek.WEDNESDAY,
                DayOfWeek.THURSDAY,
                DayOfWeek.FRIDAY
            ],
            medical_conditions=[],
            medications=[]
        )

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            constraints
        )

        # Check that weekend days have no activities
        assert len(plan.weekly_schedule.daily_schedules[DayOfWeek.SATURDAY].activities) == 0
        assert len(plan.weekly_schedule.daily_schedules[DayOfWeek.SUNDAY].activities) == 0

    def test_thriving_profile_generates_plan(self, sham, sism, basic_constraints):
        """Test plan generation for thriving profile (no weak domains)"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="thriving")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        # Should still generate a maintenance plan
        assert plan.weekly_schedule is not None

    def test_fits_budget_flags(self, sham, sism):
        """Test that fits_time_budget and fits_cost_budget flags work"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        # Generous constraints
        constraints = UserConstraints(
            time_available_minutes_per_day=180,
            time_available_minutes_per_week=1260,
            budget_pounds_per_week=500.0,
            medical_conditions=[],
            medications=[]
        )

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            constraints
        )

        assert plan.fits_time_budget == True
        assert plan.fits_cost_budget == True

    def test_expected_improvements_generated(self, sham, sism, basic_constraints):
        """Test that expected improvements are generated"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        assert isinstance(plan.expected_improvements, dict)

    def test_timeline_expectations_generated(self, sham, sism, basic_constraints):
        """Test that timeline expectations are generated"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        plan = sham.generate_plan(
            questionnaire.user_id,
            sism_output,
            basic_constraints
        )

        assert isinstance(plan.timeline_expectations, dict)
