# SANA Platform - Quick Reference Summary

## Key Algorithms at a Glance

### 1. **SISM** (Health Scoring)
- **Path**: `/backend/algorithms/scoring/sism.py`
- **Input**: 35+ questionnaire responses (5 domains)
- **Output**: Overall health score (0-100) + weak domain identification
- **Domain Weights**: Physical (0.25), Emotional (0.25), Social (0.15), Cognitive (0.20), Spiritual (0.15)
- **API**: `POST /api/v1/scoring/calculate`

### 2. **SPRM** (Practitioner Matching)
- **Path**: `/backend/algorithms/matching/sprm.py`
- **Purpose**: Match users to best practitioners using weighted scoring
- **Process**: 4-stage filtering → 5-factor scoring → Top 5 recommendations
- **Scoring Factors**:
  - Health need alignment (40%)
  - Credibility score (25%)
  - Practical fit (20%)
  - Evidence alignment (10%)
  - Preference match (5%)
- **API**: `GET /api/v1/matching/test-matching`

### 3. **SANA Index** (Practitioner Credibility)
- **Path**: `/backend/algorithms/index/sana_index.py`
- **Purpose**: Calculate overall practitioner credibility (0-100)
- **5 Components**:
  - Credentials (20%)
  - Treatment volume (20%)
  - Outcomes (40%) ← Highest weight
  - Data completeness (10%)
  - Client satisfaction (10%)
- **API**: `GET /api/v1/index/calculate`

### 4. **SCVM** (Credential Verification)
- **Path**: `/backend/algorithms/verification/scvm.py`
- **Purpose**: Verify credentials with 99%+ accuracy
- **Verification Tiers**: Unverified → Basic → Standard → Gold → Premium
- **Features**: OCR, pattern matching, fraud detection, registry verification

---

## Business Logic Flows Summary

### Health Assessment → Matching → Booking → Payment

```
User Registration (AuthService)
    ↓
User Profile Setup
    ↓
Complete Health Questionnaire (35+ questions)
    ↓
SISM Calculation (overall_score + weak_domains)
    ↓
Display Health Dashboard
    ↓
Set Matching Preferences (budget, location, etc.)
    ↓
SPRM Algorithm (4-stage filter + 5-factor scoring)
    ↓
Display Top 5 Practitioner Recommendations
    ↓
User Selects Practitioner
    ↓
View Availability → Select Date/Time
    ↓
Create Booking (status=PENDING)
    ↓
Stripe Payment Processing
    ↓
Confirm Booking (status=CONFIRMED)
    ↓
Send Reminders (24 hours before)
    ↓
Session Execution (status=COMPLETED)
    ↓
Enable Messaging & Session Notes
    ↓
Post-Session Review & Ratings
    ↓
SANA Index Auto-Updates
```

---

## Database Entity Relationships

```
User
├─→ ClientProfile
│   ├─→ HealthScore (SISM results)
│   ├─→ Booking (as client_id)
│   │   ├─→ Payment (Stripe integration)
│   │   ├─→ Session (practitioner notes)
│   │   ├─→ Conversation (real-time chat)
│   │   │   └─→ Message (conversation messages)
│   │   └─→ Review (ratings & feedback)
│   └─→ Message (as sender)
│
├─→ PractitionerProfile
│   ├─→ Booking (as practitioner_id)
│   ├─→ Session (session notes created)
│   ├─→ TimeSlot (availability)
│   ├─→ RecurringAvailability (weekly patterns)
│   ├─→ Specialties (many-to-many)
│   └─→ Modalities (many-to-many)
│
└─→ RefreshToken (JWT storage)
```

---

## API Endpoint Organization

### Core Endpoints
- **Auth**: `/api/v1/auth/` (register, login, refresh, me)
- **Scoring**: `/api/v1/scoring/` (calculate SISM)
- **Matching**: `/api/v1/matching/` (SPRM + test flow)
- **Index**: `/api/v1/index/` (SANA Index calculation)
- **Verification**: `/api/v1/verification/` (SCVM)
- **Marketplace**: `/api/v1/marketplace/` (search, reviews)
- **Practice**: `/api/v1/practice/` (bookings, scheduling)
- **Payments**: `/api/v1/payments/` (Stripe integration)
- **Messaging**: `/api/v1/messaging/` (chat + WebSocket)

---

## Frontend State Management (Flutter - Riverpod)

```
AuthProvider
├─ login()
├─ register()
├─ logout()
└─ refresh_token()

HealthProvider
├─ submit_questionnaire()
├─ get_health_score()
├─ track_history()
└─ load_health_data()

SessionProvider
├─ load_sessions()
├─ create_booking()
├─ cancel_booking()
└─ manage_schedule()

PractitionerProvider
├─ search_practitioners()
├─ filter_results()
├─ get_practitioner()
└─ get_availability()

MessagingProvider
├─ send_message()
├─ load_conversations()
├─ mark_read()
└─ archive_conversation()
```

---

## Data Flow Highlights

### SISM → SPRM → Booking Chain
1. Client completes questionnaire
2. SISM calculates health score + weak domains
3. User sets matching preferences
4. SPRM algorithm runs:
   - Filters by verification (SCVM score ≥ 85)
   - Filters by specialty match (weak domains)
   - Filters by geography (Haversine formula)
   - Filters by budget
   - Scores remaining practitioners (5 factors, 0-100 each)
   - Returns top 5 recommendations
