"""
API routes for SANA Herbs & Treatments Index

Endpoints for herb search, rankings, comparisons, and synergy detection.
"""
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query

from algorithms.herbs import (
    HerbIndexCalculator,
    SynergyDetector,
    Herb,
    HerbUsage,
    HerbOutcome,
    HerbIndexScore,
    ConditionHerbEfficacy,
    HerbCombination,
    EvidenceLevel,
    PreparationForm,
    DosageUnit,
    Frequency,
    AdverseEventSeverity,
)
from algorithms.herbs.models import (
    HerbSearchResult,
    HerbComparisonResult,
    HerbRankingResult,
    SynergySearchResult,
    HerbDetailResponse,
)

router = APIRouter()

# Initialize algorithms
shi_calculator = HerbIndexCalculator()
synergy_detector = SynergyDetector()


# ============================================================================
# Dummy Data Generation
# ============================================================================

def generate_dummy_herbs() -> List[Herb]:
    """Generate sample herbs database"""
    herbs_data = [
        {
            "botanical_name": "Passiflora incarnata",
            "common_names": ["Passionflower", "Maypop", "Wild Passion Vine"],
            "taxonomy_family": "Passifloraceae",
            "active_constituents": {"flavonoids": "chrysin, vitexin", "alkaloids": "harman, harmine"},
            "contraindications": ["Pregnancy", "MAOIs"],
        },
        {
            "botanical_name": "Withania somnifera",
            "common_names": ["Ashwagandha", "Indian Ginseng", "Winter Cherry"],
            "taxonomy_family": "Solanaceae",
            "active_constituents": {"withanolides": "withaferin A, withanolide D"},
            "contraindications": ["Thyroid disorders", "Autoimmune conditions"],
        },
        {
            "botanical_name": "Melissa officinalis",
            "common_names": ["Lemon Balm", "Melissa", "Bee Balm"],
            "taxonomy_family": "Lamiaceae",
            "active_constituents": {"volatile_oils": "citral, citronellal", "polyphenols": "rosmarinic acid"},
            "contraindications": ["Thyroid medication"],
        },
        {
            "botanical_name": "Valeriana officinalis",
            "common_names": ["Valerian", "Garden Valerian", "All-Heal"],
            "taxonomy_family": "Caprifoliaceae",
            "active_constituents": {"valepotriates": "valtrate", "sesquiterpenes": "valerenic acid"},
            "contraindications": ["Sedatives", "Alcohol"],
        },
        {
            "botanical_name": "Hypericum perforatum",
            "common_names": ["St. John's Wort", "Klamath Weed", "Goatweed"],
            "taxonomy_family": "Hypericaceae",
            "active_constituents": {"naphthodianthrones": "hypericin", "phloroglucinols": "hyperforin"},
            "contraindications": ["SSRIs", "Oral contraceptives", "Immunosuppressants"],
        },
        {
            "botanical_name": "Rhodiola rosea",
            "common_names": ["Rhodiola", "Golden Root", "Arctic Root"],
            "taxonomy_family": "Crassulaceae",
            "active_constituents": {"rosavins": "rosavin, rosarin", "salidroside": "tyrosol"},
            "contraindications": ["Bipolar disorder"],
        },
        {
            "botanical_name": "Ginkgo biloba",
            "common_names": ["Ginkgo", "Maidenhair Tree"],
            "taxonomy_family": "Ginkgoaceae",
            "active_constituents": {"flavonoids": "quercetin, kaempferol", "terpenes": "ginkgolides"},
            "contraindications": ["Anticoagulants", "Seizure disorders"],
        },
        {
            "botanical_name": "Curcuma longa",
            "common_names": ["Turmeric", "Curcuma", "Indian Saffron"],
            "taxonomy_family": "Zingiberaceae",
            "active_constituents": {"curcuminoids": "curcumin, demethoxycurcumin"},
            "contraindications": ["Gallbladder disease", "Anticoagulants"],
        },
    ]

    herbs = []
    for data in herbs_data:
        herb = Herb(
            herb_id=uuid4(),
            botanical_name=data["botanical_name"],
            common_names=data["common_names"],
            taxonomy_family=data["taxonomy_family"],
            active_constituents=data.get("active_constituents"),
            contraindications=data.get("contraindications", []),
        )
        herbs.append(herb)

    return herbs


