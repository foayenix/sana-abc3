"""
Marketplace API routes for SANA Platform.

Endpoints for practitioner discovery, search, reviews, and booking flow.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import UUID
from datetime import date, time

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.marketplace.search import (
    MarketplaceSearchService,
    SearchFilters,
    SortOption,
    Specialty,
    PractitionerListing
)
from services.marketplace.reviews import ReviewService
from services.marketplace.discovery import DiscoveryService

router = APIRouter()

# Initialize services
search_service = MarketplaceSearchService()
review_service = ReviewService()
discovery_service = DiscoveryService(search_service, review_service)


# ============================================================================
# REQUEST MODELS
# ============================================================================

class SearchRequest(BaseModel):
    """Search request body."""
    query: Optional[str] = None
    specialties: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    modalities: Optional[List[str]] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    max_distance_miles: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    telehealth_only: bool = False
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_sana_index: Optional[float] = None
    min_rating: Optional[float] = None
    verified_only: bool = False
    available_date: Optional[date] = None
    sort_by: str = "relevance"
    page: int = 1
    per_page: int = 20


class SubmitReviewRequest(BaseModel):
    """Submit a review."""
    practitioner_id: UUID
    client_id: UUID
    overall_rating: int = Field(ge=1, le=5)
    title: str
    content: str
    booking_id: Optional[UUID] = None
    communication_rating: Optional[int] = Field(default=None, ge=1, le=5)
    punctuality_rating: Optional[int] = Field(default=None, ge=1, le=5)
    effectiveness_rating: Optional[int] = Field(default=None, ge=1, le=5)
    value_rating: Optional[int] = Field(default=None, ge=1, le=5)
    treatment_type: Optional[str] = None
    condition_treated: Optional[str] = None


class PractitionerResponseRequest(BaseModel):
    """Practitioner response to review."""
    practitioner_id: UUID
    response: str


class CreateListingRequest(BaseModel):
    """Create a practitioner listing."""
    user_id: UUID
    name: str
    title: str
    bio: str
    specialties: List[str]
    conditions_treated: List[str]
    modalities: List[str]
    city: str
    state: str
    postal_code: str
    country: str = "UK"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    offers_telehealth: bool = False
    initial_consult_price: float
    followup_price: float
    currency: str = "GBP"


class RecordInteractionRequest(BaseModel):
    """Record user interaction."""
    user_id: UUID
    interaction_type: str  # view, search, book, favorite
    practitioner_id: Optional[UUID] = None
    metadata: Optional[Dict] = None


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@router.post("/search")
async def search_practitioners(request: SearchRequest):
    """
    Search for practitioners with filters.

    Returns paginated results with relevance scores.
    """
    # Build filters
    filters = SearchFilters(
        specialties=[Specialty(s) for s in request.specialties] if request.specialties else None,
        conditions=request.conditions,
        modalities=request.modalities,
        city=request.city,
        postal_code=request.postal_code,
        max_distance_miles=request.max_distance_miles,
        latitude=request.latitude,
        longitude=request.longitude,
        telehealth_only=request.telehealth_only,
        min_price=request.min_price,
        max_price=request.max_price,
        min_sana_index=request.min_sana_index,
        min_rating=request.min_rating,
        verified_only=request.verified_only,
        available_date=request.available_date
    )

    # Get sort option
    try:
        sort_by = SortOption(request.sort_by)
    except ValueError:
        sort_by = SortOption.RELEVANCE

    results = search_service.search(
        query=request.query,
        filters=filters,
        sort_by=sort_by,
        page=request.page,
        per_page=request.per_page
    )

    return {
        "results": [
            {
                "practitioner": {
                    "id": str(r.practitioner.id),
                    "name": r.practitioner.name,
                    "title": r.practitioner.title,
                    "city": r.practitioner.city,
                    "specialties": [s.value for s in r.practitioner.specialties],
                    "initial_price": r.practitioner.initial_consult_price,
                    "currency": r.practitioner.currency,
                    "sana_index": r.practitioner.sana_index,
                    "average_rating": r.practitioner.average_rating,
                    "total_reviews": r.practitioner.total_reviews,
                    "is_verified": r.practitioner.is_verified,
                    "offers_telehealth": r.practitioner.offers_telehealth,
                    "next_available": r.practitioner.next_available.isoformat() if r.practitioner.next_available else None
                },
                "relevance_score": r.relevance_score,
                "distance_miles": r.distance_miles,
                "match_reasons": r.match_reasons
            }
            for r in results["results"]
        ],
        "total": results["total"],
        "page": results["page"],
        "per_page": results["per_page"],
        "total_pages": results["total_pages"]
    }


@router.get("/practitioners/{listing_id}")
async def get_practitioner_profile(listing_id: UUID):
    """Get full practitioner profile."""
    listing = search_service.get_listing(listing_id)

    if not listing:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    # Get reviews aggregation
    aggregation = review_service.get_aggregation(listing_id)

    # Get similar practitioners
    similar = search_service.get_similar_practitioners(listing_id, limit=4)

    return {
        "profile": {
            "id": str(listing.id),
            "user_id": str(listing.user_id),
            "name": listing.name,
            "title": listing.title,
            "bio": listing.bio,
            "profile_image": listing.profile_image,
            "specialties": [s.value for s in listing.specialties],
            "conditions_treated": listing.conditions_treated,
            "modalities": listing.modalities,
            "city": listing.city,
            "state": listing.state,
            "country": listing.country,
            "offers_telehealth": listing.offers_telehealth,
            "initial_consult_price": listing.initial_consult_price,
            "followup_price": listing.followup_price,
            "currency": listing.currency,
            "sana_index": listing.sana_index,
            "is_verified": listing.is_verified,
            "credentials_verified": listing.credentials_verified,
            "accepts_new_clients": listing.accepts_new_clients,
            "next_available": listing.next_available.isoformat() if listing.next_available else None,
            "typical_wait_days": listing.typical_wait_days
        },
        "ratings": {
            "average": aggregation.average_rating if aggregation else 0,
            "total_reviews": aggregation.total_reviews if aggregation else 0,
            "distribution": aggregation.rating_distribution if aggregation else {},
            "communication": aggregation.communication_avg if aggregation else 0,
            "punctuality": aggregation.punctuality_avg if aggregation else 0,
            "effectiveness": aggregation.effectiveness_avg if aggregation else 0,
            "value": aggregation.value_avg if aggregation else 0
        },
        "similar_practitioners": [
            {
                "id": str(s.id),
                "name": s.name,
                "title": s.title,
                "city": s.city,
                "sana_index": s.sana_index,
                "average_rating": s.average_rating
            }
            for s in similar
        ]
    }


@router.get("/specialties")
async def get_specialties():
    """Get all available specialties with counts."""
    return search_service.get_specialties()


@router.get("/cities")
async def get_cities():
    """Get all cities with practitioner counts."""
    return search_service.get_cities()


@router.post("/listings")
async def create_listing(request: CreateListingRequest):
    """Create a new practitioner listing."""
    from datetime import datetime
    from uuid import uuid4

    listing = PractitionerListing(
        id=uuid4(),
        user_id=request.user_id,
        name=request.name,
        title=request.title,
        bio=request.bio,
        specialties=[Specialty(s) for s in request.specialties],
        conditions_treated=request.conditions_treated,
        modalities=request.modalities,
        city=request.city,
        state=request.state,
        country=request.country,
        postal_code=request.postal_code,
        latitude=request.latitude,
        longitude=request.longitude,
        offers_telehealth=request.offers_telehealth,
        initial_consult_price=request.initial_consult_price,
        followup_price=request.followup_price,
        currency=request.currency,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    search_service.add_listing(listing)

    return {
        "id": str(listing.id),
        "message": "Listing created successfully"
    }


# ============================================================================
# REVIEW ENDPOINTS
# ============================================================================

@router.post("/reviews")
async def submit_review(request: SubmitReviewRequest):
    """Submit a review for a practitioner."""
    # Check if can review
    eligibility = review_service.can_review(
        request.practitioner_id,
        request.client_id,
        request.booking_id
    )

    if not eligibility["can_review"]:
        raise HTTPException(
            status_code=400,
            detail=eligibility["reason"]
        )

    review = review_service.submit_review(
        practitioner_id=request.practitioner_id,
        client_id=request.client_id,
        overall_rating=request.overall_rating,
        title=request.title,
        content=request.content,
        booking_id=request.booking_id,
        communication_rating=request.communication_rating,
        punctuality_rating=request.punctuality_rating,
        effectiveness_rating=request.effectiveness_rating,
        value_rating=request.value_rating,
        treatment_type=request.treatment_type,
        condition_treated=request.condition_treated
    )

    return {
        "id": str(review.id),
        "status": review.status.value,
        "verified_booking": review.verified_booking
    }


@router.get("/reviews/{practitioner_id}")
async def get_practitioner_reviews(
    practitioner_id: UUID,
    sort_by: str = "recent",
    rating_filter: Optional[int] = Query(default=None, ge=1, le=5),
    verified_only: bool = False,
    page: int = 1,
    per_page: int = 10
):
    """Get reviews for a practitioner."""
    results = review_service.get_practitioner_reviews(
        practitioner_id,
        sort_by=sort_by,
        rating_filter=rating_filter,
        verified_only=verified_only,
        page=page,
        per_page=per_page
    )

    return {
        "reviews": [
            {
                "id": str(r.id),
                "overall_rating": r.overall_rating,
                "title": r.title,
                "content": r.content,
                "treatment_type": r.treatment_type,
                "verified_booking": r.verified_booking,
                "helpful_count": r.helpful_count,
                "practitioner_response": r.practitioner_response,
                "response_date": r.response_date.isoformat() if r.response_date else None,
                "created_at": r.created_at.isoformat()
            }
            for r in results["reviews"]
        ],
        "total": results["total"],
        "page": results["page"],
        "aggregation": {
            "average_rating": results["aggregation"].average_rating if results["aggregation"] else 0,
            "total_reviews": results["aggregation"].total_reviews if results["aggregation"] else 0,
            "distribution": results["aggregation"].rating_distribution if results["aggregation"] else {}
        }
    }


@router.post("/reviews/{review_id}/response")
async def add_review_response(review_id: UUID, request: PractitionerResponseRequest):
    """Add practitioner response to a review."""
    review = review_service.add_practitioner_response(
        review_id,
        request.practitioner_id,
        request.response
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")

    return {"message": "Response added", "review_id": str(review_id)}


@router.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(review_id: UUID, user_id: UUID):
    """Mark a review as helpful."""
    success = review_service.mark_helpful(review_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Review not found")

    return {"message": "Marked as helpful"}


@router.post("/reviews/{review_id}/report")
async def report_review(review_id: UUID, reporter_id: UUID, reason: str = ""):
    """Report a review for moderation."""
    success = review_service.report_review(review_id, reporter_id, reason)

    if not success:
        raise HTTPException(status_code=404, detail="Review not found")

    return {"message": "Review reported"}


@router.get("/reviews/eligibility/{practitioner_id}/{client_id}")
async def check_review_eligibility(
    practitioner_id: UUID,
    client_id: UUID,
    booking_id: Optional[UUID] = None
):
    """Check if a client can review a practitioner."""
    return review_service.can_review(practitioner_id, client_id, booking_id)


# ============================================================================
# DISCOVERY ENDPOINTS
# ============================================================================

@router.get("/discover")
async def get_discovery_page(user_id: Optional[UUID] = None):
    """
    Get complete discovery page content.

    Returns featured, trending, new, top rated, and recommendations.
    """
    return discovery_service.get_discovery_page(user_id)


@router.get("/discover/featured")
async def get_featured(feature_type: Optional[str] = None):
    """Get featured practitioners."""
    return discovery_service.get_featured(feature_type)


@router.get("/discover/trending")
async def get_trending(limit: int = 10):
    """Get trending practitioners."""
    results = discovery_service.get_trending(limit)

    return [
        {
            "practitioner": {
                "id": str(r["practitioner"].id),
                "name": r["practitioner"].name,
                "title": r["practitioner"].title,
                "city": r["practitioner"].city,
                "sana_index": r["practitioner"].sana_index,
                "average_rating": r["practitioner"].average_rating
            },
            "trending_score": r.get("trending_score", 0)
        }
        for r in results
    ]


@router.get("/discover/new")
async def get_new_practitioners(limit: int = 10):
    """Get recently joined practitioners."""
    results = discovery_service.get_new_practitioners(limit)

    return [
        {
            "practitioner": {
                "id": str(r["practitioner"].id),
                "name": r["practitioner"].name,
                "title": r["practitioner"].title,
                "city": r["practitioner"].city,
                "sana_index": r["practitioner"].sana_index
            },
            "days_since_joined": r["days_since_joined"]
        }
        for r in results
    ]


@router.get("/discover/top-rated")
async def get_top_rated(limit: int = 10):
    """Get top rated practitioners."""
    results = discovery_service.get_top_rated(limit)

    return [
        {
            "practitioner": {
                "id": str(r["practitioner"].id),
                "name": r["practitioner"].name,
                "title": r["practitioner"].title,
                "city": r["practitioner"].city
            },
            "average_rating": r["average_rating"],
            "total_reviews": r["total_reviews"]
        }
        for r in results
    ]


@router.get("/discover/recommended/{user_id}")
async def get_recommendations(user_id: UUID, limit: int = 10):
    """Get personalized recommendations for a user."""
    results = discovery_service.get_recommended_for_user(user_id, limit)

    return [
        {
            "practitioner": {
                "id": str(r["practitioner"].id),
                "name": r["practitioner"].name,
                "title": r["practitioner"].title,
                "city": r["practitioner"].city,
                "sana_index": r["practitioner"].sana_index,
                "average_rating": r["practitioner"].average_rating
            },
            "reason": r.get("reason", "")
        }
        for r in results
    ]


@router.get("/discover/categories")
async def get_category_spotlights():
    """Get category spotlights."""
    return discovery_service.get_categories_spotlight()


@router.post("/interactions")
async def record_interaction(request: RecordInteractionRequest):
    """Record a user interaction for recommendations."""
    discovery_service.record_interaction(
        request.user_id,
        request.interaction_type,
        request.practitioner_id,
        request.metadata
    )

    return {"message": "Interaction recorded"}


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@router.get("/test-setup")
async def test_marketplace():
    """Set up test data for marketplace."""
    from datetime import datetime, timedelta
    from uuid import uuid4

    # Create test practitioners
    practitioners = []

    for i, (name, specialty, city) in enumerate([
        ("Dr. Sarah Chen", "acupuncture", "London"),
        ("James Wilson", "herbalism", "Manchester"),
        ("Dr. Emma Thompson", "naturopathy", "London"),
        ("Michael Brown", "massage_therapy", "Bristol"),
        ("Dr. Aisha Patel", "ayurveda", "Birmingham")
    ]):
        listing = PractitionerListing(
            id=uuid4(),
            user_id=uuid4(),
            name=name,
            title=f"Certified {specialty.replace('_', ' ').title()} Practitioner",
            bio=f"Experienced practitioner specializing in {specialty}.",
            specialties=[Specialty(specialty)],
            conditions_treated=["Stress", "Pain", "Anxiety", "Fatigue"],
            modalities=["Manual therapy", "Consultation"],
            city=city,
            state="",
            postal_code=f"SW{i+1} 1AA",
            initial_consult_price=80 + (i * 10),
            followup_price=60 + (i * 5),
            sana_index=70 + (i * 5),
            average_rating=4.0 + (i * 0.2),
            total_reviews=10 + (i * 5),
            is_verified=i % 2 == 0,
            offers_telehealth=i % 2 == 1,
            next_available=datetime.utcnow() + timedelta(days=i+1),
            created_at=datetime.utcnow() - timedelta(days=30-i),
            updated_at=datetime.utcnow()
        )

        search_service.add_listing(listing)
        practitioners.append(listing)

        # Add some reviews
        for j in range(3):
            review_service.submit_review(
                practitioner_id=listing.id,
                client_id=uuid4(),
                overall_rating=4 + (j % 2),
                title=f"Great experience #{j+1}",
                content=f"Had a wonderful session with {name}. Very professional and knowledgeable.",
                communication_rating=4 + (j % 2),
                effectiveness_rating=4 + (j % 2)
            )

    return {
        "message": "Test marketplace data created",
        "practitioners": [
            {"id": str(p.id), "name": p.name, "city": p.city}
            for p in practitioners
        ]
    }
