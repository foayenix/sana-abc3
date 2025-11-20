# SANA Platform - Architecture, Algorithms & Data Flow Analysis

## Overview
SANA is a comprehensive health-tech platform connecting users with CAM (Complementary and Alternative Medicine) practitioners. It uses multiple AI algorithms to score health, match practitioners, verify credentials, and manage sessions.

---

## 1. ALGORITHMS SUMMARY

### 1.1 HEALTH SCORING ALGORITHMS

#### SISM (SANA Intake Scoring Model)
- **Location**: `/backend/algorithms/scoring/sism.py`
- **Purpose**: Calculate baseline health score from multi-domain questionnaire data
- **Input**: User responses across 5 health domains
- **Output**: Overall health score (0-100), domain-specific scores, weak domain identification
- **Domains**: Physical, Emotional, Social, Cognitive, Spiritual
- **Weights**: Physical (0.25), Emotional (0.25), Social (0.15), Cognitive (0.20), Spiritual (0.15)
- **Key Functions**:
  - `calculate()` - Main health score calculation
  - `calculate_domain_score()` - Score individual health domains
  - `identify_weak_domains()` - Find areas needing improvement
  - `normalize_score()` - Convert raw scores to 0-100 scale
- **API Route**: `POST /api/v1/scoring/calculate`

---

### 1.2 PRACTITIONER MATCHING ALGORITHMS

#### SPRM (SANA Practitioner Recommendation Model)
- **Location**: `/backend/algorithms/matching/sprm.py`
- **Purpose**: Intelligent AI-powered matching between users and verified CAM practitioners
- **Input**: 
  - User ID, SISM output (health score, weak domains)
  - User preferences (location, budget, language, philosophy)
  - Practitioner pool
  - Optional: User outcome history
- **Output**: Top 5 practitioner recommendations with detailed scoring
- **Matching Flow**:
  1. Filter by verification (MIN_VERIFICATION_SCORE ≥ 85)
  2. Filter by specialty match (target domains overlap)
  3. Filter by geography (distance or virtual preference)
  4. Filter by budget (hourly rate vs max budget)
  5. Calculate multi-factor match scores
  6. Sort and rank recommendations
  7. Generate explanations and warnings
  
- **Scoring Factors**:
  - Health need alignment (40%): Specialty overlap with weak domains
  - Credibility score (25%): Verification tier, experience, credentials, client ratings
  - Practical fit (20%): Distance, affordability, availability
  - Evidence alignment (10%): Evidence-based approach usage
  - Preference match (5%): Philosophy, communication style, language

- **Key Functions**:
  - `find_best_matches()` - Main matching function
  - `_score_health_need_alignment()` - Domain specialty matching
  - `_score_credibility()` - Practitioner credibility
  - `_score_practical_fit()` - Location and budget scoring using Haversine formula
  - `_generate_recommendation()` - Create recommendation with explanations
  
- **API Route**: `GET /api/v1/matching/test-matching`

#### SPM (SANA Practitioner Matcher)
- **Location**: `/backend/algorithms/matching/spm.py`
- **Purpose**: Basic practitioner matching (less comprehensive than SPRM)
- **Status**: TODO - Placeholder implementation
- **API Route**: `POST /api/v1/matching/recommend`

---

### 1.3 CREDIBILITY & VERIFICATION ALGORITHMS

#### SCVM (SANA Credential Vetting Model)
- **Location**: `/backend/algorithms/verification/scvm.py`
- **Purpose**: Verify practitioner credentials with 99%+ accuracy
- **Features**:
  - OCR-based document parsing (simulated)
  - Pattern matching for credential formats
  - Fraud detection with confidence scoring
  - Registry verification
  - Human review queue management
- **Input**: Uploaded credentials, documents, identity verification
- **Output**: Verification status, confidence score, fraud indicators
- **Verification Tiers**: Unverified, Basic, Standard, Gold, Premium
- **Key Functions**:
  - `verify_credentials()` - Main verification function
  - `_check_document_authenticity()` - Document fraud detection
  - `_verify_registry()` - Check against known registries
  - `_calculate_confidence_score()` - Generate confidence metrics
  - `_detect_fraud_indicators()` - Identify suspicious patterns

---

### 1.4 CREDIBILITY INDEX ALGORITHM