def generate_dummy_usage_outcomes(
    herbs: List[Herb],
    count: int = 200,
) -> tuple[List[HerbUsage], List[HerbOutcome], dict]:
    """Generate dummy usage and outcome data"""
    import random

    usage_data = []
    outcome_data = []
    herb_names = {h.herb_id: h.common_names[0] for h in herbs}

    conditions = [
        (uuid4(), "Anxiety"),
        (uuid4(), "Insomnia"),
        (uuid4(), "Depression"),
        (uuid4(), "Chronic Pain"),
        (uuid4(), "Fatigue"),
    ]

    regions = ["London", "Manchester", "Birmingham", "Edinburgh", "Cardiff"]

    for _ in range(count):
        herb = random.choice(herbs)
        condition = random.choice(conditions)
        session_id = uuid4()
        client_id = uuid4()
        practitioner_id = uuid4()

        # Create usage
        usage = HerbUsage(
            usage_id=uuid4(),
            session_id=session_id,
            herb_id=herb.herb_id,
            client_id=client_id,
            practitioner_id=practitioner_id,
            dosage_amount=random.choice([100, 200, 300, 400, 500]),
            dosage_unit=DosageUnit.MG,
            frequency=random.choice([Frequency.DAILY, Frequency.BID, Frequency.TID]),
            duration_days=random.randint(14, 90),
            preparation_form=random.choice([PreparationForm.CAPSULE, PreparationForm.TINCTURE, PreparationForm.TEA]),
            primary_condition_id=condition[0],
            region=random.choice(regions),
            prescribed_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
        )
        usage_data.append(usage)

        # Create outcome
        baseline = random.uniform(50, 90)
        # Better herbs get better improvements
        herb_index = herbs.index(herb)
        improvement_factor = 0.6 - (herb_index * 0.05)  # First herbs are "better"
        followup = baseline * (1 - random.uniform(0.2, improvement_factor))

        has_adverse = random.random() < 0.1  # 10% adverse event rate

        outcome = HerbOutcome(
            outcome_id=uuid4(),
            usage_id=usage.usage_id,
            client_id=client_id,
            outcome_measure="DASS-21-Anxiety" if "Anxiety" in condition[1] else "VAS-Symptom",
            baseline_score=baseline,
            followup_score=followup,
            days_since_start=random.randint(14, 56),
            measurement_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
            adverse_events=["Mild nausea"] if has_adverse else [],
            adverse_event_severity=AdverseEventSeverity.MILD if has_adverse else None,
            discontinued=random.random() < 0.05,
        )
        outcome_data.append(outcome)

    return usage_data, outcome_data, herb_names


# Generate cached dummy data
_dummy_herbs = generate_dummy_herbs()
_dummy_usage, _dummy_outcomes, _herb_names = generate_dummy_usage_outcomes(_dummy_herbs, count=500)
_condition_names = {
    uuid4(): "Anxiety",
    uuid4(): "Insomnia",
    uuid4(): "Depression",
    uuid4(): "Chronic Pain",
    uuid4(): "Fatigue",
}


# ============================================================================
# Search & Discovery Endpoints
# ============================================================================

