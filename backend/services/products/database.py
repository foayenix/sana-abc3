"""
Product Database Service
========================
Service for managing the product catalog and scan history.
"""

import logging
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from algorithms.product_scanner.models import (
    Product,
    ProductCategory,
    Ingredient,
    ProductSearchResult,
    ScanHistoryEntry,
    ScanStatistics,
    ScanType,
)

logger = logging.getLogger(__name__)


class ProductDatabaseService:
    """
    Product Database Service

    Manages the product catalog including:
    - Product CRUD operations
    - Product search and filtering
    - Scan history tracking
    - Product statistics
    """

    def __init__(self, db: Session = None):
        """
        Initialize the product database service

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        # In-memory product cache for demo purposes
        # In production, this would use the database
        self._product_cache: Dict[UUID, Product] = {}
        self._barcode_index: Dict[str, UUID] = {}
        self._scan_history: Dict[UUID, List[ScanHistoryEntry]] = {}

        # Seed with demo products
        self._seed_demo_products()

    def _seed_demo_products(self):
        """Seed the database with demo products"""
        demo_products = [
            Product(
                id=uuid4(),
                name="Vitamin D3 5000 IU",
                brand="Nature Made",
                category=ProductCategory.VITAMINS,
                barcode="031604026769",
                ingredients=[
                    Ingredient(name="Vitamin D3", amount=5000, unit="IU",
                               standardized_name="Cholecalciferol"),
                    Ingredient(name="Soybean Oil", standardized_name="Soybean Oil"),
                ],
                serving_size="1 softgel",
                servings_per_container=120,
                evidence_score=85.0,
                safety_score=92.0,
                average_rating=4.5,
                review_count=1250,
                certifications=["USP Verified", "Non-GMO"],
            ),
            Product(
                id=uuid4(),
                name="Omega-3 Fish Oil 1000mg",
                brand="Nordic Naturals",
                category=ProductCategory.COMBINATION,
                barcode="768990037856",
                ingredients=[
                    Ingredient(name="Fish Oil", amount=1000, unit="mg",
                               standardized_name="Omega-3 Fatty Acids"),
                    Ingredient(name="EPA", amount=650, unit="mg", standardized_name="EPA"),
                    Ingredient(name="DHA", amount=350, unit="mg", standardized_name="DHA"),
                ],
                serving_size="2 softgels",
                servings_per_container=60,
                evidence_score=88.0,
                safety_score=95.0,
                warnings=["Contains fish (anchovy, sardine)"],
                average_rating=4.7,
                review_count=3420,
                certifications=["Third-party tested", "Non-GMO"],
            ),
            Product(
                id=uuid4(),
                name="St. John's Wort 300mg",
                brand="Nature's Way",
                category=ProductCategory.HERBS,
                barcode="033674153901",
                ingredients=[
                    Ingredient(name="St. John's Wort Extract", amount=300, unit="mg",
                               standardized_name="St. John's Wort"),
                ],
                serving_size="1 capsule",
                servings_per_container=100,
                evidence_score=72.0,
                safety_score=65.0,
                warnings=[
                    "May interact with prescription medications",
                    "Avoid sun exposure while taking",
                    "Not for use during pregnancy"
                ],
                contraindications=[
                    "SSRIs", "MAOIs", "Birth control pills", "Immunosuppressants"
                ],
                average_rating=4.2,
                review_count=890,
            ),
            Product(
                id=uuid4(),
                name="Magnesium Glycinate 400mg",
                brand="Doctor's Best",
                category=ProductCategory.MINERALS,
                barcode="753950002753",
                ingredients=[
                    Ingredient(name="Magnesium Glycinate", amount=400, unit="mg",
                               standardized_name="Magnesium"),
                ],
                serving_size="2 capsules",
                servings_per_container=120,
                evidence_score=80.0,
                safety_score=94.0,
                warnings=["May interact with certain antibiotics"],
                average_rating=4.6,
                review_count=2100,
                certifications=["Vegan", "Non-GMO", "Gluten-Free"],
            ),
            Product(
                id=uuid4(),
                name="Probiotic 50 Billion CFU",
                brand="Garden of Life",
                category=ProductCategory.PROBIOTICS,
                barcode="658010115513",
                ingredients=[
                    Ingredient(name="Probiotic Blend", amount=50, unit="billion CFU",
                               standardized_name="Probiotics"),
                    Ingredient(name="Lactobacillus acidophilus",
                               standardized_name="L. acidophilus"),
                    Ingredient(name="Bifidobacterium lactis",
                               standardized_name="B. lactis"),
                ],
                serving_size="1 capsule",
                servings_per_container=30,
                evidence_score=75.0,
                safety_score=96.0,
                warnings=["Refrigerate after opening"],
                average_rating=4.4,
                review_count=1850,
                certifications=["Organic", "Non-GMO", "Gluten-Free"],
            ),
            Product(
                id=uuid4(),
                name="Turmeric Curcumin 1500mg",
                brand="Qunol",
                category=ProductCategory.HERBS,
                barcode="819903010012",
                ingredients=[
                    Ingredient(name="Turmeric Curcumin", amount=1500, unit="mg",
                               standardized_name="Turmeric"),
                    Ingredient(name="Black Pepper Extract", amount=10, unit="mg",
                               standardized_name="Piperine"),
                ],
                serving_size="2 capsules",
                servings_per_container=60,
                evidence_score=82.0,
                safety_score=88.0,
                warnings=[
                    "May interact with blood thinners",
                    "Not recommended during pregnancy"
                ],
                average_rating=4.5,
                review_count=4500,
                certifications=["Non-GMO"],
            ),
            Product(
                id=uuid4(),
                name="Ashwagandha Root Extract 600mg",
                brand="NOW Foods",
                category=ProductCategory.HERBS,
                barcode="733739046291",
                ingredients=[
                    Ingredient(name="Ashwagandha Root Extract", amount=600, unit="mg",
                               standardized_name="Ashwagandha"),
                ],
                serving_size="1 capsule",
                servings_per_container=90,
                evidence_score=78.0,
                safety_score=85.0,
                warnings=[
                    "Not for use during pregnancy",
                    "May affect thyroid hormone levels"
                ],
                average_rating=4.3,
                review_count=2800,
                certifications=["Non-GMO", "Vegan"],
            ),
            Product(
                id=uuid4(),
                name="Ginkgo Biloba 120mg",
                brand="Solgar",
                category=ProductCategory.HERBS,
                barcode="033984011045",
                ingredients=[
                    Ingredient(name="Ginkgo Biloba Extract", amount=120, unit="mg",
                               standardized_name="Ginkgo Biloba"),
                ],
                serving_size="1 capsule",
                servings_per_container=60,
                evidence_score=70.0,
                safety_score=75.0,
                warnings=[
                    "May increase bleeding risk",
                    "Avoid with blood thinners",
                    "Discontinue 2 weeks before surgery"
                ],
                contraindications=["Warfarin", "Aspirin", "NSAIDs"],
                average_rating=4.1,
                review_count=650,
            ),
            Product(
                id=uuid4(),
                name="Vitamin B Complex",
                brand="Thorne",
                category=ProductCategory.VITAMINS,
                barcode="693749001027",
                ingredients=[
                    Ingredient(name="Vitamin B1", amount=100, unit="mg",
                               standardized_name="Thiamine"),
                    Ingredient(name="Vitamin B2", amount=100, unit="mg",
                               standardized_name="Riboflavin"),
                    Ingredient(name="Vitamin B6", amount=100, unit="mg",
                               standardized_name="Pyridoxine"),
                    Ingredient(name="Vitamin B12", amount=1000, unit="mcg",
                               standardized_name="Cobalamin"),
                    Ingredient(name="Folate", amount=800, unit="mcg",
                               standardized_name="Folate"),
                ],
                serving_size="1 capsule",
                servings_per_container=60,
                evidence_score=90.0,
                safety_score=97.0,
                average_rating=4.8,
                review_count=5200,
                certifications=["NSF Certified", "Gluten-Free"],
            ),
            Product(
                id=uuid4(),
                name="Iron 65mg",
                brand="Nature Made",
                category=ProductCategory.MINERALS,
                barcode="031604026622",
                ingredients=[
                    Ingredient(name="Ferrous Sulfate", amount=65, unit="mg",
                               standardized_name="Iron"),
                ],
                serving_size="1 tablet",
                servings_per_container=180,
                evidence_score=85.0,
                safety_score=80.0,
                warnings=[
                    "Take on empty stomach for best absorption",
                    "May cause constipation",
                    "Keep out of reach of children"
                ],
                average_rating=4.2,
                review_count=1100,
                certifications=["USP Verified"],
            ),
        ]

        # Add to cache
        for product in demo_products:
            self._product_cache[product.id] = product
            if product.barcode:
                self._barcode_index[product.barcode] = product.id

    def get_product_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get a product by its ID"""
        return self._product_cache.get(product_id)

    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get a product by its barcode"""
        product_id = self._barcode_index.get(barcode)
        if product_id:
            return self._product_cache.get(product_id)
        return None

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[ProductCategory] = None,
        brand: Optional[str] = None,
        min_safety_score: float = 0,
        max_results: int = 20
    ) -> List[ProductSearchResult]:
        """
        Search products with filters

        Args:
            query: Search query (matches name, brand, ingredients)
            category: Filter by category
            brand: Filter by brand
            min_safety_score: Minimum safety score
            max_results: Maximum number of results

        Returns:
            List of ProductSearchResult with relevance scores
        """
        results = []

        for product in self._product_cache.values():
            # Apply filters
            if category and product.category != category:
                continue

            if brand and product.brand and brand.lower() not in product.brand.lower():
                continue

            if product.safety_score < min_safety_score:
                continue

            # Calculate relevance score
            relevance = 0.5  # Base relevance

            if query:
                query_lower = query.lower()

                # Name match
                if query_lower in product.name.lower():
                    relevance += 0.3

                # Brand match
                if product.brand and query_lower in product.brand.lower():
                    relevance += 0.1

                # Ingredient match
                for ing in product.ingredients:
                    if query_lower in ing.name.lower():
                        relevance += 0.1
                        break

                # Skip if no query match
                if relevance <= 0.5 and query:
                    continue

            results.append(ProductSearchResult(
                product=product,
                relevance_score=min(1.0, relevance),
                match_reason="Query match" if query else "Filter match",
            ))

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:max_results]

    def add_product(self, product: Product) -> Product:
        """Add a new product to the catalog"""
        if product.id is None:
            product.id = uuid4()

        self._product_cache[product.id] = product

        if product.barcode:
            self._barcode_index[product.barcode] = product.id

        return product

    def update_product(self, product_id: UUID, updates: Dict) -> Optional[Product]:
        """Update an existing product"""
        product = self._product_cache.get(product_id)
        if not product:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        self._product_cache[product_id] = product

        return product

    def increment_scan_count(self, product_id: UUID) -> None:
        """Increment the scan count for a product"""
        product = self._product_cache.get(product_id)
        if product:
            product.scan_count += 1

    def record_scan(
        self,
        user_id: UUID,
        product_id: Optional[UUID],
        scan_type: ScanType,
        safety_score: Optional[float] = None,
        warnings: List[str] = None
    ) -> ScanHistoryEntry:
        """Record a scan in the user's history"""
        entry = ScanHistoryEntry(
            user_id=user_id,
            product_id=product_id,
            scan_type=scan_type,
            safety_score=safety_score,
            had_warnings=bool(warnings),
            warning_count=len(warnings) if warnings else 0,
        )

        if user_id not in self._scan_history:
            self._scan_history[user_id] = []

        self._scan_history[user_id].append(entry)

        # Increment product scan count
        if product_id:
            self.increment_scan_count(product_id)

        return entry

    def get_scan_history(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[ScanHistoryEntry]:
        """Get scan history for a user"""
        history = self._scan_history.get(user_id, [])
        return sorted(
            history,
            key=lambda x: x.scanned_at,
            reverse=True
        )[:limit]

    def get_scan_statistics(self, user_id: UUID) -> ScanStatistics:
        """Get scan statistics for a user"""
        history = self._scan_history.get(user_id, [])

        if not history:
            return ScanStatistics(user_id=user_id)

        # Calculate statistics
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)

        scans_this_month = [
            s for s in history
            if s.scanned_at >= month_ago
        ]

        unique_products = set(
            s.product_id for s in history
            if s.product_id
        )

        safety_scores = [
            s.safety_score for s in history
            if s.safety_score is not None
        ]

        avg_safety = (
            sum(safety_scores) / len(safety_scores)
            if safety_scores else 0.0
        )

        # Find most scanned category
        category_counts: Dict[ProductCategory, int] = {}
        for entry in history:
            if entry.product_id:
                product = self.get_product_by_id(entry.product_id)
                if product:
                    category_counts[product.category] = (
                        category_counts.get(product.category, 0) + 1
                    )

        most_scanned = None
        if category_counts:
            most_scanned = max(category_counts, key=category_counts.get)

        return ScanStatistics(
            user_id=user_id,
            total_scans=len(history),
            scans_this_month=len(scans_this_month),
            unique_products_scanned=len(unique_products),
            average_safety_score=avg_safety,
            most_scanned_category=most_scanned,
        )

    def get_products_by_category(
        self,
        category: ProductCategory,
        limit: int = 20
    ) -> List[Product]:
        """Get products in a specific category"""
        products = [
            p for p in self._product_cache.values()
            if p.category == category
        ]
        return sorted(
            products,
            key=lambda x: x.average_rating,
            reverse=True
        )[:limit]

    def get_popular_products(self, limit: int = 10) -> List[Product]:
        """Get most popular products by scan count"""
        return sorted(
            self._product_cache.values(),
            key=lambda x: x.scan_count,
            reverse=True
        )[:limit]

    def get_top_rated_products(self, limit: int = 10) -> List[Product]:
        """Get top rated products"""
        return sorted(
            self._product_cache.values(),
            key=lambda x: (x.average_rating, x.review_count),
            reverse=True
        )[:limit]
