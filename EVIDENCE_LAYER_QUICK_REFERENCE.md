# SANA EVIDENCE LAYER - QUICK REFERENCE FOR INFOGRAPHIC

## WHAT IS THE EVIDENCE LAYER?
A comprehensive system measuring and validating treatment effectiveness through:
- Real-world outcome tracking
- Clinical evidence validation  
- Practitioner credibility scoring
- Patient health improvements

---

## 5 KEY COMPONENTS

### 1. HEALTH GRAPH (Evidence-Based Knowledge Base)
```
Links: Conditions → Interventions → Evidence → Outcomes
Features: 5 evidence strength levels, safety checking, contraindication database
```

### 2. PROMs (4 Validated Measurement Tools)
```
- WHO-5 Wellbeing: 5 questions, psychological health
- DASS-21: 21 questions, depression/anxiety/stress  
- VAS Pain: 1 question, pain intensity
- CAM Symptom: 6 questions, holistic symptoms

Timing: Pre, Post, 1-week, 1-month, 3-month, 6-month
```

### 3. HEALTH SCORE (SANA Calculator)
```
5 Domains (weights):
- Physical (25%)
- Emotional (25%)
- Social (15%)
- Cognitive (20%)
- Spiritual (15%)

Output: 0-100 score, Status level, Biological age, Top 3 action levers
```

### 4. PRACTITIONER MATCHING (SPRM - 10% Evidence Weighting)
```
Evidence Score = (evidence_based × 60) + (interventions × 8)
- No approach = 0 pts
- Evidence-based = 60 pts
- +5 interventions = 100 pts
```

### 5. CREDIBILITY INDEX (SANA Index - 40% Outcomes Weight)
```
Component Breakdown:
- Outcomes (40%) ★ LARGEST - Actual patient results
- Credentials (20%) - Qualifications
- Volume (20%) - Experience (clients & sessions)
- Completeness (10%) - Documentation quality
- Satisfaction (10%) - Reviews & referrals

Outcomes calculation includes:
  • Mean improvement % (0-50 pts)
  • Sample size bonus (0-20 pts, log scale)
  • Consistency bonus (0-15 pts)
  • Retention rate (0-15 pts)
```

---

## EVIDENCE COLLECTION FLOW

```
CLIENT BASELINE
    ↓
PRACTITIONER MATCH (evidence-based scoring)
    ↓
SESSION CONDUCTED
    ↓
PROMs COLLECTED (pre, post, follow-ups)
    ↓
OUTCOMES ANALYZED (improvement calculated)
    ↓
CREDIBILITY UPDATED (SANA Index recalculated)
    ↓
FUTURE MATCHING IMPROVED (better recommendations)
```

---

## KEY METRICS TO HIGHLIGHT

### Evidence Strength (WHO/Cochrane Standards)
- STRONG: Multiple high-quality RCTs
- MODERATE: Some RCTs, systematic reviews
- WEAK: Observational studies
- INSUFFICIENT: No quality evidence
- CONFLICTING: Mixed results

### SANA Health Status Levels
- 0-20: Needs Support (Red)
- 21-40: Rebuilding (Orange)
- 41-60: Balanced (Yellow)
- 61-80: Thriving (Light Green)
- 81-100: Radiant (Green)

### Practitioner Match Factors
1. Health Need (40%) - Weak domains coverage
2. Credibility (25%) - Trust score
3. Practical Fit (20%) - Location/cost
4. **Evidence (10%)** - Treatment approach
5. Preferences (5%) - Style/philosophy

---

## WHAT MAKES IT UNIQUE

✓ Evidence strength classifications (not just testimonials)
✓ Real-time outcome measurement (PROMs)
✓ Statistical validation (effect sizes, sample size confidence)
✓ Safety monitoring (contraindications, drug interactions)
✓ Continuous learning (data feeds back into matching)
✓ Outcome-weighted credibility (40% of score)

---

## EVIDENCE INTEGRATION POINTS

In **Matching**: Practitioners with evidence-based approaches score higher
In **Credibility**: Outcomes prove effectiveness better than credentials alone
In **Planning**: Health graph provides specific protocols & dosages
In **Tracking**: PROMs validate improvements in real-time
In **Safety**: Automatic contraindication & interaction checking

---

## EXAMPLE PRACTITIONER OUTCOME SCORE

```
Practitioner treating 50 clients with 30% avg improvement:

Calculation:
  Mean improvement: 30%              = 30 points (0-50 max)
  Sample size bonus (50 clients)     = 8.5 points (0-20 max)
  Consistency (low variation)        = 12 points (0-15 max)
  Retention rate (75% complete)      = 11.25 points (0-15 max)
  ────────────────────────────────────────────────
  Outcome Component Score            = 61.75 → 62/100

This 62/100 outcome score then:
  × 0.40 (weight) = 24.8 points toward overall SANA Index
```

---

## TIMELINE OF EVIDENCE COLLECTION

```
T-1 (Pre)      → Client baseline PROMs & health assessment
T+0 (Session)  → Treatment + documentation  
T+0 (Post)     → Immediate effect measurement (WHO-5, DASS-21, VAS, CAM)
T+7 (1-week)   → Short-term sustainability check
T+30 (1-month) → Sustained improvement validation
T+90 (3-month) → Long-term efficacy analysis (credibility update)
T+180 (6-month)→ Extended outcomes (graph evidence update)
```

---

## INFOGRAPHIC LAYOUT SUGGESTIONS

1. **Top Section**: "How SANA Validates Treatment Effectiveness"
   - Evidence Collection Flow diagram

2. **Left Column**: "Evidence Layer Components"
   - Health Graph (icon: interconnected nodes)
   - PROMs (icon: survey/measurements)
   - Health Score (icon: dashboard)

3. **Center Column**: "Credibility Scoring"
   - SANA Index 5-component pyramid
   - Outcomes 40% highlighted

4. **Right Column**: "Practitioner Matching"
   - SPRM 5-factor breakdown
   - Evidence alignment 10% highlighted

5. **Bottom Section**: "Outcome Measurement Timeline"
   - Timeline showing data collection points
   - Statistical validation metrics

---

## FILES TO REFERENCE

- `/backend/algorithms/evidence/health_graph.py` - Health Graph implementation
- `/backend/algorithms/evidence/health_score.py` - Health Score calculator
- `/backend/algorithms/outcomes/proms.py` - PROMs validation tools
- `/backend/algorithms/index/sana_index.py` - Credibility scoring (line 253-311 for outcomes)
- `/backend/algorithms/matching/sprm.py` - Matching algorithm (line 354-364 for evidence)
- `/backend/api/routes/evidence.py` - Evidence API endpoints
- `/backend/api/routes/outcomes.py` - Outcomes API endpoints

---

## CORE MESSAGE FOR INFOGRAPHIC

**SANA's Evidence Layer ensures practitioners are matched based on:**
1. Real evidence of effectiveness (actual patient outcomes)
2. Clinical best practices (health graph with WHO/Cochrane standards)
3. Continuous validation (PROMs at every touchpoint)
4. Safety assurance (automatic contraindication checking)
5. Transparent credibility (outcomes worth 40% of score, not just credentials)

**Result**: Users get matched to practitioners who provably work, not just talk.

