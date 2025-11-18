# SHAM - SANA Habit & Activity Model

## Overview
The SANA Habit & Activity Model creates personalized daily activity plans based on user preferences, health goals, and available time.

## Features

- Time-aware scheduling
- Preference optimization
- Habit formation support
- Adherence prediction

## Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | UUID | User identifier |
| health_goals | list | Target health goals |
| available_time_minutes | int | Daily available time |
| preferences | dict | User preferences |

## Algorithm

### Activity Selection
1. Filter interventions by health goals
2. Score by evidence rating and user preferences
3. Exclude contraindicated interventions

### Time Allocation
1. Prioritize high-impact activities
2. Distribute across available time slots
3. Consider optimal time of day

### Adherence Optimization
1. Start with smaller commitments
2. Progressive difficulty increase
3. Include variety for engagement

## Output

```python
{
    "user_id": UUID,
    "daily_plan": [
        {
            "activity_id": "yoga_morning",
            "name": "Morning Yoga",
            "duration_minutes": 20,
            "time_of_day": "morning",
            "frequency": "daily"
        },
        ...
    ],
    "weekly_summary": {
        "total_time": 180,
        "activities_count": 7,
        "domains_covered": ["physical", "emotional"]
    },
    "adherence_prediction": 0.75
}
```

## API Endpoint
```
POST /api/v1/planning/habits
```
