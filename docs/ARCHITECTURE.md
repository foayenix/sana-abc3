# SANA Algorithms Suite Architecture

## Overview

The SANA Algorithms Suite is a comprehensive platform for personalized Complementary & Alternative Medicine (CAM) recommendations. It combines multiple AI/ML algorithms to provide evidence-based health assessments, practitioner matching, and treatment planning.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Frontend (Web)                    │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ Screens │  │ Widgets  │  │ Services │  │    Models    │ │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘ │
│       └────────────┴─────────────┴───────────────┘          │
└─────────────────────────────┬───────────────────────────────┘
                              │ REST API
┌─────────────────────────────┴───────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Routes                          │  │
│  │  /scoring  /matching  /safety  /evidence  /planning   │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────┴─────────────────────────────┐  │
│  │                   Algorithms Layer                     │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐   │  │
│  │  │ SISM │ │ SPRM │ │ SCVM │ │  SST │ │ Evidence │   │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘   │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐   │  │
│  │  │  SEC │ │  SOU │ │ SHAM │ │Index │ │ Optimizer│   │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Layer (Models & Utils)               │  │
│  └────────────────────────┬─────────────────────────────┘  │
└─────────────────────────────┴───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│              PostgreSQL + pgvector Database                  │
│  ┌────────┐ ┌──────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ Users  │ │ Practitioners │ │Interventions│ │  Scores   │ │
│  └────────┘ └──────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Frontend (Flutter)

- **Screens**: User interface pages for testing algorithms
- **Widgets**: Reusable UI components
- **Services**: API communication layer
- **Models**: Data models matching backend

### Backend (FastAPI)

- **API Routes**: RESTful endpoints for each algorithm category
- **Algorithms**: Core algorithm implementations
- **Models**: Pydantic data validation models
- **Utils**: Shared utilities and helpers
- **Database**: SQLAlchemy ORM and migrations

### Database

- PostgreSQL with pgvector extension for embedding storage
- Tables for users, practitioners, interventions, scores, etc.

## Algorithm Categories

### Tier 1: Foundation
- **SISM** - Baseline health assessment
- **Health Graph** - CAM knowledge base

### Tier 2: Core Intelligence
- **SHAM** - Personalized daily plans
- **Evidence Engine** - Evidence-based recommendations
- **Optimizer** - Resource allocation

### Tier 3: Matching & Verification
- **SCVM** - Credential verification
- **SPRM** - Practitioner recommendations
- **SANA Index** - Credibility scoring

### Tier 4: Engagement & Safety
- **SST** - Safety monitoring
- **SEC** - Engagement prediction
- **SOU** - Outcome uplift
- **SFC** - Follow-up coaching

## Data Flow

1. User completes questionnaire in frontend
2. Frontend sends responses to SISM endpoint
3. SISM calculates health scores across 5 domains
4. Scores feed into Evidence Engine for recommendations
5. SPRM matches user with appropriate practitioners
6. Planning algorithms create personalized schedules
7. SST monitors for safety concerns continuously
8. SEC predicts engagement, SOU tracks outcomes

## Security Considerations

- JWT authentication for API access
- Encrypted database connections
- HIPAA-compliant data handling
- Audit logging for sensitive operations

## Scalability

- Stateless API design for horizontal scaling
- Database connection pooling
- Caching layer for frequent queries
- Async endpoints for long-running operations

## Future Enhancements

- ML model serving with MLflow
- Real-time streaming with WebSockets
- Mobile app support
- Integration with wearables/health devices