#### SANA Index Calculator
- **Location**: `/backend/algorithms/index/sana_index.py`
- **Purpose**: Calculate overall practitioner credibility scores (0-100)
- **Component Breakdown**:
  1. Credentials (20%): Qualifications, certifications, education
  2. Treatment Volume (20%): Total clients, sessions logged
  3. Outcomes (40%): Client health improvements, effect sizes, retention
  4. Data Completeness (10%): Session note quality, outcome measure compliance
  5. Client Satisfaction (10%): Reviews, rebooking rate, referral rate

- **Scoring Details**:
  - Credentials: Base points (PhD=25, Masters=20, etc.) × Institution multiplier (1.0-1.2)
  - Volume: Logarithmic scoring for clients and sessions
  - Outcomes: Improvement %, sample size bonus, consistency, retention
  - Completeness: Note quality %, outcome compliance %, data recency
  - Satisfaction: Weighted review ratings, rebooking %, referral %

- **Key Functions**:
  - `calculate()` - Main SANA Index calculation
  - `_calculate_credentials_score()` - Credential component
  - `_calculate_outcomes_score()` - Outcome effectiveness
  - `_calculate_volume_score()` - Treatment volume
  - `_calculate_completeness_score()` - Data quality
  - `_calculate_satisfaction_score()` - Client satisfaction
  - `_estimate_percentile()` - Rank against other practitioners
  - `_determine_trend()` - Score improvement/decline trend

- **API Route**: `GET /api/v1/index/calculate`

---

### 1.5 ADDITIONAL ALGORITHMS

#### Evidence-Based Recommendation Engine
- **Location**: `/backend/algorithms/evidence/engine.py`
- **Purpose**: Recommend evidence-based interventions for specific health conditions
- **Key Functions**: `recommend()` - Generate intervention recommendations

#### Herb Synergy Index (HSI)
- **Location**: `/backend/algorithms/herbs/shi.py`, `/backend/algorithms/herbs/synergy.py`
- **Purpose**: 
  - Calculate herb efficacy scores with statistical power
  - Recommend herbal combinations with synergy analysis
- **Key Functions**:
  - `calculate_herb_index()` - Evidence volume, efficacy, safety, data quality
  - `calculate_condition_efficacy()` - Herb effectiveness for specific conditions
  - `calculate_combination_protocol()` - Synergistic herb recommendations

#### Engagement Score (SEC, SFC, SOU)
- **Location**: `/backend/algorithms/engagement/`
- **Purpose**: Track user engagement and practice adherence
- **Algorithms**: 
  - SEC: Session Engagement Compliance
  - SFC: Session Follow-through Compliance
  - SOU: Session Outcome Utilization

#### Planning Optimization
- **Location**: `/backend/algorithms/planning/`
- **Purpose**: Multi-objective optimization for resource allocation
- **Algorithms**:
  - SHAM: Schedule/Health/Allocation Model
  - Timetable Optimizer: Optimize session scheduling
  - Constraint Optimizer: Budget, time, outcome constraints

#### Reflection & Insight (SIRM)
- **Location**: `/backend/algorithms/reflection/sirm.py`
- **Purpose**: Generate personalized health insights and recommendations

#### Safety Screening (SST)
- **Location**: `/backend/algorithms/safety/sst.py`
- **Purpose**: Screen for contraindications and safety risks

#### Outcome Measurement (PROMS)
- **Location**: `/backend/algorithms/outcomes/proms.py`
- **Purpose**: Patient-Reported Outcome Measures collection and tracking

---

## 2. BUSINESS LOGIC FLOWS

### 2.1 USER AUTHENTICATION FLOW

**Flow**: Registration → Login → Token Management → Logout

**Actors**: Client or Practitioner User

**Key Service**: `AuthService` (`/backend/services/auth.py`)

**Steps**:
1. **Registration** (`POST /api/v1/auth/register`)
   - Validate email and password (min 8 chars)
   - Hash password with bcrypt
   - Create user record (role: CLIENT or PRACTITIONER)
   - Generate access token (15 min expiry) and refresh token (7 days)
   - Store refresh token in database

2. **Login** (`POST /api/v1/auth/login`)
   - Verify email and password
   - Check user exists and credentials match
   - Generate new access + refresh token pair
   - Return tokens and user profile

3. **Token Refresh** (`POST /api/v1/auth/refresh`)
   - Validate refresh token from database
   - Revoke old token
   - Generate new token pair

