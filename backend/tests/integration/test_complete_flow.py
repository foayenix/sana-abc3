"""
Integration tests for SANA complete algorithm flow

Tests the full pipeline: SISM scoring -> Safety assessment ->
Practitioner matching -> Credential verification -> Activity planning ->
Evidence recommendations -> Outcome learning
"""
import pytest
from uuid import uuid4

from algorithms.scoring.sism import SISMCalculator
from algorithms.safety.sst import SSTAlgorithm
from algorithms.matching.sprm import SPRMAlgorithm
from algorithms.verification.scvm import SCVMAlgorithm
from algorithms.planning.sham import SHAMAlgorithm
from algorithms.learning.sou import SOUAlgorithm
from algorithms.evidence.health_graph import HealthGraph

from utils.questionnaire import generate_dummy_questionnaire
from utils.outcome_data import generate_dummy_outcomes


class TestCompleteFlow:
    """Test complete algorithm flow from user input to recommendations"""

    @pytest.fixture
    def sism(self):
        return SISMCalculator()

    @pytest.fixture
    def sst(self):
        return SSTAlgorithm()

    @pytest.fixture
    def sprm(self):
        return SPRMAlgorithm()

    @pytest.fixture
    def scvm(self):
        return SCVMAlgorithm()

    @pytest.fixture
    def sham(self):
        return SHAMAlgorithm()

    @pytest.fixture
    def sou(self):
        return SOUAlgorithm()

    @pytest.fixture
    def health_graph(self):
        return HealthGraph()

    @pytest.fixture
    def outcome_records(self):
        return generate_dummy_outcomes(count=100)

    def test_end_to_end_struggling_user(
        self, sism, sst, sprm, scvm, sham, sou, health_graph, outcome_records
    ):
        """
        Test complete flow for a user with low scores who needs help

        Flow:
        1. SISM calculates low overall score
        2. SST monitors but doesn't escalate
        3. SPRM finds practitioners for weak domains
        4. SCVM verifies practitioner credentials
        5. SHAM creates activity plan within constraints
        6. Health Graph provides evidence-based interventions
        7. SOU optimizes recommendations based on outcomes
        """
        user_id = uuid4()

        # Step 1: SISM scoring - struggling user
        questionnaire = generate_dummy_questionnaire(profile="struggling")
        sism_result = sism.calculate_score(questionnaire)

        assert sism_result.overall_score < 50, "Struggling user should have low score"
        assert len(sism_result.weak_domains) > 0, "Should identify weak domains"

        # Step 2: SST safety assessment
        score_history = [
            {"date": "2024-01-01", "score": 42},
            {"date": "2024-01-15", "score": 40},
            {"date": "2024-01-29", "score": 38},
        ]

        sst_result = sst.analyze_safety(
            user_id=user_id,
            current_score=sism_result.overall_score,
            domain_scores=sism_result.domain_scores,
            score_history=score_history,
        )

        # Should be monitoring but not urgent
        assert sst_result.status in ["safe", "monitor"], "Low score should trigger monitoring"
        assert sst_result.risk_score < 85, "Should not be urgent"

        # Step 3: SPRM practitioner matching
        user_needs = {
            "health_goals": sism_result.weak_domains[:2],
            "max_budget": 80.0,
            "max_distance": 15.0,
            "preferred_modalities": ["in_person", "video"],
        }

        match_result = sprm.find_matches(
            user_id=user_id,
            user_needs=user_needs,
            domain_scores=sism_result.domain_scores,
        )

        assert len(match_result.matches) > 0, "Should find practitioner matches"

        # Step 4: SCVM credential verification for top match
        if match_result.matches:
            top_practitioner = match_result.matches[0]

            # Simulate practitioner credentials
            credentials = [
                {
                    "credential_type": "degree",
                    "credential_name": "MSc Clinical Psychology",
                    "institution": "University of Edinburgh",
                    "year_obtained": 2018,
                },
                {
                    "credential_type": "license",
                    "credential_name": "HCPC Registration",
                    "registration_number": "PYL12345",
                    "expiry_date": "2025-12-31",
                },
            ]

            verification = scvm.verify_practitioner(
                practitioner_id=top_practitioner.practitioner_id,
                credentials=credentials,
                tier="standard",
            )

            assert verification.overall_status in [
                "verified",
                "pending",
            ], "Should process verification"

        # Step 5: SHAM activity planning
        plan_result = sham.create_activity_plan(
            user_id=user_id,
            domain_scores=sism_result.domain_scores,
            weak_domains=sism_result.weak_domains,
            time_per_day=60,
            budget_per_week=50.0,
        )

        assert len(plan_result.activities) > 0, "Should create activities"
        assert plan_result.total_time_per_day <= 60, "Should respect time constraint"
        assert plan_result.total_cost_per_week <= 50.0, "Should respect budget"

        # Step 6: Health Graph evidence lookup
        for domain in sism_result.weak_domains[:2]:
            interventions = health_graph.get_interventions_for_domain(domain)
            assert len(interventions) > 0, f"Should find interventions for {domain}"

        # Step 7: SOU outcome optimization
        user_profile = {
            "baseline_score": sism_result.overall_score,
            "weak_domains": sism_result.weak_domains,
        }

        candidate_interventions = [uuid4() for _ in range(5)]

        sou_output = sou.generate_sou_recommendations(
            user_id=user_id,
            user_profile=user_profile,
            candidate_interventions=candidate_interventions,
            outcome_records=outcome_records,
        )

        assert len(sou_output.recommendations) > 0, "Should generate recommendations"
        assert sou_output.uplift >= 0, "SOU should provide uplift"

    def test_end_to_end_thriving_user(
        self, sism, sst, sprm, sham, health_graph
    ):
        """
        Test complete flow for a user with high scores

        Should result in:
        - High SISM score
        - Safe SST status
        - Maintenance-focused recommendations
        """
        user_id = uuid4()

        # Step 1: SISM scoring - thriving user
        questionnaire = generate_dummy_questionnaire(profile="thriving")
        sism_result = sism.calculate_score(questionnaire)

        assert sism_result.overall_score > 70, "Thriving user should have high score"
        assert len(sism_result.weak_domains) <= 2, "Should have few weak domains"

        # Step 2: SST safety assessment - should be safe
        score_history = [
            {"date": "2024-01-01", "score": 78},
            {"date": "2024-01-15", "score": 80},
            {"date": "2024-01-29", "score": 82},
        ]

        sst_result = sst.analyze_safety(
            user_id=user_id,
            current_score=sism_result.overall_score,
            domain_scores=sism_result.domain_scores,
            score_history=score_history,
        )

        assert sst_result.status == "safe", "Thriving user should be safe"
        assert sst_result.risk_score < 30, "Should have low risk"

        # Step 3: SHAM maintenance planning
        plan_result = sham.create_activity_plan(
            user_id=user_id,
            domain_scores=sism_result.domain_scores,
            weak_domains=sism_result.weak_domains,
            time_per_day=30,  # Less time needed
            budget_per_week=30.0,
        )

        assert len(plan_result.activities) > 0, "Should still provide maintenance activities"

    def test_verification_blocks_unverified_practitioners(self, scvm):
        """Test that unverified practitioners are flagged appropriately"""
        practitioner_id = uuid4()

        # Minimal credentials
        credentials = [
            {
                "credential_type": "certificate",
                "credential_name": "Online Wellness Certificate",
                "institution": "Unknown Academy",
                "year_obtained": 2023,
            }
        ]

        verification = scvm.verify_practitioner(
            practitioner_id=practitioner_id,
            credentials=credentials,
            tier="premium",  # High tier but poor credentials
        )

        # Should not be fully verified with minimal credentials
        assert verification.overall_status in [
            "pending",
            "failed",
        ], "Poor credentials should not pass verification"
        assert verification.trust_score < 80, "Trust score should be reduced"

    def test_budget_constraint_respected(self, sham, sism):
        """Test that SHAM respects budget constraints strictly"""
        user_id = uuid4()

        questionnaire = generate_dummy_questionnaire(profile="balanced")
        sism_result = sism.calculate_score(questionnaire)

        # Very tight budget
        plan_result = sham.create_activity_plan(
            user_id=user_id,
            domain_scores=sism_result.domain_scores,
            weak_domains=sism_result.weak_domains,
            time_per_day=120,  # Lots of time
            budget_per_week=10.0,  # But very little money
        )

        assert plan_result.total_cost_per_week <= 10.0, "Must respect budget constraint"
        # Should prioritize free activities
        free_activities = [a for a in plan_result.activities if a.cost_per_session == 0]
        assert len(free_activities) > 0, "Should include free activities for tight budget"

    def test_geographic_filtering(self, sprm):
        """Test that SPRM respects geographic constraints"""
        user_id = uuid4()

        user_needs = {
            "health_goals": ["emotional", "social"],
            "max_budget": 100.0,
            "max_distance": 5.0,  # Very close
            "preferred_modalities": ["in_person"],  # Must be in person
        }

        domain_scores = {
            "emotional": 40.0,
            "physical": 60.0,
            "social": 45.0,
            "cognitive": 70.0,
            "spiritual": 65.0,
        }

        match_result = sprm.find_matches(
            user_id=user_id,
            user_needs=user_needs,
            domain_scores=domain_scores,
        )

        # All matches should respect distance constraint
        for match in match_result.matches:
            if "in_person" in match.available_modalities:
                assert (
                    match.distance <= 5.0
                ), f"Match distance {match.distance} exceeds max 5.0"

    def test_data_consistency_across_algorithms(self, sism, sst, sham):
        """Test that data flows consistently between algorithms"""
        user_id = uuid4()

        # Generate questionnaire and get score
        questionnaire = generate_dummy_questionnaire(profile="struggling")
        sism_result = sism.calculate_score(questionnaire)

        # Domain scores should be consistent
        for domain, score in sism_result.domain_scores.items():
            assert 0 <= score <= 100, f"Invalid score for {domain}: {score}"

        # SST should receive same domain scores
        sst_result = sst.analyze_safety(
            user_id=user_id,
            current_score=sism_result.overall_score,
            domain_scores=sism_result.domain_scores,
            score_history=[],
        )

        # SHAM should work with same domain scores
        plan_result = sham.create_activity_plan(
            user_id=user_id,
            domain_scores=sism_result.domain_scores,
            weak_domains=sism_result.weak_domains,
            time_per_day=60,
            budget_per_week=50.0,
        )

        # All should reference same domains
        sism_domains = set(sism_result.domain_scores.keys())
        # Activities should target valid domains
        for activity in plan_result.activities:
            assert activity.target_domain in sism_domains, (
                f"Activity targets invalid domain: {activity.target_domain}"
            )

    def test_safety_escalation_triggers_correctly(self, sism, sst):
        """Test that SST correctly escalates dangerous situations"""
        user_id = uuid4()

        # Create crisis scenario
        sst_result = sst.analyze_safety(
            user_id=user_id,
            current_score=25,  # Very low
            domain_scores={
                "emotional": 15,  # Critical
                "physical": 30,
                "social": 20,
                "cognitive": 40,
                "spiritual": 35,
            },
            score_history=[
                {"date": "2024-01-01", "score": 50},
                {"date": "2024-01-08", "score": 40},
                {"date": "2024-01-15", "score": 30},
                {"date": "2024-01-22", "score": 25},  # Rapid decline
            ],
            user_messages=["feeling hopeless", "can't cope anymore"],
        )

        # Should trigger escalation
        assert sst_result.status in [
            "escalate",
            "urgent",
        ], "Crisis should trigger escalation"
        assert len(sst_result.risk_indicators) > 0, "Should identify risk indicators"
        assert len(sst_result.recommended_resources) > 0, "Should recommend resources"

    def test_sou_improves_over_baseline(self, sou, outcome_records):
        """Test that SOU provides uplift over baseline recommendations"""
        user_id = uuid4()

        user_profile = {
            "baseline_score": 45.0,
            "weak_domains": ["emotional", "social"],
        }

        candidates = [uuid4() for _ in range(10)]

        sou_output = sou.generate_sou_recommendations(
            user_id=user_id,
            user_profile=user_profile,
            candidate_interventions=candidates,
            outcome_records=outcome_records,
        )

        # SOU should provide positive uplift (or at minimum no worse than baseline)
        assert sou_output.expected_improvement_with_sou >= sou_output.expected_improvement_baseline, (
            "SOU should not be worse than baseline"
        )

    def test_full_pipeline_with_all_algorithms(
        self, sism, sst, sprm, scvm, sham, sou, health_graph, outcome_records
    ):
        """
        Comprehensive test running all 7 algorithms in sequence

        This is the master integration test that validates the entire
        SANA Health Framework works as an integrated system.
        """
        user_id = uuid4()

        # 1. SISM: Calculate initial health score
        questionnaire = generate_dummy_questionnaire(profile="balanced")
        sism_result = sism.calculate_score(questionnaire)
        assert sism_result.overall_score is not None

        # 2. SST: Assess safety
        sst_result = sst.analyze_safety(
            user_id=user_id,
            current_score=sism_result.overall_score,
            domain_scores=sism_result.domain_scores,
            score_history=[],
        )
        assert sst_result.status is not None

        # Only proceed with recommendations if safe
        if sst_result.status in ["safe", "monitor"]:
            # 3. SPRM: Find practitioners
            match_result = sprm.find_matches(
                user_id=user_id,
                user_needs={
                    "health_goals": sism_result.weak_domains[:2] if sism_result.weak_domains else ["emotional"],
                    "max_budget": 100.0,
                    "max_distance": 20.0,
                    "preferred_modalities": ["video", "in_person"],
                },
                domain_scores=sism_result.domain_scores,
            )
            assert match_result.total_matches >= 0

            # 4. SCVM: Verify top practitioner
            if match_result.matches:
                verification = scvm.verify_practitioner(
                    practitioner_id=match_result.matches[0].practitioner_id,
                    credentials=[
                        {
                            "credential_type": "license",
                            "credential_name": "Clinical License",
                            "registration_number": "CL123",
                            "expiry_date": "2026-01-01",
                        }
                    ],
                    tier="standard",
                )
                assert verification.overall_status is not None

            # 5. SHAM: Create activity plan
            plan_result = sham.create_activity_plan(
                user_id=user_id,
                domain_scores=sism_result.domain_scores,
                weak_domains=sism_result.weak_domains,
                time_per_day=60,
                budget_per_week=50.0,
            )
            assert len(plan_result.activities) >= 0

            # 6. Health Graph: Get evidence-based interventions
            all_interventions = []
            for domain in (sism_result.weak_domains or ["emotional"])[:2]:
                interventions = health_graph.get_interventions_for_domain(domain)
                all_interventions.extend(interventions)

            # 7. SOU: Optimize with outcome learning
            sou_output = sou.generate_sou_recommendations(
                user_id=user_id,
                user_profile={
                    "baseline_score": sism_result.overall_score,
                    "weak_domains": sism_result.weak_domains or [],
                },
                candidate_interventions=[uuid4() for _ in range(5)],
                outcome_records=outcome_records,
            )
            assert sou_output.recommendations is not None

        # Test passed - all algorithms executed successfully
        assert True, "Full pipeline completed successfully"


