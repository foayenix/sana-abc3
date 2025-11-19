# SANA Health Platform

A comprehensive AI/ML platform for personalized health and wellness, transforming Complementary & Alternative Medicine (CAM) through evidence-based recommendations, practice management, and continuous learning.

## Overview

SANA is a complete health platform with three main products:
- **SANA Market** - Practice management and marketplace for practitioners and clients
- **SANA Evidence** - AI research infrastructure with outcome measurements
- **SANA Enterprise** - B2B solutions for NHS, corporate wellness, and clinics

## Platform Architecture

### Core Algorithms (10 Algorithms)

| Algorithm | Purpose |
|-----------|---------|
| **SISM** | Integrative Scoring Model - Calculate holistic health scores |
| **Health Graph** | Evidence engine - Knowledge base of interventions |
| **SHAM** | Habit & Activity Model - Create personalized plans |
| **SCVM** | Credential Vetting - Verify practitioner qualifications |
| **SPRM** | Practitioner Matching - Match users with practitioners |
| **SST** | Safety & Triage - Detect health crises |
| **SOU** | Outcome Uplift - Reinforcement learning with Thompson Sampling |
| **SHI** | SANA Herb Index - Score herbs and supplements |
| **SANA Index** | Practitioner credibility scoring (20/20/40/10/10 weights) |
| **SIRM** | Journal AI with 8 personas for reflective wellness |

### Platform Services (10 Service Modules)

| Module | Services | Purpose |
|--------|----------|---------|
| **Auth** | JWT Authentication | User registration, login, tokens |
| **Practice** | Scheduling, Clients, Sessions, Booking | Complete practice management |
| **Marketplace** | Search, Reviews, Discovery | Practitioner discovery and booking |
| **Payments** | Stripe, Subscriptions, Payouts | Payment processing |
| **Messaging** | Chat | Client-practitioner communication |
| **Analytics** | Practitioner, Client, Platform | Comprehensive dashboards |
| **Wearables** | Apple Health, Fitbit, Oura, WHOOP, Garmin | Health data integration |
| **Enterprise** | FHIR, NHS, Multi-tenant, Compliance | B2B features |
| **Widget** | Config, Public API | Embeddable booking widget |
| **Outcomes** | WHO-5, DASS-21, VAS, CAM | Patient-reported outcome measures |

## Complete API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Core Algorithms

#### Scoring (SISM)
- `POST /scoring/calculate` - Calculate health score
- `GET /scoring/domains` - List domains
- `GET /scoring/questionnaire` - Get questionnaire

#### Evidence (Health Graph)
- `GET /evidence/interventions/{domain}` - Get interventions
- `GET /evidence/conditions` - List conditions
- `GET /evidence/search` - Search interventions

#### Planning (SHAM)
- `POST /planning/create` - Create activity plan
- `GET /planning/activities` - List activities

#### Verification (SCVM)
- `POST /verification/verify` - Verify credentials
- `GET /verification/institutions` - List institutions

#### Matching (SPRM)
- `POST /matching/find` - Find practitioners
- `GET /matching/modalities` - List modalities

#### Safety (SST)
- `POST /safety/analyze` - Analyze user safety
- `GET /safety/resources` - List safety resources

#### Learning (SOU)
- `GET /learning/metrics` - Learning metrics
- `GET /learning/predict-outcome` - Predict outcomes
- `GET /learning/top-performers` - Top interventions

#### Herbs (SHI)
- `GET /herbs/search` - Search herbs
- `GET /herbs/rankings` - Herb rankings
- `GET /herbs/{id}` - Herb details

#### Index (SANA Index)
- `POST /index/calculate` - Calculate practitioner score
- `GET /index/leaderboard` - Top practitioners

### Platform Services

#### Authentication
- `POST /auth/register` - Register user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Get current user

#### Practice Management
- `POST /practice/availability` - Set availability
- `GET /practice/calendar/{id}` - Get calendar
- `POST /practice/clients` - Add client
- `POST /practice/sessions` - Create session
- `POST /practice/sessions/{id}/notes` - Add SOAP notes
- `POST /practice/bookings` - Create booking

#### Marketplace
- `POST /marketplace/search` - Search practitioners
- `GET /marketplace/practitioners/{id}` - Get profile
- `POST /marketplace/reviews` - Submit review
- `GET /marketplace/discover` - Discovery page
- `GET /marketplace/discover/trending` - Trending practitioners

#### Payments
- `POST /payments/create-intent` - Create payment
- `POST /payments/{id}/confirm` - Confirm payment
- `POST /payments/{id}/refund` - Refund payment
- `POST /payments/subscriptions` - Create subscription
- `GET /payments/payouts/balance/{id}` - Get balance

#### Messaging
- `POST /messaging/conversations` - Start conversation
- `POST /messaging/conversations/{id}/messages` - Send message
- `GET /messaging/conversations/{id}/messages` - Get messages
- `POST /messaging/conversations/{id}/read` - Mark as read

#### Analytics
- `GET /analytics/practitioner/{id}/dashboard` - Practitioner dashboard
- `GET /analytics/client/{id}/dashboard` - Client dashboard
- `GET /analytics/platform/overview` - Platform metrics

#### Wearables
- `GET /wearables/providers` - Available providers
- `POST /wearables/connect` - Connect device
- `POST /wearables/sync/{id}` - Sync data
- `GET /wearables/summaries/{id}` - Daily summaries

#### Enterprise
- `POST /enterprise/fhir/patient` - Map to FHIR Patient
- `GET /enterprise/fhir/patient/{id}/export` - Export as FHIR Bundle
- `GET /enterprise/nhs/validate/{nhs_number}` - Validate NHS number
- `POST /enterprise/nhs/referrals` - Create referral
- `POST /enterprise/tenants` - Create tenant
- `POST /enterprise/tenants/{id}/sso` - Configure SSO
- `POST /enterprise/compliance/audit` - Log audit event
- `GET /enterprise/compliance/gdpr/export/{id}` - GDPR export

