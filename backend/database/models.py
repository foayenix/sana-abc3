"""
SQLAlchemy ORM models for SANA Platform.

These models define the database schema for persistent storage.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum, Table, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum
from datetime import datetime


# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, enum.Enum):
    CLIENT = "client"
    PRACTITIONER = "practitioner"
    ADMIN = "admin"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    FAILED = "failed"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    SANA_PLUS = "sana_plus"  # £5/month for clients
    BASIC = "basic"          # £25/month for practitioners
    PRO = "pro"              # £50/month for practitioners
    PREMIUM = "premium"      # £75/month for practitioners


class SANAStatus(str, enum.Enum):
    NEEDS_SUPPORT = "needs_support"
    REBUILDING = "rebuilding"
    BALANCED = "balanced"
    THRIVING = "thriving"
    RADIANT = "radiant"


# ============================================================================
# ASSOCIATION TABLES
# ============================================================================

practitioner_specialties = Table(
    'practitioner_specialties',
    Base.metadata,
    Column('practitioner_id', Integer, ForeignKey('practitioners.id'), primary_key=True),
    Column('specialty_id', Integer, ForeignKey('specialties.id'), primary_key=True)
)

practitioner_modalities = Table(
    'practitioner_modalities',
    Base.metadata,
    Column('practitioner_id', Integer, ForeignKey('practitioners.id'), primary_key=True),
    Column('modality_id', Integer, ForeignKey('modalities.id'), primary_key=True)
)


# ============================================================================
# USER MODELS
# ============================================================================

class User(Base):
    """Base user model for authentication."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)

    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)

    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires_at = Column(DateTime)
    stripe_customer_id = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime)

    # Relationships
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False)
    practitioner_profile = relationship("PractitionerProfile", back_populates="user", uselist=False)
    refresh_tokens = relationship("RefreshToken", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class RefreshToken(Base):
    """Stores refresh tokens for JWT authentication."""
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")


# ============================================================================
# CLIENT MODELS
# ============================================================================

class ClientProfile(Base):
    """Extended profile for clients."""
    __tablename__ = 'client_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    # Demographics
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)

    # Preferences
    goals = Column(JSON)  # List of wellness goals
    preferences = Column(JSON)  # Treatment preferences
    budget_max = Column(Float)  # Max per session
    time_available_weekly = Column(Integer)  # Minutes per week

    # Health data
    current_conditions = Column(JSON)  # List of current health conditions
    allergies = Column(JSON)
    medications = Column(JSON)

    # SANA Health Score
    sana_health_score = Column(Float)  # 0-100
    sana_status = Column(Enum(SANAStatus))
    sana_age = Column(Float)  # Biological age estimate
    domain_scores = Column(JSON)  # {physical, emotional, social, cognitive, spiritual}
    top_levers = Column(JSON)  # Top 3 recommended actions
    score_updated_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="client_profile")
    health_scores = relationship("HealthScoreHistory", back_populates="client")
    journal_entries = relationship("JournalEntry", back_populates="client")
    bookings = relationship("Booking", back_populates="client")
    outcome_measures = relationship("OutcomeMeasure", back_populates="client")
    wellness_logs = relationship("WellnessLog", back_populates="client")


class HealthScoreHistory(Base):
    """Track health score changes over time."""
    __tablename__ = 'health_score_history'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)

    # Scores
    overall_score = Column(Float, nullable=False)
    physical_score = Column(Float)
    emotional_score = Column(Float)
    social_score = Column(Float)
    cognitive_score = Column(Float)
    spiritual_score = Column(Float)

    sana_status = Column(Enum(SANAStatus))
    sana_age = Column(Float)

    # Source
    source = Column(String(50))  # intake, outcome_measure, wearable, etc.

    created_at = Column(DateTime, server_default=func.now())

    client = relationship("ClientProfile", back_populates="health_scores")

    __table_args__ = (
        Index('ix_health_score_client_date', 'client_id', 'created_at'),
    )


class WellnessLog(Base):
    """Daily wellness tracking entries."""
    __tablename__ = 'wellness_logs'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)

    # Tracked metrics
    date = Column(DateTime, nullable=False)
    mood_score = Column(Integer)  # 1-5
    energy_score = Column(Integer)  # 1-5
    sleep_hours = Column(Float)
    sleep_quality = Column(Integer)  # 1-5
    stress_level = Column(Integer)  # 1-5
    pain_level = Column(Integer)  # 0-10

    # Symptoms
    symptoms = Column(JSON)  # List of reported symptoms
    notes = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    client = relationship("ClientProfile", back_populates="wellness_logs")

    __table_args__ = (
        Index('ix_wellness_log_client_date', 'client_id', 'date'),
    )


# ============================================================================
# PRACTITIONER MODELS
# ============================================================================