4. **Get Current User** (`GET /api/v1/auth/me`)
   - Extract user_id from access token
   - Return user profile with role and subscription

**Token Structure**:
- Access Token: `{sub: user_id, role: role, type: access, exp: timestamp, iat: timestamp}`
- Refresh Token: Stored in database, marked with expiry date

---

### 2.2 HEALTH ASSESSMENT & SCORING FLOW

**Flow**: Questionnaire → SISM Calculation → Score Interpretation → Weak Domain Identification

**Key Service**: `HealthService` (Flutter: `/client/lib/core/api/services/health_service.dart`)

**Backend**: `SISMAlgorithm` (`/backend/algorithms/scoring/sism.py`)

**Steps**:
1. **User Completes Questionnaire**
   - Answer 35+ questions across 5 domains (physical, emotional, social, cognitive, spiritual)
   - Each question rated 0-10
   - Flutter app: `HealthNotifier.submitQuestionnaire()`

2. **SISM Calculation** (`POST /api/v1/scoring/calculate`)
   - Group responses by domain
   - Normalize each score to 0-100 scale
   - Calculate weighted average per domain
   - Sum weighted contributions for overall score (0-100)
   - Identify weak domains (score < 60 threshold)

3. **Score Storage & History**
   - Save SISM output with timestamp
   - Track trends across multiple assessments
   - Identify improvement areas over time

4. **Health Dashboard Display**
   - Show current overall score
   - Display domain breakdown with visual
   - Highlight weak domains needing attention
   - Show trend arrows (improving/stable/declining)

**Data Model** (`/backend/database/models.py`):
```
HealthScore:
  - user_id
  - overall_score (0-100)
  - domain_scores: {physical, emotional, social, cognitive, spiritual}
  - weak_domains: [list]
  - created_at
```

---

### 2.3 PRACTITIONER MATCHING & RECOMMENDATION FLOW

**Flow**: Health Assessment → Match Criteria → SPRM Algorithm → Top Recommendations

**Actors**: Client User, Practitioner Pool

**Key Service**: `SPRMAlgorithm` (`/backend/algorithms/matching/sprm.py`)

**Steps**:
1. **Trigger Matching** (`GET /api/v1/matching/test-matching`)
   - User completes health questionnaire (SISM)
   - User sets matching preferences:
     - Location (latitude/longitude) + max distance
     - Budget per session
     - Virtual session willingness
     - Treatment philosophy preference
     - Languages, communication style

2. **Multi-Stage Filtering**
   - **Stage 1**: Filter by verification (min SCVM score ≥ 85)
   - **Stage 2**: Filter by specialty (target domains match weak domains)
   - **Stage 3**: Filter by geography (distance calculation using Haversine formula)
   - **Stage 4**: Filter by budget (hourly rate ≤ max budget or sliding scale available)

3. **Score Calculation** (5 factors):
   - Health Need Alignment (40%)
     - Domain coverage: overlap of practitioner specialties with weak domains
     - Experience: clients treated, outcome improvement %, credentials
   
   - Credibility Score (25%)
     - Verification tier (gold=40, standard=30, basic=20)
     - Years experience (10+=30, 5+=20, 2+=10)
     - Credentials count and professional memberships
     - Client satisfaction rating
   
   - Practical Fit (20%)
     - Distance scoring (2km=40pts, 5km=30pts, etc.)
     - Affordability ratio vs budget
     - Accepts new clients, has availability
     - Insurance acceptance
   
   - Evidence Alignment (10%)
     - Evidence-based treatment (60 pts)
     - Uses evidence-based interventions (8 pts per intervention)
   
   - Preference Match (5%)
     - Treatment philosophy match (40 pts)
     - Communication style match (30 pts)
     - Language match (20 pts)

4. **Ranking & Selection**
   - Calculate overall score: weighted sum of 5 factors
   - Sort descending by overall score
   - Select top 5 as main recommendations
   - Select 3 honorable mentions (6-8th ranked)

5. **Generate Recommendations**
   - Create headline (excellent/highly recommended/good match)
   - Why recommended (key reasons)
   - What to expect (philosophy, modalities, session focus)
   - Estimated sessions needed (based on health score)
   - Estimated total cost
   - Available time slots
   - Similar client outcomes
   - Potential concerns (if any)

