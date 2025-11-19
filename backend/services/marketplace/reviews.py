"""
Review and rating service for practitioners.
"""

from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReviewStatus(str, Enum):
    """Status of a review."""
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"
    HIDDEN = "hidden"


class Review(BaseModel):
    """A client review of a practitioner."""
    id: UUID
    practitioner_id: UUID
    client_id: UUID
    booking_id: Optional[UUID] = None

    # Ratings (1-5 stars)
    overall_rating: int = Field(ge=1, le=5)
    communication_rating: Optional[int] = Field(default=None, ge=1, le=5)
    punctuality_rating: Optional[int] = Field(default=None, ge=1, le=5)
    effectiveness_rating: Optional[int] = Field(default=None, ge=1, le=5)
    value_rating: Optional[int] = Field(default=None, ge=1, le=5)

    # Content
    title: str
    content: str
    treatment_type: Optional[str] = None
    condition_treated: Optional[str] = None

    # Response
    practitioner_response: Optional[str] = None
    response_date: Optional[datetime] = None

    # Verification
    verified_booking: bool = False
    status: ReviewStatus = ReviewStatus.PENDING

    # Metadata
    helpful_count: int = 0
    report_count: int = 0
    created_at: datetime
    updated_at: datetime


class RatingAggregation(BaseModel):
    """Aggregated ratings for a practitioner."""
    practitioner_id: UUID
    total_reviews: int = 0

    # Averages
    average_rating: float = 0.0
    communication_avg: float = 0.0
    punctuality_avg: float = 0.0
    effectiveness_avg: float = 0.0
    value_avg: float = 0.0

    # Distribution
    rating_distribution: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    # Trends
    rating_trend: float = 0.0  # Change over time
    reviews_last_30_days: int = 0

    updated_at: datetime


