"""
Index API Routes

Endpoints for SANA Index scoring.
"""
import random
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from uuid import UUID, uuid4

from algorithms.index import calculate_sana_index
from algorithms.index.models import IndexOutput

router = APIRouter()


# Sample data for testing
def generate_sample_practitioner(profile: str = "standard") -> dict:
    """Generate sample practitioner data for testing"""

    if profile == "excellent":
        credentials = [
            "PhD Clinical Psychology - University of Oxford",
            "MSc Herbal Medicine - Royal College",
            "HCPC Registration PYL12345",
            "Board Certification in Integrative Medicine"
        ]
        outcome_data = {
            "total_clients": 500,
            "mean_improvement": 55,
            "improvements": [50, 55, 60, 52, 58, 54, 56, 53, 57, 55],
            "retention_rate": 0.92,
            "trend": [75, 78, 82, 85, 88]
        }
        reviews = [
            {"rating": 5, "date": "2024-06-15", "text": "Dr. Smith is exceptional. After years of struggling with chronic fatigue, her integrative approach combining herbal medicine and lifestyle changes transformed my health completely."},
            {"rating": 5, "date": "2024-05-20", "text": "Thorough, caring, and incredibly knowledgeable. Highly recommend!"},
            {"rating": 5, "date": "2024-04-10", "text": "Life-changing treatment. Best practitioner I've ever seen."},
            {"rating": 4, "date": "2024-03-05", "text": "Very good experience overall"}
        ]
        verified = True

    elif profile == "good":
        credentials = [
            "MSc Naturopathic Medicine - University of Edinburgh",
            "Naturopath License",
            "Nutrition Certification"
        ]
        outcome_data = {
            "total_clients": 150,
            "mean_improvement": 42,
            "improvements": [35, 40, 45, 38, 50, 42, 44],
            "retention_rate": 0.80
        }
        reviews = [
            {"rating": 4, "date": "2024-05-15", "text": "Good practitioner, helped me with digestive issues."},
            {"rating": 5, "date": "2024-04-20", "text": "Very helpful and knowledgeable"},
            {"rating": 4, "date": "2024-02-10", "text": "Would recommend"}
        ]
        verified = True

    elif profile == "new":
        credentials = [
            "BSc Health Sciences",
            "Herbalist Certification",
            "Certificate in Aromatherapy"
        ]
        outcome_data = {
            "total_clients": 25,
            "mean_improvement": 35,
            "improvements": [30, 35, 40, 32, 38],
            "retention_rate": 0.70
        }
        reviews = [
            {"rating": 4, "date": "2024-06-01", "text": "Good first appointment"},
            {"rating": 5, "date": "2024-05-15", "text": "Friendly and helpful"}
        ]
        verified = True

    elif profile == "unverified":
        credentials = [
            "Certificate in Wellness Coaching",
            "Online Diploma in Holistic Health"
        ]
        outcome_data = {
            "total_clients": 10,
            "mean_improvement": 25,
            "improvements": [20, 30, 25],
            "retention_rate": 0.50
        }
        reviews = [
            {"rating": 3, "date": "2024-04-01", "text": "Average experience"}
        ]
        verified = False

    else:  # standard
        credentials = [
            "MSc Clinical Psychology - University of Manchester",
            "HCPC Registration",
            "Herbalist Certification"
        ]
        outcome_data = {
            "total_clients": 100,
            "mean_improvement": 38,
            "improvements": [35, 40, 38, 42, 36, 39],
            "retention_rate": 0.75
        }
        reviews = [
            {"rating": 4, "date": "2024-05-10", "text": "Helpful and professional, good results with treatment."},
            {"rating": 4, "date": "2024-03-15", "text": "Good experience"},
            {"rating": 5, "date": "2024-01-20", "text": "Very satisfied"}
        ]
        verified = True

    return {
        "practitioner_id": uuid4(),
        "credentials": credentials,
        "outcome_data": outcome_data,
        "reviews": reviews,
        "verification_status": verified
    }


