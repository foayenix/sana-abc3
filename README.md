# SANA Health Framework

A comprehensive AI/ML platform for personalized health and wellness, transforming Complementary & Alternative Medicine (CAM) through evidence-based recommendations and continuous learning.

## Overview

SANA integrates 9 algorithms that work together to assess user health, ensure safety, match practitioners, score herbs and treatments, and optimize interventions based on real outcomes.

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

### 8. SHI - SANA Herb Index
**Purpose**: Calculate evidence-based credibility scores for herbs and supplements

- 4-component scoring system (0-100):
  - Evidence Volume (25%): Sample size, practitioner diversity, geography
  - Efficacy (40%): Improvement rates, effect size (Cohen's d), consistency
  - Safety (20%): Adverse events, severity weighting, dropout rates
  - Data Quality (15%): Dosage, outcome, follow-up completeness
- Evidence levels: Very High, High, Moderate, Low, Insufficient
- Condition-specific herb rankings
- Synergy detection for herb combinations
- Optimal dosage calculations from successful outcomes
- Bootstrap confidence intervals

### 9. SANA Index - Practitioner Credibility Score
**Purpose**: Calculate overall credibility scores for practitioners

- 4-component weighted scoring (0-100):
  - Credentials (30%): Education, licenses, certifications
  - Outcomes (50%): Client health improvements
  - Reviews (10%): Client ratings and feedback
  - Verification (10%): Identity and credential verification
- Point-based credential scoring (20+ credential types)
- Institution reputation multipliers (Oxford, Cambridge, NHS, etc.)
- Percentile ranking against all practitioners
- Trend detection (improving/stable/declining)

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
   [9. SANA Index]  →  Practitioner Scoring
       ↓
   [5. SHAM]  →  Activity Plan
       ↓
   [6. Health Graph]  →  Evidence-Based Interventions
       ↓
   [8. SHI]   →  Herb & Treatment Scoring
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
│   │   ├── learning/     # SOU
│   │   ├── herbs/        # SHI
│   │   └── index/        # SANA Index
│   ├── api/routes/       # FastAPI endpoints
│   ├── tests/
│   │   ├── test_scoring/
│   │   ├── test_evidence/
│   │   ├── test_planning/
│   │   ├── test_verification/
│   │   ├── test_matching/
│   │   ├── test_safety/
│   │   ├── test_learning/
│   │   ├── test_herbs/
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

### Herbs (SHI)
- `GET /herbs/search` - Search herbs with filters
- `GET /herbs/rankings` - Condition-specific herb rankings
- `GET /herbs/{id}` - Get herb details with SHI score
- `GET /herbs/compare` - Compare herbs head-to-head
- `GET /herbs/combinations/synergies` - Find synergistic combinations
- `GET /herbs/combinations/{id}/protocol` - Get treatment protocol
- `GET /herbs/all-herbs` - List all indexed herbs
- `GET /herbs/evidence-levels` - Get evidence level definitions

### Index (SANA Index)
- `POST /index/calculate` - Calculate practitioner SANA Index
- `GET /index/test-calculate` - Test with sample profiles
- `GET /index/component-weights` - Get scoring weights
- `GET /index/credential-types` - Get credential point values
- `GET /index/practitioner/{id}` - Get practitioner score
- `GET /index/leaderboard` - Top practitioners ranking
- `GET /index/test-scenarios` - Available test scenarios

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
pytest tests/test_herbs/ -v

# Integration tests
pytest tests/integration/ -v
```

### Test Coverage

- **Unit Tests**: 120+ tests across all algorithms
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
- **Herb Credibility**: SHI scores herbs based on real-world outcomes
- **Practitioner Scoring**: SANA Index ranks practitioners by performance

## Technology Stack

- **Backend**: Python, FastAPI, Pydantic, NumPy
- **Frontend**: Flutter/Dart
- **Testing**: pytest, Flutter test
- **Documentation**: OpenAPI/Swagger

## License

Proprietary - SANA Technologies Ltd.
