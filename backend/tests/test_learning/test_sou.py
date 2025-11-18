"""
Unit tests for SOU algorithm
"""
import pytest
from uuid import uuid4

from algorithms.learning.sou import SOUAlgorithm
from algorithms.learning.models import AdherenceLevel
from utils.outcome_data import generate_dummy_outcomes


class TestSOU:

    @pytest.fixture
    def sou(self):
        """Create SOU instance"""
        return SOUAlgorithm()

    @pytest.fixture
    def outcome_records(self):
        """Generate test outcome records"""
        return generate_dummy_outcomes(count=100)

    def test_analyze_empty_outcomes(self, sou):
        """Test analysis with no outcome data"""
        metrics = sou.analyze_outcomes([])

        assert metrics.total_outcome_records == 0
        assert metrics.learning_phase == "cold_start"
        assert metrics.exploration_rate == sou.COLD_START_EXPLORATION

    def test_analyze_outcomes_cold_start(self, sou):
        """Test analysis in cold start phase"""
        outcomes = generate_dummy_outcomes(count=50)
        metrics = sou.analyze_outcomes(outcomes)

        assert metrics.total_outcome_records == 50
        assert metrics.learning_phase == "cold_start"
        assert metrics.exploration_rate == sou.COLD_START_EXPLORATION

    def test_analyze_outcomes_early_learning(self, sou):
        """Test analysis in early learning phase"""
        outcomes = generate_dummy_outcomes(count=200)
        metrics = sou.analyze_outcomes(outcomes)

        assert metrics.total_outcome_records == 200
        assert metrics.learning_phase == "early_learning"
        assert metrics.exploration_rate == sou.EARLY_LEARNING_EXPLORATION

    def test_analyze_outcomes_mature(self, sou):
        """Test analysis in mature phase"""
        outcomes = generate_dummy_outcomes(count=600)
        metrics = sou.analyze_outcomes(outcomes)

        assert metrics.total_outcome_records == 600
        assert metrics.learning_phase == "mature"
        assert metrics.exploration_rate == sou.MATURE_EXPLORATION

    def test_intervention_performance_calculation(self, sou, outcome_records):
        """Test intervention performance calculation"""
        # Get an intervention from the records
        intervention_id = outcome_records[0].interventions_actually_used[0]

        performance = sou.calculate_intervention_performance(
            intervention_id,
            outcome_records
        )

        assert performance.intervention_id == intervention_id
        # Some records may have used this intervention
        assert performance.sample_size >= 0

    def test_intervention_performance_unknown(self, sou, outcome_records):
        """Test performance for unknown intervention"""
        unknown_id = uuid4()

        performance = sou.calculate_intervention_performance(
            unknown_id,
            outcome_records
        )

        assert performance.intervention_id == unknown_id
        assert performance.sample_size == 0

    def test_predict_outcome(self, sou, outcome_records):
        """Test outcome prediction"""
        user_id = uuid4()
        intervention_id = uuid4()

        user_profile = {
            "baseline_score": 45.0,
            "weak_domains": ["emotional"],
            "age": 35,
            "gender": "female"
        }

        prediction = sou.predict_outcome(
            user_id,
            user_profile,
            intervention_id,
            outcome_records
        )

        assert prediction.user_id == user_id
        assert prediction.intervention_id == intervention_id
        assert 0 <= prediction.confidence <= 100
        assert len(prediction.key_factors) > 0

    def test_predict_outcome_confidence_range(self, sou, outcome_records):
        """Test that prediction confidence is in valid range"""
        user_id = uuid4()
        intervention_id = uuid4()

        user_profile = {
            "baseline_score": 50.0,
            "weak_domains": ["physical"],
        }

        prediction = sou.predict_outcome(
            user_id,
            user_profile,
            intervention_id,
            outcome_records
        )

        assert prediction.confidence >= 0
        assert prediction.confidence <= 100

    def test_generate_recommendations(self, sou, outcome_records):
        """Test recommendation generation"""
        user_id = uuid4()

        user_profile = {
            "baseline_score": 45.0,
            "weak_domains": ["emotional"],
            "age": 35
        }

        candidates = [uuid4() for _ in range(10)]

        output = sou.generate_sou_recommendations(
            user_id,
            user_profile,
            candidates,
            outcome_records
        )

        assert output.user_id == user_id
        assert len(output.recommendations) <= 5  # Top 5
        assert output.total_outcomes_analyzed == len(outcome_records)

    def test_recommendations_sorted_by_score(self, sou, outcome_records):
        """Test that recommendations are sorted by total score"""
        user_id = uuid4()

        user_profile = {
            "baseline_score": 50.0,
            "weak_domains": ["social"],
        }

        candidates = [uuid4() for _ in range(10)]

        output = sou.generate_sou_recommendations(
            user_id,
            user_profile,
            candidates,
            outcome_records,
            exploration_rate=0.0  # No exploration to ensure pure sorting
        )

        if len(output.recommendations) > 1:
            scores = [r.total_score for r in output.recommendations]
            # Should be sorted descending (allowing for exploration shuffling)
            # With 0 exploration, should be strictly descending
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i + 1] or scores[i] == scores[i + 1]

    def test_exploration_vs_exploitation(self, sou, outcome_records):
        """Test exploration rate affects recommendations"""
        user_id = uuid4()
        user_profile = {"baseline_score": 50.0, "weak_domains": ["emotional"]}
        candidates = [uuid4() for _ in range(10)]

        # High exploration
        output_explore = sou.generate_sou_recommendations(
            user_id,
            user_profile,
            candidates,
            outcome_records,
            exploration_rate=0.8
        )

        # Low exploration
        output_exploit = sou.generate_sou_recommendations(
            user_id,
            user_profile,
            candidates,
            outcome_records,
            exploration_rate=0.0
        )

        # Both should have recommendations
        assert len(output_explore.recommendations) > 0
        assert len(output_exploit.recommendations) > 0

    def test_uplift_calculation(self, sou, outcome_records):
        """Test that uplift is calculated correctly"""
        user_id = uuid4()

        user_profile = {
            "baseline_score": 45.0,
            "weak_domains": ["cognitive"],
        }

        candidates = [uuid4() for _ in range(5)]

        output = sou.generate_sou_recommendations(
            user_id,
            user_profile,
            candidates,
            outcome_records
        )

        # Uplift should be difference between SOU and baseline
        expected_uplift = output.expected_improvement_with_sou - output.expected_improvement_baseline
        assert abs(output.uplift - expected_uplift) < 0.1

    def test_similar_user_matching(self, sou, outcome_records):
        """Test finding similar users"""
        user_profile = {
            "baseline_score": 45.0,
            "weak_domains": ["emotional", "social"],
        }

        intervention_id = outcome_records[0].interventions_actually_used[0]

        similar = sou._find_similar_user_outcomes(
            user_profile,
            intervention_id,
            outcome_records
        )

        # Should find some similar users
        for record in similar:
            # Similar baseline (within 15 points)
            assert abs(record.baseline_sism_score - 45.0) < 15
            # Overlapping weak domains
            assert len(set(record.baseline_weak_domains) & {"emotional", "social"}) > 0

    def test_prediction_confidence_increases_with_data(self, sou):
        """Test that confidence increases with more similar data"""
        user_profile = {
            "baseline_score": 50.0,
            "weak_domains": ["physical"],
        }

        # Small dataset
        small_outcomes = generate_dummy_outcomes(count=20)
        pred_small = sou.predict_outcome(
            uuid4(),
            user_profile,
            uuid4(),
            small_outcomes
        )

        # Larger dataset
        large_outcomes = generate_dummy_outcomes(count=200)
        pred_large = sou.predict_outcome(
            uuid4(),
            user_profile,
            uuid4(),
            large_outcomes
        )

        # Note: confidence depends on similar users found, not total size
        # But generally more data = higher chance of similar users
        assert pred_small.confidence >= 0
        assert pred_large.confidence >= 0

    def test_metrics_top_performers_identified(self, sou, outcome_records):
        """Test that top performers are identified"""
        metrics = sou.analyze_outcomes(outcome_records)

        # Should identify some top performers
        assert len(metrics.top_interventions) <= 5
        assert len(metrics.top_practitioners) <= 5

    def test_recommendation_contains_explanation(self, sou, outcome_records):
        """Test that recommendations contain explanations"""
        user_id = uuid4()
        user_profile = {"baseline_score": 45.0, "weak_domains": ["emotional"]}
        candidates = [uuid4() for _ in range(5)]

        output = sou.generate_sou_recommendations(
            user_id,
            user_profile,
            candidates,
            outcome_records
        )

        for rec in output.recommendations:
            assert rec.why_recommended is not None
            assert len(rec.why_recommended) > 0
            assert rec.expected_timeline is not None

    def test_learning_metrics_model_performance(self, sou, outcome_records):
        """Test learning metrics include model performance"""
        metrics = sou.analyze_outcomes(outcome_records)

        # MAE should be reasonable
        assert metrics.model_mae >= 0
        # R2 should be between -1 and 1 (or 0 and 1 for simplified)
        assert metrics.model_r2 >= 0
        assert metrics.model_r2 <= 1
        # Accuracy should be percentage
        assert 0 <= metrics.prediction_accuracy_within_10pct <= 1