6. **Return to Client**
   - Display ranked recommendations with explanations
   - Allow client to book directly from recommendation
   - Provide alternative suggestions if no matches

**API Response**:
```json
{
  "sism_output": {...},
  "user_preferences": {...},
  "matches": {
    "top_recommendations": [5 recommendations],
    "honorable_mentions": [3 recommendations],
    "total_practitioners_considered": 150,
    "total_practitioners_filtered": 12,
    "match_summary": "Found X verified practitioners...",
    "key_factors": ["specialization", "gold-tier", "evidence-based"]
  }
}
```

---

### 2.4 BOOKING & SCHEDULING FLOW

**Flow**: Select Practitioner → Check Availability → Create Booking → Confirm & Pay

**Actors**: Client, Practitioner

**Key Services**: 
- Frontend: `SessionsNotifier` (`/client/lib/core/providers/session_provider.dart`)
- Backend: `BookingService` (`/backend/services/practice/booking.py`)
- Backend: `SchedulingService` (`/backend/services/practice/scheduling.py`)

**Steps**:
1. **Practitioner Availability Setup**
   - Practitioner sets recurring weekly availability (days/times)
   - System generates available time slots
   - Practitioner can block specific dates

2. **Client Booking Request** (`POST /practitioners/{id}/book`)
   - Select practitioner from recommendations
   - Choose session type (initial consult, follow-up, telehealth)
   - View available slots (next 30 days)
   - Select preferred date/time

3. **Create Booking**
   - Generate Booking record with:
     - client_id, practitioner_id
     - scheduled_date, start_time, end_time, duration_minutes
     - session_type, service_name, notes
     - price, currency, deposit_required
     - status: PENDING
   - Generate associated payment intent

4. **Confirmation Workflow**
   - Send confirmation email to practitioner
   - Practitioner approves/declines
   - If approved: status → CONFIRMED
   - If declined: return to availability search
   - Send calendar invite to client

5. **Reminder System**
   - 24 hours before: Send reminder to both parties
   - Mark reminder_sent = true

6. **Session Lifecycle**
   - Status transitions: PENDING → CONFIRMED → COMPLETED
   - Cancellation options: FREE up to 24 hours, penalty after
   - No-show handling: Status → NO_SHOW, client charged

**Data Model**:
```
Booking:
  - id (UUID)
  - client_id, practitioner_id
  - scheduled_date, start_time, end_time, duration_minutes
  - session_type, service_name, notes
  - price, currency, deposit_amount
  - status: PENDING|CONFIRMED|COMPLETED|CANCELLED|NO_SHOW
  - payment_id (links to Payment record)
  - session_note_id (links to practitioner notes)
  - reminder_sent, reminder_sent_at
  - created_at, updated_at
```

---

### 2.5 PAYMENT FLOW

**Flow**: Create Payment Intent → Process Payment → Calculate Fees → Payout

**Actors**: Client, Practitioner, Stripe, SANA Platform

**Key Service**: `StripePaymentService` (`/backend/services/payments/stripe_service.py`)

**Steps**:
1. **Payment Intent Creation** (`POST /api/v1/payments/create`)
   - Link to booking_id
   - Amount: session_price (in pence for GBP)
   - Payment type: BOOKING
   - Status: PENDING

2. **Client Payment** (`POST /api/v1/payments/process`)
   - Call Stripe API with payment intent
   - Client completes payment (card, Apple Pay, etc.)
   - Stripe webhook confirms payment
   - Status: PROCESSING → SUCCEEDED

