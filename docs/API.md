# SANA Algorithms Suite API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Authentication will be implemented using JWT tokens. Currently in development mode, no authentication is required.

## Endpoints

### Health Check
```
GET /health
```
Returns API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Scoring

#### Calculate SISM Score
```
POST /scoring/sism
```
Calculate health score using the SANA Intake Scoring Model.

**Request Body:**
```json
{
  "user_id": "uuid",
  "domain_responses": {
    "physical": {"q1": 70, "q2": 65, "q3": 80},
    "emotional": {"q1": 60, "q2": 55, "q3": 70},
    "social": {"q1": 75, "q2": 80, "q3": 65},
    "cognitive": {"q1": 85, "q2": 90, "q3": 75},
    "spiritual": {"q1": 50, "q2": 55, "q3": 60}
  },
  "custom_weights": null
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "overall_score": 68.5,
  "domain_scores": {
    "physical": 71.7,
    "emotional": 61.7,
    "social": 73.3,
    "cognitive": 83.3,
    "spiritual": 55.0
  },
  "interpretation": "Good health status with some areas for improvement"
}
```

#### Get Score History
```
GET /scoring/user/{user_id}/history
```
Returns historical health scores for trend analysis.

---

### Matching

#### Recommend Practitioners
```
POST /matching/recommend
```
Get practitioner recommendations based on user needs.

**Request Body:**
```json
{
  "user_id": "uuid",
  "health_goals": ["reduce_stress", "improve_sleep"],
  "preferences": {
    "modalities": ["yoga", "meditation"],
    "budget_max": 100,
    "location": "San Francisco"
  },
  "top_k": 5
}
```

#### Calculate Match Score
```
POST /matching/score
```
Calculate detailed match score between user and practitioner.

---

### Verification

#### Verify Credentials
```
POST /verification/verify
```
Verify practitioner credentials.

**Request Body:**
```json
{
  "practitioner_id": "uuid",
  "credentials": ["RYT-500", "L.Ac"],
  "documents": []
}
```

#### Get Verification Status
```
GET /verification/status/{practitioner_id}
```

---

### Safety

#### Assess Safety
```
POST /safety/assess
```
Assess safety risk for a user.

**Request Body:**
```json
{
  "user_id": "uuid",
  "health_data": {
    "recent_scores": {...},
    "symptoms": [...]
  },
  "recent_responses": []
}
```

#### Get User Alerts
```
GET /safety/user/{user_id}/alerts
```

---

### Engagement

#### Predict Engagement
```
POST /engagement/predict
```
Predict user engagement and churn risk.

#### Generate Follow-up
```
POST /engagement/followup
```
Generate follow-up recommendations.

#### Predict Outcome Uplift
```
POST /engagement/outcome-uplift
```
Predict health outcome improvements.

---

### Evidence

#### Recommend Interventions
```
POST /evidence/recommend
```
Get evidence-based intervention recommendations.

**Request Body:**
```json
{
  "user_id": "uuid",
  "health_goals": ["reduce_stress"],
  "domain_scores": {
    "physical": 65.0,
    "emotional": 55.0
  },
  "contraindications": ["pregnancy"],
  "top_k": 5
}
```

#### Get Intervention Evidence
```
GET /evidence/intervention/{intervention_id}
```

#### Get Interventions for Condition
```
GET /evidence/condition/{condition}
```

---

### Planning

#### Create Habit Plan
```
POST /planning/habits
```
Generate personalized habit and activity plan.

#### Create Timetable
```
POST /planning/timetable
```
Generate optimized daily timetable.

#### Optimize Allocation
```
POST /planning/optimize
```
Optimize intervention allocation considering constraints.

---

### Index

#### Calculate SANA Index
```
POST /index/calculate
```
Calculate SANA Index score for a practitioner.

**Request Body:**
```json
{
  "practitioner_id": "uuid",
  "credentials": ["RYT-500", "YACEP"],
  "outcome_data": {...},
  "reviews": [...],
  "verification_status": true
}
```

#### Get Practitioner Index
```
GET /index/practitioner/{practitioner_id}
```

#### Get Leaderboard
```
GET /index/leaderboard?specialty=yoga&top_k=10
```

---

## Error Handling

All endpoints return errors in the following format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Rate limiting will be implemented in production. Current development mode has no limits.
