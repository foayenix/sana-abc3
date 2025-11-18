"""
Unit tests for SST algorithm
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from algorithms.safety.sst import SSTAlgorithm
from algorithms.safety.models import (
    SSTInput,
    SafetyStatus,
    RiskCategory,
    HistoricalScore,
    EscalationPathway
)


class TestSST:

    @pytest.fixture
    def sst(self):
        """Create SST instance"""
        return SSTAlgorithm()

    def test_safe_user(self, sst):
        """Test that healthy user is marked safe"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=75.0,
            current_domain_scores={
                "physical": 75.0,
                "emotional": 80.0,
                "social": 70.0,
                "cognitive": 75.0,
                "spiritual": 70.0
            },
            current_sism_id=uuid4()
        )

        result = sst.analyze_safety(sst_input)

        assert result.safety_status == SafetyStatus.SAFE
        assert result.risk_score < 30
        assert not result.requires_human_review

    def test_critical_score_triggers_escalation(self, sst):
        """Test that critical score triggers escalation status"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=25.0,  # Critical
            current_domain_scores={
                "physical": 30.0,
                "emotional": 15.0,  # Very low
                "social": 25.0,
                "cognitive": 30.0,
                "spiritual": 25.0
            },
            current_sism_id=uuid4()
        )

        result = sst.analyze_safety(sst_input)

        assert result.safety_status in [SafetyStatus.ESCALATE, SafetyStatus.URGENT]
        assert result.risk_score > 60
        assert result.requires_human_review

    def test_rapid_decline_detected(self, sst):
        """Test that rapid score decline is detected"""
        user_id = uuid4()

        # Create historical data showing decline
        two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
        historical = [
            HistoricalScore(
                score_id=uuid4(),
                user_id=user_id,
                overall_score=70.0,  # Was healthy
                domain_scores={"emotional": 70.0},
                recorded_at=two_weeks_ago
            )
        ]

        sst_input = SSTInput(
            user_id=user_id,
            current_sism_score=45.0,  # Dropped 25 points
            current_domain_scores={"emotional": 40.0},
            current_sism_id=uuid4(),
            historical_scores=historical
        )

        result = sst.analyze_safety(sst_input)

        # Should detect rapid decline
        decline_indicators = [
            ind for ind in result.risk_indicators
            if ind.indicator_type == "rapid_decline"
        ]
        assert len(decline_indicators) > 0
        assert result.safety_status != SafetyStatus.SAFE

    def test_crisis_keyword_detection(self, sst):
        """Test that crisis keywords are detected"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=50.0,
            current_domain_scores={"emotional": 45.0},
            current_sism_id=uuid4(),
            recent_journal_entries=[
                "I feel like I want to hurt myself",
                "Can't see any point in going on"
            ]
        )

        result = sst.analyze_safety(sst_input)

        # Should detect keywords
        keyword_indicators = [
            ind for ind in result.risk_indicators
            if ind.indicator_type == "keyword_detected"
        ]
        assert len(keyword_indicators) > 0
        assert result.requires_human_review

    def test_chronic_low_scores(self, sst):
        """Test detection of chronically low scores"""
        user_id = uuid4()

        # Create 4 weeks of low scores
        historical = []
        for weeks_ago in range(4, 0, -1):
            date = datetime.utcnow() - timedelta(weeks=weeks_ago)
            historical.append(
                HistoricalScore(
                    score_id=uuid4(),
                    user_id=user_id,
                    overall_score=35.0,  # Consistently low
                    domain_scores={"emotional": 35.0},
                    recorded_at=date
                )
            )

        sst_input = SSTInput(
            user_id=user_id,
            current_sism_score=35.0,
            current_domain_scores={"emotional": 35.0},
            current_sism_id=uuid4(),
            historical_scores=historical
        )

        result = sst.analyze_safety(sst_input)

        # Should detect chronic low
        chronic_indicators = [
            ind for ind in result.risk_indicators
            if ind.indicator_type == "chronic_low"
        ]
        assert len(chronic_indicators) > 0

    def test_escalation_pathway_suicidal_ideation(self, sst):
        """Test that suicidal ideation escalates to Samaritans"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=30.0,
            current_domain_scores={"emotional": 20.0},
            current_sism_id=uuid4(),
            recent_journal_entries=["I want to kill myself"]
        )

        result = sst.analyze_safety(sst_input)

        # Should escalate to Samaritans
        assert result.escalation_pathway == EscalationPathway.SAMARITANS

    def test_resources_provided(self, sst):
        """Test that appropriate resources are provided"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=40.0,
            current_domain_scores={"emotional": 30.0},
            current_sism_id=uuid4()
        )

        result = sst.analyze_safety(sst_input)

        if result.safety_status != SafetyStatus.SAFE:
            assert len(result.resources_to_provide) > 0

    def test_user_message_generated(self, sst):
        """Test that user-facing message is generated"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=35.0,
            current_domain_scores={"emotional": 25.0},
            current_sism_id=uuid4()
        )

        result = sst.analyze_safety(sst_input)

        if result.safety_status != SafetyStatus.SAFE:
            assert result.user_message is not None
            assert len(result.user_message) > 0

    def test_human_review_case_created(self, sst):
        """Test that human review case is created for urgent cases"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=20.0,
            current_domain_scores={"emotional": 10.0},
            current_sism_id=uuid4(),
            recent_journal_entries=["I want to end it all"]
        )

        result = sst.analyze_safety(sst_input)

        assert result.requires_human_review
        assert result.human_review_case is not None
        assert result.review_deadline is not None

    def test_disengagement_pattern_detected(self, sst):
        """Test that disengagement patterns are detected"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=50.0,
            current_domain_scores={"emotional": 45.0},
            current_sism_id=uuid4(),
            days_since_last_activity=20
        )

        result = sst.analyze_safety(sst_input)

        # Should detect disengagement
        disengagement_indicators = [
            ind for ind in result.risk_indicators
            if ind.indicator_type == "disengagement"
        ]
        assert len(disengagement_indicators) > 0

    def test_missed_appointments_detected(self, sst):
        """Test that missed appointments are detected"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=50.0,
            current_domain_scores={"emotional": 45.0},
            current_sism_id=uuid4(),
            missed_practitioner_appointments=4
        )

        result = sst.analyze_safety(sst_input)

        # Should detect missed appointments
        appointment_indicators = [
            ind for ind in result.risk_indicators
            if ind.indicator_type == "missed_appointments"
        ]
        assert len(appointment_indicators) > 0

    def test_multiple_low_domains_detected(self, sst):
        """Test that multiple low domains are detected"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=35.0,
            current_domain_scores={
                "physical": 35.0,
                "emotional": 30.0,
                "social": 35.0,
                "cognitive": 38.0,
                "spiritual": 50.0
            },
            current_sism_id=uuid4()
        )

        result = sst.analyze_safety(sst_input)

        # Should detect multiple low domains
        multiple_low_indicators = [
            ind for ind in result.risk_indicators
            if ind.indicator_type == "multiple_low_domains"
        ]
        assert len(multiple_low_indicators) > 0

    def test_immediate_actions_for_urgent(self, sst):
        """Test that immediate actions are created for urgent status"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=20.0,
            current_domain_scores={"emotional": 10.0},
            current_sism_id=uuid4(),
            recent_journal_entries=["I want to hurt myself"]
        )

        result = sst.analyze_safety(sst_input)

        if result.safety_status == SafetyStatus.URGENT:
            assert len(result.immediate_actions) > 0
            critical_actions = [a for a in result.immediate_actions if a.urgency == "critical"]
            assert len(critical_actions) > 0

    def test_confidence_calculation(self, sst):
        """Test that confidence is calculated correctly"""
        # Low confidence (minimal data)
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=75.0,
            current_domain_scores={"emotional": 75.0},
            current_sism_id=uuid4()
        )

        result = sst.analyze_safety(sst_input)
        low_confidence = result.confidence

        # Higher confidence (with historical data and text)
        sst_input_rich = SSTInput(
            user_id=uuid4(),
            current_sism_score=40.0,
            current_domain_scores={"emotional": 35.0},
            current_sism_id=uuid4(),
            historical_scores=[
                HistoricalScore(
                    score_id=uuid4(),
                    user_id=uuid4(),
                    overall_score=50.0,
                    domain_scores={"emotional": 50.0},
                    recorded_at=datetime.utcnow() - timedelta(weeks=2)
                )
            ],
            recent_journal_entries=["Feeling down lately"]
        )

        result_rich = sst.analyze_safety(sst_input_rich)

        # Rich data should have higher confidence
        assert result_rich.confidence >= low_confidence

    def test_trend_calculation(self, sst):
        """Test that score trend is calculated correctly"""
        user_id = uuid4()

        # Declining trend
        historical = [
            HistoricalScore(
                score_id=uuid4(),
                user_id=user_id,
                overall_score=80.0,
                domain_scores={"emotional": 80.0},
                recorded_at=datetime.utcnow() - timedelta(weeks=2)
            )
        ]

        sst_input = SSTInput(
            user_id=user_id,
            current_sism_score=50.0,  # Dropped 30 points
            current_domain_scores={"emotional": 50.0},
            current_sism_id=uuid4(),
            historical_scores=historical
        )

        result = sst.analyze_safety(sst_input)

        assert result.score_trend in ["declining", "rapidly_declining"]
        assert result.trend_percentage is not None
        assert result.trend_percentage < 0  # Negative for decline

    def test_primary_concerns_summarized(self, sst):
        """Test that primary concerns are summarized"""
        sst_input = SSTInput(
            user_id=uuid4(),
            current_sism_score=30.0,
            current_domain_scores={"emotional": 20.0},
            current_sism_id=uuid4(),
            recent_journal_entries=["I can't go on"]
        )

        result = sst.analyze_safety(sst_input)

        if result.risk_indicators:
            assert len(result.primary_concerns) > 0
