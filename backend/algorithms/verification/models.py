"""
Pydantic models for verification algorithms.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime


class CredentialInput(BaseModel):
    """Input model for credential verification."""
    practitioner_id: UUID
    credentials: List[str]
    documents: List[Dict] = []


class VerificationResult(BaseModel):
    """Result for a single credential verification."""
    credential: str
    verified: bool
    source: Optional[str] = None
    expiration_date: Optional[datetime] = None
    notes: str = ""


class CredentialOutput(BaseModel):
    """Output model for credential verification."""
    practitioner_id: UUID
    verified: bool
    verification_results: List[VerificationResult]
    confidence_score: float
    flags: List[str] = []