class ReviewService:
    """
    Manages practitioner reviews and ratings.

    Features:
    - Submit and moderate reviews
    - Calculate aggregations
    - Detect fake/suspicious reviews
    - Practitioner responses
    """

    def __init__(self):
        self.reviews: Dict[UUID, Review] = {}
        self.aggregations: Dict[UUID, RatingAggregation] = {}
        logger.info("ReviewService initialized")

    def submit_review(
        self,
        practitioner_id: UUID,
        client_id: UUID,
        overall_rating: int,
        title: str,
        content: str,
        booking_id: Optional[UUID] = None,
        communication_rating: Optional[int] = None,
        punctuality_rating: Optional[int] = None,
        effectiveness_rating: Optional[int] = None,
        value_rating: Optional[int] = None,
        treatment_type: Optional[str] = None,
        condition_treated: Optional[str] = None
    ) -> Review:
        """
        Submit a new review.

        Args:
            practitioner_id: Practitioner being reviewed
            client_id: Client submitting review
            overall_rating: 1-5 star rating
            title: Review title
            content: Review content
            booking_id: Associated booking (for verification)
            ...: Optional sub-ratings

        Returns:
            Created review
        """
        now = datetime.utcnow()

        review = Review(
            id=uuid4(),
            practitioner_id=practitioner_id,
            client_id=client_id,
            booking_id=booking_id,
            overall_rating=overall_rating,
            communication_rating=communication_rating,
            punctuality_rating=punctuality_rating,
            effectiveness_rating=effectiveness_rating,
            value_rating=value_rating,
            title=title,
            content=content,
            treatment_type=treatment_type,
            condition_treated=condition_treated,
            verified_booking=booking_id is not None,
            status=ReviewStatus.APPROVED,  # Auto-approve for now
            created_at=now,
            updated_at=now
        )

        # Check for suspicious patterns
        if self._is_suspicious(review, client_id):
            review.status = ReviewStatus.FLAGGED
            logger.warning(f"Review {review.id} flagged as suspicious")

        self.reviews[review.id] = review

        # Update aggregations
        self._update_aggregation(practitioner_id)

        logger.info(
            f"Review {review.id} submitted for practitioner {practitioner_id}"
        )

        return review

    def _is_suspicious(self, review: Review, client_id: UUID) -> bool:
        """Check if review seems suspicious."""
        # Check for duplicate reviews from same client
        existing = [
            r for r in self.reviews.values()
            if r.practitioner_id == review.practitioner_id
            and r.client_id == client_id
            and r.status == ReviewStatus.APPROVED
        ]

        if existing:
            return True

        # Check for very short content
        if len(review.content) < 20:
            return True

        return False

    def _update_aggregation(self, practitioner_id: UUID) -> None:
        """Recalculate aggregated ratings for a practitioner."""
        reviews = [
            r for r in self.reviews.values()
            if r.practitioner_id == practitioner_id
            and r.status == ReviewStatus.APPROVED
        ]

        if not reviews:
            if practitioner_id in self.aggregations:
                del self.aggregations[practitioner_id]
            return

        # Calculate averages
        total = len(reviews)
        avg_rating = sum(r.overall_rating for r in reviews) / total

        # Sub-ratings (only from reviews that have them)
        comm_reviews = [r for r in reviews if r.communication_rating]
        punct_reviews = [r for r in reviews if r.punctuality_rating]
        effect_reviews = [r for r in reviews if r.effectiveness_rating]
        value_reviews = [r for r in reviews if r.value_rating]

        comm_avg = (
            sum(r.communication_rating for r in comm_reviews) / len(comm_reviews)
            if comm_reviews else 0
        )
        punct_avg = (
            sum(r.punctuality_rating for r in punct_reviews) / len(punct_reviews)
            if punct_reviews else 0
        )
        effect_avg = (
            sum(r.effectiveness_rating for r in effect_reviews) / len(effect_reviews)
            if effect_reviews else 0
        )
        value_avg = (
            sum(r.value_rating for r in value_reviews) / len(value_reviews)
            if value_reviews else 0
        )

        # Distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in reviews:
            distribution[r.overall_rating] += 1

        # Recent trend
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_reviews = [
            r for r in reviews
            if r.created_at >= thirty_days_ago
        ]

        # Calculate trend (recent avg vs overall avg)
        trend = 0.0
        if recent_reviews and len(reviews) > len(recent_reviews):
            recent_avg = sum(r.overall_rating for r in recent_reviews) / len(recent_reviews)
            trend = recent_avg - avg_rating

        self.aggregations[practitioner_id] = RatingAggregation(
            practitioner_id=practitioner_id,
            total_reviews=total,
            average_rating=round(avg_rating, 2),
            communication_avg=round(comm_avg, 2),
            punctuality_avg=round(punct_avg, 2),
            effectiveness_avg=round(effect_avg, 2),
            value_avg=round(value_avg, 2),
            rating_distribution=distribution,
            rating_trend=round(trend, 2),
            reviews_last_30_days=len(recent_reviews),
            updated_at=datetime.utcnow()
        )

    def get_practitioner_reviews(
        self,
        practitioner_id: UUID,
        sort_by: str = "recent",
        rating_filter: Optional[int] = None,
        verified_only: bool = False,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Get reviews for a practitioner.

        Args:
            practitioner_id: Practitioner UUID
            sort_by: Sort option (recent, helpful, rating_high, rating_low)
            rating_filter: Filter by specific rating
            verified_only: Only verified booking reviews
            page: Page number
            per_page: Results per page

        Returns:
            Paginated reviews
        """
        reviews = [
            r for r in self.reviews.values()
            if r.practitioner_id == practitioner_id
            and r.status == ReviewStatus.APPROVED
        ]

        # Apply filters
        if rating_filter:
            reviews = [r for r in reviews if r.overall_rating == rating_filter]

        if verified_only:
            reviews = [r for r in reviews if r.verified_booking]

        # Sort
        if sort_by == "recent":
            reviews.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "helpful":
            reviews.sort(key=lambda x: x.helpful_count, reverse=True)
        elif sort_by == "rating_high":
            reviews.sort(key=lambda x: x.overall_rating, reverse=True)
        elif sort_by == "rating_low":
            reviews.sort(key=lambda x: x.overall_rating)

        # Paginate
        total = len(reviews)
        start = (page - 1) * per_page
        end = start + per_page
        page_reviews = reviews[start:end]

        return {
            "reviews": page_reviews,
            "total": total,
            "page": page,
            "per_page": per_page,
            "aggregation": self.aggregations.get(practitioner_id)
        }

    def get_aggregation(self, practitioner_id: UUID) -> Optional[RatingAggregation]:
        """Get rating aggregation for a practitioner."""
        return self.aggregations.get(practitioner_id)

    def add_practitioner_response(
        self,
        review_id: UUID,
        practitioner_id: UUID,
        response: str
    ) -> Optional[Review]:
        """
        Add practitioner response to a review.

        Args:
            review_id: Review UUID
            practitioner_id: Practitioner UUID (for verification)
            response: Response text

        Returns:
            Updated review or None
        """
        if review_id not in self.reviews:
            return None

        review = self.reviews[review_id]

        # Verify ownership
        if review.practitioner_id != practitioner_id:
            return None

        review.practitioner_response = response
        review.response_date = datetime.utcnow()
        review.updated_at = datetime.utcnow()

        return review

    def mark_helpful(self, review_id: UUID, user_id: UUID) -> bool:
        """Mark a review as helpful."""
        if review_id not in self.reviews:
            return False

        # In production, track who marked helpful to prevent duplicates
        self.reviews[review_id].helpful_count += 1
        return True

    def report_review(
        self,
        review_id: UUID,
        reporter_id: UUID,
        reason: str
    ) -> bool:
        """Report a review for moderation."""
        if review_id not in self.reviews:
            return False

        review = self.reviews[review_id]
        review.report_count += 1

        # Auto-flag if too many reports
        if review.report_count >= 3:
            review.status = ReviewStatus.FLAGGED
            logger.warning(f"Review {review_id} auto-flagged due to reports")

        return True

    def get_client_reviews(self, client_id: UUID) -> List[Review]:
        """Get all reviews submitted by a client."""
        return [
            r for r in self.reviews.values()
            if r.client_id == client_id
        ]

    def can_review(
        self,
        practitioner_id: UUID,
        client_id: UUID,
        booking_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Check if a client can review a practitioner.

        Returns eligibility and reason.
        """
        # Check for existing review
        existing = [
            r for r in self.reviews.values()
            if r.practitioner_id == practitioner_id
            and r.client_id == client_id
            and r.status in [ReviewStatus.APPROVED, ReviewStatus.PENDING]
        ]

        if existing:
            return {
                "can_review": False,
                "reason": "You have already reviewed this practitioner"
            }

        # In production, check if client has had a session
        # For now, allow all

        return {
            "can_review": True,
            "verified_booking": booking_id is not None
        }

    def get_review_stats(self) -> Dict[str, Any]:
        """Get overall review statistics."""
        total = len(self.reviews)
        approved = len([r for r in self.reviews.values() if r.status == ReviewStatus.APPROVED])
        flagged = len([r for r in self.reviews.values() if r.status == ReviewStatus.FLAGGED])

        all_ratings = [r.overall_rating for r in self.reviews.values() if r.status == ReviewStatus.APPROVED]
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0

        return {
            "total_reviews": total,
            "approved": approved,
            "flagged": flagged,
            "pending": total - approved - flagged,
            "platform_average": round(avg_rating, 2)
        }
