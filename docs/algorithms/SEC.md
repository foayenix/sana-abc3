# SEC - SANA Engagement & Churn Predictor

## Overview
Predicts user engagement levels and churn risk, enabling proactive retention interventions.

## Engagement Signals

### Positive
- Regular app usage
- Completed activities
- Questionnaire responses
- Appointment attendance

### Negative
- Declining usage
- Skipped activities
- Unresponsive to reminders
- Negative feedback

## Features Used

| Feature | Description |
|---------|-------------|
| days_since_login | Time since last activity |
| completion_rate | Activity completion percentage |
| score_trend | Health score trajectory |
| response_rate | Questionnaire response rate |
| appointment_attendance | Kept vs. cancelled appointments |

## Algorithm

### Engagement Score
Weighted combination of engagement signals normalized to 0-100.

### Churn Prediction
Classification model predicting probability of churning within 30 days.

### Retention Recommendations
Rule-based recommendations based on risk factors.

## Input

```python
{
    "user_id": UUID,
    "activity_history": {
        "logins": [...],
        "activities_completed": [...],
        "appointments": [...]
    }
}
```

## Output

```python
{
    "user_id": UUID,
    "engagement_score": 72.5,
    "churn_probability": 0.25,
    "risk_factors": [
        "Declining login frequency",
        "Last activity 5 days ago"
    ],
    "retention_recommendations": [
        "Send personalized check-in",
        "Suggest new intervention",
        "Schedule progress review"
    ]
}
```

## API Endpoint
```
POST /api/v1/engagement/predict
```
