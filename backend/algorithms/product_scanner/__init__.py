"""
Product Scanner Algorithm Package
=================================

SANA Product Scanner - "Vivino for Supplements"

This package provides comprehensive product scanning capabilities including:
- Barcode recognition (UPC, EAN, QR codes)
- OCR label parsing for ingredient extraction
- Herb-drug and supplement-supplement interaction checking
- Personalized safety analysis based on user health profile

Modules:
--------
- barcode_recognition: Scan and decode product barcodes
- ocr_label_parser: Extract text and ingredients from label images
- interaction_checker: Check for ingredient interactions
- safety_analyzer: Personalized safety scoring

Usage:
------
    from algorithms.product_scanner import (
        BarcodeRecognizer,
        LabelParser,
        InteractionChecker,
        SafetyAnalyzer,
    )

    # Scan a barcode
    recognizer = BarcodeRecognizer()
    result = recognizer.scan_barcode(BarcodeScanInput(barcode="012345678901"))

    # Parse a label image
    parser = LabelParser()
    ocr_result = parser.parse_label(ImageScanInput(image_base64="..."))

    # Check interactions
    checker = InteractionChecker()
    warnings = checker.check_product_interactions(product, medications)

    # Analyze safety
    analyzer = SafetyAnalyzer()
    safety = analyzer.analyze_safety(product, health_profile)
"""

# Models
from .models import (
    # Enums
    ProductCategory,
    InteractionSeverity,
    EvidenceQuality,
    SafetyRating,
    ScanType,

    # Ingredient Models
    Ingredient,
    IngredientInteraction,

    # Product Models
    ProductBase,
    Product,
    ProductSearchResult,

    # Scan Models
    BarcodeScanInput,
    ImageScanInput,
    ManualProductInput,
    ScanResult,

    # Safety Models
    UserHealthProfile,
    SafetyCheckInput,
    InteractionWarning,
    SafetyCheckResult,

    # Recommendation Models
    ProductRecommendation,
    RecommendationRequest,
    RecommendationResponse,

    # History Models
    ScanHistoryEntry,
    ScanStatistics,

    # OCR Models
    OCRResult,
    LabelRegion,
)

# Algorithms
from .barcode_recognition import (
    BarcodeRecognizer,
    normalize_barcode,
    convert_upc_to_ean,
    is_supplement_barcode,
)

from .ocr_label_parser import (
    LabelParser,
    scan_label_image,
)

from .interaction_checker import (
    InteractionChecker,
)

from .safety_analyzer import (
    SafetyAnalyzer,
)

__all__ = [
    # Enums
    "ProductCategory",
    "InteractionSeverity",
    "EvidenceQuality",
    "SafetyRating",
    "ScanType",

    # Models
    "Ingredient",
    "IngredientInteraction",
    "ProductBase",
    "Product",
    "ProductSearchResult",
    "BarcodeScanInput",
    "ImageScanInput",
    "ManualProductInput",
    "ScanResult",
    "UserHealthProfile",
    "SafetyCheckInput",
    "InteractionWarning",
    "SafetyCheckResult",
    "ProductRecommendation",
    "RecommendationRequest",
    "RecommendationResponse",
    "ScanHistoryEntry",
    "ScanStatistics",
    "OCRResult",
    "LabelRegion",

    # Algorithms
    "BarcodeRecognizer",
    "LabelParser",
    "InteractionChecker",
    "SafetyAnalyzer",

    # Utility functions
    "normalize_barcode",
    "convert_upc_to_ean",
    "is_supplement_barcode",
    "scan_label_image",
]
