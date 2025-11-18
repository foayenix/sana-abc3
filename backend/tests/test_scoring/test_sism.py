"""
Unit tests for SISM algorithm
"""
import pytest
from uuid import uuid4
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from algorithms.scoring.sism import SISMAlgorithm
from algorithms.scoring.models import (
    QuestionnaireInput,
    QuestionResponse,
    DomainWeights
)
from utils.dummy_data import DummyDataGenerator


class TestSISM:

    @pytest.fixture
    def sism(self):
        """Create SISM instance with default weights"""
        return SISMAlgorithm()

    @pytest.fixture
    def sample_questionnaire(self):
        """Generate a sample questionnaire"""
        return DummyDataGenerator.generate_questionnaire(profile="balanced")

    def test_normalize_score(self, sism):
        """Test score normalization"""
        assert sism.normalize_score(0, 0, 10) == 0.0
        assert sism.normalize_score(10, 0, 10) == 100.0
        assert sism.normalize_score(5, 0, 10) == 50.0
        assert sism.normalize_score(7, 0, 10) == 70.0

    def test_calculate_basic(self, sism, sample_questionnaire):
        """Test basic SISM calculation"""
        result = sism.calculate(sample_questionnaire)

        # Check output structure
        assert result.user_id == sample_questionnaire.user_id
        assert 0 <= result.overall_score <= 100
        assert len(result.domain_scores) == 5
        assert all(domain in result.domain_scores for domain in
                  ['physical', 'emotional', 'social', 'cognitive', 'spiritual'])

    def test_domain_scores_sum_correctly(self, sism, sample_questionnaire):
        """Test that domain contributions sum to overall score"""
        result = sism.calculate(sample_questionnaire)

        calculated_total = sum(
            score.weighted_contribution
            for score in result.domain_scores.values()
        )

        # Allow small floating point differences
        assert abs(calculated_total - result.overall_score) < 0.1

    def test_weak_domain_identification(self, sism):
        """Test that weak domains are correctly identified"""
        # Create questionnaire with intentionally weak physical domain
        questionnaire = DummyDataGenerator.generate_questionnaire(
            profile="physical_weak"
        )

        result = sism.calculate(questionnaire)

        assert "physical" in result.weak_domains
        assert len(result.weak_domains) <= 5

    def test_custom_weights(self, sism, sample_questionnaire):
        """Test calculation with custom weights"""
        custom_weights = DomainWeights(
            physical=0.30,
            emotional=0.30,
            social=0.10,
            cognitive=0.20,
            spiritual=0.10
        )

        result = sism.recalculate_with_weights(
            sample_questionnaire,
            custom_weights
        )

        # Verify custom weights were used
        assert result.domain_scores['physical'].weight == 0.30
        assert result.domain_scores['emotional'].weight == 0.30

    def test_invalid_questionnaire_missing_domain(self, sism):
        """Test that missing domain raises error"""
        # Create questionnaire missing spiritual domain
        responses = [
            QuestionResponse(question_id="PHY_001", domain="physical", raw_score=7),
            QuestionResponse(question_id="EMO_001", domain="emotional", raw_score=6),
            QuestionResponse(question_id="SOC_001", domain="social", raw_score=8),
            QuestionResponse(question_id="COG_001", domain="cognitive", raw_score=7),
            # Missing spiritual
        ]

        with pytest.raises(ValueError, match="Missing responses for domains"):
            QuestionnaireInput(
                user_id=uuid4(),
                responses=responses
            )

    def test_invalid_weights_sum(self):
        """Test that weights must sum to 1.0"""
        invalid_weights = DomainWeights(
            physical=0.30,
            emotional=0.30,
            social=0.10,
            cognitive=0.20,
            spiritual=0.20  # Sum = 1.10, invalid!
        )

        with pytest.raises(ValueError, match="must sum to 1.0"):
            invalid_weights.validate_sum()

    def test_thriving_profile_scores_high(self, sism):
        """Test that thriving profile produces high scores"""
        questionnaire = DummyDataGenerator.generate_questionnaire(
            profile="thriving"
        )

        result = sism.calculate(questionnaire)

        assert result.overall_score >= 75
        assert len(result.weak_domains) == 0

    def test_struggling_profile_scores_low(self, sism):
        """Test that struggling profile produces low scores"""
        questionnaire = DummyDataGenerator.generate_questionnaire(
            profile="struggling"
        )

        result = sism.calculate(questionnaire)

        assert result.overall_score <= 55
        assert len(result.weak_domains) >= 3

    def test_metadata_completeness(self, sism, sample_questionnaire):
        """Test that calculation metadata is complete"""
        result = sism.calculate(sample_questionnaire)

        metadata = result.calculation_metadata
        assert "weights_used" in metadata
        assert "total_questions" in metadata
        assert "domains_analyzed" in metadata
        assert "weak_domain_threshold" in metadata
        assert "calculation_timestamp" in metadata

    def test_user_journey_shows_improvement(self, sism):
        """Test that user journey data shows score improvement"""
        user_id = uuid4()
        journey = DummyDataGenerator.generate_user_journey(
            user_id=user_id,
            weeks=12,
            improvement=True
        )

        # Calculate scores for first and last questionnaire
        first_score = sism.calculate(journey[0]).overall_score
        last_score = sism.calculate(journey[-1]).overall_score

        # Last score should be higher
        assert last_score > first_score

    def test_domain_score_details(self, sism, sample_questionnaire):
        """Test that domain scores contain all required details"""
        result = sism.calculate(sample_questionnaire)

        for domain, score in result.domain_scores.items():
            assert hasattr(score, 'domain')
            assert hasattr(score, 'raw_average')
            assert hasattr(score, 'normalized_score')
            assert hasattr(score, 'weight')
            assert hasattr(score, 'weighted_contribution')
            assert hasattr(score, 'question_count')
            assert hasattr(score, 'questions_scored')

            assert score.domain == domain
            assert 0 <= score.normalized_score <= 100
            assert score.weight > 0
            assert score.question_count > 0

    def test_questionnaire_version_preserved(self, sism, sample_questionnaire):
        """Test that questionnaire version is preserved in output"""
        result = sism.calculate(sample_questionnaire)
        assert result.questionnaire_version == sample_questionnaire.questionnaire_version

    def test_multiple_questionnaires_different_scores(self, sism):
        """Test that different profiles produce different scores"""
        balanced = DummyDataGenerator.generate_questionnaire(profile="balanced")
        thriving = DummyDataGenerator.generate_questionnaire(profile="thriving")
        struggling = DummyDataGenerator.generate_questionnaire(profile="struggling")

        balanced_score = sism.calculate(balanced).overall_score
        thriving_score = sism.calculate(thriving).overall_score
        struggling_score = sism.calculate(struggling).overall_score

        # Thriving should be highest, struggling should be lowest
        assert thriving_score > balanced_score > struggling_score
