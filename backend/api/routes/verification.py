"""
API routes for SCVM verification endpoints

Provides credential verification with fraud detection,
confidence scoring, and human review queue management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta

from algorithms.verification.scvm import SCVMAlgorithm, verify_credentials
from algorithms.verification.models import (
    PractitionerVerificationInput,
    PractitionerCredential,
    InsurancePolicy,
    UploadedDocument,
    SCVMOutput,
    VerificationTier,
    DocumentType,
    CredentialOutput
)

router = APIRouter()

# Initialize SCVM algorithm
scvm = SCVMAlgorithm()


@router.post("/verify-full", response_model=SCVMOutput)
async def verify_practitioner_full(
    input_data: PractitionerVerificationInput
):
    """
    Run full SCVM verification process

    **Input**: Complete practitioner information with credentials and documents
    **Output**: Comprehensive verification results with confidence scores

    Features:
    - Credential verification with pattern matching
    - Institution verification
    - Insurance policy validation
    - Fraud detection
    - Human review queue management
    """
    try:
        result = scvm.verify(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@router.get("/test-full-flow")
async def test_complete_verification_flow(
    profile: str = Query(
        default="standard",
        description="Test profile: standard, suspicious, expired, multi_credential"
    ),
    tier: VerificationTier = Query(
        default=VerificationTier.STANDARD,
        description="Verification tier"
    )
):
    """
    Complete end-to-end verification test with dummy data

    **Perfect for demo and testing**

    Profiles:
    - standard: Valid practitioner with good credentials
    - suspicious: Practitioner with potential fraud indicators
    - expired: Practitioner with expired credentials
    - multi_credential: Practitioner with many qualifications
    """
    try:
        # Generate dummy practitioner data based on profile
        practitioner_id = uuid4()

        if profile == "standard":
            input_data = _generate_standard_practitioner(practitioner_id, tier)
        elif profile == "suspicious":
            input_data = _generate_suspicious_practitioner(practitioner_id, tier)
        elif profile == "expired":
            input_data = _generate_expired_practitioner(practitioner_id, tier)
        elif profile == "multi_credential":
            input_data = _generate_multi_credential_practitioner(practitioner_id, tier)
        else:
            input_data = _generate_standard_practitioner(practitioner_id, tier)

        # Run verification
        result = scvm.verify(input_data)

        return {
            "input": input_data,
            "result": result,
            "profile_used": profile,
            "message": "Verification flow completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test flow error: {str(e)}")


@router.get("/tiers")
async def get_verification_tiers():
    """Get information about verification tiers and requirements"""
    return {
        "tiers": {
            "basic": {
                "name": "Basic",
                "description": "Email verification + self-declared credentials",
                "checks": ["email_verification", "format_validation"],
                "badge": "Basic Verified"
            },
            "standard": {
                "name": "Standard",
                "description": "Document upload + basic verification checks",
                "checks": [
                    "email_verification",
                    "format_validation",
                    "document_verification",
                    "institution_check"
                ],
                "badge": "Standard Verified"
            },
            "enhanced": {
                "name": "Enhanced",
                "description": "Registry verification + fraud detection",
                "checks": [
                    "email_verification",
                    "format_validation",
                    "document_verification",
                    "institution_check",
                    "registry_verification",
                    "fraud_detection"
                ],
                "badge": "Enhanced Verified"
            },
            "premium": {
                "name": "Premium",
                "description": "Full background check + references",
                "checks": [
                    "email_verification",
                    "format_validation",
                    "document_verification",
                    "institution_check",
                    "registry_verification",
                    "fraud_detection",
                    "background_check",
                    "reference_verification"
                ],
                "badge": "Premium Verified"
            }
        },
        "known_registries": list(scvm.KNOWN_REGISTRIES.keys()),
        "known_institutions": list(scvm.KNOWN_INSTITUTIONS.keys())
    }


@router.get("/registries")
async def get_supported_registries():
    """Get list of supported professional registries"""
    return {
        "registries": [
            {
                "code": code,
                "name": name,
                "verification_supported": True
            }
            for code, name in scvm.KNOWN_REGISTRIES.items()
        ]
    }


@router.get("/institutions")
async def get_known_institutions():
    """Get list of known/verified institutions"""
    return {
        "institutions": [
            {
                "name": name.title(),
                "type": info["type"],
                "country": info["country"]
            }
            for name, info in scvm.KNOWN_INSTITUTIONS.items()
        ]
    }


@router.post("/check-institution")
async def check_institution(institution_name: str):
    """
    Quick check if an institution is in our verified database

    Returns verification status and any warnings
    """
    normalized = institution_name.lower().strip()

    if normalized in scvm.KNOWN_INSTITUTIONS:
        info = scvm.KNOWN_INSTITUTIONS[normalized]
        return {
            "institution": institution_name,
            "known": True,
            "verified": True,
            "type": info["type"],
            "country": info["country"],
            "message": "Institution is in our verified database"
        }

    # Check for diploma mill patterns
    for mill in scvm.fraud_patterns["diploma_mills"]:
        if mill in normalized:
            return {
                "institution": institution_name,
                "known": True,
                "verified": False,
                "warning": "potential_diploma_mill",
                "message": f"Institution flagged as potential diploma mill"
            }

    return {
        "institution": institution_name,
        "known": False,
        "verified": False,
        "message": "Institution not in our database - manual verification required"
    }


# Legacy endpoints for backwards compatibility
@router.post("/verify", response_model=CredentialOutput)
async def verify_legacy(
    practitioner_id: UUID,
    credentials: List[str],
    documents: List[Dict] = None
):
    """
    Legacy: Verify practitioner credentials.

    Returns basic verification status and confidence score.
    Use /verify-full for comprehensive verification.
    """
    try:
        result = verify_credentials(
            practitioner_id=practitioner_id,
            credentials=credentials,
            documents=documents
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{practitioner_id}")
async def get_verification_status(practitioner_id: UUID):
    """
    Get verification status for a practitioner.

    Returns current verification status.
    """
    # In production, this would query the database
    return {
        "practitioner_id": practitioner_id,
        "verified": False,
        "status": "pending",
        "last_checked": None,
        "message": "No verification record found"
    }


# Helper functions to generate test data
def _generate_standard_practitioner(
    practitioner_id: UUID,
    tier: VerificationTier
) -> PractitionerVerificationInput:
    """Generate a standard practitioner with valid credentials"""
    doc_id = uuid4()
    cred_id = uuid4()
    policy_id = uuid4()

    return PractitionerVerificationInput(
        practitioner_id=practitioner_id,
        email="practitioner@example.com",
        full_name="Dr. Sarah Johnson",
        date_of_birth=date(1985, 6, 15),
        credentials=[
            PractitionerCredential(
                credential_id=cred_id,
                credential_type="BSc",
                credential_name="BSc Nutritional Science",
                issuing_body="University of Westminster",
                issue_date=date(2010, 7, 1),
                expiry_date=None,
                credential_number="NUT-2010-1234",
                supporting_documents=[doc_id],
                verification_url="https://westminster.ac.uk/verify"
            )
        ],
        professional_memberships=["BANT", "ANP"],
        registry_numbers={"CNHC": "12345", "BANT": "67890"},
        insurance_policies=[
            InsurancePolicy(
                policy_id=policy_id,
                provider="Balens Insurance",
                policy_number="BAL-2024-001",
                coverage_amount=2000000.0,
                start_date=date(2024, 1, 1),
                end_date=date(2025, 1, 1),
                covers_cam_practice=True
            )
        ],
        uploaded_documents=[
            UploadedDocument(
                document_id=doc_id,
                document_type=DocumentType.DEGREE_CERTIFICATE,
                filename="bsc_certificate.pdf",
                file_size_bytes=1024000,
                upload_timestamp=datetime.utcnow(),
                mime_type="application/pdf",
                ocr_text="University of Westminster Bachelor of Science Nutritional Science Sarah Johnson",
                metadata_extracted={"software": "Adobe Acrobat"},
                hash_value="abc123def456"
            )
        ],
        practice_specialties=["Nutrition", "Weight Management"],
        years_of_experience=14,
        verification_tier=tier
    )


def _generate_suspicious_practitioner(
    practitioner_id: UUID,
    tier: VerificationTier
) -> PractitionerVerificationInput:
    """Generate a practitioner with suspicious indicators"""
    doc_id = uuid4()
    cred_id = uuid4()

    return PractitionerVerificationInput(
        practitioner_id=practitioner_id,
        email="suspicious@example.com",
        full_name="John Smith",
        date_of_birth=date(1990, 1, 1),
        credentials=[
            PractitionerCredential(
                credential_id=cred_id,
                credential_type="PhD",
                credential_name="PhD Alternative Medicine",
                issuing_body="Belford University",  # Known diploma mill
                issue_date=date(2023, 1, 1),
                expiry_date=date(2022, 12, 31),  # Date inconsistency
                credential_number="PHD-001",
                supporting_documents=[doc_id]
            )
        ],
        professional_memberships=[],
        registry_numbers={"FAKE_REGISTRY": "00000"},
        insurance_policies=[],
        uploaded_documents=[
            UploadedDocument(
                document_id=doc_id,
                document_type=DocumentType.DEGREE_CERTIFICATE,
                filename="certificate.pdf",
                file_size_bytes=500000,
                upload_timestamp=datetime.utcnow(),
                mime_type="application/pdf",
                ocr_text="",
                metadata_extracted={"software": "photoshop cs6"},  # Edited document
                hash_value="suspicious123"
            )
        ],
        practice_specialties=["Everything"],
        years_of_experience=20,
        verification_tier=tier
    )


def _generate_expired_practitioner(
    practitioner_id: UUID,
    tier: VerificationTier
) -> PractitionerVerificationInput:
    """Generate a practitioner with expired credentials"""
    cred_id = uuid4()
    policy_id = uuid4()

    return PractitionerVerificationInput(
        practitioner_id=practitioner_id,
        email="expired@example.com",
        full_name="Jane Doe",
        date_of_birth=date(1975, 3, 20),
        credentials=[
            PractitionerCredential(
                credential_id=cred_id,
                credential_type="Diploma",
                credential_name="Diploma in Naturopathy",
                issuing_body="College of Naturopathic Medicine",
                issue_date=date(2015, 1, 1),
                expiry_date=date(2020, 1, 1),  # Expired
                credential_number="NAT-2015-999"
            )
        ],
        professional_memberships=["ANP"],
        registry_numbers={"ANP": "11111"},
        insurance_policies=[
            InsurancePolicy(
                policy_id=policy_id,
                provider="Old Insurance Co",
                policy_number="OLD-2019-001",
                coverage_amount=1000000.0,
                start_date=date(2019, 1, 1),
                end_date=date(2020, 1, 1),  # Expired
                covers_cam_practice=True
            )
        ],
        uploaded_documents=[],
        practice_specialties=["Naturopathy"],
        years_of_experience=9,
        verification_tier=tier
    )


def _generate_multi_credential_practitioner(
    practitioner_id: UUID,
    tier: VerificationTier
) -> PractitionerVerificationInput:
    """Generate a practitioner with multiple credentials"""
    credentials = []
    documents = []

    # Create multiple credentials
    specialties = [
        ("BSc", "Nutritional Science", "University of Westminster"),
        ("MSc", "Clinical Nutrition", "University of Lincoln"),
        ("Diploma", "Herbal Medicine", "College of Naturopathic Medicine"),
        ("Certificate", "Sports Nutrition", "Institute for Optimum Nutrition"),
    ]

    for i, (cred_type, name, institution) in enumerate(specialties):
        cred_id = uuid4()
        doc_id = uuid4()

        credentials.append(PractitionerCredential(
            credential_id=cred_id,
            credential_type=cred_type,
            credential_name=f"{cred_type} {name}",
            issuing_body=institution,
            issue_date=date(2010 + i, 7, 1),
            credential_number=f"{cred_type}-{2010+i}-{i:04d}",
            supporting_documents=[doc_id]
        ))

        documents.append(UploadedDocument(
            document_id=doc_id,
            document_type=DocumentType.DEGREE_CERTIFICATE,
            filename=f"{cred_type.lower()}_certificate.pdf",
            file_size_bytes=1024000 + i * 100000,
            upload_timestamp=datetime.utcnow(),
            mime_type="application/pdf",
            ocr_text=f"{institution} {cred_type} {name}",
            metadata_extracted={"software": "Adobe Acrobat DC"},
            hash_value=f"hash{i:03d}"
        ))

    return PractitionerVerificationInput(
        practitioner_id=practitioner_id,
        email="multi@example.com",
        full_name="Dr. Elizabeth Chen",
        date_of_birth=date(1980, 8, 25),
        credentials=credentials,
        professional_memberships=["BANT", "ANP", "NIMH", "CNHC"],
        registry_numbers={
            "CNHC": "98765",
            "BANT": "54321",
            "ANP": "11223"
        },
        insurance_policies=[
            InsurancePolicy(
                policy_id=uuid4(),
                provider="Balens Insurance",
                policy_number="BAL-2024-MULTI",
                coverage_amount=5000000.0,
                start_date=date(2024, 1, 1),
                end_date=date(2025, 1, 1),
                covers_cam_practice=True
            )
        ],
        uploaded_documents=documents,
        practice_specialties=["Nutrition", "Herbal Medicine", "Sports Nutrition"],
        years_of_experience=14,
        verification_tier=tier
    )
