"""
SANA Index Algorithm

Calculates credibility scores (0-100) for practitioners based on:
- Credentials: 30% - Qualifications, certifications, education
- Outcomes: 50% - Client health improvements
- Reviews: 10% - Client feedback and ratings
- Verification: 10% - Identity and credential verification status
"""
import math
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

import numpy as np

from .models import IndexInput, IndexOutput, IndexComponent


class SANAIndexCalculator:
    """SANA Index score calculator for practitioner credibility."""

    # Component weights (must sum to 1.0)
    COMPONENT_WEIGHTS = {
        "credentials": 0.30,
        "outcomes": 0.50,
        "reviews": 0.10,
        "verification": 0.10
    }

    # Credential type scores
    CREDENTIAL_SCORES = {
        # Degrees
        "phd": 25,
        "doctorate": 25,
        "md": 25,
        "do": 25,
        "masters": 20,
        "msc": 20,
        "ma": 18,
        "bachelors": 15,
        "bsc": 15,
        "ba": 14,

        # Professional licenses
        "medical_license": 25,
        "hcpc_registration": 22,
        "nursing_license": 20,
        "clinical_license": 20,

        # Certifications
        "board_certification": 18,
        "specialist_certification": 15,
        "professional_certification": 12,
        "practitioner_certification": 10,

        # CAM specific
        "acupuncture_license": 18,
        "herbalist_certification": 15,
        "naturopath_license": 18,
        "homeopath_certification": 12,
        "nutrition_certification": 12,

        # General
        "diploma": 8,
        "certificate": 5,
        "training": 3,
    }

    # Known reputable institutions (sample)
    KNOWN_INSTITUTIONS = {
        "university of oxford": 1.2,
        "university of cambridge": 1.2,
        "imperial college london": 1.15,
        "university college london": 1.15,
        "king's college london": 1.1,
        "university of edinburgh": 1.1,
        "university of manchester": 1.05,
        "university of birmingham": 1.05,
        "nhs": 1.1,
        "royal college": 1.15,
    }

    def __init__(self):
        """Initialize the SANA Index calculator."""
        self.current_year = datetime.now().year

    def calculate(self, input_data: IndexInput) -> IndexOutput:
        """
        Calculate SANA Index score.

        Args:
            input_data: Practitioner data including credentials, outcomes, reviews

        Returns:
            SANA Index score (0-100) with component breakdown
        """
        components = []

        # Calculate each component
        cred_score, cred_details = self._calculate_credentials_score(
            input_data.credentials
        )
        components.append(IndexComponent(
            name="credentials",
            score=cred_score,
            weight=self.COMPONENT_WEIGHTS["credentials"],
            details=cred_details
        ))

        outcome_score, outcome_details = self._calculate_outcomes_score(
            input_data.outcome_data
        )
        components.append(IndexComponent(
            name="outcomes",
            score=outcome_score,
            weight=self.COMPONENT_WEIGHTS["outcomes"],
            details=outcome_details
        ))

        review_score, review_details = self._calculate_reviews_score(
            input_data.reviews
        )
        components.append(IndexComponent(
            name="reviews",
            score=review_score,
            weight=self.COMPONENT_WEIGHTS["reviews"],
            details=review_details
        ))

        verif_score, verif_details = self._calculate_verification_score(
            input_data.verification_status,
            input_data.credentials
        )
        components.append(IndexComponent(
            name="verification",
            score=verif_score,
            weight=self.COMPONENT_WEIGHTS["verification"],
            details=verif_details
        ))

        # Calculate weighted overall score
        overall_score = sum(
            comp.score * comp.weight for comp in components
        )

        # Calculate percentile (simplified - in production would compare to database)
        percentile = self._estimate_percentile(overall_score)

        # Determine trend (simplified - in production would compare historical)
        trend = self._determine_trend(input_data.outcome_data)

        return IndexOutput(
            practitioner_id=input_data.practitioner_id,
            overall_score=round(overall_score, 1),
            components=components,
            percentile=percentile,
            trend=trend
        )

    def _calculate_credentials_score(
        self,
        credentials: List[str]
    ) -> tuple[float, Dict[str, Any]]:
        """
        Calculate credentials component score (0-100).

        Factors:
        - Credential types and their values
        - Institution reputation
        - Diversity of qualifications
        """
        if not credentials:
            return 0.0, {"reason": "No credentials provided"}

        total_points = 0
        credential_breakdown = []

        for cred in credentials:
            cred_lower = cred.lower()

            # Find matching credential type
            points = 0
            matched_type = None
            for cred_type, cred_points in self.CREDENTIAL_SCORES.items():
                if cred_type.replace("_", " ") in cred_lower or cred_type in cred_lower:
                    points = cred_points
                    matched_type = cred_type
                    break

            # Default points for unrecognized credentials
            if points == 0:
                points = 3
                matched_type = "other"

            # Institution multiplier
            multiplier = 1.0
            for inst, mult in self.KNOWN_INSTITUTIONS.items():
                if inst in cred_lower:
                    multiplier = mult
                    break

            final_points = points * multiplier
            total_points += final_points

            credential_breakdown.append({
                "credential": cred,
                "type": matched_type,
                "base_points": points,
                "multiplier": multiplier,
                "final_points": final_points
            })

        # Normalize to 0-100 scale
        # Cap at 100 points raw, diminishing returns after 50
        if total_points <= 50:
            score = total_points * 2
        else:
            # Logarithmic scaling for higher values
            score = 100 - (50 / math.log10(total_points - 39))

        score = min(100, max(0, score))

        # Diversity bonus (up to 10 points)
        unique_types = len(set(c["type"] for c in credential_breakdown))
        diversity_bonus = min(10, unique_types * 2)
        score = min(100, score + diversity_bonus)

        return score, {
            "total_credentials": len(credentials),
            "raw_points": total_points,
            "diversity_bonus": diversity_bonus,
            "breakdown": credential_breakdown
        }

    def _calculate_outcomes_score(
        self,
        outcome_data: Dict
    ) -> tuple[float, Dict[str, Any]]:
        """
        Calculate outcomes component score (0-100).

        Factors:
        - Mean improvement percentage
        - Sample size (more data = higher confidence)
        - Consistency (lower variance = better)
        - Retention rate
        """
        if not outcome_data:
            return 50.0, {"reason": "No outcome data - default score"}

        # Extract metrics from outcome_data
        total_clients = outcome_data.get("total_clients", 0)
        mean_improvement = outcome_data.get("mean_improvement", 0)
        improvements = outcome_data.get("improvements", [])
        retention_rate = outcome_data.get("retention_rate", 0.5)

        if total_clients == 0:
            return 50.0, {"reason": "No clients - default score"}

        # Base score from mean improvement (0-50 points)
        # 50% improvement = 50 points
        improvement_score = min(50, mean_improvement)

        # Sample size bonus (0-20 points)
        # Logarithmic scale: 10 clients = 10pts, 100 = 15pts, 1000 = 20pts
        if total_clients >= 10:
            sample_bonus = min(20, 5 * math.log10(total_clients))
        else:
            sample_bonus = total_clients / 2

        # Consistency bonus (0-15 points)
        if improvements and len(improvements) > 1:
            improvements_array = np.array(improvements)
            cv = np.std(improvements_array) / max(np.mean(improvements_array), 1)
            consistency_bonus = min(15, max(0, 15 * (1 - cv)))
        else:
            consistency_bonus = 7.5  # Default if not enough data

        # Retention bonus (0-15 points)
        retention_bonus = retention_rate * 15

        total_score = improvement_score + sample_bonus + consistency_bonus + retention_bonus
        score = min(100, max(0, total_score))

        return score, {
            "total_clients": total_clients,
            "mean_improvement": mean_improvement,
            "retention_rate": retention_rate,
            "improvement_score": round(improvement_score, 1),
            "sample_bonus": round(sample_bonus, 1),
            "consistency_bonus": round(consistency_bonus, 1),
            "retention_bonus": round(retention_bonus, 1)
        }

    def _calculate_reviews_score(
        self,
        reviews: List[Dict]
    ) -> tuple[float, Dict[str, Any]]:
        """
        Calculate reviews component score (0-100).

        Factors:
        - Average rating
        - Number of reviews
        - Recency of reviews
        - Review quality (length, detail)
        """
        if not reviews:
            return 50.0, {"reason": "No reviews - default score"}

        ratings = []
        recency_weights = []
        quality_scores = []

        for review in reviews:
            rating = review.get("rating", 3)
            ratings.append(rating)

            # Recency weight (reviews in last year worth more)
            review_date = review.get("date")
            if review_date:
                try:
                    if isinstance(review_date, str):
                        review_year = int(review_date[:4])
                    else:
                        review_year = review_date.year
                    years_old = self.current_year - review_year
                    recency_weight = max(0.5, 1 - (years_old * 0.1))
                except Exception:
                    recency_weight = 0.8
            else:
                recency_weight = 0.8
            recency_weights.append(recency_weight)

            # Quality score based on review text length
            text = review.get("text", "")
            if len(text) > 200:
                quality_scores.append(1.0)
            elif len(text) > 50:
                quality_scores.append(0.7)
            else:
                quality_scores.append(0.4)

        # Weighted average rating
        if recency_weights:
            weighted_rating = np.average(ratings, weights=recency_weights)
        else:
            weighted_rating = np.mean(ratings)

        # Convert 1-5 rating to 0-100 scale (base score)
        # 3 stars = 60, 4 stars = 80, 5 stars = 100
        base_score = (weighted_rating - 1) * 25

        # Volume bonus (0-10 points)
        volume_bonus = min(10, len(reviews) * 0.5)

        # Quality bonus (0-10 points)
        avg_quality = np.mean(quality_scores) if quality_scores else 0.5
        quality_bonus = avg_quality * 10

        total_score = base_score + volume_bonus + quality_bonus
        score = min(100, max(0, total_score))

        return score, {
            "total_reviews": len(reviews),
            "average_rating": round(float(weighted_rating), 2),
            "base_score": round(base_score, 1),
            "volume_bonus": round(volume_bonus, 1),
            "quality_bonus": round(quality_bonus, 1)
        }

    def _calculate_verification_score(
        self,
        verification_status: bool,
        credentials: List[str]
    ) -> tuple[float, Dict[str, Any]]:
        """
        Calculate verification component score (0-100).

        Factors:
        - Basic verification status
        - Credential verification level
        - Identity verification
        """
        score = 0
        details = {}

        # Basic verification (40 points)
        if verification_status:
            score += 40
            details["basic_verified"] = True
        else:
            details["basic_verified"] = False

        # Credential count verification bonus (up to 30 points)
        # More verified credentials = higher score
        verified_count = len(credentials) if verification_status else 0
        cred_bonus = min(30, verified_count * 5)
        score += cred_bonus
        details["verified_credentials"] = verified_count
        details["credential_bonus"] = cred_bonus

        # Infer verification tier based on credentials
        has_license = any(
            "license" in c.lower() or "registration" in c.lower()
            for c in credentials
        )
        has_degree = any(
            any(d in c.lower() for d in ["phd", "md", "masters", "msc", "bachelors", "bsc"])
            for c in credentials
        )

        # Tier bonus (up to 30 points)
        tier_bonus = 0
        if has_license and has_degree:
            tier_bonus = 30
            details["tier"] = "premium"
        elif has_license or has_degree:
            tier_bonus = 20
            details["tier"] = "standard"
        elif len(credentials) > 0:
            tier_bonus = 10
            details["tier"] = "basic"
        else:
            details["tier"] = "unverified"

        score += tier_bonus
        details["tier_bonus"] = tier_bonus

        return min(100, score), details

    def _estimate_percentile(self, score: float) -> float:
        """
        Estimate percentile ranking based on score.

        In production, would compare against actual database distribution.
        """
        # Simplified sigmoid-based percentile estimation
        # Assumes normal distribution centered around 60
        if score >= 90:
            return 95 + (score - 90) * 0.5
        elif score >= 80:
            return 85 + (score - 80)
        elif score >= 70:
            return 65 + (score - 70) * 2
        elif score >= 60:
            return 40 + (score - 60) * 2.5
        elif score >= 50:
            return 20 + (score - 50) * 2
        else:
            return max(1, score * 0.4)

    def _determine_trend(self, outcome_data: Dict) -> str:
        """
        Determine score trend based on outcome history.

        In production, would compare against historical scores.
        """
        if not outcome_data:
            return "stable"

        # Check if there's trend data
        trend_data = outcome_data.get("trend", [])
        if len(trend_data) < 2:
            return "stable"

        # Simple trend detection
        recent = trend_data[-3:] if len(trend_data) >= 3 else trend_data
        if len(recent) >= 2:
            change = recent[-1] - recent[0]
            if change > 5:
                return "improving"
            elif change < -5:
                return "declining"

        return "stable"


def calculate_sana_index(
    practitioner_id: UUID,
    credentials: List[str],
    outcome_data: Dict,
    reviews: List[Dict],
    verification_status: bool
) -> IndexOutput:
    """
    Calculate SANA Index for a practitioner.

    Args:
        practitioner_id: Practitioner identifier
        credentials: List of credential strings
        outcome_data: Dict with keys:
            - total_clients: int
            - mean_improvement: float (0-100)
            - improvements: List[float] (individual improvements)
            - retention_rate: float (0-1)
        reviews: List of dicts with keys:
            - rating: float (1-5)
            - date: str or datetime
            - text: str
        verification_status: Whether practitioner is verified

    Returns:
        IndexOutput with overall score and component breakdown
    """
    calculator = SANAIndexCalculator()
    input_data = IndexInput(
        practitioner_id=practitioner_id,
        credentials=credentials,
        outcome_data=outcome_data,
        reviews=reviews,
        verification_status=verification_status
    )
    return calculator.calculate(input_data)
