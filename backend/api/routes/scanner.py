"""
Product Scanner API Routes
==========================
API endpoints for the SANA Product Scanner - "Vivino for Supplements"
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

from algorithms.product_scanner import (
    Product,
    UserHealthProfile,
    SafetyCheckResult,
    InteractionWarning,
    RecommendationRequest,
    ProductCategory,
)
from services.products import (
    ProductScannerService,
    ProductRecommendationService,
)

router = APIRouter()

# Initialize services
scanner_service = ProductScannerService()
recommendation_service = ProductRecommendationService()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class BarcodeScanRequest(BaseModel):
    """Request body for barcode scanning"""
    barcode: str = Field(..., min_length=8, max_length=14, description="Product barcode")


class ImageScanRequest(BaseModel):
    """Request body for image OCR scanning"""
    image_base64: str = Field(..., min_length=100, description="Base64-encoded image")
    image_format: str = Field(default="jpeg", description="Image format (jpeg, png, webp)")


class SafetyCheckRequest(BaseModel):
    """Request body for personalized safety check"""
    product_id: UUID = Field(..., description="Product ID to check")
    conditions: List[str] = Field(default_factory=list, description="User's health conditions")
    medications: List[str] = Field(default_factory=list, description="Current medications")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")
    age: Optional[int] = Field(None, ge=1, le=120, description="User's age")
    is_pregnant: bool = Field(default=False)
    is_breastfeeding: bool = Field(default=False)
    supplements_currently_taking: List[str] = Field(
        default_factory=list,
        description="Other supplements currently being taken"
    )


class InteractionCheckRequest(BaseModel):
    """Request body for interaction checking"""
    product_id: UUID = Field(..., description="Product ID to check")
    medications: List[str] = Field(default_factory=list, description="Current medications")
    other_supplements: List[str] = Field(
        default_factory=list,
        description="Other supplements being taken"
    )


class QuickCheckRequest(BaseModel):
    """Request body for quick ingredient check"""
    ingredient: str = Field(..., description="Ingredient name to check")
    medications: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)


class RecommendationRequestBody(BaseModel):
    """Request body for recommendations"""
    product_id: Optional[UUID] = Field(None, description="Current product (for alternatives)")
    condition: Optional[str] = Field(None, description="Target health condition")
    conditions: List[str] = Field(default_factory=list, description="User's conditions")
    medications: List[str] = Field(default_factory=list, description="Current medications")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")
    max_results: int = Field(default=10, ge=1, le=50)


class ProductSearchRequest(BaseModel):
    """Request body for product search"""
    query: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    min_safety_score: float = Field(default=0, ge=0, le=100)
    limit: int = Field(default=20, ge=1, le=100)


# ============================================================================
# SCANNING ENDPOINTS
# ============================================================================

@router.post("/barcode", summary="Scan product barcode")
async def scan_barcode(request: BarcodeScanRequest):
    """
    Scan a product barcode and return product information.

    Supports:
    - UPC-A (12 digits)
    - UPC-E (8 digits)
    - EAN-13 (13 digits)
    - EAN-8 (8 digits)

    Returns product details if found in our database, or an error if not found.
    """
    try:
        result = scanner_service.scan_barcode(request.barcode)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/image", summary="Scan product label image")
async def scan_image(request: ImageScanRequest):
    """
    Scan a product label image using OCR to extract information.

    The image should be a clear photo of the supplement facts label
    or ingredients list.

    Returns extracted product name, ingredients, and serving size.
    """
    try:
        result = scanner_service.scan_image(request.image_base64)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image scan failed: {str(e)}")


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@router.get("/product/{product_id}", summary="Get product details")
async def get_product(product_id: UUID):
    """
    Get full product details including evidence scores and known interactions.
    """
    result = scanner_service.get_product_details(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result


@router.post("/products/search", summary="Search products")
async def search_products(request: ProductSearchRequest):
    """
    Search products with filters.

    Can filter by:
    - Query (matches name, brand, ingredients)
    - Category (herbs, vitamins, minerals, etc.)
    - Brand
    - Minimum safety score
    """
    results = scanner_service.search_products(
        query=request.query,
        category=request.category,
        brand=request.brand,
        min_safety_score=request.min_safety_score,
        limit=request.limit,
    )
    return {
        "products": results,
        "total": len(results),
        "query": request.query,
        "filters": {
            "category": request.category,
            "brand": request.brand,
            "min_safety_score": request.min_safety_score,
        }
    }


@router.get("/products/popular", summary="Get popular products")
async def get_popular_products(limit: int = Query(10, ge=1, le=50)):
    """Get most scanned/popular products"""
    products = scanner_service.get_popular_products(limit)
    return {"products": products, "total": len(products)}


@router.get("/products/top-rated", summary="Get top rated products")
async def get_top_rated_products(limit: int = Query(10, ge=1, le=50)):
    """Get highest rated products"""
    products = scanner_service.get_top_rated_products(limit)
    return {"products": products, "total": len(products)}


@router.get("/products/categories", summary="Get product categories")
async def get_categories():
    """Get all available product categories"""
    return {
        "categories": [
            {"value": cat.value, "label": cat.value.replace("_", " ").title()}
            for cat in ProductCategory
        ]
    }


# ============================================================================
# SAFETY ENDPOINTS
# ============================================================================

@router.post("/safety-check", summary="Personalized safety analysis")
async def check_product_safety(request: SafetyCheckRequest):
    """
    Perform a personalized safety check for a product based on user's
    health profile.

    Checks for:
    - Medication interactions
    - Condition contraindications
    - Allergies
    - Pregnancy/breastfeeding concerns
    - Age-related warnings

    Returns:
    - Overall safety score (0-100)
    - Safety rating (safe, generally_safe, use_caution, not_recommended, contraindicated)
    - Detailed warnings and recommendations
    """
    try:
        # Build health profile
        health_profile = UserHealthProfile(
            user_id=UUID("00000000-0000-0000-0000-000000000000"),  # Anonymous
            conditions=request.conditions,
            medications=request.medications,
            allergies=request.allergies,
            age=request.age,
            is_pregnant=request.is_pregnant,
            is_breastfeeding=request.is_breastfeeding,
            supplements_currently_taking=request.supplements_currently_taking,
        )

        result = scanner_service.check_product_safety(
            product_id=request.product_id,
            health_profile=health_profile,
        )

        return {
            "product_id": str(request.product_id),
            "is_safe": result.is_safe,
            "safety_score": result.safety_score,
            "safety_rating": result.safety_rating.value,
            "interaction_warnings": [
                {
                    "items": w.interacting_items,
                    "severity": w.severity.value,
                    "description": w.description,
                    "recommendation": w.recommendation,
                }
                for w in result.interaction_warnings
            ],
            "condition_warnings": result.condition_warnings,
            "allergy_warnings": result.allergy_warnings,
            "pregnancy_warnings": result.pregnancy_warnings,
            "recommendations": result.recommendations,
            "checked_at": result.checked_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety check failed: {str(e)}")


@router.post("/interactions", summary="Check product interactions")
async def check_interactions(request: InteractionCheckRequest):
    """
    Check for interactions between a product and medications/supplements.

    Returns list of interaction warnings with severity levels:
    - none: No interaction
    - minor: Generally safe, monitor
    - moderate: Use with caution
    - severe: Avoid combination
    - contraindicated: Do not use together
    """
    try:
        warnings = scanner_service.check_interactions(
            product_id=request.product_id,
            medications=request.medications,
            other_supplements=request.other_supplements,
        )

        return {
            "product_id": str(request.product_id),
            "interactions_found": len(warnings),
            "warnings": [
                {
                    "items": w.interacting_items,
                    "severity": w.severity.value,
                    "description": w.description,
                    "recommendation": w.recommendation,
                    "evidence_quality": w.evidence_quality.value,
                }
                for w in warnings
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/quick-check", summary="Quick ingredient safety check")
async def quick_ingredient_check(request: QuickCheckRequest):
    """
    Quick safety check for a single ingredient.

    Useful for checking individual ingredients before scanning a full product.
    """
    result = scanner_service.quick_ingredient_check(
        ingredient=request.ingredient,
        medications=request.medications,
        conditions=request.conditions,
    )
    return result


# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@router.post("/recommendations", summary="Get product recommendations")
async def get_recommendations(request: RecommendationRequestBody):
    """
    Get personalized product recommendations.

    Can recommend based on:
    - Health condition (e.g., "anxiety", "sleep", "energy")
    - Current product (find alternatives)
    - User health profile
    """
    health_profile = None
    if request.conditions or request.medications or request.allergies:
        health_profile = UserHealthProfile(
            user_id=UUID("00000000-0000-0000-0000-000000000000"),
            conditions=request.conditions,
            medications=request.medications,
            allergies=request.allergies,
        )

    rec_request = RecommendationRequest(
        product_id=request.product_id,
        user_health_profile=health_profile,
        condition=request.condition,
        max_results=request.max_results,
    )

    response = recommendation_service.get_recommendations(rec_request)

    return {
        "recommendations": [
            {
                "product": rec.product.model_dump(),
                "score": rec.recommendation_score,
                "reasons": rec.reasons,
                "is_safer_alternative": rec.is_safer_alternative,
            }
            for rec in response.recommendations
        ],
        "based_on": response.based_on,
        "total": response.total_found,
    }


@router.get(
    "/recommendations/for-condition/{condition}",
    summary="Get recommendations for condition"
)
async def get_recommendations_for_condition(
    condition: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get product recommendations for a specific health condition.

    Supported conditions:
    - anxiety, sleep, depression, energy
    - immune support, digestion, inflammation
    - joint health, heart health, cognitive
    """
    rec_request = RecommendationRequest(
        condition=condition,
        max_results=limit,
    )

    response = recommendation_service.get_recommendations(rec_request)

    return {
        "condition": condition,
        "recommendations": [
            {
                "product": rec.product.model_dump(),
                "score": rec.recommendation_score,
                "reasons": rec.reasons,
            }
            for rec in response.recommendations
        ],
        "total": response.total_found,
    }


