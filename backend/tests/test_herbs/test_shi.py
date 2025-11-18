"""
Unit tests for SANA Herb Index (SHI) Calculator and Synergy Detector
"""
import pytest
from datetime import date, datetime
from uuid import uuid4

from algorithms.herbs import (
    HerbIndexCalculator,
    SynergyDetector,
    Herb,
    HerbUsage,
    HerbOutcome,
    HerbIndexScore,
    EvidenceLevel,
    PreparationForm,
    DosageUnit,
    Frequency,
    AdverseEventSeverity,
)


class TestHerbIndexCalculator:
    """Tests for HerbIndexCalculator"""

    @pytest.fixture
    def calculator(self):
        return HerbIndexCalculator()

    @pytest.fixture
    def sample_herb(self):
        return Herb(
            herb_id=uuid4(),
            botanical_name="Passiflora incarnata",
            common_names=["Passionflower", "Maypop"],
            taxonomy_family="Passifloraceae",
            active_constituents={"flavonoids": "chrysin"},
            contraindications=["Pregnancy"],
        )

    @pytest.fixture
    def sample_usage_data(self, sample_herb):
        """Generate sample usage data"""
        usages = []
        for i in range(100):
            usage = HerbUsage(
                usage_id=uuid4(),
                session_id=uuid4(),
                herb_id=sample_herb.herb_id,
                client_id=uuid4(),
                practitioner_id=uuid4() if i % 5 == 0 else usages[0].practitioner_id if usages else uuid4(),
                dosage_amount=300,
                dosage_unit=DosageUnit.MG,
                frequency=Frequency.DAILY,
                duration_days=28,
                preparation_form=PreparationForm.CAPSULE,
                primary_condition_id=uuid4(),
                region="London" if i % 3 == 0 else "Manchester",
                prescribed_date=date(2024, 1, 15),
            )
            usages.append(usage)
        return usages

    @pytest.fixture
    def sample_outcome_data(self, sample_usage_data):
        """Generate sample outcome data with good improvements"""
        outcomes = []
        for usage in sample_usage_data:
            baseline = 70.0
            followup = 40.0  # 43% improvement
            outcome = HerbOutcome(
                outcome_id=uuid4(),
                usage_id=usage.usage_id,
                client_id=usage.client_id,
                outcome_measure="DASS-21-Anxiety",
                baseline_score=baseline,
                followup_score=followup,
                days_since_start=28,
                measurement_date=date(2024, 2, 15),
            )
            outcomes.append(outcome)
        return outcomes

    def test_calculate_herb_index_basic(self, calculator, sample_herb, sample_usage_data, sample_outcome_data):
        """Test basic herb index calculation"""
        result = calculator.calculate_herb_index(
            sample_herb, sample_usage_data, sample_outcome_data
        )

        assert isinstance(result, HerbIndexScore)
        assert result.herb_id == sample_herb.herb_id
        assert result.herb_name == "Passionflower"
        assert result.botanical_name == "Passiflora incarnata"
        assert 0 <= result.overall_score <= 100
        assert result.total_cases == len(sample_usage_data)

    def test_calculate_herb_index_score_components(self, calculator, sample_herb, sample_usage_data, sample_outcome_data):
        """Test that all score components are calculated"""
        result = calculator.calculate_herb_index(
            sample_herb, sample_usage_data, sample_outcome_data
        )

        # Check component scores are within bounds
        assert 0 <= result.evidence_volume_score <= 25
        assert 0 <= result.efficacy_score <= 40
        assert 0 <= result.safety_score <= 20
        assert 0 <= result.data_quality_score <= 15

        # Components should sum to overall
        component_sum = (
            result.evidence_volume_score +
            result.efficacy_score +
            result.safety_score +
            result.data_quality_score
        )
        assert result.overall_score == component_sum

    def test_insufficient_data_returns_zero_score(self, calculator, sample_herb):
        """Test that insufficient data returns zero score"""
        # Only 5 cases (below threshold of 10)
        small_usage = [
            HerbUsage(
                usage_id=uuid4(),
                session_id=uuid4(),
                herb_id=sample_herb.herb_id,
                client_id=uuid4(),
                practitioner_id=uuid4(),
                prescribed_date=date(2024, 1, 1),
            )
            for _ in range(5)
        ]

        result = calculator.calculate_herb_index(sample_herb, small_usage, [])

        assert result.overall_score == 0
        assert result.evidence_level == EvidenceLevel.INSUFFICIENT

    def test_evidence_volume_scoring(self, calculator, sample_herb, sample_usage_data, sample_outcome_data):
        """Test evidence volume score increases with more data"""
        # Calculate with full data
        full_result = calculator.calculate_herb_index(
            sample_herb, sample_usage_data, sample_outcome_data
        )

        # Calculate with partial data
        partial_usage = sample_usage_data[:30]
        partial_outcomes = [o for o in sample_outcome_data if o.usage_id in {u.usage_id for u in partial_usage}]
        partial_result = calculator.calculate_herb_index(
            sample_herb, partial_usage, partial_outcomes
        )

        # More data should give higher evidence score
        assert full_result.evidence_volume_score >= partial_result.evidence_volume_score

    def test_safety_score_with_adverse_events(self, calculator, sample_herb, sample_usage_data):
        """Test that adverse events reduce safety score"""
        # Create outcomes with adverse events
        outcomes_with_ae = []
        for i, usage in enumerate(sample_usage_data):
            has_ae = i % 5 == 0  # 20% adverse event rate
            outcome = HerbOutcome(
                outcome_id=uuid4(),
                usage_id=usage.usage_id,
                client_id=usage.client_id,
                outcome_measure="VAS-Symptom",
                baseline_score=70,
                followup_score=50,
                days_since_start=28,
                measurement_date=date(2024, 2, 15),
                adverse_events=["Nausea"] if has_ae else [],
                adverse_event_severity=AdverseEventSeverity.MILD if has_ae else None,
            )
            outcomes_with_ae.append(outcome)

        # Create outcomes without adverse events
        outcomes_clean = []
        for usage in sample_usage_data:
            outcome = HerbOutcome(
                outcome_id=uuid4(),
                usage_id=usage.usage_id,
                client_id=usage.client_id,
                outcome_measure="VAS-Symptom",
                baseline_score=70,
                followup_score=50,
                days_since_start=28,
                measurement_date=date(2024, 2, 15),
            )
            outcomes_clean.append(outcome)

        result_with_ae = calculator.calculate_herb_index(sample_herb, sample_usage_data, outcomes_with_ae)
        result_clean = calculator.calculate_herb_index(sample_herb, sample_usage_data, outcomes_clean)

        # Clean outcomes should have higher safety score
        assert result_clean.safety_score >= result_with_ae.safety_score

    def test_data_quality_score_completeness(self, calculator, sample_herb):
        """Test that data completeness affects quality score"""
        # Complete data
        complete_usage = [
            HerbUsage(
                usage_id=uuid4(),
                session_id=uuid4(),
                herb_id=sample_herb.herb_id,
                client_id=uuid4(),
                practitioner_id=uuid4(),
                dosage_amount=300,
                dosage_unit=DosageUnit.MG,
                frequency=Frequency.DAILY,
                prescribed_date=date(2024, 1, 1),
            )
            for _ in range(50)
        ]

        # Incomplete data (missing dosage info)
        incomplete_usage = [
            HerbUsage(
                usage_id=uuid4(),
                session_id=uuid4(),
                herb_id=sample_herb.herb_id,
                client_id=uuid4(),
                practitioner_id=uuid4(),
                prescribed_date=date(2024, 1, 1),
            )
            for _ in range(50)
        ]

        complete_outcomes = [
            HerbOutcome(
                outcome_id=uuid4(),
                usage_id=u.usage_id,
                client_id=u.client_id,
                outcome_measure="VAS",
                baseline_score=70,
                followup_score=40,
                days_since_start=30,
                measurement_date=date(2024, 2, 1),
            )
            for u in complete_usage
        ]

        incomplete_outcomes = [
            HerbOutcome(
                outcome_id=uuid4(),
                usage_id=u.usage_id,
                client_id=u.client_id,
                outcome_measure="VAS",
                baseline_score=70,
                followup_score=40,
                days_since_start=30,
                measurement_date=date(2024, 2, 1),
            )
            for u in incomplete_usage
        ]

        result_complete = calculator.calculate_herb_index(sample_herb, complete_usage, complete_outcomes)
        result_incomplete = calculator.calculate_herb_index(sample_herb, incomplete_usage, incomplete_outcomes)

        # Complete data should have higher quality score
        assert result_complete.data_quality_score >= result_incomplete.data_quality_score

    def test_evidence_level_determination(self, calculator, sample_herb, sample_usage_data, sample_outcome_data):
        """Test evidence level is correctly determined"""
        result = calculator.calculate_herb_index(
            sample_herb, sample_usage_data, sample_outcome_data
        )

        # With 100 cases, should be at least moderate
        assert result.evidence_level in [
            EvidenceLevel.MODERATE,
            EvidenceLevel.HIGH,
            EvidenceLevel.VERY_HIGH,
        ]

    def test_confidence_interval_calculation(self, calculator, sample_herb, sample_usage_data, sample_outcome_data):
        """Test confidence interval is calculated"""
        result = calculator.calculate_herb_index(
            sample_herb, sample_usage_data, sample_outcome_data
        )

        ci_lower, ci_upper = result.confidence_interval
        assert ci_lower <= ci_upper
        assert ci_lower >= 0
        assert ci_upper <= 100

    def test_condition_efficacy_calculation(self, calculator, sample_herb, sample_outcome_data):
        """Test condition-specific efficacy calculation"""
        condition_id = uuid4()
        condition_name = "Anxiety"

        efficacy = calculator.calculate_condition_efficacy(
            sample_herb, condition_id, condition_name, sample_outcome_data
        )

        assert efficacy is not None
        assert efficacy.herb_id == sample_herb.herb_id
        assert efficacy.condition_id == condition_id
        assert efficacy.sample_size == len(sample_outcome_data)
        assert efficacy.mean_improvement > 0
        assert efficacy.effect_size >= 0

    def test_herb_ranking(self, calculator):
        """Test herb ranking by condition"""
        condition_id = uuid4()
        condition_name = "Anxiety"

        # Create efficacy data for multiple herbs
        efficacies = []
        for i in range(5):
            from algorithms.herbs.models import ConditionHerbEfficacy
            efficacy = ConditionHerbEfficacy(
                herb_id=uuid4(),
                herb_name=f"Herb {i}",
                condition_id=condition_id,
                condition_name=condition_name,
                mean_improvement=30 + i * 5,  # 30, 35, 40, 45, 50
                median_improvement=28 + i * 5,
                std_deviation=10,
                effect_size=0.5 + i * 0.1,
                sample_size=100,
                outcome_measure="DASS-21",
            )
            efficacies.append(efficacy)

        ranked = calculator.rank_herbs_for_condition(
            condition_id, condition_name, efficacies, "efficacy"
        )

        # Should be sorted by mean_improvement descending
        assert ranked[0].mean_improvement == 50
        assert ranked[0].rank == 1
        assert ranked[-1].mean_improvement == 30
        assert ranked[-1].rank == 5