@router.post("/calculate")
async def calculate(
    practitioner_id: UUID,
    credentials: List[str],
    outcome_data: Dict,
    reviews: List[Dict],
    verification_status: bool
):
    """
    Calculate SANA Index score for a practitioner.

    Returns overall score and component breakdown.
    """
    try:
        result = calculate_sana_index(
            practitioner_id=practitioner_id,
            credentials=credentials,
            outcome_data=outcome_data,
            reviews=reviews,
            verification_status=verification_status
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-calculate")
async def test_calculate(
    profile: str = Query("standard", description="Profile: excellent, good, standard, new, unverified")
):
    """
    Test SANA Index calculation with sample data.

    Returns calculated score for sample practitioner profile.
    """
    sample = generate_sample_practitioner(profile)

    result = calculate_sana_index(
        practitioner_id=sample["practitioner_id"],
        credentials=sample["credentials"],
        outcome_data=sample["outcome_data"],
        reviews=sample["reviews"],
        verification_status=sample["verification_status"]
    )

    return {
        "profile": profile,
        "input_data": sample,
        "result": result
    }


@router.get("/component-weights")
async def get_component_weights():
    """Get current component weight configuration"""
    return {
        "weights": {
            "credentials": {"weight": 0.30, "max_score": 100, "description": "Education, licenses, certifications"},
            "outcomes": {"weight": 0.50, "max_score": 100, "description": "Client health improvements"},
            "reviews": {"weight": 0.10, "max_score": 100, "description": "Client ratings and feedback"},
            "verification": {"weight": 0.10, "max_score": 100, "description": "Identity and credential verification"}
        },
        "score_interpretation": {
            "90-100": "Exceptional - Top tier practitioner",
            "75-89": "Excellent - Highly recommended",
            "60-74": "Good - Solid track record",
            "45-59": "Developing - Building experience",
            "0-44": "Emerging - Limited data"
        }
    }


@router.get("/credential-types")
async def get_credential_types():
    """Get supported credential types and their point values"""
    from algorithms.index.sana_index import SANAIndexCalculator
    calc = SANAIndexCalculator()

    # Group by category
    degrees = {k: v for k, v in calc.CREDENTIAL_SCORES.items() if k in ["phd", "doctorate", "md", "do", "masters", "msc", "ma", "bachelors", "bsc", "ba"]}
    licenses = {k: v for k, v in calc.CREDENTIAL_SCORES.items() if "license" in k or "registration" in k}
    certifications = {k: v for k, v in calc.CREDENTIAL_SCORES.items() if "certification" in k}
    other = {k: v for k, v in calc.CREDENTIAL_SCORES.items() if k in ["diploma", "certificate", "training"]}

    return {
        "degrees": degrees,
        "licenses": licenses,
        "certifications": certifications,
        "other": other,
        "institution_multipliers": calc.KNOWN_INSTITUTIONS
    }


@router.get("/practitioner/{practitioner_id}")
async def get_practitioner_index(practitioner_id: UUID):
    """
    Get current SANA Index for a practitioner.

    Returns cached score and last update time.
    """
    # For demo: generate random historical data
    return {
        "practitioner_id": practitioner_id,
        "current_score": random.randint(60, 85),
        "percentile": random.randint(50, 90),
        "trend": random.choice(["improving", "stable", "declining"]),
        "last_updated": "2024-06-15T10:30:00Z",
        "note": "Demo data - in production would fetch from database"
    }


@router.get("/leaderboard")
async def get_leaderboard(
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Get top practitioners by SANA Index.

    Returns ranked list of practitioners.
    """
    # Generate demo leaderboard
    practitioners = []
    specialties = ["Herbalism", "Naturopathy", "Acupuncture", "Nutrition", "Mind-Body"]

    for i in range(top_k):
        spec = specialty if specialty else random.choice(specialties)
        practitioners.append({
            "rank": i + 1,
            "practitioner_id": str(uuid4()),
            "name": f"Dr. Practitioner {i+1}",
            "specialty": spec,
            "sana_index": round(95 - i * 2 + random.uniform(-1, 1), 1),
            "percentile": round(99 - i * 2, 1),
            "total_clients": random.randint(100, 500),
            "verified": True
        })

    return {
        "specialty_filter": specialty,
        "total_count": top_k,
        "practitioners": practitioners,
        "note": "Demo data - in production would fetch from database"
    }


@router.get("/test-scenarios")
async def get_test_scenarios():
    """Get available test scenarios"""
    return {
        "scenarios": [
            {
                "profile": "excellent",
                "description": "Top-tier practitioner with PhD, high outcomes, excellent reviews",
                "expected_score": "85-95"
            },
            {
                "profile": "good",
                "description": "Solid practitioner with masters, good outcomes",
                "expected_score": "70-80"
            },
            {
                "profile": "standard",
                "description": "Average practitioner with typical credentials",
                "expected_score": "60-75"
            },
            {
                "profile": "new",
                "description": "New practitioner with limited track record",
                "expected_score": "50-65"
            },
            {
                "profile": "unverified",
                "description": "Unverified practitioner with minimal credentials",
                "expected_score": "30-45"
            }
        ],
        "endpoint": "/test-calculate?profile={profile}"
    }
