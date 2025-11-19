"""
Discovery service for featured and recommended practitioners.
"""

from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel
import random
import logging

logger = logging.getLogger(__name__)


class FeaturedPractitioner(BaseModel):
    """A featured practitioner on marketplace."""
    practitioner_id: UUID
    feature_type: str  # "spotlight", "trending", "new", "top_rated"
    reason: str
    priority: int = 0
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True


class DiscoveryService:
    """
    Manages practitioner discovery and recommendations.

    Features:
    - Featured practitioners
    - Trending practitioners
    - Personalized recommendations
    - Category spotlights
    """

    def __init__(self, search_service=None, review_service=None):
        self.search_service = search_service
        self.review_service = review_service
        self.featured: List[FeaturedPractitioner] = []
        self.user_interactions: Dict[UUID, List[Dict]] = {}  # Track user behavior
        logger.info("DiscoveryService initialized")

    def set_services(self, search_service, review_service):
        """Set service dependencies."""
        self.search_service = search_service
        self.review_service = review_service

    def add_featured(
        self,
        practitioner_id: UUID,
        feature_type: str,
        reason: str,
        priority: int = 0,
        duration_days: Optional[int] = None
    ) -> FeaturedPractitioner:
        """Add a practitioner to featured section."""
        now = datetime.utcnow()
        end_date = now + timedelta(days=duration_days) if duration_days else None

        featured = FeaturedPractitioner(
            practitioner_id=practitioner_id,
            feature_type=feature_type,
            reason=reason,
            priority=priority,
            start_date=now,
            end_date=end_date
        )

        self.featured.append(featured)
        return featured

    def get_featured(self, feature_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get featured practitioners.

        Args:
            feature_type: Filter by type (spotlight, trending, new, top_rated)

        Returns:
            List of featured practitioners with details
        """
        now = datetime.utcnow()

        # Filter active featured
        active = [
            f for f in self.featured
            if f.is_active
            and (f.end_date is None or f.end_date > now)
        ]

        if feature_type:
            active = [f for f in active if f.feature_type == feature_type]

        # Sort by priority
        active.sort(key=lambda x: x.priority, reverse=True)

        # Get practitioner details
        results = []
        if self.search_service:
            for f in active:
                listing = self.search_service.get_listing(f.practitioner_id)
                if listing:
                    results.append({
                        "practitioner": listing,
                        "feature_type": f.feature_type,
                        "reason": f.reason
                    })

        return results

    def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending practitioners based on recent activity.

        Factors:
        - Recent bookings
        - Recent reviews
        - Profile views
        - SANA Index changes
        """
        if not self.search_service:
            return []

        # Score all practitioners by trending metrics
        scored = []
        for listing in self.search_service.listings.values():
            if not listing.is_active:
                continue

            score = 0

            # Recent reviews boost
            if self.review_service:
                agg = self.review_service.get_aggregation(listing.id)
                if agg:
                    score += agg.reviews_last_30_days * 10
                    # Positive trend boost
                    if agg.rating_trend > 0:
                        score += agg.rating_trend * 5

            # High SANA Index
            if listing.sana_index >= 80:
                score += 20

            # Quick availability
            if listing.next_available:
                days_until = (listing.next_available.date() - datetime.utcnow().date()).days
                if days_until <= 3:
                    score += 10

            # New practitioners get a boost
            days_since_created = (datetime.utcnow() - listing.created_at).days
            if days_since_created <= 30:
                score += 15

            if score > 0:
                scored.append({
                    "practitioner": listing,
                    "trending_score": score,
                    "feature_type": "trending"
                })

        # Sort and return top
        scored.sort(key=lambda x: x["trending_score"], reverse=True)
        return scored[:limit]

    def get_new_practitioners(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently joined practitioners."""
        if not self.search_service:
            return []

        # Get practitioners created in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        new_practitioners = [
            listing for listing in self.search_service.listings.values()
            if listing.is_active and listing.created_at >= thirty_days_ago
        ]

        # Sort by SANA Index (quality new practitioners first)
        new_practitioners.sort(key=lambda x: x.sana_index, reverse=True)

        return [
            {
                "practitioner": p,
                "feature_type": "new",
                "days_since_joined": (datetime.utcnow() - p.created_at).days
            }
            for p in new_practitioners[:limit]
        ]

    def get_top_rated(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top rated practitioners."""
        if not self.search_service or not self.review_service:
            return []

        # Get practitioners with good ratings and sufficient reviews
        rated = []
        for listing in self.search_service.listings.values():
            if not listing.is_active:
                continue

            agg = self.review_service.get_aggregation(listing.id)
            if agg and agg.total_reviews >= 5:  # Minimum reviews threshold
                rated.append({
                    "practitioner": listing,
                    "feature_type": "top_rated",
                    "average_rating": agg.average_rating,
                    "total_reviews": agg.total_reviews
                })

        # Sort by rating then review count
        rated.sort(
            key=lambda x: (x["average_rating"], x["total_reviews"]),
            reverse=True
        )

        return rated[:limit]

    def get_recommended_for_user(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a user.

        Based on:
        - Past bookings
        - Viewed profiles
        - Similar users
        - Health profile
        """
        if not self.search_service:
            return []

        # Get user's interaction history
        interactions = self.user_interactions.get(user_id, [])

        recommendations = []

        if interactions:
            # Get specialties and conditions user has shown interest in
            interested_specialties = set()
            interested_conditions = set()

            for interaction in interactions:
                if "specialty" in interaction:
                    interested_specialties.add(interaction["specialty"])
                if "condition" in interaction:
                    interested_conditions.add(interaction["condition"])

            # Find practitioners matching interests
            for listing in self.search_service.listings.values():
                if not listing.is_active:
                    continue

                score = 0

                # Specialty match
                specialty_overlap = len(
                    interested_specialties & set(s.value for s in listing.specialties)
                )
                score += specialty_overlap * 20

                # Condition match
                condition_overlap = len(
                    interested_conditions &
                    set(c.lower() for c in listing.conditions_treated)
                )
                score += condition_overlap * 15

                # Quality factors
                score += listing.sana_index * 0.1

                if score > 0:
                    recommendations.append({
                        "practitioner": listing,
                        "recommendation_score": score,
                        "reason": self._get_recommendation_reason(
                            listing, interested_specialties, interested_conditions
                        )
                    })

            # Sort by score
            recommendations.sort(
                key=lambda x: x["recommendation_score"],
                reverse=True
            )

        # If not enough recommendations, add popular ones
        if len(recommendations) < limit:
            trending = self.get_trending(limit - len(recommendations))
            for t in trending:
                if not any(
                    r["practitioner"].id == t["practitioner"].id
                    for r in recommendations
                ):
                    recommendations.append({
                        "practitioner": t["practitioner"],
                        "recommendation_score": t.get("trending_score", 0),
                        "reason": "Popular on SANA"
                    })

        return recommendations[:limit]

    def _get_recommendation_reason(
        self,
        listing,
        interested_specialties,
        interested_conditions
    ) -> str:
        """Generate a recommendation reason."""
        reasons = []

        # Check specialty match
        for specialty in listing.specialties:
            if specialty.value in interested_specialties:
                reasons.append(f"Specializes in {specialty.value.replace('_', ' ')}")
                break

        # Check condition match
        for condition in listing.conditions_treated:
            if condition.lower() in interested_conditions:
                reasons.append(f"Treats {condition}")
                break

        if listing.sana_index >= 80:
            reasons.append("High SANA Index")

        return reasons[0] if reasons else "Recommended for you"

    def record_interaction(
        self,
        user_id: UUID,
        interaction_type: str,
        practitioner_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Record a user interaction for recommendations.

        Types: view, search, book, favorite
        """
        if user_id not in self.user_interactions:
            self.user_interactions[user_id] = []

        interaction = {
            "type": interaction_type,
            "practitioner_id": str(practitioner_id) if practitioner_id else None,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }

        self.user_interactions[user_id].append(interaction)

        # Keep only recent interactions (last 100)
        if len(self.user_interactions[user_id]) > 100:
            self.user_interactions[user_id] = self.user_interactions[user_id][-100:]

    def get_categories_spotlight(self) -> List[Dict[str, Any]]:
        """Get spotlight for each category/specialty."""
        if not self.search_service:
            return []

        specialties = self.search_service.get_specialties()
        spotlights = []

        for spec_info in specialties[:6]:  # Top 6 categories
            specialty = spec_info["specialty"]

            # Get top practitioner in this specialty
            from .search import SearchFilters, Specialty
            try:
                spec_enum = Specialty(specialty)
                filters = SearchFilters(specialties=[spec_enum])
                results = self.search_service.search(filters=filters, per_page=1)

                if results["results"]:
                    top = results["results"][0]
                    spotlights.append({
                        "specialty": specialty,
                        "practitioner_count": spec_info["count"],
                        "top_practitioner": top.practitioner,
                        "display_name": specialty.replace("_", " ").title()
                    })
            except Exception:
                continue

        return spotlights

    def get_discovery_page(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get complete discovery page content.

        Returns all sections for the marketplace homepage.
        """
        result = {
            "featured": self.get_featured("spotlight")[:3],
            "trending": self.get_trending(6),
            "new_arrivals": self.get_new_practitioners(6),
            "top_rated": self.get_top_rated(6),
            "categories": self.get_categories_spotlight()
        }

        if user_id:
            result["recommended"] = self.get_recommended_for_user(user_id, 6)

        return result
