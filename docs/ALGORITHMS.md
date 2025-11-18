# SANA Algorithms Overview

## Introduction

The SANA Algorithms Suite contains 25+ AI/ML algorithms organized into four tiers, each serving specific functions within the health recommendation ecosystem.

## Algorithm Tiers

### Tier 1: Foundation

#### SISM - SANA Intake Scoring Model
**Purpose**: Calculate baseline health scores across five domains.

**Domains**:
- Physical (25%)
- Emotional (25%)
- Social (15%)
- Cognitive (20%)
- Spiritual (15%)

**Input**: Questionnaire responses (0-100 scale per question)
**Output**: Overall score and domain-specific scores

#### SANA Health Graph
**Purpose**: Knowledge base for CAM interventions and their relationships.

**Features**:
- Intervention-condition mappings
- Evidence ratings
- Contraindication relationships

---

### Tier 2: Core Intelligence

#### SHAM - SANA Habit & Activity Model
**Purpose**: Create personalized daily activity plans.

**Considers**:
- User preferences
- Available time
- Health goals
- Current health status

#### Evidence Engine (Lite)
**Purpose**: Match interventions to user needs based on research evidence.

**Features**:
- Evidence rating lookup
- Contraindication checking
- Relevance scoring

#### Constraint-Aware Allocation Optimizer
**Purpose**: Multi-objective optimization for intervention selection.

**Constraints**:
- Time budget
- Financial budget
- Health priorities
- Contraindications

---

### Tier 3: Matching & Verification

#### SCVM - SANA Credential Vetting Model
**Purpose**: Verify practitioner credentials with 99%+ accuracy.

**Checks**:
- License verification
- Certification validation
- Professional membership

#### SPRM - SANA Practitioner Recommendation Model
**Purpose**: Recommend practitioners based on user needs.

**Factors**:
- Specialty match
- Location
- Availability
- Budget
- User preferences

#### SANA Index
**Purpose**: Calculate credibility scores for practitioners.

**Components**:
- Credentials (30%)
- Outcomes (35%)
- Reviews (20%)
- Verification (15%)

---

### Tier 4: Engagement & Safety

#### SST - SANA Safety & Triage Model
**Purpose**: Monitor for safety concerns and crisis situations.

**Risk Levels**:
- Low
- Medium
- High
- Critical

**Actions**: Alerts, escalation, intervention recommendations

#### SEC - SANA Engagement & Churn Predictor
**Purpose**: Predict user engagement and churn risk.

**Outputs**:
- Engagement score
- Churn probability
- Retention recommendations

#### SOU - SANA Outcome Uplift Model
**Purpose**: Predict and measure health outcome improvements.

**Features**:
- Uplift prediction per domain
- Confidence intervals
- Contributing factors

#### SFC - SANA Follow-up & Care Coach
**Purpose**: Generate personalized follow-up and coaching.

**Outputs**:
- Next actions
- Reminders
- Progress summaries
- Plan adjustments

---

## Algorithm Integration

```
User Input → SISM → Health Scores
                ↓
            Evidence Engine → Intervention Recommendations
                ↓
            SPRM → Practitioner Matches
                ↓
            SHAM + Optimizer → Personalized Plan
                ↓
            SST (continuous) → Safety Monitoring
                ↓
            SEC + SOU → Engagement & Outcomes
                ↓
            SFC → Follow-up Coaching
```

## Technical Implementation

### Common Patterns

1. **Input Validation**: Pydantic models for all inputs
2. **Score Normalization**: 0-100 scale standardization
3. **Weighted Calculations**: Configurable domain weights
4. **Confidence Scores**: Uncertainty quantification

### ML Techniques Used

- **Collaborative Filtering**: Practitioner matching
- **Content-Based Filtering**: Intervention recommendations
- **Linear Programming**: Resource optimization
- **Classification**: Risk assessment
- **Regression**: Score prediction

### Performance Targets

- SISM calculation: < 100ms
- Practitioner matching: < 500ms
- Full optimization: < 2s
- Safety assessment: < 50ms (real-time)

---

## For More Details

See individual algorithm documentation in `/docs/algorithms/`:
- [SISM.md](algorithms/SISM.md)
- [SHAM.md](algorithms/SHAM.md)
- [SPRM.md](algorithms/SPRM.md)
- [SCVM.md](algorithms/SCVM.md)
- [SST.md](algorithms/SST.md)
- [SEC.md](algorithms/SEC.md)
- [SOU.md](algorithms/SOU.md)
- [SANA_INDEX.md](algorithms/SANA_INDEX.md)
