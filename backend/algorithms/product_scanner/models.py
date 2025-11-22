"""
Product Scanner Models
======================
Pydantic models for the Product Scanner algorithm.
Handles barcode recognition, OCR parsing, interaction checking, and safety analysis.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
from uuid import UUID, uuid4
from datetime import datetime, date
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ProductCategory(str, Enum):
    """Categories of wellness products"""
    HERBS = "herbs"
    VITAMINS = "vitamins"
    MINERALS = "minerals"
    AMINO_ACIDS = "amino_acids"
    PROBIOTICS = "probiotics"
    ENZYMES = "enzymes"
    HOMEOPATHIC = "homeopathic"
    ESSENTIAL_OILS = "essential_oils"
    COMBINATION = "combination"
    OTHER = "other"


class InteractionSeverity(str, Enum):
    """Severity level of ingredient interactions"""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CONTRAINDICATED = "contraindicated"


class EvidenceQuality(str, Enum):
    """Quality of scientific evidence"""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"
    INSUFFICIENT = "insufficient"


class SafetyRating(str, Enum):
    """Overall safety rating"""
    SAFE = "safe"
    GENERALLY_SAFE = "generally_safe"
    USE_CAUTION = "use_caution"
    NOT_RECOMMENDED = "not_recommended"
    CONTRAINDICATED = "contraindicated"


class ScanType(str, Enum):
    """Type of product scan"""
    BARCODE = "barcode"
    QR_CODE = "qr_code"
    IMAGE_OCR = "image_ocr"
    MANUAL = "manual"


# ============================================================================
# INGREDIENT MODELS
# ============================================================================

class Ingredient(BaseModel):
    """Individual ingredient in a product"""
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    daily_value_percentage: Optional[float] = None
    standardized_name: Optional[str] = None  # Normalized ingredient name
    cas_number: Optional[str] = None  # Chemical Abstracts Service number


class IngredientInteraction(BaseModel):
    """Interaction between two ingredients or ingredient and medication"""
    id: UUID = Field(default_factory=uuid4)
    ingredient_a: str
    ingredient_b: str
    interaction_type: str  # "herb-drug", "supplement-supplement", "food-drug"
    severity: InteractionSeverity
    description: str
    mechanism: Optional[str] = None
    clinical_significance: Optional[str] = None
    evidence_quality: EvidenceQuality = EvidenceQuality.MODERATE
    references: List[str] = Field(default_factory=list)


# ============================================================================
# PRODUCT MODELS
# ============================================================================

class ProductBase(BaseModel):
    """Base product information"""
    name: str
    brand: Optional[str] = None
    category: ProductCategory
    barcode: Optional[str] = None
    description: Optional[str] = None


class Product(ProductBase):
    """Full product model with all details"""
    id: UUID = Field(default_factory=uuid4)
    ingredients: List[Ingredient] = Field(default_factory=list)
    serving_size: Optional[str] = None
    servings_per_container: Optional[int] = None

    # Evidence & Safety
    evidence_score: float = Field(default=0.0, ge=0, le=100)
    safety_score: float = Field(default=0.0, ge=0, le=100)

    # Warnings & Contraindications
    warnings: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)

    # Community Data
    average_rating: float = Field(default=0.0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    scan_count: int = Field(default=0, ge=0)

    # Metadata
    manufacturer: Optional[str] = None
    country_of_origin: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)  # "GMP", "Organic", "NSF"

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductSearchResult(BaseModel):
    """Product search result with relevance score"""
    product: Product
    relevance_score: float = Field(ge=0, le=1)
    match_reason: Optional[str] = None


# ============================================================================
# SCAN INPUT/OUTPUT MODELS
# ============================================================================

class BarcodeScanInput(BaseModel):
    """Input for barcode scanning"""
    barcode: str = Field(..., min_length=8, max_length=14)
    scan_type: ScanType = ScanType.BARCODE


class ImageScanInput(BaseModel):
    """Input for OCR image scanning"""
    image_base64: str = Field(..., min_length=100)
    image_format: str = Field(default="jpeg")  # "jpeg", "png", "webp"


class ManualProductInput(BaseModel):
    """Manual product entry"""
    name: str
    brand: Optional[str] = None
    ingredients: List[str] = Field(default_factory=list)
    category: Optional[ProductCategory] = None


class ScanResult(BaseModel):
    """Result of a product scan"""
    id: UUID = Field(default_factory=uuid4)
    scan_type: ScanType
    product: Optional[Product] = None
    product_found: bool = False

    # Extracted Data (from OCR)
    extracted_text: Optional[str] = None
    extracted_ingredients: List[Ingredient] = Field(default_factory=list)

    # Confidence
    confidence_score: float = Field(default=0.0, ge=0, le=1)

    # Errors
    error_message: Optional[str] = None

    # Timestamps
    scanned_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SAFETY CHECK MODELS
# ============================================================================

class UserHealthProfile(BaseModel):
    """User's health profile for personalized safety checks"""
    user_id: UUID
    conditions: List[str] = Field(default_factory=list)  # ["anxiety", "IBS", "hypertension"]
    medications: List[str] = Field(default_factory=list)  # ["warfarin", "metformin"]
    allergies: List[str] = Field(default_factory=list)
    age: Optional[int] = None
    is_pregnant: bool = False
    is_breastfeeding: bool = False
    supplements_currently_taking: List[str] = Field(default_factory=list)