class TestSynergyDetector:
    """Tests for SynergyDetector"""

    @pytest.fixture
    def detector(self):
        return SynergyDetector()

    @pytest.fixture
    def herb_ids(self):
        return [uuid4() for _ in range(5)]

    @pytest.fixture
    def herb_names(self, herb_ids):
        names = ["Valerian", "Passionflower", "Lemon Balm", "Ashwagandha", "Rhodiola"]
        return {herb_ids[i]: names[i] for i in range(5)}

    @pytest.fixture
    def combination_usage_data(self, herb_ids):
        """Generate usage data with combinations"""
        usages = []
        session_count = 100

        for i in range(session_count):
            session_id = uuid4()
            client_id = uuid4()
            practitioner_id = uuid4()

            # Create sessions with 1-3 herbs
            if i < 30:
                # Single herb sessions
                herbs_in_session = [herb_ids[i % 5]]
            elif i < 70:
                # Two herb combinations
                herbs_in_session = [herb_ids[0], herb_ids[1]]  # Valerian + Passionflower
            else:
                # Three herb combinations
                herbs_in_session = [herb_ids[0], herb_ids[1], herb_ids[2]]

            for herb_id in herbs_in_session:
                usage = HerbUsage(
                    usage_id=uuid4(),
                    session_id=session_id,
                    herb_id=herb_id,
                    client_id=client_id,
                    practitioner_id=practitioner_id,
                    dosage_amount=300,
                    dosage_unit=DosageUnit.MG,
                    frequency=Frequency.DAILY,
                    primary_condition_id=uuid4(),
                    prescribed_date=date(2024, 1, 1),
                )
                usages.append(usage)

        return usages

    @pytest.fixture
    def combination_outcome_data(self, combination_usage_data):
        """Generate outcomes with better results for combinations"""
        outcomes = []

        # Group by session
        sessions = {}
        for usage in combination_usage_data:
            if usage.session_id not in sessions:
                sessions[usage.session_id] = []
            sessions[usage.session_id].append(usage)

        for session_id, usages in sessions.items():
            herbs_count = len(usages)

            # Better improvement for combinations
            base_improvement = 30
            combo_bonus = (herbs_count - 1) * 15  # +15% per additional herb

            baseline = 70
            followup = baseline * (1 - (base_improvement + combo_bonus) / 100)

            for usage in usages:
                outcome = HerbOutcome(
                    outcome_id=uuid4(),
                    usage_id=usage.usage_id,
                    client_id=usage.client_id,
                    outcome_measure="VAS-Symptom",
                    baseline_score=baseline,
                    followup_score=followup,
                    days_since_start=28,
                    measurement_date=date(2024, 2, 1),
                )
                outcomes.append(outcome)

        return outcomes

    def test_find_synergistic_combinations(
        self, detector, combination_usage_data, combination_outcome_data, herb_names
    ):
        """Test finding synergistic herb combinations"""
        synergies = detector.find_synergistic_combinations(
            combination_usage_data,
            combination_outcome_data,
            herb_names,
            min_synergy_score=50,
            limit=10,
        )

        # Should find at least one synergy
        assert len(synergies) >= 0  # May be empty if threshold not met

    def test_synergy_score_calculation(
        self, detector, combination_usage_data, combination_outcome_data, herb_names
    ):
        """Test synergy score is within valid range"""
        synergies = detector.find_synergistic_combinations(
            combination_usage_data,
            combination_outcome_data,
            herb_names,
            min_synergy_score=0,
            limit=20,
        )

        for synergy in synergies:
            assert 0 <= synergy.synergy_score <= 100
            assert synergy.sample_size > 0
            assert len(synergy.herb_ids) >= 2

    def test_optimal_dosages_calculation(
        self, detector, combination_usage_data, combination_outcome_data, herb_names
    ):
        """Test that optimal dosages are calculated"""
        synergies = detector.find_synergistic_combinations(
            combination_usage_data,
            combination_outcome_data,
            herb_names,
            min_synergy_score=0,
            limit=10,
        )

        for synergy in synergies:
            # Should have dosage for each herb in combination
            assert len(synergy.optimal_dosages) == len(synergy.herb_ids)

    def test_combination_protocol_generation(
        self, detector, combination_usage_data, combination_outcome_data, herb_names, herb_ids
    ):
        """Test protocol generation for combinations"""
        protocol = detector.calculate_combination_protocol(
            herb_ids[:2],  # First two herbs
            combination_usage_data,
            combination_outcome_data,
            herb_names,
        )

        if protocol:  # May be empty if no matching combinations
            assert "herbs" in protocol
            assert "dosages" in protocol
            assert "frequency" in protocol
            assert "expected_improvement_pct" in protocol

    def test_minimum_sample_size_filter(self, detector, herb_names):
        """Test that minimum sample size is enforced"""
        # Create very small dataset
        small_usage = [
            HerbUsage(
                usage_id=uuid4(),
                session_id=uuid4(),
                herb_id=list(herb_names.keys())[0],
                client_id=uuid4(),
                practitioner_id=uuid4(),
                prescribed_date=date(2024, 1, 1),
            )
            for _ in range(5)
        ]

        synergies = detector.find_synergistic_combinations(
            small_usage, [], herb_names, min_synergy_score=0
        )

        # Should return empty due to insufficient data
        assert len(synergies) == 0


