# SANA Index Algorithm

## Overview
Calculates credibility scores for practitioners based on credentials, outcomes, reviews, and verification status.

## Index Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Credentials | 30% | Quality and quantity of certifications |
| Outcomes | 35% | Patient health improvements |
| Reviews | 20% | Patient satisfaction ratings |
| Verification | 15% | Verification status and confidence |

## Calculation

### Credentials Score
```
credentials_score =
    Σ(credential_weight × credential_level) / max_possible
```

### Outcomes Score
```
outcomes_score =
    average_patient_improvement × consistency_factor
```

### Reviews Score
```
reviews_score =
    weighted_average_rating × volume_adjustment
```

### Verification Score
```
verification_score =
    verified ? confidence_score : 0
```

### Overall Index
```
sana_index = Σ(component_score × component_weight)
```

## Input

```python
{
    "practitioner_id": UUID,
    "credentials": ["RYT-500", "YACEP", "Meditation Teacher"],
    "outcome_data": {
        "patients_treated": 150,
        "average_improvement": 15.5,
        "consistency": 0.82
    },
    "reviews": [
        {"rating": 5, "text": "..."},
        ...
    ],
    "verification_status": true
}
```

## Output

```python
{
    "practitioner_id": UUID,
    "overall_score": 88.5,
    "components": [
        {"name": "credentials", "score": 85.0, "weight": 0.30},
        {"name": "outcomes", "score": 92.0, "weight": 0.35},
        {"name": "reviews", "score": 88.0, "weight": 0.20},
        {"name": "verification", "score": 85.0, "weight": 0.15}
    ],
    "percentile": 85.0,
    "trend": "improving"
}
```

## Score Interpretation

| Score | Percentile | Badge |
|-------|------------|-------|
| 90+ | Top 10% | Platinum |
| 80-89 | Top 25% | Gold |
| 70-79 | Top 50% | Silver |
| 60-69 | Average | Bronze |
| <60 | Below Average | None |

## API Endpoints
```
POST /api/v1/index/calculate
GET /api/v1/index/practitioner/{id}
GET /api/v1/index/leaderboard
```
