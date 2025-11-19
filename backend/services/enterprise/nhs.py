"""
NHS Connect integration service.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NHSReferralStatus(str, Enum):
    """NHS referral status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class NHSReferral(BaseModel):
    """An NHS referral."""
    id: UUID
    nhs_reference: str

    # Patient
    patient_nhs_number: str
    patient_name: str

    # Referring GP
    gp_practice_code: str
    gp_name: str

    # Referral details
    condition: str
    clinical_notes: str
    urgency: str = "routine"

    # SANA matching
    matched_practitioner_id: Optional[UUID] = None
    matched_specialty: Optional[str] = None

    # Status
    status: NHSReferralStatus = NHSReferralStatus.PENDING

    # Timestamps
    referred_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class NHSConnectService:
    """
    NHS integration service.

    Features:
    - GP referral management
    - NHS number validation
    - PDS (Personal Demographics Service) lookup
    - NHS login integration
    - Referral tracking
    """

    def __init__(self):
        self.referrals: Dict[UUID, NHSReferral] = {}
        self.nhs_logins: Dict[str, UUID] = {}  # NHS number -> user_id
        logger.info("NHSConnectService initialized")

    def validate_nhs_number(self, nhs_number: str) -> Dict[str, Any]:
        """
        Validate NHS number using check digit.

        NHS numbers are 10 digits with a check digit.
        """
        # Remove spaces
        nhs_number = nhs_number.replace(" ", "")

        if len(nhs_number) != 10:
            return {"valid": False, "error": "NHS number must be 10 digits"}

        if not nhs_number.isdigit():
            return {"valid": False, "error": "NHS number must contain only digits"}

        # Calculate check digit
        total = 0
        for i, digit in enumerate(nhs_number[:9]):
            total += int(digit) * (10 - i)

        remainder = total % 11
        check_digit = 11 - remainder

        if check_digit == 11:
            check_digit = 0

        if check_digit == 10:
            return {"valid": False, "error": "Invalid NHS number"}

        if check_digit != int(nhs_number[9]):
            return {"valid": False, "error": "Invalid check digit"}

        return {"valid": True, "formatted": f"{nhs_number[:3]} {nhs_number[3:6]} {nhs_number[6:]}"}

    def lookup_patient_demographics(self, nhs_number: str) -> Dict[str, Any]:
        """
        Look up patient demographics from PDS.

        In production, calls NHS PDS API.
        """
        validation = self.validate_nhs_number(nhs_number)
        if not validation["valid"]:
            return {"found": False, "error": validation["error"]}

        # Simulated PDS response
        return {
            "found": True,
            "patient": {
                "nhs_number": nhs_number,
                "given_name": "John",
                "family_name": "Smith",
                "gender": "male",
                "birth_date": "1980-01-15",
                "address": {
                    "line": ["123 High Street"],
                    "city": "London",
                    "postal_code": "SW1A 1AA"
                },
                "gp_practice": {
                    "ods_code": "A12345",
                    "name": "Example Surgery"
                }
            }
        }

    def create_referral(
        self,
        patient_nhs_number: str,
        patient_name: str,
        gp_practice_code: str,
        gp_name: str,
        condition: str,
        clinical_notes: str,
        urgency: str = "routine"
    ) -> NHSReferral:
        """
        Create an NHS referral.

        Args:
            patient_nhs_number: Patient's NHS number
            patient_name: Patient name
            gp_practice_code: ODS code of GP practice
            gp_name: Referring GP name
            condition: Primary condition
            clinical_notes: Clinical notes
            urgency: Referral urgency (routine, urgent, emergency)

        Returns:
            Created referral
        """
        # Generate NHS-style reference
        nhs_reference = f"SANA-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"

        referral = NHSReferral(
            id=uuid4(),
            nhs_reference=nhs_reference,
            patient_nhs_number=patient_nhs_number,
            patient_name=patient_name,
            gp_practice_code=gp_practice_code,
            gp_name=gp_name,
            condition=condition,
            clinical_notes=clinical_notes,
            urgency=urgency,
            referred_at=datetime.utcnow()
        )

        self.referrals[referral.id] = referral

        logger.info(f"Created NHS referral {nhs_reference}")

        return referral

    def match_referral_to_practitioner(
        self,
        referral_id: UUID,
        practitioner_id: UUID,
        specialty: str
    ) -> NHSReferral:
        """Match a referral to a SANA practitioner."""
        if referral_id not in self.referrals:
            raise ValueError("Referral not found")

        referral = self.referrals[referral_id]
        referral.matched_practitioner_id = practitioner_id
        referral.matched_specialty = specialty

        logger.info(f"Matched referral {referral.nhs_reference} to practitioner {practitioner_id}")

        return referral

    def accept_referral(self, referral_id: UUID) -> NHSReferral:
        """Accept a referral."""
        if referral_id not in self.referrals:
            raise ValueError("Referral not found")

        referral = self.referrals[referral_id]
        referral.status = NHSReferralStatus.ACCEPTED
        referral.accepted_at = datetime.utcnow()

        return referral

    def complete_referral(self, referral_id: UUID) -> NHSReferral:
        """Mark referral as completed."""
        if referral_id not in self.referrals:
            raise ValueError("Referral not found")

        referral = self.referrals[referral_id]
        referral.status = NHSReferralStatus.COMPLETED
        referral.completed_at = datetime.utcnow()

        return referral

    def get_referral(self, referral_id: UUID) -> Optional[NHSReferral]:
        """Get a referral by ID."""
        return self.referrals.get(referral_id)

    def get_referrals_by_status(self, status: NHSReferralStatus) -> List[NHSReferral]:
        """Get all referrals with a given status."""
        return [r for r in self.referrals.values() if r.status == status]

    def get_practitioner_referrals(self, practitioner_id: UUID) -> List[NHSReferral]:
        """Get all referrals for a practitioner."""
        return [
            r for r in self.referrals.values()
            if r.matched_practitioner_id == practitioner_id
        ]

    def link_nhs_login(self, nhs_number: str, user_id: UUID) -> bool:
        """Link NHS login to SANA user account."""
        validation = self.validate_nhs_number(nhs_number)
        if not validation["valid"]:
            return False

        self.nhs_logins[nhs_number] = user_id
        logger.info(f"Linked NHS number to user {user_id}")
        return True

    def get_user_by_nhs_number(self, nhs_number: str) -> Optional[UUID]:
        """Get SANA user ID from NHS number."""
        return self.nhs_logins.get(nhs_number)

    def generate_discharge_summary(
        self,
        referral_id: UUID,
        outcomes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate discharge summary for GP."""
        if referral_id not in self.referrals:
            raise ValueError("Referral not found")

        referral = self.referrals[referral_id]

        return {
            "nhs_reference": referral.nhs_reference,
            "patient_nhs_number": referral.patient_nhs_number,
            "patient_name": referral.patient_name,
            "referring_gp": {
                "name": referral.gp_name,
                "practice_code": referral.gp_practice_code
            },
            "referral_date": referral.referred_at.isoformat(),
            "condition": referral.condition,
            "treatment_provided": outcomes.get("treatment_type", ""),
            "sessions_completed": outcomes.get("sessions", 0),
            "outcome_summary": outcomes.get("summary", ""),
            "recommendations": outcomes.get("recommendations", []),
            "discharge_date": datetime.utcnow().isoformat(),
            "practitioner": {
                "id": str(referral.matched_practitioner_id),
                "specialty": referral.matched_specialty
            }
        }

    def get_referral_statistics(self) -> Dict[str, Any]:
        """Get referral statistics."""
        total = len(self.referrals)
        by_status = {}
        by_urgency = {}

        for referral in self.referrals.values():
            by_status[referral.status.value] = by_status.get(referral.status.value, 0) + 1
            by_urgency[referral.urgency] = by_urgency.get(referral.urgency, 0) + 1

        return {
            "total_referrals": total,
            "by_status": by_status,
            "by_urgency": by_urgency
        }