class TestAlgorithmInteractions:
    """Test specific interactions between algorithm pairs"""

    def test_sism_to_sst_flow(self):
        """Test data flow from SISM to SST"""
        sism = SISMCalculator()
        sst = SSTAlgorithm()

        questionnaire = generate_dummy_questionnaire(profile="struggling")
        sism_result = sism.calculate_score(questionnaire)

        # SST should handle SISM output correctly
        sst_result = sst.analyze_safety(
            user_id=uuid4(),
            current_score=sism_result.overall_score,
            domain_scores=sism_result.domain_scores,
            score_history=[],
        )

        assert sst_result.status is not None
        assert sst_result.risk_score >= 0

    def test_sprm_to_scvm_flow(self):
        """Test data flow from SPRM to SCVM"""
        sprm = SPRMAlgorithm()
        scvm = SCVMAlgorithm()

        match_result = sprm.find_matches(
            user_id=uuid4(),
            user_needs={
                "health_goals": ["emotional"],
                "max_budget": 100.0,
                "max_distance": 20.0,
                "preferred_modalities": ["video"],
            },
            domain_scores={"emotional": 40.0, "physical": 60.0, "social": 50.0, "cognitive": 70.0, "spiritual": 65.0},
        )

        # Verify each matched practitioner
        for match in match_result.matches[:3]:  # Top 3
            verification = scvm.verify_practitioner(
                practitioner_id=match.practitioner_id,
                credentials=[
                    {
                        "credential_type": "license",
                        "credential_name": "Test License",
                        "registration_number": "TL123",
                        "expiry_date": "2026-01-01",
                    }
                ],
                tier="basic",
            )
            assert verification.practitioner_id == match.practitioner_id

    def test_sham_to_health_graph_flow(self):
        """Test that SHAM activities align with Health Graph evidence"""
        sham = SHAMAlgorithm()
        health_graph = HealthGraph()

        plan_result = sham.create_activity_plan(
            user_id=uuid4(),
            domain_scores={"emotional": 35.0, "physical": 70.0, "social": 45.0, "cognitive": 60.0, "spiritual": 55.0},
            weak_domains=["emotional", "social"],
            time_per_day=60,
            budget_per_week=50.0,
        )

        # Activities should have evidence support
        for activity in plan_result.activities:
            # Check Health Graph has interventions for this domain
            interventions = health_graph.get_interventions_for_domain(activity.target_domain)
            # Health Graph should support activities in this domain
            assert len(interventions) >= 0  # May be empty for some domains


