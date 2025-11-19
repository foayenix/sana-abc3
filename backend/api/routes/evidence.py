"""
API routes for SANA Health Graph and evidence queries
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from algorithms.evidence.health_graph import HealthGraph
from algorithms.evidence.models import (
    Intervention,
    Domain,
    EvidenceStrength,
)
from utils.health_graph_data import seed_health_graph

router = APIRouter()

# Initialize health graph and seed with sample data
health_graph = HealthGraph()
num_interventions = seed_health_graph(health_graph)

@router.get("/")
async def graph_info():
    """Get health graph information and statistics"""
    stats = health_graph.get_statistics()
    return {
        "status": "operational",
        "statistics": stats,
        "message": f"Health graph loaded with {num_interventions} interventions"
    }

@router.get("/interventions", response_model=List[Intervention])
async def list_all_interventions():
    """List all interventions in the graph"""
    return list(health_graph.interventions.values())

@router.get("/interventions/{intervention_id}", response_model=Intervention)
async def get_intervention(intervention_id: UUID):
    """Get specific intervention by ID"""
    intervention = health_graph.get_intervention(intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    return intervention

@router.get("/interventions/domain/{domain}", response_model=List[Intervention])
async def find_by_domain(
    domain: str,
    min_evidence: str = Query(default="weak", description="Minimum evidence strength: strong, moderate, weak, insufficient"),
    user_conditions: Optional[str] = Query(default=None, description="Comma-separated list of user conditions"),
    user_medications: Optional[str] = Query(default=None, description="Comma-separated list of medication classes")
):
    """
    Find interventions for a specific wellness domain

    **Example**: `/interventions/domain/emotional?min_evidence=moderate&user_conditions=pregnancy`
    """
    try:
        domain_enum = Domain(domain.lower())
        evidence_enum = EvidenceStrength(min_evidence.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")

    # Parse user conditions and medications
    conditions = set(user_conditions.split(",")) if user_conditions else set()
    medications = set(user_medications.split(",")) if user_medications else set()

    interventions = health_graph.find_interventions_for_domain(
        domain_enum,
        evidence_enum,
        conditions,
        medications
    )

    return interventions

@router.get("/interventions/condition/{condition}", response_model=List[Intervention])
async def find_by_condition(
    condition: str,
    min_evidence: str = Query(default="weak"),
    user_conditions: Optional[str] = Query(default=None),
    user_medications: Optional[str] = Query(default=None)
):
    """
    Find interventions for a specific condition

    **Example**: `/interventions/condition/anxiety?min_evidence=strong`
    """
    try:
        evidence_enum = EvidenceStrength(min_evidence.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid evidence strength: {str(e)}")

    conditions = set(user_conditions.split(",")) if user_conditions else set()
    medications = set(user_medications.split(",")) if user_medications else set()

    interventions = health_graph.find_interventions_for_condition(
        condition,
        evidence_enum,
        conditions,
        medications
    )

    return interventions

@router.post("/interventions/weak-domains")
async def find_for_weak_domains(
    weak_domains: List[str],
    min_evidence: str = Query(default="moderate"),
    user_conditions: Optional[List[str]] = None,
    user_medications: Optional[List[str]] = None,
    max_per_domain: int = Query(default=5)
):
    """
    Find interventions for multiple weak domains (from SISM output)

    **Example Request Body**:
    ```json
    {
        "weak_domains": ["emotional", "physical"],
        "user_conditions": ["pregnancy"],
        "user_medications": ["antidepressants"]
    }
    ```
    """
    try:
        evidence_enum = EvidenceStrength(min_evidence.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid evidence strength: {str(e)}")

    conditions = set(user_conditions) if user_conditions else set()
    medications = set(user_medications) if user_medications else set()

    results = health_graph.find_interventions_for_weak_domains(
        weak_domains,
        evidence_enum,
        conditions,
        medications,
        max_per_domain
    )

    # Convert Intervention objects to dicts for JSON serialization
    serialized_results = {}
    for domain, interventions in results.items():
        serialized_results[domain] = [intervention.model_dump() for intervention in interventions]

    return serialized_results

@router.get("/safety-check/{intervention_id}")
async def check_safety(
    intervention_id: UUID,
    user_conditions: str = Query(..., description="Comma-separated conditions"),
    user_medications: str = Query(default="", description="Comma-separated medication classes")
):
    """
    Check if an intervention is safe for a user

    **Returns**: Safety status and any warnings
    """
    conditions = set(user_conditions.split(",")) if user_conditions else set()
    medications = set(user_medications.split(",")) if user_medications else set()

    is_safe, warnings = health_graph.get_contraindications_for_user(
        intervention_id,
        conditions,
        medications
    )

    return {
        "intervention_id": str(intervention_id),
        "is_safe": is_safe,
        "warnings": warnings,
        "user_conditions_checked": list(conditions),
        "user_medications_checked": list(medications)
    }

@router.get("/statistics")
async def get_statistics():
    """Get detailed statistics about the health graph"""
    return health_graph.get_statistics()


# ============================================================================
# HEALTH SCORE ENDPOINTS
# ============================================================================

from algorithms.evidence.health_score import (
    HealthScoreCalculator,
    HealthScoreOutput,
    SANAStatus
)
from pydantic import BaseModel, Field
from typing import Dict

# Initialize health score calculator
health_score_calculator = HealthScoreCalculator()


class HealthScoreRequest(BaseModel):
    """Request to calculate SANA Health Score."""
    domain_scores: Dict[str, float] = Field(
        ...,
        description="Scores for each domain (0-100)",
        example={
            "physical": 65.0,
            "emotional": 55.0,
            "social": 70.0,
            "cognitive": 60.0,
            "spiritual": 50.0
        }
    )
    chronological_age: int = Field(..., ge=18, le=120)
    historical_scores: Optional[List[float]] = None
    current_activities: Optional[List[str]] = None


@router.post("/health-score/calculate")
async def calculate_health_score(request: HealthScoreRequest):
    """
    Calculate complete SANA Health Score output.

    Returns:
    - SANA Health Score (0-100)
    - SANA Status (needs_support, rebuilding, balanced, thriving, radiant)
    - SANA Age (biological wellness estimate)
    - Top 3 Levers (personalized action recommendations)
    - Weak and strong domains
    """
    result = health_score_calculator.calculate(
        domain_scores=request.domain_scores,
        chronological_age=request.chronological_age,
        historical_scores=request.historical_scores,
        current_activities=request.current_activities
    )

    # Get status description
    status_info = health_score_calculator.get_status_description(result.sana_status)

    return {
        "sana_health_score": result.sana_health_score,
        "sana_status": {
            "status": result.sana_status.value,
            **status_info
        },
        "sana_age": result.sana_age,
        "chronological_age": result.chronological_age,
        "age_difference": round(result.chronological_age - result.sana_age, 1),
        "domain_scores": result.domain_scores,
        "weak_domains": result.weak_domains,
        "strong_domains": result.strong_domains,
        "top_levers": [
            {
                "priority": lever.priority,
                "action": lever.action,
                "domain": lever.domain,
                "expected_impact": lever.expected_impact,
                "difficulty": lever.difficulty,
                "time_investment": lever.time_investment,
                "evidence_strength": lever.evidence_strength
            }
            for lever in result.top_levers
        ],
        "score_trend": result.score_trend,
        "potential_score": result.potential_score
    }


@router.get("/health-score/test")
async def test_health_score():
    """Test health score calculation with sample profiles."""
    profiles = [
        {
            "name": "Needs Support",
            "domain_scores": {
                "physical": 25.0,
                "emotional": 30.0,
                "social": 20.0,
                "cognitive": 35.0,
                "spiritual": 15.0
            },
            "age": 45
        },
        {
            "name": "Rebuilding",
            "domain_scores": {
                "physical": 40.0,
                "emotional": 35.0,
                "social": 45.0,
                "cognitive": 40.0,
                "spiritual": 30.0
            },
            "age": 35
        },
        {
            "name": "Balanced",
            "domain_scores": {
                "physical": 55.0,
                "emotional": 50.0,
                "social": 60.0,
                "cognitive": 55.0,
                "spiritual": 45.0
            },
            "age": 40
        },
        {
            "name": "Thriving",
            "domain_scores": {
                "physical": 75.0,
                "emotional": 70.0,
                "social": 80.0,
                "cognitive": 65.0,
                "spiritual": 70.0
            },
            "age": 50
        },
        {
            "name": "Radiant",
            "domain_scores": {
                "physical": 90.0,
                "emotional": 85.0,
                "social": 95.0,
                "cognitive": 88.0,
                "spiritual": 92.0
            },
            "age": 30
        }
    ]

    results = []
    for profile in profiles:
        result = health_score_calculator.calculate(
            domain_scores=profile["domain_scores"],
            chronological_age=profile["age"]
        )
        results.append({
            "profile": profile["name"],
            "sana_score": result.sana_health_score,
            "sana_status": result.sana_status.value,
            "sana_age": result.sana_age,
            "chrono_age": result.chronological_age,
            "age_diff": round(result.chronological_age - result.sana_age, 1),
            "weak_domains": result.weak_domains,
            "top_lever": result.top_levers[0].action if result.top_levers else None
        })

    return {
        "message": "Test health score calculations complete",
        "results": results
    }


@router.get("/health-score/status-info")
async def get_status_info():
    """Get information about all SANA Status levels."""
    statuses = {}
    for status in SANAStatus:
        statuses[status.value] = health_score_calculator.get_status_description(status)

    return {
        "statuses": statuses,
        "note": "Status is determined by overall SANA Health Score"
    }


@router.get("/health-score/domain-weights")
async def get_domain_weights():
    """Get the weights used for each wellness domain."""
    return {
        "weights": HealthScoreCalculator.DOMAIN_WEIGHTS,
        "note": "Weights sum to 1.0 and determine domain contribution to overall score"
    }
