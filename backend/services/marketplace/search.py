"""
Marketplace search service for practitioner discovery.
"""

from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, date, time
from pydantic import BaseModel, Field
from enum import Enum
import math
import logging

logger = logging.getLogger(__name__)


class Specialty(str, Enum):
    """Practitioner specialties available on marketplace."""
    ACUPUNCTURE = "acupuncture"
    HERBALISM = "herbalism"
    NATUROPATHY = "naturopathy"
    HOMEOPATHY = "homeopathy"
    AYURVEDA = "ayurveda"
    TCM = "traditional_chinese_medicine"
    MASSAGE = "massage_therapy"
    NUTRITION = "nutrition"
    YOGA = "yoga_therapy"
    MEDITATION = "meditation"
    REIKI = "reiki"
    CHIROPRACTIC = "chiropractic"
    OSTEOPATHY = "osteopathy"
    AROMATHERAPY = "aromatherapy"
    REFLEXOLOGY = "reflexology"


class SortOption(str, Enum):
    """Sort options for search results."""
    RELEVANCE = "relevance"
    SANA_INDEX = "sana_index"
    PRICE_LOW = "price_low"
    PRICE_HIGH = "price_high"
    RATING = "rating"
    DISTANCE = "distance"
    AVAILABILITY = "availability"


class PractitionerListing(BaseModel):
    """A practitioner listing in marketplace."""
    id: UUID
    user_id: UUID

    # Profile
    name: str
    title: str  # e.g., "Licensed Acupuncturist"
    bio: str
    profile_image: Optional[str] = None

    # Specialties & services
    specialties: List[Specialty]
    conditions_treated: List[str]
    modalities: List[str]

    # Location
    city: str
    state: str
    country: str = "UK"
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    offers_telehealth: bool = False

    # Pricing
    initial_consult_price: float
    followup_price: float
    currency: str = "GBP"

    # SANA metrics
    sana_index: float = 0.0
    total_reviews: int = 0
    average_rating: float = 0.0

    # Availability
    next_available: Optional[datetime] = None
    typical_wait_days: int = 7

    # Verification
    is_verified: bool = False
    credentials_verified: bool = False

    # Status
    is_active: bool = True
    accepts_new_clients: bool = True

    created_at: datetime
    updated_at: datetime


class SearchFilters(BaseModel):
    """Filters for marketplace search."""
    specialties: Optional[List[Specialty]] = None
    conditions: Optional[List[str]] = None
    modalities: Optional[List[str]] = None

    # Location
    city: Optional[str] = None
    postal_code: Optional[str] = None
    max_distance_miles: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    telehealth_only: bool = False

    # Price
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    # Quality
    min_sana_index: Optional[float] = None
    min_rating: Optional[float] = None
    verified_only: bool = False

    # Availability
    available_date: Optional[date] = None
    available_time: Optional[time] = None

    # Other
    accepts_new_clients: bool = True


class SearchResult(BaseModel):
    """Search result with relevance info."""
    practitioner: PractitionerListing
    relevance_score: float
    distance_miles: Optional[float] = None
    match_reasons: List[str] = []


