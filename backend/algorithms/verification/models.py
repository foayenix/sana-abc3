"""
Pydantic models for SCVM (Credential Vetting Model) algorithm.

SCVM provides automated verification of practitioner credentials with
fraud detection, confidence scoring, and human review queue management.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, date
from enum import Enum


class DocumentType(str, Enum):
    """Types of documents that can be verified"""
    DEGREE_CERTIFICATE = "degree_certificate"
    LICENSE = "license"
    CERTIFICATION = "certification"
    INSURANCE_POLICY = "insurance_policy"
    ID_DOCUMENT = "id_document"
    TRAINING_CERTIFICATE = "training_certificate"
    CPD_RECORD = "cpd_record"
    REFERENCE_LETTER = "reference_letter"
    BACKGROUND_CHECK = "background_check"
    OTHER = "other"


class VerificationStatus(str, Enum):
    """Status of verification process"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"
    REQUIRES_REVIEW = "requires_review"
    FLAGGED = "flagged"


class VerificationTier(str, Enum):
    """Verification confidence tiers"""
    BASIC = "basic"           # Email + self-declared
    STANDARD = "standard"     # Document upload + basic checks
    ENHANCED = "enhanced"     # Registry verification + fraud checks
    PREMIUM = "premium"       # Full background check + references


class FraudRiskLevel(str, Enum):
    """Risk level for fraud indicators"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CheckResult(BaseModel):
    """Result of a single verification check"""
    check_name: str
    passed: bool
    confidence: float = Field(ge=0.0, le=1.0)
    details: str = ""
    source: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None


class UploadedDocument(BaseModel):
    """Document uploaded for verification"""
    document_id: UUID
    document_type: DocumentType
    filename: str
    file_size_bytes: int
    upload_timestamp: datetime
    mime_type: str
    ocr_text: Optional[str] = None
    metadata_extracted: Dict = Field(default_factory=dict)
    hash_value: Optional[str] = None


class PractitionerCredential(BaseModel):
    """A single credential claimed by practitioner"""
    credential_id: UUID
    credential_type: str  # e.g., "BSc", "MSc", "Diploma", "Certificate"
    credential_name: str  # e.g., "Bachelor of Science in Nutrition"
    issuing_body: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_number: Optional[str] = None
    supporting_documents: List[UUID] = Field(default_factory=list)
    verification_url: Optional[str] = None


class InsurancePolicy(BaseModel):
    """Professional indemnity insurance details"""
    policy_id: UUID
    provider: str
    policy_number: str
    coverage_amount: float
    start_date: date
    end_date: date
    covers_cam_practice: bool = True
    supporting_document: Optional[UUID] = None


class PractitionerVerificationInput(BaseModel):
    """Input for SCVM verification process"""
    practitioner_id: UUID
    email: str
    full_name: str
    date_of_birth: Optional[date] = None

    # Credentials to verify
    credentials: List[PractitionerCredential] = Field(default_factory=list)

    # Professional memberships
    professional_memberships: List[str] = Field(default_factory=list)
    registry_numbers: Dict[str, str] = Field(default_factory=dict)  # registry_name -> number

    # Insurance
    insurance_policies: List[InsurancePolicy] = Field(default_factory=list)

    # Documents
    uploaded_documents: List[UploadedDocument] = Field(default_factory=list)

    # Practice details
    practice_specialties: List[str] = Field(default_factory=list)
    years_of_experience: int = 0

    # Verification tier requested
    verification_tier: VerificationTier = VerificationTier.STANDARD


class VerificationIssue(BaseModel):
    """Issue found during verification"""
    issue_id: UUID
    severity: FraudRiskLevel
    issue_type: str  # e.g., "document_mismatch", "expired_credential", "unverifiable_claim"
    description: str
    affected_credential: Optional[UUID] = None
    affected_document: Optional[UUID] = None
    requires_human_review: bool = False
    suggested_action: str = ""


class FraudIndicator(BaseModel):
    """Indicator of potential fraud"""
    indicator_id: UUID
    indicator_type: str  # e.g., "metadata_manipulation", "institution_mismatch", "duplicate_submission"
    risk_level: FraudRiskLevel
    description: str
    evidence: Dict = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class HumanReviewRequest(BaseModel):
    """Request for human review of verification"""
    request_id: UUID
    practitioner_id: UUID
    reason: str
    priority: int = Field(ge=1, le=5, default=3)  # 1=highest, 5=lowest
    issues_to_review: List[UUID] = Field(default_factory=list)
    documents_to_review: List[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    notes: str = ""


class CredentialVerificationResult(BaseModel):
    """Result for a single credential verification"""
    credential_id: UUID
    credential_name: str
    status: VerificationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    checks_performed: List[CheckResult] = Field(default_factory=list)
    issues: List[VerificationIssue] = Field(default_factory=list)
    verified_details: Dict = Field(default_factory=dict)
    expiry_warning: bool = False


class VerificationBadge(BaseModel):
    """Badge awarded upon successful verification"""
    badge_id: UUID
    badge_type: str  # e.g., "verified_practitioner", "verified_insurance", "background_checked"
    tier: VerificationTier
    awarded_at: datetime
    valid_until: datetime
    display_text: str
    icon_url: Optional[str] = None


class SCVMOutput(BaseModel):
    """Output from SCVM verification process"""
    practitioner_id: UUID
    verification_tier: VerificationTier

    # Overall results
    overall_status: VerificationStatus
    overall_confidence: float = Field(ge=0.0, le=1.0)
    verified: bool = False

    # Detailed results
    credential_results: List[CredentialVerificationResult] = Field(default_factory=list)
    insurance_verified: bool = False
    background_check_passed: Optional[bool] = None

    # Issues and fraud detection
    issues: List[VerificationIssue] = Field(default_factory=list)
    fraud_indicators: List[FraudIndicator] = Field(default_factory=list)
    fraud_risk_score: float = Field(ge=0.0, le=1.0, default=0.0)

    # Human review
    requires_human_review: bool = False
    human_review_request: Optional[HumanReviewRequest] = None

    # Badges awarded
    badges: List[VerificationBadge] = Field(default_factory=list)

    # Summary
    summary: str = ""
    recommendations: List[str] = Field(default_factory=list)

    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Metrics
    total_checks_performed: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    processing_time_seconds: float = 0.0


# Legacy models for backwards compatibility
class CredentialInput(BaseModel):
    """Legacy input model for credential verification."""
    practitioner_id: UUID
    credentials: List[str]
    documents: List[Dict] = []


class VerificationResult(BaseModel):
    """Legacy result for a single credential verification."""
    credential: str
    verified: bool
    source: Optional[str] = None
    expiration_date: Optional[datetime] = None
    notes: str = ""


class CredentialOutput(BaseModel):
    """Legacy output model for credential verification."""
    practitioner_id: UUID
    verified: bool
    verification_results: List[VerificationResult]
    confidence_score: float
    flags: List[str] = []