@router.get(
    "/recommendations/alternatives/{product_id}",
    summary="Get product alternatives"
)
async def get_alternatives(
    product_id: UUID,
    limit: int = Query(5, ge=1, le=20)
):
    """
    Get alternative products similar to the specified product.

    Returns products with similar ingredients, potentially higher safety
    scores, or better evidence ratings.
    """
    rec_request = RecommendationRequest(
        product_id=product_id,
        max_results=limit,
    )

    response = recommendation_service.get_recommendations(rec_request)

    return {
        "product_id": str(product_id),
        "alternatives": [
            {
                "product": rec.product.model_dump(),
                "score": rec.recommendation_score,
                "reasons": rec.reasons,
                "is_safer": rec.is_safer_alternative,
            }
            for rec in response.recommendations
        ],
        "total": response.total_found,
    }


# ============================================================================
# HISTORY ENDPOINTS
# ============================================================================

@router.get("/history/{user_id}", summary="Get user's scan history")
async def get_scan_history(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=200)
):
    """Get user's product scan history"""
    history = scanner_service.get_user_scan_history(user_id, limit)
    return {
        "user_id": str(user_id),
        "history": history,
        "total": len(history),
    }


@router.get("/statistics/{user_id}", summary="Get user's scan statistics")
async def get_scan_statistics(user_id: UUID):
    """Get statistics about user's scanning activity"""
    stats = scanner_service.get_user_scan_statistics(user_id)
    return stats


