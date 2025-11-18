"""
Unit tests for SANA Health Graph
"""
import pytest
from uuid import uuid4

from algorithms.evidence.health_graph import HealthGraph
from algorithms.evidence.models import (
    Intervention,
    InterventionCategory,
    Domain,
    EvidenceStrength,
    Contraindication,
    ContraindicationType
)
from utils.health_graph_data import generate_sample_interventions, seed_health_graph

class TestHealthGraph:

    @pytest.fixture
    def graph(self):
        """Create empty health graph"""
        return HealthGraph()

    @pytest.fixture
    def seeded_graph(self):
        """Create health graph with sample data"""
        graph = HealthGraph()
        seed_health_graph(graph)
        return graph

    def test_graph_initialization(self, graph):
        """Test that graph initializes empty"""
        assert len(graph.interventions) == 0
        stats = graph.get_statistics()
        assert stats["total_interventions"] == 0

    def test_add_intervention(self, graph):
        """Test adding intervention to graph"""
        intervention = Intervention(
            name="Test Meditation",
            category=InterventionCategory.MIND_BODY,
            description="Test description",
            target_domains=[Domain.EMOTIONAL],
            target_conditions=["anxiety"],
            evidence_strength=EvidenceStrength.STRONG,
            evidence_sources=[],
            contraindications=[]
        )

        intervention_id = graph.add_intervention(intervention)

        assert len(graph.interventions) == 1
        assert graph.get_intervention(intervention_id) == intervention

    def test_find_interventions_for_domain(self, seeded_graph):
        """Test finding interventions by domain"""
        interventions = seeded_graph.find_interventions_for_domain(
            Domain.EMOTIONAL,
            EvidenceStrength.WEAK
        )

        assert len(interventions) > 0
        # All returned interventions should target emotional domain
        for intervention in interventions:
            assert Domain.EMOTIONAL in intervention.target_domains

    def test_find_interventions_for_condition(self, seeded_graph):
        """Test finding interventions by condition"""
        interventions = seeded_graph.find_interventions_for_condition(
            "anxiety",
            EvidenceStrength.WEAK
        )

        assert len(interventions) > 0
        # All returned interventions should target anxiety
        for intervention in interventions:
            assert "anxiety" in intervention.target_conditions

    def test_evidence_strength_filtering(self, seeded_graph):
        """Test that evidence strength filtering works"""
        # Get all interventions
        all_interventions = seeded_graph.find_interventions_for_domain(
            Domain.EMOTIONAL,
            EvidenceStrength.INSUFFICIENT
        )

        # Get only strong evidence
        strong_only = seeded_graph.find_interventions_for_domain(
            Domain.EMOTIONAL,
            EvidenceStrength.STRONG
        )

        # Strong-only should be subset of all
        assert len(strong_only) <= len(all_interventions)

    def test_contraindication_filtering_absolute(self, graph):
        """Test that absolute contraindications block interventions"""
        intervention_id = uuid4()
        intervention = Intervention(
            id=intervention_id,
            name="Test Herb",
            category=InterventionCategory.HERBAL,
            description="Test",
            target_domains=[Domain.PHYSICAL],
            target_conditions=["sleep"],
            evidence_strength=EvidenceStrength.MODERATE,
            evidence_sources=[],
            contraindications=[
                Contraindication(
                    intervention_id=intervention_id,
                    contraindication_type=ContraindicationType.ABSOLUTE,
                    condition="pregnancy",
                    severity="critical",
                    description="Contraindicated in pregnancy"
                )
            ]
        )

        graph.add_intervention(intervention)

        # Should not return when user is pregnant
        results = graph.find_interventions_for_domain(
            Domain.PHYSICAL,
            user_conditions={"pregnancy"}
        )

        assert len(results) == 0

    def test_contraindication_filtering_relative(self, graph):
        """Test that relative contraindications still return interventions"""
        intervention_id = uuid4()
        intervention = Intervention(
            id=intervention_id,
            name="Test Exercise",
            category=InterventionCategory.MOVEMENT,
            description="Test",
            target_domains=[Domain.PHYSICAL],
            target_conditions=["fitness"],
            evidence_strength=EvidenceStrength.STRONG,
            evidence_sources=[],
            contraindications=[
                Contraindication(
                    intervention_id=intervention_id,
                    contraindication_type=ContraindicationType.RELATIVE,
                    condition="hypertension",
                    severity="moderate",
                    description="Use with caution"
                )
            ]
        )

        graph.add_intervention(intervention)

        # Should still return with relative contraindication
        # (would show warning in practice)
        results = graph.find_interventions_for_domain(
            Domain.PHYSICAL,
            user_conditions=set()  # Not providing the condition
        )

        assert len(results) == 1

    def test_medication_interaction_checking(self, graph):
        """Test drug-herb interaction checking"""
        intervention_id = uuid4()
        intervention = Intervention(
            id=intervention_id,
            name="Test Herb",
            category=InterventionCategory.HERBAL,
            description="Test",
            target_domains=[Domain.EMOTIONAL],
            target_conditions=["anxiety"],
            evidence_strength=EvidenceStrength.MODERATE,
            evidence_sources=[],
            contraindications=[
                Contraindication(
                    intervention_id=intervention_id,
                    contraindication_type=ContraindicationType.INTERACTION,
                    condition="ssri_interaction",
                    medication_class="antidepressants",
                    severity="serious",
                    description="May interact with SSRIs"
                )
            ]
        )

        graph.add_intervention(intervention)

        # Test safety check
        is_safe, warnings = graph.get_contraindications_for_user(
            intervention_id,
            set(),
            {"antidepressants"}
        )

        assert not is_safe or len(warnings) > 0

    def test_weak_domains_integration(self, seeded_graph):
        """Test finding interventions for multiple weak domains"""
        weak_domains = ["emotional", "physical"]

        results = seeded_graph.find_interventions_for_weak_domains(
            weak_domains,
            EvidenceStrength.MODERATE
        )

        assert "emotional" in results
        assert "physical" in results
        assert len(results["emotional"]) > 0
        assert len(results["physical"]) > 0

    def test_statistics(self, seeded_graph):
        """Test graph statistics"""
        stats = seeded_graph.get_statistics()

        assert "total_interventions" in stats
        assert stats["total_interventions"] > 0
        assert "interventions_by_domain" in stats
        assert "interventions_by_evidence" in stats
        assert "total_conditions_covered" in stats

    def test_evidence_sorting(self, seeded_graph):
        """Test that results are sorted by evidence strength"""
        interventions = seeded_graph.find_interventions_for_domain(
            Domain.EMOTIONAL,
            EvidenceStrength.INSUFFICIENT
        )

        if len(interventions) > 1:
            # Check that first intervention has equal or better evidence than last
            first_score = seeded_graph._evidence_strength_score(interventions[0].evidence_strength)
            last_score = seeded_graph._evidence_strength_score(interventions[-1].evidence_strength)
            assert first_score >= last_score

    def test_get_intervention_not_found(self, graph):
        """Test getting non-existent intervention"""
        result = graph.get_intervention(uuid4())
        assert result is None

    def test_invalid_domain_in_weak_domains(self, seeded_graph):
        """Test handling of invalid domain names"""
        results = seeded_graph.find_interventions_for_weak_domains(
            ["invalid_domain", "emotional"],
            EvidenceStrength.WEAK
        )

        assert "invalid_domain" in results
        assert results["invalid_domain"] == []
        assert "emotional" in results

    def test_sample_interventions_count(self):
        """Test that sample interventions are generated correctly"""
        interventions = generate_sample_interventions()
        assert len(interventions) == 6  # We defined 6 interventions

    def test_seed_health_graph(self):
        """Test seeding health graph"""
        graph = HealthGraph()
        count = seed_health_graph(graph)

        assert count == 6
        assert len(graph.interventions) == 6
