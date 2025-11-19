"""
Outcome Measures API routes for SANA Platform.

Provides endpoints for managing Patient-Reported Outcome Measures (PROMs).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from algorithms.outcomes.proms import (
    WHO5,
    DASS21,
    VASPain,
    CAMSymptomScale,
    OutcomeMeasureScheduler
)
from algorithms.outcomes.models import (
    OutcomeMeasureType,
    MeasureTiming,
    QuestionResponse,
    DeliveryMethod
)

router = APIRouter()

# Initialize scheduler
scheduler = OutcomeMeasureScheduler()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class SubmitResponsesRequest(BaseModel):
    """Request to submit outcome measure responses."""
    measure_type: OutcomeMeasureType
    responses: List[dict]  # [{question_id, value}]
    client_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    timing: MeasureTiming = MeasureTiming.PRE_SESSION


class ScheduleRequest(BaseModel):
    """Request to schedule measures for a session."""
    client_id: UUID
    session_id: UUID
    practitioner_id: UUID
    session_time: datetime
    measure_types: Optional[List[OutcomeMeasureType]] = None
    delivery_method: DeliveryMethod = DeliveryMethod.EMAIL


# ============================================================================
# QUESTIONNAIRE ENDPOINTS
# ============================================================================

@router.get("/questionnaire/{measure_type}")
async def get_questionnaire(
    measure_type: OutcomeMeasureType,
    client_id: Optional[UUID] = None,
    session_id: Optional[UUID] = None,
    timing: MeasureTiming = MeasureTiming.PRE_SESSION
):
    """
    Get a questionnaire for a specific outcome measure.

    Returns the questions, instructions, and response options.
    """
    client_id = client_id or uuid4()

    if measure_type == OutcomeMeasureType.WHO5:
        questionnaire = WHO5.get_questionnaire(client_id, session_id, timing)
    elif measure_type == OutcomeMeasureType.DASS21:
        questionnaire = DASS21.get_questionnaire(client_id, session_id, timing)
    elif measure_type == OutcomeMeasureType.VAS_PAIN:
        questionnaire = VASPain.get_questionnaire(client_id, session_id, timing)
    elif measure_type == OutcomeMeasureType.CAM_SYMPTOM:
        questionnaire = CAMSymptomScale.get_questionnaire(client_id, session_id, timing)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown measure type: {measure_type}")

    return {
        "measure_type": questionnaire.measure_type.value,
        "instructions": questionnaire.instructions,
        "estimated_time": questionnaire.estimated_time,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "type": q.question_type.value,
                "options": q.options,
                "min_value": q.min_value,
                "max_value": q.max_value,
                "subscale": q.subscale
            }
            for q in questionnaire.questions
        ]
    }


@router.post("/submit")
async def submit_responses(request: SubmitResponsesRequest):
    """
    Submit responses and get scored results.

    Returns total score, subscale scores, severity, and interpretation.
    """
    # Convert to QuestionResponse objects
    responses = [
        QuestionResponse(
            question_id=r["question_id"],
            value=r["value"],
            response_time_ms=r.get("response_time_ms")
        )
        for r in request.responses
    ]

    # Score based on measure type
    if request.measure_type == OutcomeMeasureType.WHO5:
        result = WHO5.score(responses)
    elif request.measure_type == OutcomeMeasureType.DASS21:
        result = DASS21.score(responses)
    elif request.measure_type == OutcomeMeasureType.VAS_PAIN:
        result = VASPain.score(responses)
    elif request.measure_type == OutcomeMeasureType.CAM_SYMPTOM:
        result = CAMSymptomScale.score(responses)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown measure type: {request.measure_type}")

    # Override client_id if provided
    if request.client_id:
        result.client_id = request.client_id
    if request.session_id:
        result.session_id = request.session_id
    result.timing = request.timing

    return {
        "measure_id": str(result.measure_id),
        "measure_type": result.measure_type.value,
        "total_score": result.total_score,
        "subscale_scores": result.subscale_scores,
        "percentile": result.percentile,
        "severity": result.severity,
        "interpretation": result.interpretation,
        "clinical_flags": result.clinical_flags,
        "completed_at": result.completed_at.isoformat()
    }


# ============================================================================
# SCHEDULING ENDPOINTS
# ============================================================================

@router.post("/schedule")
async def schedule_measures(request: ScheduleRequest):
    """
    Schedule outcome measures for a session.

    Automatically schedules post-session, 1-week, and 1-month follow-ups.
    """
    scheduled = scheduler.schedule_for_session(
        client_id=request.client_id,
        session_id=request.session_id,
        practitioner_id=request.practitioner_id,
        session_time=request.session_time,
        measure_types=request.measure_types,
        delivery_method=request.delivery_method
    )

    return {
        "message": f"Scheduled {len(scheduled)} outcome measures",
        "scheduled": [
            {
                "id": str(s.id),
                "measure_type": s.measure_type.value,
                "timing": s.timing.value,
                "scheduled_for": s.scheduled_for.isoformat(),
                "delivery_method": s.delivery_method.value
            }
            for s in scheduled
        ]
    }


@router.get("/pending/{client_id}")
async def get_pending_measures(client_id: UUID):
    """Get all pending outcome measures for a client."""
    pending = scheduler.get_pending_for_client(client_id)

    return {
        "client_id": str(client_id),
        "pending_count": len(pending),
        "measures": [
            {
                "id": str(m.id),
                "measure_type": m.measure_type.value,
                "timing": m.timing.value,
                "scheduled_for": m.scheduled_for.isoformat(),
                "delivered": m.delivered,
                "reminder_count": m.reminder_count
            }
            for m in pending
        ]
    }


@router.get("/due")
async def get_due_measures():
    """Get all measures due for delivery right now."""
    due = scheduler.get_due_measures()

    return {
        "due_count": len(due),
        "measures": [
            {
                "id": str(m.id),
                "client_id": str(m.client_id),
                "measure_type": m.measure_type.value,
                "timing": m.timing.value,
                "scheduled_for": m.scheduled_for.isoformat()
            }
            for m in due
        ]
    }


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@router.get("/test/{measure_type}")
async def test_measure_scoring(measure_type: OutcomeMeasureType):
    """Test scoring with sample responses for each measure type."""

    if measure_type == OutcomeMeasureType.WHO5:
        # Test WHO-5 with different profiles
        profiles = [
            {"name": "Poor wellbeing", "values": [1, 1, 1, 0, 1]},  # Score: 16
            {"name": "Moderate wellbeing", "values": [3, 3, 3, 2, 3]},  # Score: 56
            {"name": "Good wellbeing", "values": [5, 4, 4, 5, 4]},  # Score: 88
        ]

        results = []
        for profile in profiles:
            responses = [
                QuestionResponse(question_id=f"who5_{i+1}", value=v)
                for i, v in enumerate(profile["values"])
            ]
            result = WHO5.score(responses)
            results.append({
                "profile": profile["name"],
                "responses": profile["values"],
                "score": result.total_score,
                "severity": result.severity,
                "interpretation": result.interpretation
            })

        return {"measure": "WHO-5", "test_results": results}

    elif measure_type == OutcomeMeasureType.DASS21:
        # Test DASS-21 with moderate profile
        # All 2s = moderate across all scales
        responses = [
            QuestionResponse(question_id=f"dass_{i+1}", value=2)
            for i in range(21)
        ]
        result = DASS21.score(responses)

        return {
            "measure": "DASS-21",
            "test_result": {
                "profile": "Moderate symptoms",
                "total_score": result.total_score,
                "subscale_scores": result.subscale_scores,
                "severity": result.severity,
                "interpretation": result.interpretation
            }
        }

    elif measure_type == OutcomeMeasureType.VAS_PAIN:
        # Test VAS with different pain levels
        profiles = [
            {"name": "No pain", "value": 0},
            {"name": "Mild pain", "value": 25},
            {"name": "Moderate pain", "value": 50},
            {"name": "Severe pain", "value": 80},
        ]

        results = []
        for profile in profiles:
            responses = [QuestionResponse(question_id="vas_pain_1", value=profile["value"])]
            result = VASPain.score(responses)
            results.append({
                "profile": profile["name"],
                "value": profile["value"],
                "severity": result.severity,
                "interpretation": result.interpretation
            })

        return {"measure": "VAS Pain", "test_results": results}

    elif measure_type == OutcomeMeasureType.CAM_SYMPTOM:
        # Test CAM scale with mixed profile
        responses = [
            QuestionResponse(question_id="cam_1", value=7),  # Energy
            QuestionResponse(question_id="cam_2", value=5),  # Sleep
            QuestionResponse(question_id="cam_3", value=8),  # Digestion
            QuestionResponse(question_id="cam_4", value=4),  # Emotional
            QuestionResponse(question_id="cam_5", value=6),  # Tension (reverse)
            QuestionResponse(question_id="cam_6", value=6),  # Overall
        ]
        result = CAMSymptomScale.score(responses)

        return {
            "measure": "CAM Symptom Scale",
            "test_result": {
                "profile": "Mixed symptoms",
                "total_score": result.total_score,
                "subscale_scores": result.subscale_scores,
                "severity": result.severity,
                "clinical_flags": result.clinical_flags
            }
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown measure type: {measure_type}")


@router.get("/info")
async def get_measures_info():
    """Get information about all available outcome measures."""
    return {
        "available_measures": [
            {
                "type": "who5",
                "name": "WHO-5 Wellbeing Index",
                "questions": 5,
                "time": "1-2 minutes",
                "description": "Validated measure of psychological wellbeing",
                "scoring": "0-100 scale (higher = better)"
            },
            {
                "type": "dass21",
                "name": "DASS-21",
                "questions": 21,
                "time": "3-5 minutes",
                "description": "Depression, Anxiety, Stress Scale",
                "scoring": "Subscales for depression, anxiety, stress"
            },
            {
                "type": "vas_pain",
                "name": "VAS Pain",
                "questions": 1,
                "time": "30 seconds",
                "description": "Visual Analogue Scale for pain intensity",
                "scoring": "0-100 scale (lower = better)"
            },
            {
                "type": "cam_symptom",
                "name": "CAM Symptom Scale",
                "questions": 6,
                "time": "1-2 minutes",
                "description": "Custom scale for CAM-relevant symptoms",
                "scoring": "Subscales for energy, sleep, digestion, etc."
            }
        ],
        "delivery_methods": ["email", "sms", "app"],
        "timing_options": ["pre_session", "post_session", "1_week", "1_month", "3_month", "6_month"]
    }
