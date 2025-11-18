# SPRM - SANA Practitioner Recommendation Model

## Overview
Recommends practitioners based on user needs, preferences, and health goals using collaborative and content-based filtering.

## Matching Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Specialty Match | 35% | Alignment with user's health goals |
| Location | 20% | Proximity and accessibility |
| Availability | 15% | Schedule compatibility |
| Budget | 15% | Within user's price range |
| Reviews | 15% | Patient satisfaction scores |

## Algorithm

### Content-Based Filtering
1. Extract user requirements
2. Match against practitioner profiles
3. Score based on feature similarity

### Collaborative Filtering
1. Find similar users
2. Identify preferred practitioners
3. Weight by similarity score

### Hybrid Ranking
1. Combine content and collaborative scores
2. Apply business rules
3. Return top-k recommendations

## Input

```python
{
    "user_id": UUID,
    "health_goals": ["reduce_stress", "improve_sleep"],
    "preferences": {
        "modalities": ["yoga", "meditation"],
        "budget_max": 100,
        "location": "San Francisco"
    },
    "top_k": 5
}
```

## Output

```python
{
    "user_id": UUID,
    "recommendations": [
        {
            "practitioner_id": UUID,
            "match_score": 0.92,
            "match_reasons": [
                "Specializes in stress reduction",
                "Within budget",
                "High patient ratings"
            ],
            "specialties_matched": ["Meditation", "Yoga"]
        },
        ...
    ]
}
```

## API Endpoint
```
POST /api/v1/matching/recommend
```
