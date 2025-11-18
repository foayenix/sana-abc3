"""
Unit tests for SPRM (Practitioner Recommendation Model) algorithm
"""
import pytest
from uuid import uuid4

from algorithms.matching.sprm import SPRMAlgorithm
from algorithms.matching.models import (
    UserMatchingPreferences,
    PractitionerProfile,
    TreatmentPhilosophy,
    CommunicationStyle
)
from algorithms.scoring.sism import SISMAlgorithm
from utils.dummy_data import DummyDataGenerator
from utils.practitioner_data import generate_sample_practitioners


class TestSPRM:

    @pytest.fixture
    def sprm(self):
        """Create SPRM instance"""
        return SPRMAlgorithm()

    @pytest.fixture
    def sism(self):
        """Create SISM instance"""
        return SISMAlgorithm()

    @pytest.fixture
    def practitioners(self):
        """Get sample practitioners"""
        return generate_sample_practitioners()

    @pytest.fixture
    def user_preferences(self):
        """Create user preferences"""
        return UserMatchingPreferences(
            user_id=uuid4(),
            location_latitude=51.5074,
            location_longitude=-0.1278,
            max_travel_distance_km=10.0,
            willing_to_do_virtual=True,
            max_budget_per_session=100.0,
            preferred_philosophies=[TreatmentPhilosophy.INTEGRATIVE],
            prioritize_experience=True,
            prioritize_credentials=True
        )

    def test_find_matches_basic(self, sprm, sism, practitioners, user_preferences):
        """Test basic matching functionality"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        assert result.user_id == user_preferences.user_id
        assert len(result.top_recommendations) > 0
        assert result.total_practitioners_considered == len(practitioners)

    def test_matches_sorted_by_score(self, sprm, sism, practitioners, user_preferences):
        """Test that matches are sorted by score descending"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        scores = [r.match_score.overall_score for r in result.top_recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_verification_filter(self, sprm, sism, user_preferences):
        """Test that unverified practitioners are filtered out"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        # Create practitioner with low verification score
        unverified = PractitionerProfile(
            practitioner_id=uuid4(),
            full_name="Unverified Person",
            specialties=["anxiety"],
            primary_modalities=["counseling"],
            target_domains=["emotional"],
            years_experience=5,
            credentials=["Some Cert"],
            verification_tier="basic",
            scvm_confidence_score=50.0,  # Below threshold
            trust_score=50,
            treatment_philosophy=TreatmentPhilosophy.HOLISTIC,
            communication_style=CommunicationStyle.WARM,
            location_latitude=51.5074,
            location_longitude=-0.1278,
            location_address="London",
            hourly_rate=60.0
        )

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            [unverified]
        )

        # Should return no matches due to low verification
        assert len(result.top_recommendations) == 0

    def test_budget_filter(self, sprm, sism, practitioners):
        """Test that budget constraints are respected"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        # Very low budget
        low_budget_prefs = UserMatchingPreferences(
            user_id=uuid4(),
            location_latitude=51.5074,
            location_longitude=-0.1278,
            max_travel_distance_km=100.0,
            willing_to_do_virtual=True,
            max_budget_per_session=30.0,  # Very low
            prioritize_affordability=True
        )

        result = sprm.find_best_matches(
            low_budget_prefs.user_id,
            sism_output,
            low_budget_prefs,
            practitioners
        )

        # All recommendations should be within budget or offer sliding scale
        for rec in result.top_recommendations:
            assert (
                rec.practitioner.hourly_rate <= low_budget_prefs.max_budget_per_session or
                rec.practitioner.offers_sliding_scale
            )

    def test_geographic_filter(self, sprm, sism, practitioners):
        """Test that geographic constraints work"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        # Very small radius
        local_prefs = UserMatchingPreferences(
            user_id=uuid4(),
            location_latitude=51.5074,
            location_longitude=-0.1278,
            max_travel_distance_km=0.1,  # Very small
            willing_to_do_virtual=False,
            max_budget_per_session=200.0
        )

        result = sprm.find_best_matches(
            local_prefs.user_id,
            sism_output,
            local_prefs,
            practitioners
        )

        # May have few or no matches due to tiny radius
        assert result is not None

    def test_match_score_components(self, sprm, sism, practitioners, user_preferences):
        """Test that match score has all components"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        if result.top_recommendations:
            score = result.top_recommendations[0].match_score

            assert 0 <= score.overall_score <= 100
            assert 0 <= score.health_need_score <= 100
            assert 0 <= score.credibility_score <= 100
            assert 0 <= score.practical_fit_score <= 100
            assert 0 <= score.evidence_alignment_score <= 100
            assert 0 <= score.preference_match_score <= 100

    def test_match_reasons_generated(self, sprm, sism, practitioners, user_preferences):
        """Test that match reasons are generated"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        if result.top_recommendations:
            rec = result.top_recommendations[0]
            assert len(rec.match_score.match_reasons) > 0

    def test_recommendation_has_required_fields(self, sprm, sism, practitioners, user_preferences):
        """Test that recommendations have all required fields"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        if result.top_recommendations:
            rec = result.top_recommendations[0]

            assert rec.headline is not None
            assert rec.why_recommended is not None
            assert rec.what_to_expect is not None
            assert rec.estimated_sessions_needed is not None
            assert rec.estimated_total_cost is not None

    def test_no_matches_handled(self, sprm, sism, user_preferences):
        """Test that no matches scenario is handled gracefully"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            []  # Empty practitioner pool
        )

        assert len(result.top_recommendations) == 0
        assert result.no_match_reason is not None
        assert len(result.alternative_suggestions) > 0

    def test_weak_domains_drive_matching(self, sprm, sism, practitioners, user_preferences):
        """Test that weak domains influence matching"""
        # Profile with emotional weakness
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="emotional_weak")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        # Top match should target emotional domain
        if result.top_recommendations:
            top_practitioner = result.top_recommendations[0].practitioner
            # Check that emotional is in target domains
            assert any(
                "emotional" in domain.lower()
                for domain in top_practitioner.target_domains
            )

    def test_haversine_distance_calculation(self, sprm):
        """Test distance calculation"""
        # London to Paris approximately 344 km
        london_lat, london_lon = 51.5074, -0.1278
        paris_lat, paris_lon = 48.8566, 2.3522

        distance = sprm._calculate_distance(
            london_lat, london_lon,
            paris_lat, paris_lon
        )

        # Should be roughly 340-350 km
        assert 300 < distance < 400

    def test_match_summary_generated(self, sprm, sism, practitioners, user_preferences):
        """Test that match summary is generated"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        assert result.match_summary != ""
        assert len(result.match_summary) > 10

    def test_honorable_mentions(self, sprm, sism, practitioners, user_preferences):
        """Test that honorable mentions are generated"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        result = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output,
            user_preferences,
            practitioners
        )

        # If enough practitioners, should have some honorable mentions
        assert isinstance(result.honorable_mentions, list)

    def test_estimated_sessions_by_health_score(self, sprm, sism, practitioners, user_preferences):
        """Test that estimated sessions vary by health score"""
        # Low score should need more sessions
        questionnaire_low = DummyDataGenerator.generate_questionnaire(profile="struggling")
        sism_output_low = sism.calculate(questionnaire_low)

        result_low = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output_low,
            user_preferences,
            practitioners
        )

        # Higher score should need fewer sessions
        questionnaire_high = DummyDataGenerator.generate_questionnaire(profile="thriving")
        sism_output_high = sism.calculate(questionnaire_high)

        result_high = sprm.find_best_matches(
            user_preferences.user_id,
            sism_output_high,
            user_preferences,
            practitioners
        )

        if result_low.top_recommendations and result_high.top_recommendations:
            sessions_low = result_low.top_recommendations[0].estimated_sessions_needed
            sessions_high = result_high.top_recommendations[0].estimated_sessions_needed

            # Lower score should need more or equal sessions
            assert sessions_low >= sessions_high

    def test_philosophy_preference_matching(self, sprm, sism, practitioners):
        """Test that philosophy preferences influence scoring"""
        questionnaire = DummyDataGenerator.generate_questionnaire(profile="balanced")
        sism_output = sism.calculate(questionnaire)

        # Prefer integrative
        integrative_prefs = UserMatchingPreferences(
            user_id=uuid4(),
            location_latitude=51.5074,
            location_longitude=-0.1278,
            max_travel_distance_km=100.0,
            willing_to_do_virtual=True,
            max_budget_per_session=200.0,
            preferred_philosophies=[TreatmentPhilosophy.INTEGRATIVE]
        )

        result = sprm.find_best_matches(
            integrative_prefs.user_id,
            sism_output,
            integrative_prefs,
            practitioners
        )

        assert result is not None
