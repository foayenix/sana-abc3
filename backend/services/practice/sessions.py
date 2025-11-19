"""
Session notes service for practitioners.
"""

from typing import List, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class SOAPNote(BaseModel):
    """SOAP format session note."""
    subjective: str = ""  # Client's reported symptoms, concerns
    objective: str = ""   # Practitioner's observations
    assessment: str = ""  # Diagnosis/assessment
    plan: str = ""        # Treatment plan


class SessionNote(BaseModel):
    """Complete session documentation."""
    id: UUID
    practitioner_id: UUID
    client_id: UUID
    booking_id: Optional[UUID] = None

    # Session info
    session_date: datetime
    duration_minutes: int
    session_type: str  # initial, follow_up, discharge

    # SOAP notes
    soap_note: SOAPNote

    # Treatments
    treatments_applied: List[str] = []
    herbs_prescribed: List[str] = []
    supplements_prescribed: List[str] = []

    # Recommendations
    recommendations: List[str] = []
    homework: List[str] = []
    follow_up_date: Optional[datetime] = None

    # Attachments
    attachments: List[str] = []  # File URLs

    # Metadata
    is_complete: bool = False
    created_at: datetime
    updated_at: datetime


class SessionTemplate(BaseModel):
    """Reusable session note template."""
    id: UUID
    practitioner_id: UUID
    name: str
    session_type: str
    default_treatments: List[str] = []
    default_recommendations: List[str] = []
    soap_prompts: Dict[str, str] = {}  # Prompts for each SOAP section


class SessionService:
    """
    Manages session notes and documentation.

    Features:
    - SOAP format notes
    - Templates for efficiency
    - Treatment tracking
    - Follow-up scheduling
    """

    def __init__(self):
        self.sessions: Dict[UUID, SessionNote] = {}
        self.templates: Dict[UUID, SessionTemplate] = {}
        logger.info("SessionService initialized")

    def create_session(
        self,
        practitioner_id: UUID,
        client_id: UUID,
        session_date: datetime,
        duration_minutes: int = 60,
        session_type: str = "follow_up",
        booking_id: Optional[UUID] = None
    ) -> SessionNote:
        """Create a new session note."""
        now = datetime.utcnow()

        session = SessionNote(
            id=uuid4(),
            practitioner_id=practitioner_id,
            client_id=client_id,
            booking_id=booking_id,
            session_date=session_date,
            duration_minutes=duration_minutes,
            session_type=session_type,
            soap_note=SOAPNote(),
            created_at=now,
            updated_at=now
        )

        self.sessions[session.id] = session
        logger.info(f"Created session {session.id}")

        return session

    def update_soap_notes(
        self,
        session_id: UUID,
        subjective: Optional[str] = None,
        objective: Optional[str] = None,
        assessment: Optional[str] = None,
        plan: Optional[str] = None
    ) -> Optional[SessionNote]:
        """Update SOAP notes for a session."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        if subjective is not None:
            session.soap_note.subjective = subjective
        if objective is not None:
            session.soap_note.objective = objective
        if assessment is not None:
            session.soap_note.assessment = assessment
        if plan is not None:
            session.soap_note.plan = plan

        session.updated_at = datetime.utcnow()
        return session

    def add_treatments(
        self,
        session_id: UUID,
        treatments: List[str] = None,
        herbs: List[str] = None,
        supplements: List[str] = None
    ) -> Optional[SessionNote]:
        """Add treatments to a session."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        if treatments:
            session.treatments_applied.extend(treatments)
        if herbs:
            session.herbs_prescribed.extend(herbs)
        if supplements:
            session.supplements_prescribed.extend(supplements)

        session.updated_at = datetime.utcnow()
        return session

    def add_recommendations(
        self,
        session_id: UUID,
        recommendations: List[str] = None,
        homework: List[str] = None,
        follow_up_date: Optional[datetime] = None
    ) -> Optional[SessionNote]:
        """Add recommendations and follow-up to a session."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        if recommendations:
            session.recommendations.extend(recommendations)
        if homework:
            session.homework.extend(homework)
        if follow_up_date:
            session.follow_up_date = follow_up_date

        session.updated_at = datetime.utcnow()
        return session

    def complete_session(self, session_id: UUID) -> bool:
        """Mark a session as complete."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.is_complete = True
        session.updated_at = datetime.utcnow()
        return True

    def get_client_sessions(
        self,
        practitioner_id: UUID,
        client_id: UUID,
        limit: int = 10
    ) -> List[SessionNote]:
        """Get session history for a client."""
        sessions = [
            s for s in self.sessions.values()
            if s.practitioner_id == practitioner_id and s.client_id == client_id
        ]

        return sorted(sessions, key=lambda x: x.session_date, reverse=True)[:limit]

    def get_session(self, session_id: UUID) -> Optional[SessionNote]:
        """Get a specific session."""
        return self.sessions.get(session_id)

    def create_template(
        self,
        practitioner_id: UUID,
        name: str,
        session_type: str,
        default_treatments: List[str] = None,
        default_recommendations: List[str] = None,
        soap_prompts: Dict[str, str] = None
    ) -> SessionTemplate:
        """Create a reusable session template."""
        template = SessionTemplate(
            id=uuid4(),
            practitioner_id=practitioner_id,
            name=name,
            session_type=session_type,
            default_treatments=default_treatments or [],
            default_recommendations=default_recommendations or [],
            soap_prompts=soap_prompts or {}
        )

        self.templates[template.id] = template
        return template

    def get_templates(self, practitioner_id: UUID) -> List[SessionTemplate]:
        """Get all templates for a practitioner."""
        return [
            t for t in self.templates.values()
            if t.practitioner_id == practitioner_id
        ]

    def apply_template(
        self,
        session_id: UUID,
        template_id: UUID
    ) -> Optional[SessionNote]:
        """Apply a template to a session."""
        if session_id not in self.sessions or template_id not in self.templates:
            return None

        session = self.sessions[session_id]
        template = self.templates[template_id]

        session.treatments_applied = template.default_treatments.copy()
        session.recommendations = template.default_recommendations.copy()
        session.updated_at = datetime.utcnow()

        return session

    def get_practitioner_stats(self, practitioner_id: UUID) -> Dict:
        """Get session statistics for a practitioner."""
        sessions = [
            s for s in self.sessions.values()
            if s.practitioner_id == practitioner_id
        ]

        completed = len([s for s in sessions if s.is_complete])
        total_duration = sum(s.duration_minutes for s in sessions)

        # Treatment frequency
        treatment_counts: Dict[str, int] = {}
        for session in sessions:
            for treatment in session.treatments_applied:
                treatment_counts[treatment] = treatment_counts.get(treatment, 0) + 1

        top_treatments = sorted(
            treatment_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_sessions": len(sessions),
            "completed_sessions": completed,
            "total_hours": total_duration / 60,
            "avg_duration_minutes": total_duration / len(sessions) if sessions else 0,
            "top_treatments": dict(top_treatments)
        }
