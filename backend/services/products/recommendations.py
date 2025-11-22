"""
Product Recommendation Service
==============================
Provides intelligent product recommendations based on user profile,
safety, and effectiveness.
"""

import logging
from typing import List, Optional, Dict
from uuid import UUID

from algorithms.product_scanner import (
    Product,
    ProductCategory,
    UserHealthProfile,
    ProductRecommendation,
    RecommendationRequest,
    RecommendationResponse,
    SafetyAnalyzer,
)
from .database import ProductDatabaseService

logger = logging.getLogger(__name__)


class ProductRecommendationService:
    """
    Product Recommendation Service

    Provides recommendations based on:
    - User health profile and conditions
    - Current product (for alternatives)
    - Safety scores
    - Evidence/effectiveness ratings
    - Community reviews
    """

    # Condition to ingredient/product mappings
    CONDITION_RECOMMENDATIONS = {
        "anxiety": {
            "categories": [ProductCategory.HERBS],
            "ingredients": [
                "ashwagandha", "l-theanine", "magnesium", "passionflower",
                "valerian", "chamomile", "lavender"
            ],
            "avoid": ["caffeine", "guarana", "ginseng"],
        },
        "sleep": {
            "categories": [ProductCategory.HERBS, ProductCategory.AMINO_ACIDS],
            "ingredients": [
                "melatonin", "valerian", "magnesium", "l-theanine",
                "passionflower", "chamomile", "gaba"
            ],
            "avoid": ["caffeine", "guarana", "ginseng"],
        },
        "depression": {
            "categories": [ProductCategory.HERBS, ProductCategory.VITAMINS],
            "ingredients": [
                "vitamin d", "omega-3", "sam-e", "5-htp",
                "st. john's wort", "vitamin b12", "folate"
            ],
            "caution": ["st. john's wort"],  # May interact with SSRIs
        },
        "energy": {
            "categories": [ProductCategory.VITAMINS, ProductCategory.HERBS],
            "ingredients": [
                "vitamin b12", "iron", "coq10", "ashwagandha",
                "rhodiola", "ginseng", "maca"
            ],
        },
        "immune support": {
            "categories": [ProductCategory.VITAMINS, ProductCategory.HERBS],
            "ingredients": [
                "vitamin c", "vitamin d", "zinc", "elderberry",
                "echinacea", "astragalus"
            ],
        },
        "digestion": {
            "categories": [ProductCategory.PROBIOTICS, ProductCategory.ENZYMES],
            "ingredients": [
                "probiotics", "digestive enzymes", "ginger",
                "peppermint", "fiber", "l-glutamine"
            ],
        },
        "inflammation": {
            "categories": [ProductCategory.HERBS],
            "ingredients": [
                "turmeric", "curcumin", "omega-3", "boswellia",
                "ginger", "quercetin"
            ],
        },
        "joint health": {
            "categories": [ProductCategory.COMBINATION],
            "ingredients": [
                "glucosamine", "chondroitin", "msm", "collagen",
                "turmeric", "omega-3", "boswellia"
            ],
        },
        "heart health": {
            "categories": [ProductCategory.COMBINATION, ProductCategory.VITAMINS],
            "ingredients": [
                "omega-3", "coq10", "magnesium", "vitamin k2",
                "nattokinase", "garlic"
            ],
        },
        "cognitive": {
            "categories": [ProductCategory.HERBS, ProductCategory.AMINO_ACIDS],
            "ingredients": [
                "omega-3", "ginkgo biloba", "bacopa", "lion's mane",
                "phosphatidylserine", "acetyl-l-carnitine"
            ],
        },
    }

    def __init__(self, product_db: ProductDatabaseService = None):
        """
        Initialize the recommendation service

        Args:
            product_db: Product database service
        """
        self.product_db = product_db or ProductDatabaseService()
        self.safety_analyzer = SafetyAnalyzer()

    def get_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Get product recommendations based on request

        Args:
            request: RecommendationRequest with criteria

        Returns:
            RecommendationResponse with recommendations
        """
        recommendations = []

        # If condition specified, get recommendations for that condition
        if request.condition:
            recommendations = self._get_recommendations_for_condition(
                condition=request.condition,
                health_profile=request.user_health_profile,
                max_results=request.max_results,
            )

        # If product_id specified, get alternatives
        elif request.product_id:
            recommendations = self._get_alternatives(
                product_id=request.product_id,
                health_profile=request.user_health_profile,
                max_results=request.max_results,
            )

        # Otherwise, get general recommendations based on profile
        elif request.user_health_profile:
            recommendations = self._get_profile_recommendations(
                health_profile=request.user_health_profile,
                max_results=request.max_results,
            )

        based_on = "condition" if request.condition else \
                   "current_product" if request.product_id else \
                   "health_profile"

        return RecommendationResponse(
            recommendations=recommendations,
            based_on=based_on,
            total_found=len(recommendations),
        )

    def _get_recommendations_for_condition(
        self,
        condition: str,
        health_profile: Optional[UserHealthProfile],
        max_results: int
    ) -> List[ProductRecommendation]:
        """Get recommendations for a specific health condition"""
        recommendations = []

        # Find matching condition config
        condition_lower = condition.lower()
        config = None
        for cond_name, cond_config in self.CONDITION_RECOMMENDATIONS.items():
            if cond_name in condition_lower or condition_lower in cond_name:
                config = cond_config
                break

        if not config:
            # No specific recommendations, return top-rated products
            return self._get_top_rated_recommendations(max_results)

        # Get products with recommended ingredients
        all_products = list(self.product_db._product_cache.values())
        scored_products = []

        for product in all_products:
            score = 0
            reasons = []

            # Check category match
            if product.category in config.get("categories", []):
                score += 20
                reasons.append(f"Good category for {condition}")

            # Check ingredient matches
            product_ingredients = [
                (ing.standardized_name or ing.name).lower()
                for ing in product.ingredients
            ]

            for rec_ing in config.get("ingredients", []):
                for prod_ing in product_ingredients:
                    if rec_ing in prod_ing or prod_ing in rec_ing:
                        score += 15
                        reasons.append(f"Contains {rec_ing}")
                        break

            # Check for avoided ingredients
            for avoid_ing in config.get("avoid", []):
                for prod_ing in product_ingredients:
                    if avoid_ing in prod_ing:
                        score -= 30
                        reasons.append(f"Contains {avoid_ing} (not recommended)")

            # Add evidence and safety scores
            score += product.evidence_score * 0.3
            score += product.safety_score * 0.2

            # Check safety against user profile if provided
            is_safe = True
            if health_profile:
                safety_result = self.safety_analyzer.analyze_safety(
                    product, health_profile
                )
                if not safety_result.is_safe:
                    is_safe = False
                    score -= 50
                    reasons.append("Safety concerns for your profile")

            if score > 0:
                scored_products.append({
                    "product": product,
                    "score": score,
                    "reasons": reasons,
                    "is_safe": is_safe,
                })

        # Sort by score
        scored_products.sort(key=lambda x: x["score"], reverse=True)

        # Create recommendations
        for item in scored_products[:max_results]:
            recommendations.append(ProductRecommendation(
                product=item["product"],
                recommendation_score=min(100, item["score"]),
                reasons=item["reasons"],
                is_safer_alternative=item["is_safe"],
            ))

        return recommendations

    def _get_alternatives(
        self,
        product_id: UUID,
        health_profile: Optional[UserHealthProfile],
        max_results: int
    ) -> List[ProductRecommendation]:
        """Get alternative products similar to the given product"""
        current_product = self.product_db.get_product_by_id(product_id)
        if not current_product:
            return []

        recommendations = []
        all_products = list(self.product_db._product_cache.values())

        # Get current product's ingredients
        current_ingredients = set(
            (ing.standardized_name or ing.name).lower()
            for ing in current_product.ingredients
        )

        for product in all_products:
            # Skip current product
            if product.id == product_id:
                continue

            score = 0
            reasons = []

            # Same category bonus
            if product.category == current_product.category:
                score += 30
                reasons.append("Same category")

            # Similar ingredients
            product_ingredients = set(
                (ing.standardized_name or ing.name).lower()
                for ing in product.ingredients
            )

            overlap = current_ingredients & product_ingredients
            if overlap:
                score += len(overlap) * 10
                reasons.append(f"Similar ingredients ({len(overlap)} match)")

            # Better safety score
            if product.safety_score > current_product.safety_score:
                score += 15
                reasons.append("Higher safety score")
                is_safer = True
            else:
                is_safer = False

            # Better evidence score
            if product.evidence_score > current_product.evidence_score:
                score += 10
                reasons.append("Better evidence")

            # Better rating
            if product.average_rating > current_product.average_rating:
                score += 5
                reasons.append("Higher rated")

            # Check safety against user profile
            if health_profile:
                safety_result = self.safety_analyzer.analyze_safety(
                    product, health_profile
                )
                if safety_result.is_safe:
                    score += 20
                    reasons.append("Safe for your profile")
                else:
                    score -= 30

            if score > 0:
                recommendations.append(ProductRecommendation(
                    product=product,
                    recommendation_score=min(100, score),
                    reasons=reasons,
                    is_safer_alternative=is_safer,
                ))

        # Sort by score
        recommendations.sort(
            key=lambda x: x.recommendation_score,
            reverse=True
        )

        return recommendations[:max_results]

    def _get_profile_recommendations(
        self,
        health_profile: UserHealthProfile,
        max_results: int
    ) -> List[ProductRecommendation]:
        """Get recommendations based on user's health profile"""
        recommendations = []

        # Get recommendations for each condition
        for condition in health_profile.conditions:
            cond_recs = self._get_recommendations_for_condition(
                condition=condition,
                health_profile=health_profile,
                max_results=3,  # Get top 3 per condition
            )
            recommendations.extend(cond_recs)

        # Remove duplicates and sort by score
        seen_ids = set()
        unique_recs = []
        for rec in recommendations:
            if rec.product.id not in seen_ids:
                seen_ids.add(rec.product.id)
                unique_recs.append(rec)

        unique_recs.sort(
            key=lambda x: x.recommendation_score,
            reverse=True
        )

        return unique_recs[:max_results]

    def _get_top_rated_recommendations(
        self,
        max_results: int
    ) -> List[ProductRecommendation]:
        """Get top-rated products as recommendations"""
        top_products = self.product_db.get_top_rated_products(max_results)

        return [
            ProductRecommendation(
                product=product,
                recommendation_score=product.average_rating * 20,
                reasons=[
                    f"Highly rated ({product.average_rating}/5)",
                    f"{product.review_count} reviews"
                ],
            )
            for product in top_products
        ]

    def get_safer_alternatives(
        self,
        product_id: UUID,
        health_profile: UserHealthProfile,
        max_results: int = 5
    ) -> List[ProductRecommendation]:
        """
        Get safer alternatives for a product that has safety concerns

        Args:
            product_id: Product to find alternatives for
            health_profile: User's health profile
            max_results: Maximum results

        Returns:
            List of safer alternatives
        """
        current_product = self.product_db.get_product_by_id(product_id)
        if not current_product:
            return []

        # Get current product's safety result
        current_safety = self.safety_analyzer.analyze_safety(
            current_product, health_profile
        )

        alternatives = self._get_alternatives(
            product_id=product_id,
            health_profile=health_profile,
            max_results=max_results * 2,  # Get more to filter
        )

        # Filter to only safer alternatives
        safer = [
            alt for alt in alternatives
            if alt.is_safer_alternative or alt.recommendation_score > 50
        ]

        return safer[:max_results]