@router.get("/search", response_model=HerbSearchResult)
async def search_herbs(
    q: Optional[str] = Query(None, description="Search query"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    min_score: int = Query(0, ge=0, le=100, description="Minimum SHI score"),
    min_evidence: Optional[str] = Query(None, description="Minimum evidence level"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
):
    """
    Search herbs by name or filter by criteria

    Returns herbs sorted by relevance and SHI score.
    """
    results = []

    for herb in _dummy_herbs:
        # Filter by search query
        if q:
            q_lower = q.lower()
            matches = (
                q_lower in herb.botanical_name.lower() or
                any(q_lower in name.lower() for name in herb.common_names)
            )
            if not matches:
                continue

        # Calculate SHI score
        herb_usage = [u for u in _dummy_usage if u.herb_id == herb.herb_id]
        herb_outcomes = [o for o in _dummy_outcomes if o.usage_id in {u.usage_id for u in herb_usage}]

        score = shi_calculator.calculate_herb_index(herb, herb_usage, herb_outcomes)

        # Filter by min score
        if score.overall_score < min_score:
            continue

        # Filter by evidence level
        if min_evidence:
            level_order = ["insufficient", "low", "moderate", "high", "very_high"]
            if level_order.index(score.evidence_level.value) < level_order.index(min_evidence.lower()):
                continue

        results.append(score)

    # Sort by score
    results.sort(key=lambda x: x.overall_score, reverse=True)

    return HerbSearchResult(
        herbs=results[:limit],
        total_count=len(results),
        query=q,
        filters_applied={
            "min_score": str(min_score),
            "condition": condition or "all",
        },
    )


@router.get("/rankings", response_model=HerbRankingResult)
async def get_herb_rankings(
    condition: str = Query(..., description="Condition name"),
    metric: str = Query("efficacy", description="Ranking metric: efficacy, effect_size, safety"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
):
    """
    Get ranked list of most effective herbs for a specific condition

    Returns herbs sorted by the specified metric with efficacy data.
    """
    # Find condition ID (in real system, would lookup)
    condition_id = uuid4()

    # Calculate efficacy for each herb
    efficacies = []
    for herb in _dummy_herbs:
        herb_usage = [u for u in _dummy_usage if u.herb_id == herb.herb_id]
        herb_outcomes = [o for o in _dummy_outcomes if o.usage_id in {u.usage_id for u in herb_usage}]

        if len(herb_outcomes) >= 30:
            efficacy = shi_calculator.calculate_condition_efficacy(
                herb, condition_id, condition, herb_outcomes
            )
            if efficacy:
                efficacies.append(efficacy)

    # Rank herbs
    ranked = shi_calculator.rank_herbs_for_condition(
        condition_id, condition, efficacies, metric
    )

    return HerbRankingResult(
        condition_id=condition_id,
        condition_name=condition,
        metric=metric,
        rankings=ranked[:limit],
    )


# ============================================================================
# Herb Details Endpoints
# ============================================================================

@router.get("/{herb_id}", response_model=HerbIndexScore)
async def get_herb_details(herb_id: UUID):
    """
    Get full details for a specific herb

    Returns SHI score, efficacy data, safety profile, and usage guidelines.
    """
    # Find herb
    herb = next((h for h in _dummy_herbs if h.herb_id == herb_id), None)
    if not herb:
        raise HTTPException(status_code=404, detail="Herb not found")

    # Calculate score
    herb_usage = [u for u in _dummy_usage if u.herb_id == herb.herb_id]
    herb_outcomes = [o for o in _dummy_outcomes if o.usage_id in {u.usage_id for u in herb_usage}]

    return shi_calculator.calculate_herb_index(herb, herb_usage, herb_outcomes)


@router.get("/compare", response_model=HerbComparisonResult)
async def compare_herbs(
    herb_ids: str = Query(..., description="Comma-separated herb IDs"),
    condition: Optional[str] = Query(None, description="Condition for comparison"),
):
    """
    Compare multiple herbs head-to-head

    Returns comparative effectiveness data for the specified herbs.
    """
    ids = [UUID(id.strip()) for id in herb_ids.split(",")]

    herbs_data = []
    metrics = {"overall_score": {}, "efficacy_score": {}, "safety_score": {}}

    for herb_id in ids:
        herb = next((h for h in _dummy_herbs if h.herb_id == herb_id), None)
        if not herb:
            continue

        herb_usage = [u for u in _dummy_usage if u.herb_id == herb.herb_id]
        herb_outcomes = [o for o in _dummy_outcomes if o.usage_id in {u.usage_id for u in herb_usage}]

        score = shi_calculator.calculate_herb_index(herb, herb_usage, herb_outcomes)
        herbs_data.append(score)

        # Add to comparison metrics
        metrics["overall_score"][str(herb_id)] = score.overall_score
        metrics["efficacy_score"][str(herb_id)] = score.efficacy_score
        metrics["safety_score"][str(herb_id)] = score.safety_score

    return HerbComparisonResult(
        herbs=herbs_data,
        comparison_metrics=metrics,
    )


# ============================================================================
# Synergy Detection Endpoints
# ============================================================================

@router.get("/combinations/synergies", response_model=SynergySearchResult)
async def find_synergies(
    min_score: int = Query(70, ge=0, le=100, description="Minimum synergy score"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    limit: int = Query(20, ge=1, le=50, description="Maximum results"),
):
    """
    Find herb combinations with synergistic effects

    Returns combinations where outcome exceeds expected individual performance.
    """
    synergies = synergy_detector.find_synergistic_combinations(
        _dummy_usage,
        _dummy_outcomes,
        _herb_names,
        condition_id=None,
        min_synergy_score=min_score,
        limit=limit,
    )

    return SynergySearchResult(
        combinations=synergies,
        total_found=len(synergies),
    )


@router.get("/combinations/{combination_id}/protocol")
async def get_combination_protocol(combination_id: UUID):
    """
    Get detailed treatment protocol for a herb combination

    Returns optimal dosages, timing, duration, and expected outcomes.
    """
    # In real system, would lookup combination by ID
    # For demo, return sample protocol
    return {
        "combination_id": combination_id,
        "herbs": ["Valerian", "Passionflower", "Magnesium"],
        "dosages": {
            "Valerian": 300,
            "Passionflower": 200,
            "Magnesium": 400,
        },
        "frequency": "daily",
        "timing": "60 minutes before bed",
        "duration_days": 28,
        "expected_improvement_pct": 45.0,
        "typical_days_to_improvement": 7,
        "sample_size": 687,
        "confidence": "high",
    }


# ============================================================================
# Test & Demo Endpoints
# ============================================================================

@router.get("/test-scenarios")
async def get_test_scenarios():
    """Get test scenarios for herb index demonstration"""
    return {
        "scenarios": [
            {
                "name": "anxiety_herbs",
                "description": "Top herbs for anxiety management",
                "endpoint": "/rankings?condition=Anxiety&metric=efficacy",
            },
            {
                "name": "high_evidence",
                "description": "Herbs with high evidence scores",
                "endpoint": "/search?min_score=70&min_evidence=high",
            },
            {
                "name": "synergies",
                "description": "High-synergy herb combinations",
                "endpoint": "/combinations/synergies?min_score=60",
            },
            {
                "name": "compare",
                "description": "Compare adaptogenic herbs",
                "endpoint": f"/compare?herb_ids={_dummy_herbs[1].herb_id},{_dummy_herbs[5].herb_id}",
            },
        ],
        "available_herbs": [
            {"id": str(h.herb_id), "name": h.common_names[0], "botanical": h.botanical_name}
            for h in _dummy_herbs
        ],
    }


@router.get("/evidence-levels")
async def get_evidence_levels():
    """Get evidence level definitions"""
    return {
        "levels": [
            {
                "level": "very_high",
                "score_range": "85-100",
                "min_cases": 500,
                "description": "Strong evidence from large sample",
            },
            {
                "level": "high",
                "score_range": "70-84",
                "min_cases": 100,
                "description": "Good evidence from substantial sample",
            },
            {
                "level": "moderate",
                "score_range": "50-69",
                "min_cases": 30,
                "description": "Moderate evidence, more data needed",
            },
            {
                "level": "low",
                "score_range": "30-49",
                "min_cases": 10,
                "description": "Limited evidence available",
            },
            {
                "level": "insufficient",
                "score_range": "0-29",
                "min_cases": 0,
                "description": "Insufficient data for assessment",
            },
        ],
        "score_components": {
            "evidence_volume": {"max": 25, "description": "Sample size and diversity"},
            "efficacy": {"max": 40, "description": "Outcome improvement metrics"},
            "safety": {"max": 20, "description": "Adverse event profile"},
            "data_quality": {"max": 15, "description": "Data completeness"},
        },
    }


@router.get("/all-herbs")
async def get_all_herbs():
    """Get list of all herbs in the database"""
    results = []
    for herb in _dummy_herbs:
        herb_usage = [u for u in _dummy_usage if u.herb_id == herb.herb_id]
        herb_outcomes = [o for o in _dummy_outcomes if o.usage_id in {u.usage_id for u in herb_usage}]
        score = shi_calculator.calculate_herb_index(herb, herb_usage, herb_outcomes)
        results.append(score)

    results.sort(key=lambda x: x.overall_score, reverse=True)
    return {"herbs": results, "total": len(results)}
