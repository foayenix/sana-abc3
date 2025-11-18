# SANA Health Framework

A comprehensive AI/ML platform for personalized health and wellness, transforming Complementary & Alternative Medicine (CAM) through evidence-based recommendations and continuous learning.

## Overview

SANA integrates 7 algorithms that work together to assess user health, ensure safety, match practitioners, and optimize interventions based on real outcomes.

## Implemented Algorithms

### 1. SISM - Integrative Scoring Model
**Purpose**: Calculate holistic health scores from questionnaire responses

- Scores users across 5 domains (0-100 scale):
  - Emotional, Physical, Social, Cognitive, Spiritual
- Identifies weak domains needing intervention
- Weighted scoring based on question importance
- Provides domain-specific insights

### 2. Health Graph - Evidence Engine
**Purpose**: Knowledge base of evidence-based interventions

- Maps conditions to treatments with evidence levels
- Evidence ratings: Strong, Moderate, Weak, Emerging
- Links interventions to health domains
- Provides scientific backing for recommendations

### 3. SHAM - Habit & Activity Model
**Purpose**: Create personalized daily activity plans

- Generates optimal activity schedules
- Respects time and budget constraints
- Prioritizes weak domains
- Balances activity types throughout the day
- Calculates expected improvement scores

### 4. SCVM - Credential Vetting Model
**Purpose**: Verify practitioner credentials and qualifications

- Validates degrees, licenses, and certifications
- Checks against known institutions and registries
- Calculates trust scores (0-100)
- Verification tiers: Basic, Standard, Premium
- Flags expired or suspicious credentials

### 5. SPRM - Practitioner Recommendation Model
**Purpose**: Match users with verified practitioners

- Filters by budget, distance, and modality
- Modalities: In-person, Video, Phone, Chat
- Ranks by specialty match to user's weak domains
- Calculates match scores based on multiple factors
- Returns paginated, sorted results

### 6. SST - Safety & Triage Model
**Purpose**: Detect health crises and safety concerns

- Multi-layer risk detection:
  - Score analysis (critical thresholds)
  - Trend analysis (rapid decline detection)
  - Crisis keyword detection in messages
  - Pattern recognition across domains
- Safety statuses: Safe, Monitor, Escalate, Urgent
- Escalation pathways:
  - NHS 111 for medical concerns
  - Samaritans (116 123) for emotional crisis
  - Emergency services (999) for immediate danger
- Generates human review cases with priority levels

### 7. SOU - Outcome Uplift Model
**Purpose**: Learn which interventions work best through reinforcement learning

- Multi-armed bandit for exploration vs exploitation
- Thompson Sampling for contextual recommendations
- Learning phases:
  - Cold Start (<100 outcomes): 50% exploration
  - Early Learning (100-500): 30% exploration
  - Mature (>500): 10% exploration
- Predicts outcomes with confidence intervals
- Calculates uplift over baseline recommendations
- Improves continuously as users provide feedback

## Complete User Flow

```
User Questionnaire
       ↓
   [1. SISM]  →  Health Score & Weak Domains
       ↓
   [2. SST]   →  Safety Assessment
       ↓
   (If Safe)
       ↓
   [3. SPRM]  →  Practitioner Matches
       ↓
   [4. SCVM]  →  Credential Verification
       ↓
   [5. SHAM]  →  Activity Plan
       ↓
   [6. Health Graph]  →  Evidence-Based Interventions
       ↓
   [7. SOU]   →  Optimized Recommendations
       ↓
   User Outcomes  →  Feedback Loop to SOU
```

## Project Structure

```
sana-abc3/
├── backend/
│   ├── algorithms/
│   │   ├── scoring/      # SISM
│   │   ├── evidence/     # Health Graph
│   │   ├── planning/     # SHAM
│   │   ├── verification/ # SCVM
│   │   ├── matching/     # SPRM
│   │   ├── safety/       # SST
│   │   └── learning/     # SOU
│   ├── api/routes/       # FastAPI endpoints
│   ├── tests/
│   │   ├── test_scoring/
│   │   ├── test_evidence/
│   │   ├── test_planning/
│   │   ├── test_verification/
│   │   ├── test_matching/
│   │   ├── test_safety/
│   │   ├── test_learning/
│   │   └── integration/  # Complete flow tests
│   └── utils/
├── frontend/
│   ├── lib/
│   │   ├── screens/      # Test screens for each algorithm
│   │   └── services/     # API client
│   └── pubspec.yaml
└── README.md
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
flutter pub get
flutter run -d chrome
```

### Docker Setup

```bash
docker-compose up -d
```

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Scoring (SISM)
- `POST /scoring/calculate` - Calculate health score from questionnaire
- `GET /scoring/domains` - List available domains
- `GET /scoring/questionnaire` - Get questionnaire template

### Evidence (Health Graph)
- `GET /evidence/interventions/{domain}` - Get interventions for domain
- `GET /evidence/conditions` - List all conditions
- `GET /evidence/search` - Search interventions

### Planning (SHAM)
- `POST /planning/create` - Create activity plan
- `GET /planning/activities` - List available activities
- `GET /planning/constraints` - Get constraint templates

### Verification (SCVM)
- `POST /verification/verify` - Verify practitioner credentials
- `GET /verification/institutions` - List known institutions
- `GET /verification/credential-types` - List credential types

### Matching (SPRM)
- `POST /matching/find` - Find practitioner matches
- `GET /matching/modalities` - List available modalities
- `GET /matching/specialties` - List specialties

### Safety (SST)
- `POST /safety/analyze` - Analyze user safety
- `GET /safety/test-scenarios` - Get test scenarios
- `GET /safety/resources` - List safety resources
- `GET /safety/crisis-keywords` - List monitored keywords
- `GET /safety/thresholds` - Get risk thresholds

### Learning (SOU)
- `GET /learning/metrics` - Get learning metrics
- `GET /learning/test-recommendations` - Test recommendation engine
- `GET /learning/intervention-performance/{id}` - Get intervention stats
- `GET /learning/predict-outcome` - Predict outcome for intervention
- `GET /learning/learning-phase` - Get current learning phase
- `GET /learning/top-performers` - Get top performing interventions

## Testing

### Run All Backend Tests

```bash
cd backend
pytest
```

### Run Specific Test Suites

```bash
# Unit tests by algorithm
pytest tests/test_scoring/ -v
pytest tests/test_evidence/ -v
pytest tests/test_planning/ -v
pytest tests/test_verification/ -v
pytest tests/test_matching/ -v
pytest tests/test_safety/ -v
pytest tests/test_learning/ -v

# Integration tests
pytest tests/integration/ -v
```

### Test Coverage

- **Unit Tests**: 100+ tests across all algorithms
- **Integration Tests**: Complete flow tests covering:
  - End-to-end user journeys
  - Algorithm interactions
  - Constraint validation
  - Error handling

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

- **Evidence-Based**: All recommendations backed by Health Graph evidence
- **Safety-First**: SST monitors for crises and escalates appropriately
- **Personalized**: Recommendations tailored to user's weak domains
- **Constraint-Aware**: Respects time, budget, and geographic constraints
- **Continuously Learning**: SOU improves recommendations over time
- **Verified Practitioners**: SCVM ensures credential authenticity

## Technology Stack

- **Backend**: Python, FastAPI, Pydantic
- **Frontend**: Flutter/Dart
- **Testing**: pytest, Flutter test
- **Documentation**: OpenAPI/Swagger

## License

Proprietary - SANA Technologies Ltd.