class SafetyCheckInput(BaseModel):
    """Input for personalized safety check"""
    product_id: UUID
    user_health_profile: UserHealthProfile


class InteractionWarning(BaseModel):
    """Individual interaction warning"""
    id: UUID = Field(default_factory=uuid4)
    interacting_items: Tuple[str, str]
    severity: InteractionSeverity
    description: str
    recommendation: str
    evidence_quality: EvidenceQuality


class SafetyCheckResult(BaseModel):
    """Result of a personalized safety check"""
    id: UUID = Field(default_factory=uuid4)
    product_id: UUID
    user_id: UUID

    # Overall Safety Assessment
    is_safe: bool = True
    safety_score: float = Field(ge=0, le=100)
    safety_rating: SafetyRating

    # Detailed Findings
    interaction_warnings: List[InteractionWarning] = Field(default_factory=list)
    condition_warnings: List[str] = Field(default_factory=list)
    allergy_warnings: List[str] = Field(default_factory=list)
    pregnancy_warnings: List[str] = Field(default_factory=list)

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    alternative_products: List[UUID] = Field(default_factory=list)

    # Metadata
    checked_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# RECOMMENDATION MODELS
# ============================================================================

class ProductRecommendation(BaseModel):
    """Product recommendation with reasoning"""
    product: Product
    recommendation_score: float = Field(ge=0, le=100)
    reasons: List[str] = Field(default_factory=list)
    is_safer_alternative: bool = False
    price_comparison: Optional[str] = None  # "cheaper", "similar", "more_expensive"


class RecommendationRequest(BaseModel):
    """Request for product recommendations"""
    product_id: Optional[UUID] = None  # Current product (for alternatives)
    user_health_profile: Optional[UserHealthProfile] = None
    condition: Optional[str] = None  # Target condition
    max_results: int = Field(default=10, le=50)


class RecommendationResponse(BaseModel):
    """Response with product recommendations"""
    recommendations: List[ProductRecommendation]
    based_on: str  # "current_product", "health_profile", "condition"
    total_found: int


# ============================================================================
# SCAN HISTORY MODELS
# ============================================================================

class ScanHistoryEntry(BaseModel):
    """Entry in user's scan history"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    product_id: Optional[UUID] = None
    scan_type: ScanType

    # Safety Results
    safety_score: Optional[float] = None
    had_warnings: bool = False
    warning_count: int = 0

    # Timestamps
    scanned_at: datetime = Field(default_factory=datetime.utcnow)


class ScanStatistics(BaseModel):
    """Statistics about a user's scanning activity"""
    user_id: UUID
    total_scans: int = 0
    scans_this_month: int = 0
    unique_products_scanned: int = 0
    average_safety_score: float = 0.0
    most_scanned_category: Optional[ProductCategory] = None


# ============================================================================
# OCR MODELS
# ============================================================================

class OCRResult(BaseModel):
    """Result from OCR processing"""
    raw_text: str
    confidence: float = Field(ge=0, le=1)
    detected_language: str = "en"

    # Structured extraction
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    ingredients_text: Optional[str] = None
    serving_size: Optional[str] = None
    warnings_text: Optional[str] = None

    # Parsed ingredients
    parsed_ingredients: List[Ingredient] = Field(default_factory=list)

    # Processing metadata
    processing_time_ms: int = 0
    ocr_engine: str = "google_vision"  # or "tesseract"


class LabelRegion(BaseModel):
    """Detected region on a product label"""
    region_type: str  # "supplement_facts", "ingredients", "warnings", "brand"
    text: str
    confidence: float
    bounding_box: Optional[Dict[str, float]] = None  # x, y, width, height
