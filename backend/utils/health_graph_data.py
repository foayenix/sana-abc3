"""
Sample data generator for SANA Health Graph
Contains evidence-based CAM interventions with real research backing
"""
from uuid import uuid4
from typing import List

from algorithms.evidence.models import (
    Intervention,
    InterventionCategory,
    Domain,
    EvidenceStrength,
    EvidenceSource,
    Contraindication,
    ContraindicationType,
    DosageProtocol,
    ExpectedOutcome
)

def generate_sample_interventions() -> List[Intervention]:
    """
    Generate sample interventions with realistic evidence-based data

    Note: This is sample data for testing. Production would use
    a comprehensive database of peer-reviewed interventions.
    """
    interventions = []

    # 1. Meditation for Emotional Health
    meditation_id = uuid4()
    interventions.append(Intervention(
        id=meditation_id,
        name="Mindfulness Meditation",
        category=InterventionCategory.MIND_BODY,
        description="Systematic practice of focused attention and present-moment awareness",
        target_domains=[Domain.EMOTIONAL, Domain.COGNITIVE],
        target_conditions=["anxiety", "stress", "depression", "focus_issues"],
        evidence_strength=EvidenceStrength.STRONG,
        evidence_sources=[
            EvidenceSource(
                source_type="Cochrane",
                citation="Goyal et al. (2014). Meditation programs for psychological stress and well-being",
                year=2014,
                url="https://www.cochrane.org/CD004464",
                summary="Moderate evidence for reducing anxiety, depression, and pain"
            ),
            EvidenceSource(
                source_type="NCCIH",
                citation="NCCIH Evidence Map: Meditation",
                year=2022,
                summary="Strong evidence for stress reduction and emotional regulation"
            )
        ],
        contraindications=[
            Contraindication(
                intervention_id=meditation_id,
                contraindication_type=ContraindicationType.RELATIVE,
                condition="severe_psychosis",
                severity="serious",
                description="May exacerbate symptoms in acute psychotic episodes. Consult mental health professional."
            )
        ],
        dosage_protocols=[
            DosageProtocol(
                intervention_id=meditation_id,
                min_dose=10,
                max_dose=30,
                dose_unit="minutes",
                frequency_per_day=1,
                min_duration_weeks=8,
                max_duration_weeks=52,
                instructions="Daily practice, preferably same time each day. Start with 10 minutes."
            )
        ],
        expected_outcomes=[
            ExpectedOutcome(
                intervention_id=meditation_id,
                condition="anxiety",
                typical_timeline_weeks=8,
                outcome_description="Significant reduction in anxiety symptoms",
                success_rate_percentage=65.0
            ),
            ExpectedOutcome(
                intervention_id=meditation_id,
                condition="stress",
                typical_timeline_weeks=4,
                outcome_description="Improved stress management and emotional regulation",
                success_rate_percentage=70.0
            )
        ],
        typical_duration_minutes=20,
        cost_estimate_min=0.0,
        cost_estimate_max=30.0,
        requires_practitioner=False
    ))

    # 2. Ashwagandha for Stress and Sleep
    ashwagandha_id = uuid4()
    interventions.append(Intervention(
        id=ashwagandha_id,
        name="Ashwagandha (Withania somnifera)",
        category=InterventionCategory.HERBAL,
        description="Adaptogenic herb used for stress reduction and sleep improvement",
        target_domains=[Domain.PHYSICAL, Domain.EMOTIONAL],
        target_conditions=["stress", "anxiety", "insomnia", "low_energy"],
        evidence_strength=EvidenceStrength.MODERATE,
        evidence_sources=[
            EvidenceSource(
                source_type="PubMed",
                citation="Chandrasekhar et al. (2012). A prospective study on ashwagandha in stress reduction",
                year=2012,
                summary="Significant reduction in cortisol and stress scores"
            ),
            EvidenceSource(
                source_type="WHO",
                citation="WHO Monographs on Selected Medicinal Plants, Volume 4",
                year=2009,
                summary="Traditional use supported by moderate clinical evidence"
            )
        ],
        contraindications=[
            Contraindication(
                intervention_id=ashwagandha_id,
                contraindication_type=ContraindicationType.ABSOLUTE,
                condition="pregnancy",
                severity="critical",
                description="Contraindicated in pregnancy - may induce miscarriage"
            ),
            Contraindication(
                intervention_id=ashwagandha_id,
                contraindication_type=ContraindicationType.INTERACTION,
                condition="thyroid_medication",
                medication_class="thyroid_hormones",
                severity="moderate",
                description="May enhance thyroid hormone effects. Monitor thyroid levels."
            ),
            Contraindication(
                intervention_id=ashwagandha_id,
                contraindication_type=ContraindicationType.INTERACTION,
                condition="sedative_medications",
                medication_class="benzodiazepines",
                severity="moderate",
                description="May enhance sedative effects. Use caution."
            )
        ],
        dosage_protocols=[
            DosageProtocol(
                intervention_id=ashwagandha_id,
                min_dose=300,
                max_dose=600,
                dose_unit="mg",
                frequency_per_day=2,
                min_duration_weeks=8,
                max_duration_weeks=12,
                instructions="Take with food. Standardized extract (5% withanolides)."
            )
        ],
        expected_outcomes=[
            ExpectedOutcome(
                intervention_id=ashwagandha_id,
                condition="stress",
                typical_timeline_weeks=8,
                outcome_description="Reduced cortisol levels and perceived stress",
                success_rate_percentage=60.0
            ),
            ExpectedOutcome(
                intervention_id=ashwagandha_id,
                condition="insomnia",
                typical_timeline_weeks=6,
                outcome_description="Improved sleep quality and duration",
                success_rate_percentage=55.0
            )
        ],
        typical_duration_minutes=None,
        cost_estimate_min=15.0,
        cost_estimate_max=40.0,
        requires_practitioner=False
    ))

    # 3. Yoga for Physical and Emotional Health
    yoga_id = uuid4()
    interventions.append(Intervention(
        id=yoga_id,
        name="Hatha Yoga",
        category=InterventionCategory.MOVEMENT,
        description="Physical postures, breathing exercises, and meditation",
        target_domains=[Domain.PHYSICAL, Domain.EMOTIONAL, Domain.SPIRITUAL],
        target_conditions=["anxiety", "stress", "low_energy", "pain", "flexibility"],
        evidence_strength=EvidenceStrength.STRONG,
        evidence_sources=[
            EvidenceSource(
                source_type="Cochrane",
                citation="Cramer et al. (2013). Yoga for depression",
                year=2013,
                summary="Moderate evidence for reducing depression symptoms"
            ),
            EvidenceSource(
                source_type="NCCIH",
                citation="NCCIH: Yoga for Health",
                year=2021,
                summary="Strong evidence for chronic pain, anxiety, and stress"
            )
        ],
        contraindications=[
            Contraindication(
                intervention_id=yoga_id,
                contraindication_type=ContraindicationType.RELATIVE,
                condition="severe_osteoporosis",
                severity="moderate",
                description="Avoid inversions and deep forward bends. Modify poses."
            ),
            Contraindication(
                intervention_id=yoga_id,
                contraindication_type=ContraindicationType.RELATIVE,
                condition="uncontrolled_hypertension",
                severity="moderate",
                description="Avoid inversions until blood pressure is controlled."
            )
        ],
        dosage_protocols=[
            DosageProtocol(
                intervention_id=yoga_id,
                min_dose=30,
                max_dose=90,
                dose_unit="minutes",
                frequency_per_week=3,
                min_duration_weeks=8,
                max_duration_weeks=52,
                instructions="Start with beginner classes. Practice 3-5x per week for best results."
            )
        ],
        expected_outcomes=[
            ExpectedOutcome(
                intervention_id=yoga_id,
                condition="anxiety",
                typical_timeline_weeks=8,
                outcome_description="Reduced anxiety symptoms and improved mood",
                success_rate_percentage=68.0
            ),
            ExpectedOutcome(
                intervention_id=yoga_id,
                condition="pain",
                typical_timeline_weeks=12,
                outcome_description="Reduced chronic pain intensity",
                success_rate_percentage=55.0
            )
        ],
        typical_duration_minutes=60,
        cost_estimate_min=15.0,
        cost_estimate_max=30.0,
        requires_practitioner=False
    ))

    # 4. Acupuncture for Pain
    acupuncture_id = uuid4()
    interventions.append(Intervention(
        id=acupuncture_id,
        name="Acupuncture",
        category=InterventionCategory.ENERGY_WORK,
        description="Traditional Chinese medicine technique using fine needles at specific points",
        target_domains=[Domain.PHYSICAL],
        target_conditions=["pain", "headache", "back_pain", "nausea"],
        evidence_strength=EvidenceStrength.MODERATE,
        evidence_sources=[
            EvidenceSource(
                source_type="Cochrane",
                citation="Vickers et al. (2018). Acupuncture for chronic pain",
                year=2018,
                summary="Moderate evidence for chronic pain conditions"
            ),
            EvidenceSource(
                source_type="WHO",
                citation="WHO Guidelines on Acupuncture",
                year=2002,
                summary="Effective for various pain conditions and nausea"
            )
        ],
        contraindications=[
            Contraindication(
                intervention_id=acupuncture_id,
                contraindication_type=ContraindicationType.ABSOLUTE,
                condition="bleeding_disorders",
                severity="critical",
                description="Contraindicated with clotting disorders or anticoagulant therapy"
            ),
            Contraindication(
                intervention_id=acupuncture_id,
                contraindication_type=ContraindicationType.RELATIVE,
                condition="pregnancy",
                severity="moderate",
                description="Certain points contraindicated in pregnancy. Use certified practitioner."
            )
        ],
        dosage_protocols=[
            DosageProtocol(
                intervention_id=acupuncture_id,
                min_dose=1,
                max_dose=2,
                dose_unit="sessions",
                frequency_per_week=2,
                min_duration_weeks=4,
                max_duration_weeks=12,
                instructions="Initial series of 6-12 sessions, then maintenance as needed."
            )
        ],
        expected_outcomes=[
            ExpectedOutcome(
                intervention_id=acupuncture_id,
                condition="chronic_pain",
                typical_timeline_weeks=6,
                outcome_description="Significant pain reduction",
                success_rate_percentage=50.0
            )
        ],
        typical_duration_minutes=60,
        cost_estimate_min=60.0,
        cost_estimate_max=120.0,
        requires_practitioner=True
    ))

    # 5. Omega-3 for Cognitive Health
    omega3_id = uuid4()
    interventions.append(Intervention(
        id=omega3_id,
        name="Omega-3 Fatty Acids (EPA/DHA)",
        category=InterventionCategory.NUTRITION,
        description="Essential fatty acids from fish oil or algae",
        target_domains=[Domain.COGNITIVE, Domain.EMOTIONAL],
        target_conditions=["depression", "cognitive_decline", "memory_issues"],
        evidence_strength=EvidenceStrength.MODERATE,
        evidence_sources=[
            EvidenceSource(
                source_type="Cochrane",
                citation="Appleton et al. (2016). Omega-3 for depression in adults",
                year=2016,
                summary="Small benefit for depression, especially EPA-rich formulations"
            ),
            EvidenceSource(
                source_type="NCCIH",
                citation="NCCIH: Omega-3 Supplements",
                year=2020,
                summary="Moderate evidence for cardiovascular and mental health"
            )
        ],
        contraindications=[
            Contraindication(
                intervention_id=omega3_id,
                contraindication_type=ContraindicationType.INTERACTION,
                condition="blood_thinners",
                medication_class="anticoagulants",
                severity="moderate",
                description="High doses may increase bleeding risk. Consult physician."
            )
        ],
        dosage_protocols=[
            DosageProtocol(
                intervention_id=omega3_id,
                min_dose=1000,
                max_dose=2000,
                dose_unit="mg",
                frequency_per_day=1,
                min_duration_weeks=8,
                max_duration_weeks=52,
                instructions="Take with meals. Look for EPA:DHA ratio of 2:1 for mood support."
            )
        ],
        expected_outcomes=[
            ExpectedOutcome(
                intervention_id=omega3_id,
                condition="depression",
                typical_timeline_weeks=12,
                outcome_description="Modest improvement in depressive symptoms",
                success_rate_percentage=45.0
            )
        ],
        typical_duration_minutes=None,
        cost_estimate_min=15.0,
        cost_estimate_max=35.0,
        requires_practitioner=False
    ))

    # 6. Cognitive Behavioral Therapy (CBT) techniques
    cbt_id = uuid4()
    interventions.append(Intervention(
        id=cbt_id,
        name="Cognitive Behavioral Therapy (CBT)",
        category=InterventionCategory.MIND_BODY,
        description="Evidence-based psychotherapy focusing on thought patterns and behaviors",
        target_domains=[Domain.EMOTIONAL, Domain.COGNITIVE],
        target_conditions=["anxiety", "depression", "insomnia", "stress"],
        evidence_strength=EvidenceStrength.STRONG,
        evidence_sources=[
            EvidenceSource(
                source_type="Cochrane",
                citation="James et al. (2015). CBT for anxiety disorders",
                year=2015,
                summary="Strong evidence as first-line treatment for anxiety"
            )
        ],
        contraindications=[],
        dosage_protocols=[
            DosageProtocol(
                intervention_id=cbt_id,
                min_dose=45,
                max_dose=60,
                dose_unit="minutes",
                frequency_per_week=1,
                min_duration_weeks=12,
                max_duration_weeks=20,
                instructions="Weekly sessions with licensed therapist, plus homework exercises"
            )
        ],
        expected_outcomes=[
            ExpectedOutcome(
                intervention_id=cbt_id,
                condition="anxiety",
                typical_timeline_weeks=12,
                outcome_description="Significant reduction in anxiety symptoms",
                success_rate_percentage=75.0
            )
        ],
        typical_duration_minutes=60,
        cost_estimate_min=80.0,
        cost_estimate_max=200.0,
        requires_practitioner=True
    ))

    return interventions

def seed_health_graph(graph):
    """
    Seed a HealthGraph instance with sample interventions

    Args:
        graph: HealthGraph instance to populate
    """
    interventions = generate_sample_interventions()
    for intervention in interventions:
        graph.add_intervention(intervention)

    return len(interventions)