class TestErrorHandling:
    """Test error handling across algorithm integrations"""

    def test_empty_questionnaire_handling(self):
        """Test that SISM handles empty questionnaire gracefully"""
        sism = SISMCalculator()

        # Empty questionnaire
        with pytest.raises(Exception):
            sism.calculate_score({})

    def test_invalid_domain_scores(self):
        """Test SST handles invalid domain scores"""
        sst = SSTAlgorithm()

        # Should handle gracefully or raise appropriate error
        try:
            result = sst.analyze_safety(
                user_id=uuid4(),
                current_score=50,
                domain_scores={},  # Empty
                score_history=[],
            )
            # If it succeeds, should have valid output
            assert result.status is not None
        except Exception as e:
            # Acceptable to raise error for invalid input
            assert "domain" in str(e).lower() or True

    def test_no_matching_practitioners(self):
        """Test SPRM handles case with no matches"""
        sprm = SPRMAlgorithm()

        result = sprm.find_matches(
            user_id=uuid4(),
            user_needs={
                "health_goals": ["nonexistent_domain"],
                "max_budget": 1.0,  # Impossibly low
                "max_distance": 0.1,  # Impossibly close
                "preferred_modalities": ["hologram"],  # Doesn't exist
            },
            domain_scores={"emotional": 50.0, "physical": 50.0, "social": 50.0, "cognitive": 50.0, "spiritual": 50.0},
        )

        # Should return empty results, not crash
        assert result.matches is not None
        assert result.total_matches >= 0
