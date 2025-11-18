# SISM - SANA Intake Scoring Model

## Overview
The SANA Intake Scoring Model (SISM) calculates baseline health scores across five wellness domains, providing a comprehensive health assessment that serves as the foundation for personalized recommendations.

## Domains

| Domain | Weight | Description |
|--------|--------|-------------|
| Physical | 25% | Energy, sleep, pain, activity, digestion |
| Emotional | 25% | Mood, stress, anxiety, resilience |
| Social | 15% | Relationships, support, community |
| Cognitive | 20% | Focus, clarity, memory, problem-solving |
| Spiritual | 15% | Purpose, mindfulness, peace, meaning |

## Algorithm

### Input
```python
{
    "user_id": UUID,
    "domain_responses": {
        "physical": {"q1": 70, "q2": 65, ...},
        "emotional": {"q1": 60, "q2": 55, ...},
        ...
    }
}
```

### Calculation

1. **Domain Score**: Average of all question scores in domain
   ```
   domain_score = sum(responses) / len(responses)
   ```

2. **Overall Score**: Weighted average of domain scores
   ```
   overall = Σ (domain_score × weight)
   ```

### Output
```python
{
    "user_id": UUID,
    "overall_score": 68.5,
    "domain_scores": [
        {"domain": "physical", "score": 71.7, "weight": 0.25},
        ...
    ],
    "metadata": {"weights_used": {...}}
}
```

## Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| 80-100 | Excellent health status |
| 60-79 | Good with areas for improvement |
| 40-59 | Moderate - consider interventions |
| 0-39 | Needs attention - comprehensive assessment |

## Usage

```python
from algorithms.scoring import calculate_sism_score

result = calculate_sism_score(
    user_id=user_id,
    domain_responses=responses,
    weights=custom_weights  # optional
)
```

## API Endpoint
```
POST /api/v1/scoring/sism
```
