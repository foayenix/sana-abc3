"""
Product Services Package
========================

Services for product scanning, database management, and recommendations.

Services:
---------
- ProductScannerService: Main service for scanning and analyzing products
- ProductDatabaseService: Product catalog management
- ProductRecommendationService: Product recommendation engine
"""

from .scanner import ProductScannerService
from .database import ProductDatabaseService
from .recommendations import ProductRecommendationService

__all__ = [
    "ProductScannerService",
    "ProductDatabaseService",
    "ProductRecommendationService",
]