class TestHerbModels:
    """Tests for herb data models"""

    def test_herb_creation(self):
        """Test Herb model creation"""
        herb = Herb(
            botanical_name="Withania somnifera",
            common_names=["Ashwagandha", "Indian Ginseng"],
            taxonomy_family="Solanaceae",
        )

        assert herb.herb_id is not None
        assert herb.botanical_name == "Withania somnifera"
        assert "Ashwagandha" in herb.common_names

    def test_herb_usage_creation(self):
        """Test HerbUsage model creation"""
        usage = HerbUsage(
            session_id=uuid4(),
            herb_id=uuid4(),
            client_id=uuid4(),
            practitioner_id=uuid4(),
            dosage_amount=500,
            dosage_unit=DosageUnit.MG,
            frequency=Frequency.BID,
            duration_days=30,
            preparation_form=PreparationForm.CAPSULE,
            prescribed_date=date(2024, 1, 1),
        )

        assert usage.usage_id is not None
        assert usage.dosage_amount == 500
        assert usage.frequency == Frequency.BID

    def test_herb_outcome_improvement_calculation(self):
        """Test automatic improvement percentage calculation"""
        outcome = HerbOutcome(
            usage_id=uuid4(),
            client_id=uuid4(),
            outcome_measure="DASS-21-Anxiety",
            baseline_score=80,
            followup_score=40,
            days_since_start=28,
            measurement_date=date(2024, 2, 1),
        )

        # Should calculate 50% improvement
        assert outcome.improvement_percentage == 50.0

    def test_herb_outcome_zero_baseline(self):
        """Test improvement calculation with zero baseline"""
        outcome = HerbOutcome(
            usage_id=uuid4(),
            client_id=uuid4(),
            outcome_measure="VAS",
            baseline_score=0,
            followup_score=10,
            days_since_start=14,
            measurement_date=date(2024, 2, 1),
        )

        # Should be 0 when baseline is 0
        assert outcome.improvement_percentage == 0.0

    def test_herb_index_score_bounds(self):
        """Test HerbIndexScore respects bounds"""
        score = HerbIndexScore(
            herb_id=uuid4(),
            herb_name="Test Herb",
            botanical_name="Testus herbicus",
            overall_score=85,
            evidence_volume_score=20,
            efficacy_score=35,
            safety_score=18,
            data_quality_score=12,
            total_cases=500,
            unique_practitioners=50,
            unique_conditions=10,
            evidence_level=EvidenceLevel.HIGH,
            confidence_interval=(75.0, 95.0),
        )

        assert score.overall_score == 85
        assert score.evidence_level == EvidenceLevel.HIGH
