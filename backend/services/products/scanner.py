"""
Product Scanner Service
=======================
Main service for scanning products and performing safety analysis.
"""

import logging
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from algorithms.product_scanner import (
    BarcodeRecognizer,
    LabelParser,
    InteractionChecker,
    SafetyAnalyzer,
    Product,
    BarcodeScanInput,
    ImageScanInput,
    ScanResult,
    ScanType,
    UserHealthProfile,
    SafetyCheckResult,
    InteractionWarning,
)
from .database import ProductDatabaseService

logger = logging.getLogger(__name__)


class ProductScannerService:
    """
    Product Scanner Service

    Main service that orchestrates:
    - Barcode scanning
    - Label image OCR
    - Product lookup
    - Safety analysis
    - Scan history tracking
    """

    def __init__(self, db: Session = None):
        """
        Initialize the product scanner service

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.barcode_recognizer = BarcodeRecognizer()
        self.label_parser = LabelParser()
        self.interaction_checker = InteractionChecker()
        self.safety_analyzer = SafetyAnalyzer()
        self.product_db = ProductDatabaseService(db)

    def scan_barcode(
        self,
        barcode: str,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Scan a product barcode and return product information

        Args:
            barcode: Barcode string (UPC, EAN, etc.)
            user_id: Optional user ID for tracking

        Returns:
            Dictionary with scan result and product info
        """
        # Validate barcode
        scan_input = BarcodeScanInput(barcode=barcode)
        scan_result = self.barcode_recognizer.scan_barcode(scan_input)

        # Look up product in database
        product = self.product_db.get_product_by_barcode(barcode)

        if product:
            scan_result.product = product
            scan_result.product_found = True

            # Record scan if user is authenticated
            if user_id:
                self.product_db.record_scan(
                    user_id=user_id,
                    product_id=product.id,
                    scan_type=ScanType.BARCODE,
                    safety_score=product.safety_score,
                )

        return {
            "success": True,
            "scan_type": "barcode",
            "barcode": barcode,
            "product_found": scan_result.product_found,
            "product": product.model_dump() if product else None,
            "confidence": scan_result.confidence_score,
            "scanned_at": datetime.utcnow().isoformat(),
        }

    def scan_image(
        self,
        image_base64: str,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Scan a product label image using OCR

        Args:
            image_base64: Base64-encoded image
            user_id: Optional user ID for tracking

        Returns:
            Dictionary with OCR results and extracted information
        """
        # Parse label using OCR
        scan_input = ImageScanInput(image_base64=image_base64)
        ocr_result = self.label_parser.parse_label(scan_input)

        # Try to find product by name
        product = None
        if ocr_result.product_name:
            search_results = self.product_db.search_products(
                query=ocr_result.product_name,
                max_results=1
            )
            if search_results:
                product = search_results[0].product

        # Create product from OCR if not found
        if not product and ocr_result.product_name:
            product = Product(
                name=ocr_result.product_name,
                brand=ocr_result.brand_name,
                ingredients=ocr_result.parsed_ingredients,
                serving_size=ocr_result.serving_size,
            )

        # Record scan if user is authenticated
        if user_id:
            self.product_db.record_scan(
                user_id=user_id,
                product_id=product.id if product else None,
                scan_type=ScanType.IMAGE_OCR,
                safety_score=product.safety_score if product else None,
            )

        return {
            "success": True,
            "scan_type": "image",
            "ocr_confidence": ocr_result.confidence,
            "processing_time_ms": ocr_result.processing_time_ms,
            "extracted_data": {
                "product_name": ocr_result.product_name,
                "brand_name": ocr_result.brand_name,
                "serving_size": ocr_result.serving_size,
                "ingredients": [
                    ing.model_dump() for ing in ocr_result.parsed_ingredients
                ],
                "raw_text": ocr_result.raw_text[:500] if ocr_result.raw_text else None,
            },
            "product_found": product is not None,
            "product": product.model_dump() if product else None,
            "scanned_at": datetime.utcnow().isoformat(),
        }

    def check_product_safety(
        self,
        product_id: UUID,
        health_profile: UserHealthProfile
    ) -> SafetyCheckResult:
        """
        Perform personalized safety check for a product

        Args:
            product_id: Product ID to check
            health_profile: User's health profile

        Returns:
            SafetyCheckResult with detailed findings
        """
        # Get product
        product = self.product_db.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        # Analyze safety
        result = self.safety_analyzer.analyze_safety(product, health_profile)

        return result

    def check_interactions(
        self,
        product_id: UUID,
        medications: List[str] = None,
        other_supplements: List[str] = None
    ) -> List[InteractionWarning]:
        """
        Check for interactions between a product and medications/supplements

        Args:
            product_id: Product ID to check
            medications: List of current medications
            other_supplements: List of other supplements

        Returns:
            List of interaction warnings
        """
        product = self.product_db.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        return self.interaction_checker.check_product_interactions(
            product=product,
            medications=medications or [],
            other_supplements=other_supplements or [],
        )

    def get_product_details(self, product_id: UUID) -> Optional[Dict]:
        """
        Get full product details including evidence scores

        Args:
            product_id: Product ID

        Returns:
            Product details dictionary or None
        """
        product = self.product_db.get_product_by_id(product_id)
        if not product:
            return None

        # Get all known interactions for product ingredients
        interactions = []
        for ingredient in product.ingredients:
            ing_interactions = self.interaction_checker.get_all_interactions_for_ingredient(
                ingredient.standardized_name or ingredient.name
            )
            interactions.extend(ing_interactions)

        return {
            "product": product.model_dump(),
            "known_interactions": [
                {
                    "ingredient_a": i.ingredient_a,
                    "ingredient_b": i.ingredient_b,
                    "severity": i.severity.value,
                    "description": i.description,
                }
                for i in interactions
            ],
            "interaction_count": len(interactions),
        }

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_safety_score: float = 0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search products with filters

        Args:
            query: Search query
            category: Product category filter
            brand: Brand filter
            min_safety_score: Minimum safety score
            limit: Maximum results

        Returns:
            List of product search results
        """
        from algorithms.product_scanner.models import ProductCategory

        cat = None
        if category:
            try:
                cat = ProductCategory(category.lower())
            except ValueError:
                pass

        results = self.product_db.search_products(
            query=query,
            category=cat,
            brand=brand,
            min_safety_score=min_safety_score,
            max_results=limit,
        )

        return [
            {
                "product": r.product.model_dump(),
                "relevance_score": r.relevance_score,
                "match_reason": r.match_reason,
            }
            for r in results
        ]

    def get_user_scan_history(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get user's scan history

        Args:
            user_id: User ID
            limit: Maximum number of results

        Returns:
            List of scan history entries
        """
        history = self.product_db.get_scan_history(user_id, limit)

        result = []
        for entry in history:
            item = entry.model_dump()
            if entry.product_id:
                product = self.product_db.get_product_by_id(entry.product_id)
                if product:
                    item["product"] = product.model_dump()
            result.append(item)

        return result

    def get_user_scan_statistics(self, user_id: UUID) -> Dict:
        """
        Get user's scanning statistics

        Args:
            user_id: User ID

        Returns:
            Scan statistics dictionary
        """
        stats = self.product_db.get_scan_statistics(user_id)
        return stats.model_dump()

    def quick_ingredient_check(
        self,
        ingredient: str,
        medications: List[str] = None,
        conditions: List[str] = None
    ) -> Dict:
        """
        Quick safety check for a single ingredient

        Args:
            ingredient: Ingredient name
            medications: Current medications
            conditions: Health conditions

        Returns:
            Safety information dictionary
        """
        return self.safety_analyzer.quick_safety_check(
            ingredient_name=ingredient,
            medications=medications,
            conditions=conditions,
        )

    def get_popular_products(self, limit: int = 10) -> List[Dict]:
        """Get most popular products by scan count"""
        products = self.product_db.get_popular_products(limit)
        return [p.model_dump() for p in products]

    def get_top_rated_products(self, limit: int = 10) -> List[Dict]:
        """Get top rated products"""
        products = self.product_db.get_top_rated_products(limit)
        return [p.model_dump() for p in products]