3. **Fee Calculation** (after successful payment):
   - Platform fee: 10% of session price
   - Stripe fee: ~2.9% + £0.30 (Stripe's standard)
   - Practitioner payout: 100% - platform fee - Stripe fee
   - Example: £100 booking → Stripe £3.20 → Platform £10 → Practitioner £86.80

4. **Payout Processing** (`POST /api/v1/payments/payouts`)
   - Aggregate weekly payouts per practitioner
   - Transfer to practitioner's Stripe Connect account
   - Payout status: PENDING → COMPLETED
   - Frequency: Weekly (Mondays)

5. **Refund Handling**
   - Client requests cancellation within 24 hours
   - Automatic refund to client
   - Practitioner doesn't receive commission
   - Status: REFUNDED

**Data Model**:
```
Payment:
  - id (UUID)
  - stripe_payment_intent_id
  - client_id, practitioner_id
  - amount, currency (GBP)
  - payment_type: BOOKING|SUBSCRIPTION|TIP|PRODUCT
  - booking_id, subscription_id
  - status: PENDING|PROCESSING|SUCCEEDED|FAILED|REFUNDED
  - platform_fee, stripe_fee, practitioner_payout
  - created_at, completed_at, refunded_at
  - metadata (custom data)
```

---

### 2.6 MESSAGING FLOW

**Flow**: Start Conversation → Send Message → Real-time Updates → Archive

**Actors**: Client and Practitioner in booking context

**Key Service**: `MessagingService` (`/backend/services/messaging/chat.py`)

**Steps**:
1. **Conversation Initiation**
   - Auto-create conversation when booking confirmed
   - Link conversation to booking_id
   - Add both parties as participants
   - Status: ACTIVE

2. **Message Types**
   - TEXT: Plain text messages
   - IMAGE: Image with URL reference
   - FILE: Document/file attachment
   - SYSTEM: Automated system messages (booking confirmed, etc.)

3. **Send Message** (`POST /api/v1/messaging/send`)
   - Create Message record:
     - message_id, conversation_id, sender_id
     - message_type, content, attachment_url
     - is_read: false, read_at: null
     - created_at, edited_at, deleted_at
   - Update conversation last_message_at and preview
   - Emit WebSocket event to recipient (real-time)

4. **Read Receipts**
   - Recipient receives message via WebSocket
   - Message auto-marked as read when conversation opened
   - is_read: true, read_at: timestamp
   - Update unread_counts[participant_id] -= 1

5. **Conversation Management**
   - Archive conversation: status → ARCHIVED (after session ends)
   - Block conversation: status → BLOCKED (dispute/safety)
   - Display unread counts per conversation

**Data Model**:
```
Message:
  - id (UUID)
  - conversation_id, sender_id
  - message_type, content
  - attachment_url, attachment_name
  - is_read, read_at
  - created_at, edited_at, deleted_at

Conversation:
  - id (UUID)
  - participant_ids: [client_id, practitioner_id]
  - booking_id (optional)
  - status: ACTIVE|ARCHIVED|BLOCKED
  - last_message_at, last_message_preview
  - unread_counts: {participant_id: count}
  - created_at, updated_at
```

**Technology**: WebSockets or Firebase Realtime (for instant message delivery)

---

## 3. DATA CONNECTIONS & ARCHITECTURE

### 3.1 Data Flow Diagram (High Level)

```
FLUTTER CLIENT (iOS/Android)
├── Auth Flow
│   ├── Register/Login → Auth Service
│   └── Token Management (Access + Refresh tokens)
│
├── Health Assessment Flow
│   ├── Questionnaire Input → Health Provider (Riverpod)
│   └── POST /api/v1/scoring/calculate → SISM Algorithm
│
├── Practitioner Discovery Flow
│   ├── Search Filter → Practitioner Provider
│   ├── GET /api/v1/practitioners → Marketplace Search
│   └── GET /api/v1/matching/test-matching → SPRM Algorithm
│
├── Booking Flow
│   ├── Session Provider → Booking Service
│   ├── POST /practitioners/{id}/book → Booking Service
│   └── Payment Processing → Stripe Service
│
├── Messaging Flow
│   ├── Messaging Provider
│   ├── WebSocket connection → Chat Service
│   └── Real-time message updates
│
└── Health Tracking
    ├── Health Provider → Health Service
    └── Journal entries, mood tracking, health scores

BACKEND SERVICES (FastAPI)
├── Authentication Service
│   ├── User model (role: CLIENT|PRACTITIONER)
│   ├── JWT tokens (bcrypt password hashing)
│   └── Refresh token database storage
│
├── Algorithm Services
│   ├── SISM (Scoring) → Domain health scores
│   ├── SPRM (Matching) → Practitioner recommendations
│   ├── SCVM (Verification) → Credential validation
│   ├── SANA Index → Practitioner credibility scoring
│   └── Evidence Engine → Intervention recommendations
│
├── Business Logic Services
│   ├── Booking Service → Appointment management
│   ├── Scheduling Service → Practitioner availability
│   ├── Marketplace Search → Practitioner discovery + filters
│   ├── Payments Service → Stripe integration + payouts
│   ├── Messaging Service → Chat + WebSockets
│   └── Review Service → Ratings and reviews
│
└── Database (SQLAlchemy ORM)
    ├── User (base user)
    ├── ClientProfile (extends User)
    ├── PractitionerProfile (extends User, includes SANA Index)
    ├── HealthScore (SISM results per user)
    ├── Booking (appointment records)
    ├── Session (completed session data with notes)
    ├── Payment (transaction records)
    ├── Message (conversation messages)
    ├── Review (practitioner ratings)
    └── Verification (credential verification status)
```

### 3.2 Database Entity Relationships

```
User (Base)
├── id, email, hashed_password, role (CLIENT|PRACTITIONER|ADMIN)
├── first_name, last_name, phone, avatar_url
├── subscription_tier (FREE|SANA_PLUS|BASIC|PRO|PREMIUM)
├── is_verified (from SCVM)
└── created_at, updated_at

├─→ ClientProfile (1:1)
│   ├── age_range, gender, medical_conditions
│   ├── preferences (languages, philosophies, modalities)
│   ├── location (latitude, longitude)
│   ├── health_goals (array)
│   └── avatar_url
│
├─→ PractitionerProfile (1:1)
│   ├── license_number, verification_tier, scvm_confidence_score
│   ├── specialties (many-to-many: Specialty)
│   ├── modalities (many-to-many: Modality)
│   ├── credentials (array of strings)
│   ├── experience_years, bio
│   ├── location (latitude, longitude)
│   ├── service_area_km
│   ├── hourly_rate, accepts_insurance
│   ├── availability_windows (array)
│   ├── sana_index_score (0-100, from SANAIndexCalculator)
│   ├── total_clients_treated
│   ├── average_outcome_improvement (%)
│   ├── client_satisfaction_rating (0-5)
│   └── verification_status
│
└─→ RefreshToken
    ├── token (JWT)
    ├── expires_at
    └── user_id (FK)

HealthScore (stores SISM results)
├── user_id (FK → User)
├── overall_score (0-100)
├── domain_scores {physical, emotional, social, cognitive, spiritual}
├── weak_domains (array)
├── questionnaire_version
├── calculated_at
└── calculation_metadata

Booking
├── id (UUID)
├── client_id (FK → User)
├── practitioner_id (FK → User)
├── scheduled_date, start_time, end_time, duration_minutes
├── session_type (initial|follow_up|telehealth)
├── service_name, notes
├── price, currency, deposit_required
├── status (PENDING|CONFIRMED|COMPLETED|CANCELLED|NO_SHOW)
├── payment_id (FK → Payment)
├── session_note_id (FK → Session)
├── reminder_sent, reminder_sent_at
└── created_at, updated_at

Session (practitioner's session notes)
├── id (UUID)
├── booking_id (FK)
├── practitioner_id (FK)
├── client_id (FK)
├── chief_complaint, assessment, diagnosis
├── treatment_provided, recommendations
├── session_date, duration
├── outcomes (client improvement %, domain improvements)
├── follow_up_plan
└── created_at, updated_at

Payment
├── id (UUID)
├── stripe_payment_intent_id
├── client_id (FK)
├── practitioner_id (FK)
├── booking_id (FK)
├── amount (in pence)
├── currency (GBP)
├── payment_type (BOOKING|SUBSCRIPTION|TIP|PRODUCT)
├── status (PENDING|PROCESSING|SUCCEEDED|FAILED|REFUNDED)
├── platform_fee (10% of amount)
├── stripe_fee (~2.9% + £0.30)
├── practitioner_payout (amount - fees)
├── created_at, completed_at, refunded_at
└── metadata

Message
├── id (UUID)
├── conversation_id (FK)
├── sender_id (FK)
├── message_type (TEXT|IMAGE|FILE|SYSTEM)
├── content, attachment_url
├── is_read, read_at
├── created_at, edited_at, deleted_at

Conversation
├── id (UUID)
├── participant_ids [client_id, practitioner_id]
├── booking_id (FK)
├── status (ACTIVE|ARCHIVED|BLOCKED)
├── last_message_at, last_message_preview
├── unread_counts {participant_id: count}
└── created_at, updated_at

Review
├── id (UUID)
├── practitioner_id (FK)
├── client_id (FK)
├── booking_id (FK)
├── overall_rating (1-5)
├── communication_rating, punctuality_rating, effectiveness_rating, value_rating
├── title, content, treatment_type
├── condition_treated
├── created_at, updated_at
└── practitioner_response (optional)
```

### 3.3 Key Data Dependencies

```
User Registration/Login
  ↓
User Record Created
  ↓
ClientProfile or PractitionerProfile
  ↓
HealthScore (client) + SCVM Verification (practitioner)
  ↓
SANA Index Calculation (practitioner credibility)
  ↓
Booking Creation (links client + practitioner)
  ↓
Payment Processing (Stripe)
  ↓
Session Completion → Session notes stored
  ↓
Review Submission
  ↓
SANA Index Update (incorporates review + session outcomes)
```

---

## 4. KEY BUSINESS LOGIC PROCESSES

### 4.1 Complete User Journey (Client)

1. **Registration** → Create account (email, password)
2. **Health Assessment** → Complete 35+ question questionnaire
3. **Health Scoring** → SISM calculates overall health score + weak domains
4. **Practitioner Matching** → SPRM algorithm finds 5 best-fit practitioners
5. **Practitioner Selection** → User reviews recommendations, chooses practitioner
6. **Booking** → Select available time slot, create booking
7. **Payment** → Process payment via Stripe, receive confirmation
8. **Pre-Session** → Receive reminder 24 hours before
9. **Session** → Meet with practitioner (in-person or telehealth)
10. **Post-Session** → Access session notes, messaging available
11. **Review** → Submit rating and review
12. **Outcome Tracking** → Re-assess health via follow-up questionnaire

### 4.2 Complete Practitioner Journey

1. **Registration** → Create account (email, password, role=PRACTITIONER)
2. **Credential Upload** → Submit credentials, documents (PDF, images)
3. **SCVM Verification** → Automated credential checking + optional human review
4. **Profile Setup** → Add specialties, modalities, bio, rates, availability
5. **SANA Index Calculation** → Automatic calculation based on credentials
6. **Marketplace Listing** → Profile visible to clients (if verified)
7. **Receive Bookings** → Clients book sessions
8. **Booking Management** → Confirm/decline bookings, manage schedule
9. **Session Execution** → Conduct session, document notes
10. **Outcome Tracking** → Record client improvements, PROM data
11. **Payment** → Receive weekly payout after platform fees
12. **Index Update** → SANA Index auto-updates with new session data

### 4.3 Admin/Platform Management

1. **Verification Review** → Human review of flagged credentials (SCVM)
2. **Quality Assurance** → Monitor practitioner SANA Index scores
3. **Dispute Resolution** → Handle client complaints, payment disputes
4. **Analytics** → Track platform metrics (bookings, revenue, etc.)
5. **Feature Deployment** → Algorithm updates, new modalities, specialties

---

## 5. TECHNOLOGY STACK OVERVIEW

### Frontend (Flutter - Multi-platform)
- **State Management**: Riverpod (reactive state containers)
- **Providers**:
  - `auth_provider.dart` → AuthNotifier (login, logout, token refresh)
  - `session_provider.dart` → SessionsNotifier (bookings, scheduling)
  - `health_provider.dart` → HealthNotifier (health scores, assessments)
  - `practitioner_provider.dart` → PractitionerNotifier (search, filter)
  - `messaging_provider.dart` → MessagingNotifier (real-time chat)
- **Features**:
  - Health assessment screens
  - Practitioner search/filter UI
  - Booking flow
  - Chat/messaging
  - Session history
  - Health dashboard

### Backend (Python FastAPI)
- **Framework**: FastAPI with Pydantic models
- **Database**: SQLAlchemy ORM with SQL database
- **Authentication**: JWT (PyJWT) + bcrypt password hashing
- **Algorithms**: Custom Python implementations
- **Payment**: Stripe API integration
- **Messaging**: WebSockets (or Firebase Realtime)

### Infrastructure
- **Docker**: Containerized FastAPI application
- **Database Migration**: Alembic (SQLAlchemy migrations)
- **API Documentation**: FastAPI auto-generated Swagger UI

---

## 6. ALGORITHM INTERDEPENDENCIES

```
Client Assessment Path:
  Questionnaire Input
      ↓
  SISM (Health Scoring)
      ↓ [weak_domains identified]
  SPRM (Practitioner Matching)
      ↓ [needs practitioner credibility]
  SANA Index (for each practitioner)
      ↓ [selects best matches]
  Return Top 5 Recommendations

Practitioner Assessment Path:
  Credential Upload
      ↓
  SCVM (Credential Verification)
      ↓ [if verified]
  SANA Index Calculation
      ↓ [based on credentials, outcomes, reviews]
  Index Score Used by SPRM for matching

Session Outcome Path:
  Session Completed
      ↓
  Session Notes + PROMs (PROMS algorithm)
      ↓
  Client Outcome Measured
      ↓
  SANA Index Update (outcomes component updated)
      ↓
  Practitioner Score Changes
      ↓
  May affect future matching recommendations
```

---

## 7. API ENDPOINT ORGANIZATION

```
/api/v1/
├── /auth/
│   ├── POST /register
│   ├── POST /login
│   ├── POST /refresh
│   ├── GET /me (current user)
│   └── POST /logout
│
├── /scoring/
│   ├── POST /calculate (SISM)
│   ├── POST /calculate-with-weights
│   ├── GET /generate-dummy
│   ├── GET /test-full-flow
│   └── GET /domains/list
│
├── /matching/
│   ├── GET /test-matching (SPRM + demo)
│   ├── GET /practitioners (list all)
│   ├── GET /practitioner/{id}
│   ├── GET /specialties
│   └── GET /modalities
│
├── /index/
│   ├── GET /calculate (SANA Index)
│   └── GET /practitioners/{id}/index
│
├── /verification/
│   ├── POST /verify-credentials (SCVM)
│   └── GET /credential-status/{id}
│
├── /marketplace/
│   ├── POST /search
│   ├── GET /practitioners
│   ├── GET /practitioner/{id}
│   ├── POST /reviews
│   ├── GET /reviews/{practitioner_id}
│   └── POST /review-response
│
├── /practice/
│   ├── POST /bookings (create)
│   ├── GET /bookings (list)
│   ├── GET /bookings/{id}
│   ├── PUT /bookings/{id} (confirm)
│   ├── DELETE /bookings/{id} (cancel)
│   ├── POST /availability (set)
│   ├── GET /availability/{practitioner_id}
│   ├── POST /sessions (create notes)
│   └── GET /sessions/{booking_id}
│
├── /payments/
│   ├── POST /create-intent
│   ├── POST /process
│   ├── GET /{id}
│   ├── POST /refund
│   ├── POST /payouts (weekly)
│   └── GET /history
│
├── /messaging/
│   ├── POST /conversations
│   ├── GET /conversations
│   ├── POST /messages (send)
│   ├── GET /conversations/{id}/messages
│   ├── PUT /messages/{id}/read
│   └── WebSocket /ws/chat/{conversation_id}
│
├── /health/
│   ├── GET /score
│   ├── GET /score-history
│   ├── GET /dimensions
│   ├── POST /journal
│   └── GET /journal-entries
│
└── /evidence/
    ├── GET /interventions
    ├── POST /recommend
    └── GET /conditions
```

---

## 8. SUMMARY OF KEY CONNECTIONS

| Component | Connects To | Purpose |
|-----------|-----------|---------|
| SISM Output | SPRM | Provides weak_domains for matching |
| SPRM Output | Booking Service | Recommendations become clickable bookings |
| SCVM Output | SANA Index | Credentials score component |
| SANA Index | SPRM | Credibility score used in matching |
| Booking | Payment | Each booking creates payment intent |
| Payment | Stripe | Processes actual transaction |
| Session Notes | SANA Index | Outcomes component updated |
| Review | SANA Index | Satisfaction component updated |
| Client Health Score | SPRM | Weak domains drive matching |
| Practitioner Availability | Booking | Time slots populated from availability |
| Conversation | Booking | Linked via booking_id |

---

## 9. CONCLUSION

The SANA platform uses a sophisticated multi-algorithm approach where:

1. **SISM** measures client health across 5 domains
2. **SPRM** intelligently matches clients to best practitioners using weighted scoring
3. **SCVM** rigorously verifies practitioner credentials
4. **SANA Index** calculates overall practitioner credibility (5 components)
5. Supporting algorithms handle booking, payments, messaging, and outcomes

The entire flow is coordinated through RESTful APIs and real-time WebSocket connections, with data flowing bidirectionally between Flutter clients and FastAPI backend, all backed by a relational database model that tracks users, profiles, health scores, bookings, payments, and sessions.