class PractitionerProfile(Base):
    """Extended profile for practitioners."""
    __tablename__ = 'practitioners'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    # Professional info
    business_name = Column(String(255))
    bio = Column(Text)
    years_experience = Column(Integer)

    # Location
    practice_address = Column(String(500))
    city = Column(String(100))
    postcode = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    offers_remote = Column(Boolean, default=False)

    # Pricing
    session_rate = Column(Float)  # Base rate
    session_duration = Column(Integer, default=60)  # Minutes
    currency = Column(String(3), default='GBP')

    # Verification
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    verification_score = Column(Float)  # 0-100 from SCVM
    verified_at = Column(DateTime)
    verification_expires_at = Column(DateTime)

    # SANA Index
    sana_index_score = Column(Float)  # 0-100
    credential_score = Column(Float)
    volume_score = Column(Float)
    outcome_score = Column(Float)
    completeness_score = Column(Float)
    satisfaction_score = Column(Float)
    index_updated_at = Column(DateTime)

    # Statistics
    total_sessions = Column(Integer, default=0)
    total_clients = Column(Integer, default=0)
    avg_rating = Column(Float)
    review_count = Column(Integer, default=0)

    # Payment
    stripe_account_id = Column(String(100))
    payout_enabled = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="practitioner_profile")
    credentials = relationship("Credential", back_populates="practitioner")
    specialties = relationship("Specialty", secondary=practitioner_specialties, back_populates="practitioners")
    modalities = relationship("Modality", secondary=practitioner_modalities, back_populates="practitioners")
    availability = relationship("Availability", back_populates="practitioner")
    bookings = relationship("Booking", back_populates="practitioner")
    sessions = relationship("Session", back_populates="practitioner")
    reviews = relationship("Review", back_populates="practitioner")


class Credential(Base):
    """Practitioner credentials and qualifications."""
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)

    # Credential details
    credential_type = Column(String(100), nullable=False)  # degree, certification, license
    name = Column(String(255), nullable=False)  # e.g., "BSc Nutrition", "CNHC Registered"
    issuing_body = Column(String(255))
    registration_number = Column(String(100))

    # Dates
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)

    # Verification
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    verification_confidence = Column(Float)  # 0-100
    verified_at = Column(DateTime)
    verification_notes = Column(Text)

    # Documents
    document_url = Column(String(500))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    practitioner = relationship("PractitionerProfile", back_populates="credentials")


class Specialty(Base):
    """Treatment specialties."""
    __tablename__ = 'specialties'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))  # e.g., "mental_health", "physical", "nutrition"

    practitioners = relationship("PractitionerProfile", secondary=practitioner_specialties, back_populates="specialties")


class Modality(Base):
    """Treatment modalities."""
    __tablename__ = 'modalities'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))  # e.g., "cam", "bodywork", "energy"

    practitioners = relationship("PractitionerProfile", secondary=practitioner_modalities, back_populates="modalities")


class Availability(Base):
    """Practitioner availability slots."""
    __tablename__ = 'availability'

    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)

    # Time slot
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    start_time = Column(String(5))  # HH:MM
    end_time = Column(String(5))  # HH:MM

    # Or specific date
    specific_date = Column(DateTime)

    # Type
    is_recurring = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)  # For time off

    practitioner = relationship("PractitionerProfile", back_populates="availability")


# ============================================================================
# BOOKING & SESSION MODELS
# ============================================================================

class Booking(Base):
    """Appointment bookings."""
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)

    # Timing
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default='Europe/London')

    # Details
    session_type = Column(String(50))  # initial, follow_up, telehealth
    notes = Column(Text)  # Client notes for practitioner

    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    confirmed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)

    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("ClientProfile", back_populates="bookings")
    practitioner = relationship("PractitionerProfile", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    session = relationship("Session", back_populates="booking", uselist=False)

    __table_args__ = (
        Index('ix_booking_practitioner_date', 'practitioner_id', 'scheduled_at'),
        Index('ix_booking_client_date', 'client_id', 'scheduled_at'),
    )


class Session(Base):
    """Completed treatment sessions with notes."""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), unique=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)

    # Session details
    session_date = Column(DateTime, nullable=False)
    actual_duration = Column(Integer)  # Actual minutes

    # Practitioner notes (free text)
    subjective_notes = Column(Text)  # Client reported symptoms
    objective_notes = Column(Text)  # Practitioner observations
    assessment_notes = Column(Text)  # Diagnosis/assessment
    plan_notes = Column(Text)  # Treatment plan

    # Structured data (extracted by Session Summarization Engine)
    structured_data = Column(JSON)  # {treatment_type, dosage, modality, herbs, etc.}

    # Treatments applied
    treatments_applied = Column(JSON)  # List of treatment IDs

    # Recommendations
    recommendations = Column(JSON)  # Follow-up actions for client
    follow_up_date = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    booking = relationship("Booking", back_populates="session")
    practitioner = relationship("PractitionerProfile", back_populates="sessions")


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class Payment(Base):
    """Payment transactions."""
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)

    # Amounts
    amount = Column(Float, nullable=False)  # Total charged
    currency = Column(String(3), default='GBP')
    platform_fee = Column(Float)  # SANA commission (10-15%)
    practitioner_amount = Column(Float)  # After commission

    # Stripe
    stripe_payment_intent_id = Column(String(100))
    stripe_charge_id = Column(String(100))

    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Refund
    refunded_amount = Column(Float)
    refund_reason = Column(Text)
    refunded_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    captured_at = Column(DateTime)

    booking = relationship("Booking", back_populates="payment")