class MarketplaceSearchService:
    """
    Search and filter practitioners in marketplace.

    Features:
    - Full-text search
    - Multi-faceted filtering
    - Geolocation distance
    - Relevance scoring
    - SANA Index integration
    """

    def __init__(self):
        self.listings: Dict[UUID, PractitionerListing] = {}
        self._index: Dict[str, List[UUID]] = {}  # Inverted index
        logger.info("MarketplaceSearchService initialized")

    def add_listing(self, listing: PractitionerListing) -> None:
        """Add or update a practitioner listing."""
        self.listings[listing.id] = listing
        self._update_index(listing)
        logger.info(f"Added/updated listing {listing.id}")

    def _update_index(self, listing: PractitionerListing) -> None:
        """Update inverted index for search."""
        # Index by specialty
        for specialty in listing.specialties:
            key = f"specialty:{specialty.value}"
            if key not in self._index:
                self._index[key] = []
            if listing.id not in self._index[key]:
                self._index[key].append(listing.id)

        # Index by city
        key = f"city:{listing.city.lower()}"
        if key not in self._index:
            self._index[key] = []
        if listing.id not in self._index[key]:
            self._index[key].append(listing.id)

        # Index by conditions
        for condition in listing.conditions_treated:
            key = f"condition:{condition.lower()}"
            if key not in self._index:
                self._index[key] = []
            if listing.id not in self._index[key]:
                self._index[key].append(listing.id)

    def search(
        self,
        query: Optional[str] = None,
        filters: Optional[SearchFilters] = None,
        sort_by: SortOption = SortOption.RELEVANCE,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search for practitioners.

        Args:
            query: Text search query
            filters: Search filters
            sort_by: Sort option
            page: Page number
            per_page: Results per page

        Returns:
            Paginated search results
        """
        # Start with all active listings
        candidates = [
            l for l in self.listings.values()
            if l.is_active
        ]

        # Apply filters
        if filters:
            candidates = self._apply_filters(candidates, filters)

        # Text search
        if query:
            candidates = self._text_search(candidates, query)

        # Calculate relevance scores
        results = []
        for listing in candidates:
            score = self._calculate_relevance(listing, query, filters)
            distance = None

            if filters and filters.latitude and filters.longitude:
                distance = self._calculate_distance(
                    filters.latitude, filters.longitude,
                    listing.latitude, listing.longitude
                )

            results.append(SearchResult(
                practitioner=listing,
                relevance_score=score,
                distance_miles=distance,
                match_reasons=self._get_match_reasons(listing, query, filters)
            ))

        # Sort results
        results = self._sort_results(results, sort_by)

        # Paginate
        total = len(results)
        start = (page - 1) * per_page
        end = start + per_page
        page_results = results[start:end]

        return {
            "results": page_results,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": math.ceil(total / per_page) if total > 0 else 0
        }

    def _apply_filters(
        self,
        candidates: List[PractitionerListing],
        filters: SearchFilters
    ) -> List[PractitionerListing]:
        """Apply all filters to candidates."""
        results = candidates

        # Specialty filter
        if filters.specialties:
            results = [
                l for l in results
                if any(s in l.specialties for s in filters.specialties)
            ]

        # Conditions filter
        if filters.conditions:
            filter_conditions = [c.lower() for c in filters.conditions]
            results = [
                l for l in results
                if any(c.lower() in filter_conditions for c in l.conditions_treated)
            ]

        # Modalities filter
        if filters.modalities:
            filter_modalities = [m.lower() for m in filters.modalities]
            results = [
                l for l in results
                if any(m.lower() in filter_modalities for m in l.modalities)
            ]

        # City filter
        if filters.city:
            results = [
                l for l in results
                if l.city.lower() == filters.city.lower()
            ]

        # Telehealth filter
        if filters.telehealth_only:
            results = [l for l in results if l.offers_telehealth]

        # Price filters
        if filters.min_price is not None:
            results = [
                l for l in results
                if l.initial_consult_price >= filters.min_price
            ]

        if filters.max_price is not None:
            results = [
                l for l in results
                if l.initial_consult_price <= filters.max_price
            ]

        # SANA Index filter
        if filters.min_sana_index is not None:
            results = [
                l for l in results
                if l.sana_index >= filters.min_sana_index
            ]

        # Rating filter
        if filters.min_rating is not None:
            results = [
                l for l in results
                if l.average_rating >= filters.min_rating
            ]

        # Verified filter
        if filters.verified_only:
            results = [l for l in results if l.is_verified]

        # Accepts new clients
        if filters.accepts_new_clients:
            results = [l for l in results if l.accepts_new_clients]

        # Distance filter
        if filters.max_distance_miles and filters.latitude and filters.longitude:
            filtered = []
            for l in results:
                if l.latitude and l.longitude:
                    distance = self._calculate_distance(
                        filters.latitude, filters.longitude,
                        l.latitude, l.longitude
                    )
                    if distance <= filters.max_distance_miles:
                        filtered.append(l)
                elif l.offers_telehealth:
                    filtered.append(l)
            results = filtered

        return results

    def _text_search(
        self,
        candidates: List[PractitionerListing],
        query: str
    ) -> List[PractitionerListing]:
        """Perform text search across listing fields."""
        query_lower = query.lower()
        query_terms = query_lower.split()

        scored = []
        for listing in candidates:
            # Build searchable text
            searchable = " ".join([
                listing.name.lower(),
                listing.title.lower(),
                listing.bio.lower(),
                " ".join(s.value for s in listing.specialties),
                " ".join(c.lower() for c in listing.conditions_treated),
                " ".join(m.lower() for m in listing.modalities),
                listing.city.lower()
            ])

            # Count matching terms
            matches = sum(1 for term in query_terms if term in searchable)

            if matches > 0:
                scored.append((listing, matches))

        # Sort by match count and return
        scored.sort(key=lambda x: x[1], reverse=True)
        return [l for l, _ in scored]

    def _calculate_relevance(
        self,
        listing: PractitionerListing,
        query: Optional[str],
        filters: Optional[SearchFilters]
    ) -> float:
        """Calculate relevance score for a listing."""
        score = 50.0  # Base score

        # SANA Index boost (up to 30 points)
        score += listing.sana_index * 0.3

        # Rating boost (up to 10 points)
        if listing.total_reviews > 0:
            score += listing.average_rating * 2

        # Verified boost
        if listing.is_verified:
            score += 5

        # Availability boost
        if listing.next_available:
            days_until = (listing.next_available.date() - date.today()).days
            if days_until <= 7:
                score += 5

        # Review count boost (social proof)
        score += min(listing.total_reviews * 0.1, 5)

        return min(score, 100)

    def _get_match_reasons(
        self,
        listing: PractitionerListing,
        query: Optional[str],
        filters: Optional[SearchFilters]
    ) -> List[str]:
        """Get reasons why this listing matched."""
        reasons = []

        if listing.is_verified:
            reasons.append("Verified practitioner")

        if listing.sana_index >= 80:
            reasons.append("High SANA Index")

        if listing.average_rating >= 4.5 and listing.total_reviews >= 10:
            reasons.append("Highly rated")

        if listing.next_available:
            days_until = (listing.next_available.date() - date.today()).days
            if days_until <= 3:
                reasons.append("Available soon")

        if listing.offers_telehealth:
            reasons.append("Telehealth available")

        return reasons

    def _sort_results(
        self,
        results: List[SearchResult],
        sort_by: SortOption
    ) -> List[SearchResult]:
        """Sort results by specified option."""
        if sort_by == SortOption.RELEVANCE:
            return sorted(results, key=lambda x: x.relevance_score, reverse=True)

        elif sort_by == SortOption.SANA_INDEX:
            return sorted(
                results,
                key=lambda x: x.practitioner.sana_index,
                reverse=True
            )

        elif sort_by == SortOption.PRICE_LOW:
            return sorted(
                results,
                key=lambda x: x.practitioner.initial_consult_price
            )

        elif sort_by == SortOption.PRICE_HIGH:
            return sorted(
                results,
                key=lambda x: x.practitioner.initial_consult_price,
                reverse=True
            )

        elif sort_by == SortOption.RATING:
            return sorted(
                results,
                key=lambda x: (
                    x.practitioner.average_rating,
                    x.practitioner.total_reviews
                ),
                reverse=True
            )

        elif sort_by == SortOption.DISTANCE:
            # None distances go to end
            return sorted(
                results,
                key=lambda x: x.distance_miles if x.distance_miles else float('inf')
            )

        elif sort_by == SortOption.AVAILABILITY:
            # Sort by next available date
            def avail_key(r):
                if r.practitioner.next_available:
                    return r.practitioner.next_available
                return datetime.max
            return sorted(results, key=avail_key)

        return results

    def _calculate_distance(
        self,
        lat1: float, lon1: float,
        lat2: Optional[float], lon2: Optional[float]
    ) -> Optional[float]:
        """Calculate distance between two points in miles using Haversine."""
        if lat2 is None or lon2 is None:
            return None

        R = 3959  # Earth's radius in miles

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def get_listing(self, listing_id: UUID) -> Optional[PractitionerListing]:
        """Get a specific listing."""
        return self.listings.get(listing_id)

    def get_specialties(self) -> List[Dict[str, Any]]:
        """Get all available specialties with counts."""
        counts = {}
        for listing in self.listings.values():
            if listing.is_active:
                for specialty in listing.specialties:
                    counts[specialty.value] = counts.get(specialty.value, 0) + 1

        return [
            {"specialty": s, "count": c}
            for s, c in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]

    def get_cities(self) -> List[Dict[str, Any]]:
        """Get all cities with practitioner counts."""
        counts = {}
        for listing in self.listings.values():
            if listing.is_active:
                counts[listing.city] = counts.get(listing.city, 0) + 1

        return [
            {"city": c, "count": n}
            for c, n in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]

    def get_similar_practitioners(
        self,
        listing_id: UUID,
        limit: int = 5
    ) -> List[PractitionerListing]:
        """Get practitioners similar to a given one."""
        if listing_id not in self.listings:
            return []

        target = self.listings[listing_id]

        # Score other listings by similarity
        scored = []
        for listing in self.listings.values():
            if listing.id == listing_id or not listing.is_active:
                continue

            score = 0

            # Specialty overlap
            overlap = len(set(target.specialties) & set(listing.specialties))
            score += overlap * 20

            # Same city
            if listing.city == target.city:
                score += 10

            # Similar price range (within 30%)
            if target.initial_consult_price > 0:
                price_diff = abs(
                    listing.initial_consult_price - target.initial_consult_price
                ) / target.initial_consult_price
                if price_diff <= 0.3:
                    score += 10

            # Condition overlap
            target_conditions = set(c.lower() for c in target.conditions_treated)
            listing_conditions = set(c.lower() for c in listing.conditions_treated)
            condition_overlap = len(target_conditions & listing_conditions)
            score += condition_overlap * 5

            if score > 0:
                scored.append((listing, score))

        # Sort and return top
        scored.sort(key=lambda x: (x[1], x[0].sana_index), reverse=True)
        return [l for l, _ in scored[:limit]]
