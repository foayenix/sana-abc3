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