5. Client books from recommendations
6. Payment processed via Stripe
7. Session created and tracked
8. Session outcomes update SANA Index

### Payment Fee Structure
- **Amount**: £X (session price)
- **Stripe Fee**: ~2.9% + £0.30
- **Platform Fee**: 10%
- **Practitioner Payout**: Amount - Stripe Fee - Platform Fee
- **Payout Frequency**: Weekly (automated)

### Messaging Flow
- Auto-created when booking confirmed
- Real-time delivery via WebSocket
- Read receipts tracked
- Archived after session
- Can be blocked for safety

---

## Key Scoring Details

### SPRM Matching Score Formula
```
overall_score = 
  (health_alignment × 0.40) +
  (credibility × 0.25) +
  (practical_fit × 0.20) +
  (evidence_alignment × 0.10) +
  (preference_match × 0.05)
Range: 0-100
```

### SANA Index Formula
```
sana_index = 
  (credentials_score × 0.20) +
  (volume_score × 0.20) +
  (outcomes_score × 0.40) +
  (completeness_score × 0.10) +
  (satisfaction_score × 0.10)
Range: 0-100
```

### SISM Health Score
```
overall_score = Σ(domain_score × domain_weight)
Where domain_weights = {
  physical: 0.25,
  emotional: 0.25,
  social: 0.15,
  cognitive: 0.20,
  spiritual: 0.15
}
Weak domains identified where score < 60
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy ORM (SQL)
- **Authentication**: JWT + bcrypt
- **Payments**: Stripe API
- **Messaging**: WebSockets
- **Deployment**: Docker

### Frontend
- **Framework**: Flutter (iOS/Android)
- **State Management**: Riverpod
- **HTTP Client**: dio
- **Local Storage**: Secure Storage

---

## Important File Locations

```
Backend Algorithms:
├─ /backend/algorithms/scoring/sism.py
├─ /backend/algorithms/matching/sprm.py
├─ /backend/algorithms/index/sana_index.py
├─ /backend/algorithms/verification/scvm.py
└─ /backend/algorithms/[evidence,herbs,planning,etc]

Backend Services:
├─ /backend/services/auth.py
├─ /backend/services/practice/[booking,scheduling,sessions]
├─ /backend/services/payments/stripe_service.py
├─ /backend/services/messaging/chat.py
└─ /backend/services/marketplace/[search,discovery,reviews]

Backend API Routes:
├─ /backend/api/routes/auth.py
├─ /backend/api/routes/scoring.py
├─ /backend/api/routes/matching.py
├─ /backend/api/routes/index.py
└─ /backend/api/routes/[marketplace,practice,payments,etc]

Database:
└─ /backend/database/models.py

Flutter Frontend:
├─ /client/lib/core/providers/[auth,health,session,etc]_provider.dart
├─ /client/lib/core/api/services/[auth,health,etc]_service.dart
└─ /client/lib/features/[auth,health,booking,etc]/screens/

Configuration:
├─ /backend/config.py (settings)
├─ /backend/main.py (FastAPI app)
└─ /backend/requirements.txt (dependencies)
```

---

## Integration Points

### Client → Backend
- HTTP REST API calls for all CRUD operations
- WebSocket connection for real-time messaging
- JWT authentication with access + refresh tokens

### Backend → Third-party
- **Stripe**: Payment processing and payouts
- **Database**: SQL for persistence
- **Firebase** (optional): Real-time messaging alternative

### Algorithm Dependencies
```
QUESTIONNAIRE → SISM (health score) 
    ↓
SISM OUTPUT + PREFERENCES → SPRM (top 5 practitioners)
    ↓
PRACTITIONER DATA → SANA INDEX (credibility score)
    ↓
SANA INDEX + SISM → SPRM (for matching)
    ↓
SESSION COMPLETION → OUTCOMES → SANA INDEX UPDATE
```

---

## For Diagram Creation

### Key Nodes to Include
1. **Frontend Screens**: Auth, Health Assessment, Practitioner Search, Booking, Messaging
2. **Algorithms**: SISM, SPRM, SANA Index, SCVM, Evidence Engine
3. **Services**: Auth, Booking, Payment, Messaging, Marketplace
4. **Database**: Users, Profiles, HealthScores, Bookings, Payments, Sessions, Messages
5. **External**: Stripe, WebSocket Server, Firebase (optional)

### Key Flows to Show
1. Health Assessment → SISM → Dashboard
2. SISM Output → SPRM → Recommendations → Booking
3. Booking → Payment → Stripe → Payout
4. Booking → Conversation → WebSocket → Real-time Chat
5. Session → Review → SANA Index Update

---

## Quick Stats

- **Health Domains**: 5 (physical, emotional, social, cognitive, spiritual)
- **Questionnaire Questions**: 35+
- **Top Recommendations**: 5
- **SANA Index Components**: 5
- **Scoring Factors in SPRM**: 5
- **Verification Tiers**: 5
- **Practitioner Specialties**: 15+
- **Booking Status States**: 6
- **Payment Status States**: 5
- **Message Types**: 4
- **Conversation States**: 3

---

## Notes for Diagram

- Color-code algorithms (green), services (blue), database (orange), frontend (purple)
- Use arrows to show data flow and dependencies
- Highlight the critical path: Questionnaire → SISM → SPRM → Booking → Payment
- Show feedback loops: Session Outcomes → SANA Index Updates
- Indicate real-time vs synchronous connections
- Mark external dependencies (Stripe, WebSocket)