#### Widget (Embeddable Booking)
- `POST /widget/config` - Create widget
- `GET /widget/config/{id}/embed-code` - Get embed codes
- `GET /widget/config/{id}/links` - Get shareable links
- `GET /widget/public/{key}` - Get widget data (no auth)
- `GET /widget/public/{key}/availability` - Get slots (no auth)
- `POST /widget/public/{key}/book` - Create booking (no auth)
- `GET /widget/book/{slug}` - Shareable booking page

#### Outcomes (PROMs)
- `GET /outcomes/questionnaire/{type}` - Get questionnaire
- `POST /outcomes/submit` - Submit responses
- `POST /outcomes/schedule` - Schedule assessments

## Widget Integration

### Embed on Your Website

**Iframe:**
```html
<iframe src="https://sana.health/widget/{widget_key}"
        style="width: 100%; min-height: 600px; border: none;">
</iframe>
```

**JavaScript:**
```html
<div id="sana-widget"></div>
<script src="https://sana.health/widget/embed.js"></script>
<script>
  SANAWidget.init({
    key: 'your-widget-key',
    container: '#sana-widget',
    style: 'inline',
    theme: 'light'
  });
</script>
```

**Shareable Link:**
```
https://sana.health/book/{your-slug}
```

## Project Structure

```
sana-abc3/
├── backend/
│   ├── algorithms/
│   │   ├── scoring/          # SISM
│   │   ├── evidence/         # Health Graph, Health Score
│   │   ├── planning/         # SHAM
│   │   ├── verification/     # SCVM
│   │   ├── matching/         # SPRM
│   │   ├── safety/           # SST
│   │   ├── learning/         # SOU (Thompson Sampling)
│   │   ├── herbs/            # SHI
│   │   ├── index/            # SANA Index
│   │   ├── reflection/       # SIRM (Journal AI)
│   │   └── outcomes/         # PROMs
│   ├── services/
│   │   ├── auth/             # JWT Authentication
│   │   ├── practice/         # Scheduling, Clients, Sessions
│   │   ├── marketplace/      # Search, Reviews, Discovery
│   │   ├── payments/         # Stripe, Subscriptions, Payouts
│   │   ├── messaging/        # Chat
│   │   ├── analytics/        # Dashboards
│   │   ├── wearables/        # Device Integrations
│   │   ├── enterprise/       # FHIR, NHS, Multi-tenant
│   │   └── widget/           # Embeddable Booking
│   ├── api/routes/           # 20 route modules
│   ├── database/             # SQLAlchemy models
│   ├── tests/                # Pytest suites
│   ├── main.py               # FastAPI app
│   └── requirements.txt
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

### Environment Variables

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/sana

# JWT
JWT_SECRET_KEY=your-secret-key

# Stripe
STRIPE_SECRET_KEY=sk_test_...

# Wearables
FITBIT_CLIENT_ID=...
OURA_CLIENT_ID=...
```

### Docker Setup

```bash
docker-compose up -d
```

## Testing

### Run All Tests

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov
pytest tests/ -v
```

### Run Specific Tests

```bash
pytest tests/test_scoring/ -v       # SISM
pytest tests/test_learning/ -v      # SOU
pytest tests/integration/ -v        # Complete flows
```

## Key Features

### For Practitioners (SANA Pro)
- **Practice Management**: Scheduling, client roster, SOAP notes
- **SANA Index**: Credibility score based on outcomes (40% weight)
- **Widget**: Embeddable booking for your website
- **Analytics**: Revenue, clients, sessions, outcomes dashboards
- **Payouts**: Automated earnings with Stripe Connect

### For Clients (SANA Connect)
- **Marketplace**: Find practitioners by specialty, location, price
- **Booking**: Book directly or through practitioner's website
- **Messaging**: Communicate with practitioners
- **Progress Tracking**: Health score, PROMs, wearable data
- **Journal**: AI-powered reflections with 8 personas

### For Enterprise (SANA Enterprise)
- **NHS Integration**: FHIR R4, PDS lookup, GP referrals
- **Multi-Tenant**: Corporate wellness, clinics, universities
- **SSO**: SAML, OIDC, Azure AD, Okta, NHS Login
- **Compliance**: Audit logging, GDPR export, retention policies

## Technology Stack

- **Backend**: Python 3.11, FastAPI, Pydantic v2
- **Database**: PostgreSQL, SQLAlchemy 2.0
- **Auth**: JWT (python-jose), bcrypt
- **Payments**: Stripe
- **ML**: NumPy, SciPy, scikit-learn
- **Testing**: pytest, pytest-asyncio

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Subscription Tiers

| Tier | Monthly | Features |
|------|---------|----------|
| **Free** | £0 | 5 clients, 20 bookings/month |
| **Basic** | £29 | 50 clients, outcome tracking |
| **Professional** | £79 | 200 clients, custom branding |
| **Enterprise** | £199 | Unlimited, dedicated support |

## SANA Index Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Credentials | 20% | Education, licenses, certifications |
| Volume | 20% | Treatment volume and experience |
| **Outcomes** | **40%** | Client health improvements |
| Completeness | 10% | Profile and data completeness |
| Satisfaction | 10% | Client ratings and reviews |

## Supported Wearables

- Apple Health
- Fitbit
- Oura Ring
- WHOOP
- Garmin
- Google Fit

## License

Proprietary - SANA Technologies Ltd.

---

**Total API Endpoints: 300+**
**Total Service Modules: 20**
**Total Algorithms: 10**