# ============================================================================
# TEST SCENARIOS
# ============================================================================

@router.get("/test-scenarios", summary="Get test scenarios for the scanner")
async def get_test_scenarios():
    """
    Get test scenarios for exploring the Product Scanner API.

    Returns example requests for each endpoint.
    """
    return {
        "scenarios": [
            {
                "name": "Scan Vitamin D barcode",
                "endpoint": "POST /scanner/barcode",
                "request": {"barcode": "031604026769"},
            },
            {
                "name": "Safety check with medications",
                "endpoint": "POST /scanner/safety-check",
                "request": {
                    "product_id": "any-st-johns-wort-product",
                    "medications": ["sertraline", "warfarin"],
                    "conditions": ["depression"],
                },
            },
            {
                "name": "Get recommendations for anxiety",
                "endpoint": "GET /scanner/recommendations/for-condition/anxiety",
            },
            {
                "name": "Search herbs products",
                "endpoint": "POST /scanner/products/search",
                "request": {
                    "category": "herbs",
                    "min_safety_score": 70,
                },
            },
            {
                "name": "Quick ingredient check",
                "endpoint": "POST /scanner/quick-check",
                "request": {
                    "ingredient": "ginkgo biloba",
                    "medications": ["warfarin"],
                },
            },
        ]
    }
