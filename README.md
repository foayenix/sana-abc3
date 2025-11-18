# SANA Algorithms Suite

A comprehensive algorithm suite for the SANA Health Framework - transforming Complementary & Alternative Medicine (CAM) through evidence-based AI and personalization.

## Algorithms Included

### Tier 1: Foundation
- **SISM** - Intake Scoring Model (Baseline health assessment)
- **SANA Health Graph** - Knowledge base for CAM interventions

### Tier 2: Core Intelligence
- **SHAM** - Habit & Activity Model (Personalized daily plans)
- **Evidence Engine** - Evidence-based recommendation system
- **Constraint-Aware Allocation** - Multi-objective optimization

### Tier 3: Matching & Verification
- **SCVM** - Credential Vetting Model (99% accurate verification)
- **SPRM** - Practitioner Recommendation Model
- **SANA Index** - Credibility scoring for practitioners

### Tier 4: Engagement & Safety
- **SST** - Safety & Triage Model (Crisis detection)
- **SEC** - Engagement & Churn Predictor
- **SOU** - Outcome Uplift Model (Continuous learning)
- **SFC** - Follow-up & Care Coach

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

## Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
flutter test
```

## API Documentation
Once running, visit: http://localhost:8000/docs

## Architecture
See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## License
Proprietary - SANA Technologies Ltd.