# ============================================================================
# JOURNAL & REFLECTION MODELS
# ============================================================================

class JournalEntry(Base):
    """User journal entries for SIRM analysis."""
    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)

    # Content
    content = Column(Text, nullable=False)

    # AI Analysis (from SIRM)
    ai_analysis = Column(JSON)  # {mood_detected, themes, patterns}
    ai_reflection = Column(Text)  # AI generated reflection
    persona_used = Column(String(50))  # philosopher, therapist, poet, scientist
    wellness_suggestions = Column(JSON)  # Evidence-based suggestions

    # Sentiment
    sentiment_score = Column(Float)  # -1 to 1
    emotional_tone = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    client = relationship("ClientProfile", back_populates="journal_entries")

    __table_args__ = (
        Index('ix_journal_client_date', 'client_id', 'created_at'),
    )


# ============================================================================
# OUTCOME MEASUREMENT MODELS
# ============================================================================

class OutcomeMeasure(Base):
    """Patient-Reported Outcome Measures (PROMs)."""
    __tablename__ = 'outcome_measures'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.id'))

    # Measure type
    measure_type = Column(String(50), nullable=False)  # WHO5, DASS21, VAS, custom
    timing = Column(String(20))  # pre_session, post_session, 1_week, 1_month

    # Scores
    responses = Column(JSON, nullable=False)  # Raw responses
    total_score = Column(Float)
    subscale_scores = Column(JSON)  # {anxiety, depression, stress} for DASS21

    # Delivery
    delivered_via = Column(String(20))  # email, sms, app
    delivered_at = Column(DateTime)
    completed_at = Column(DateTime)
    reminder_count = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())

    client = relationship("ClientProfile", back_populates="outcome_measures")

    __table_args__ = (
        Index('ix_outcome_client_type', 'client_id', 'measure_type'),
    )


# ============================================================================
# MESSAGING MODELS
# ============================================================================

class Conversation(Base):
    """Conversations between clients and practitioners."""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """Individual messages in conversations."""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Content
    content = Column(Text, nullable=False)
    attachment_url = Column(String(500))

    # Status
    read_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index('ix_message_conversation', 'conversation_id', 'created_at'),
    )


# ============================================================================
# REVIEW MODELS
# ============================================================================

class Review(Base):
    """Client reviews of practitioners."""
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.id'))

    # Rating
    overall_rating = Column(Integer, nullable=False)  # 1-5
    professionalism_rating = Column(Integer)
    effectiveness_rating = Column(Integer)
    communication_rating = Column(Integer)

    # Content
    comment = Column(Text)

    # Verification
    is_verified = Column(Boolean, default=False)  # Verified they had a session

    # Moderation
    is_published = Column(Boolean, default=True)
    moderated_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

    practitioner = relationship("PractitionerProfile", back_populates="reviews")

    __table_args__ = (
        CheckConstraint('overall_rating >= 1 AND overall_rating <= 5', name='check_rating_range'),
    )


# ============================================================================
# WEARABLE INTEGRATION MODELS
# ============================================================================

class WearableConnection(Base):
    """Connected wearable devices/services."""
    __tablename__ = 'wearable_connections'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)

    # Provider
    provider = Column(String(50), nullable=False)  # apple_health, fitbit, oura, whoop, garmin

    # Auth
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)

    # Sync
    last_sync_at = Column(DateTime)
    sync_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WearableData(Base):
    """Data synced from wearables."""
    __tablename__ = 'wearable_data'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client_profiles.id'), nullable=False)
    connection_id = Column(Integer, ForeignKey('wearable_connections.id'), nullable=False)

    # Data
    date = Column(DateTime, nullable=False)
    metric_type = Column(String(50), nullable=False)  # heart_rate, hrv, sleep, steps, etc.
    value = Column(Float)
    unit = Column(String(20))
    metadata = Column(JSON)  # Additional context

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('ix_wearable_client_date_type', 'client_id', 'date', 'metric_type'),
    )
