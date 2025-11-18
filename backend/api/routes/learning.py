"""
API routes for SOU learning system
"""
from fastapi import APIRouter, HTTPException, Query
from uuid import UUID, uuid4

from algorithms.learning.sou import SOUAlgorithm
from algorithms.learning.models import SOUOutput, LearningMetrics
from utils.outcome_data import generate_dummy_outcomes

router = APIRouter()

# Initialize SOU
sou = SOUAlgorithm()

# Generate and cache dummy outcome data
DUMMY_OUTCOMES = generate_dummy_outcomes(count=200)


@router.get("/metrics", response_model=LearningMetrics)
async def get_learning_metrics():
    """
    Get overall learning system metrics

    Shows how well the system is learning and improving
    """
    try:
        metrics = sou.analyze_outcomes(DUMMY_OUTCOMES)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")


@router.get("/test-recommendations")
async def test_sou_recommendations(
    baseline_score: float = Query(default=45.0, ge=0, le=100),
    weak_domain: str = Query(default="emotional")
):
    """
    Test SOU recommendation generation

    **Demonstrates outcome-optimized recommendations vs baseline**
    """
    try:
        user_id = uuid4()

        # Create user profile
        user_profile = {
            "baseline_score": baseline_score,
            "weak_domains": [weak_domain],
            "age": 35,
            "gender": "female"
        }

        # Generate candidate interventions (mock)
        candidate_interventions = [uuid4() for _ in range(10)]

        # Get SOU recommendations
        sou_output = sou.generate_sou_recommendations(
            user_id,
            user_profile,
            candidate_interventions,
            DUMMY_OUTCOMES
        )

        return {
            "user_profile": user_profile,
            "sou_recommendations": sou_output,
            "explanation": f"SOU predicts {sou_output.expected_improvement_with_sou:.1f}% improvement vs {sou_output.expected_improvement_baseline:.1f}% baseline (uplift: +{sou_output.uplift:.1f}%)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/intervention-performance/{intervention_id}")
async def get_intervention_performance(intervention_id: UUID):
    """Get performance metrics for a specific intervention"""
    try:
        performance = sou.calculate_intervention_performance(
            intervention_id,
            DUMMY_OUTCOMES
        )
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance error: {str(e)}")


@router.get("/predict-outcome")
async def predict_outcome(
    baseline_score: float = Query(default=50.0, ge=0, le=100),
    weak_domain: str = Query(default="emotional")
):
    """
    Predict outcome for a user + intervention combination

    Shows confidence intervals and key factors
    """
    try:
        user_id = uuid4()
        intervention_id = uuid4()

        user_profile = {
            "baseline_score": baseline_score,
            "weak_domains": [weak_domain],
            "age": 40,
            "gender": "male"
        }

        prediction = sou.predict_outcome(
            user_id,
            user_profile,
            intervention_id,
            DUMMY_OUTCOMES
        )

        return {
            "user_profile": user_profile,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.get("/learning-phase")
async def get_learning_phase():
    """Get current learning phase and exploration rate"""
    metrics = sou.analyze_outcomes(DUMMY_OUTCOMES)

    return {
        "learning_phase": metrics.learning_phase,
        "exploration_rate": metrics.exploration_rate,
        "total_outcomes": metrics.total_outcome_records,
        "thresholds": {
            "cold_start": f"< {sou.COLD_START_THRESHOLD} outcomes",
            "early_learning": f"{sou.COLD_START_THRESHOLD}-{sou.EARLY_LEARNING_THRESHOLD} outcomes",
            "mature": f"> {sou.EARLY_LEARNING_THRESHOLD} outcomes"
        }
    }


@router.get("/top-performers")
async def get_top_performers():
    """Get top performing interventions and practitioners"""
    metrics = sou.analyze_outcomes(DUMMY_OUTCOMES)

    return {
        "top_interventions": metrics.top_interventions,
        "top_practitioners": metrics.top_practitioners,
        "average_improvement": metrics.average_improvement_with_sou,
        "uplift_vs_baseline": metrics.uplift_percentage
    }
