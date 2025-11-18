# SST - SANA Safety & Triage Model

## Overview
Monitors for safety concerns and provides appropriate triage recommendations. Detects crisis situations requiring immediate intervention.

## Risk Levels

| Level | Description | Action |
|-------|-------------|--------|
| Low | Normal variation | Continue monitoring |
| Medium | Concerning pattern | Alert care team |
| High | Significant risk | Immediate outreach |
| Critical | Crisis detected | Emergency escalation |

## Detection Signals

### Behavioral
- Sudden score drops
- Missed appointments
- Unusual response patterns

### Content-Based
- Concerning language
- Self-harm indicators
- Crisis keywords

### Contextual
- Medical history
- Previous alerts
- Current medications

## Algorithm

1. **Signal Detection**
   - Analyze recent responses
   - Compare to baseline
   - Check for keywords

2. **Risk Scoring**
   - Weight by signal severity
   - Consider history
   - Apply thresholds

3. **Action Determination**
   - Map risk to action level
   - Generate recommendations
   - Notify appropriate parties

## Input

```python
{
    "user_id": UUID,
    "health_data": {
        "recent_scores": {...},
        "symptoms": [...]
    },
    "recent_responses": [...]
}
```

## Output

```python
{
    "user_id": UUID,
    "risk_level": "medium",
    "risk_score": 0.62,
    "flags": [
        "Significant score decline in emotional domain",
        "Sleep disturbance reported"
    ],
    "recommendations": [
        "Schedule check-in with care team",
        "Consider sleep-focused intervention"
    ],
    "requires_immediate_action": false
}
```

## API Endpoint
```
POST /api/v1/safety/assess
```
