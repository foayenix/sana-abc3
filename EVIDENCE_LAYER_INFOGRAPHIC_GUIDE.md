# SANA EVIDENCE LAYER - COMPREHENSIVE ANALYSIS
## Complete Guide for Infographic Creation

---

## OVERVIEW
The SANA Evidence Layer is a multi-dimensional system that collects, validates, measures, and validates treatment effectiveness across the entire platform. It sits at the heart of practitioner matching, credibility scoring, and outcome tracking.

---

## 1. CORE COMPONENTS OF THE EVIDENCE LAYER

### 1.1 Evidence-Based Health Graph
**Location**: `/backend/algorithms/evidence/health_graph.py`

A structured knowledge base that links:
- **Domains** (5 wellness areas: physical, emotional, social, cognitive, spiritual)
- **Conditions** (insomnia, anxiety, pain, stress, etc.)
- **Interventions** (herbal, nutrition, movement, mind-body, etc.)
- **Evidence Strength** (strong, moderate, weak, insufficient, conflicting)
- **Contraindications** (safety warnings, drug interactions, absolute/relative)
- **Dosage Protocols** (specific guidance for implementation)
- **Expected Outcomes** (timeline & success rates)

**Evidence Strength Categories** (WHO/Cochrane Standards):
- **STRONG**: Multiple high-quality RCTs, meta-analyses
- **MODERATE**: Some RCTs, systematic reviews
- **WEAK**: Observational studies, case reports
- **INSUFFICIENT**: No quality studies, traditional use only
- **CONFLICTING**: Mixed results across studies

**Key Functions**:
- Find interventions by domain
- Find interventions by condition
- Check safety for user conditions & medications
- Filter by evidence strength
- Return sorted results (strong evidence first)

---

### 1.2 Patient-Reported Outcome Measures (PROMs)
**Location**: `/backend/algorithms/outcomes/proms.py`
**API Route**: `POST /api/v1/outcomes/submit`

**Four Validated Measurement Tools**:

#### WHO-5 Wellbeing Index
- **Measures**: Psychological wellbeing
- **Questions**: 5 items (0-5 scale, multiply by 4 for 0-100)
- **Timing**: Pre-session, post-session, 1-week, 1-month follow-up
- **Cutoffs**:
  - <50: Poor wellbeing, depression screening indicated
  - 50-72: Moderate wellbeing
  - >72: Good wellbeing

#### DASS-21 (Depression, Anxiety, Stress Scale)
- **Measures**: Mental health symptoms (3 subscales)
- **Questions**: 21 items with separate scoring for:
  - Depression
  - Anxiety
  - Stress
- **Timing**: Baseline, post-treatment, follow-ups

#### VAS Pain Scale
- **Measures**: Pain intensity
- **Questions**: 1 item (0-100 visual analogue scale)
- **Timing**: Frequent assessment (ideal for pain conditions)
- **Severity Levels**: None (0), Mild (1-25), Moderate (26-50), Severe (51-75), Worst (76-100)

#### CAM Symptom Scale (Custom)
- **Measures**: CAM-relevant symptoms
- **Questions**: 6 items covering:
  - Energy level
  - Sleep quality
  - Digestion
  - Emotional balance
  - Physical tension (reverse scored)
  - Overall wellbeing

**Scheduling System**:
- Pre-session: Baseline establishment
- Post-session: Immediate effect measurement
- 1-week follow-up: Short-term sustainability
- 1-month follow-up: Sustained improvement
- 3-month and 6-month: Long-term tracking

---

### 1.3 SANA Health Score Calculator
**Location**: `/backend/algorithms/evidence/health_score.py`
**API Route**: `POST /api/v1/evidence/health-score/calculate`

**5 Wellness Domains** (with weights):
- Physical (25%)
- Emotional (25%)
- Social (15%)
- Cognitive (20%)
- Spiritual (15%)

**Outputs**:
1. **SANA Health Score** (0-100)
2. **SANA Status** (5 levels):
   - Needs Support (0-20)
   - Rebuilding (21-40)
   - Balanced (41-60)
   - Thriving (61-80)
   - Radiant (81-100)

3. **SANA Age** (Biological wellness estimate vs chronological age)
4. **Top 3 Levers** (Personalized, evidence-based action recommendations)
5. **Weak & Strong Domains** (Areas for focus)
6. **Potential Score** (Achievable with improvements)

**Evidence-Based Levers Example**:
Each domain has 5 action recommendations ranked by:
- Impact score (1-10)
- Evidence strength (strong, moderate, weak)
- Difficulty (easy, moderate, challenging)
- Time investment required

Example:
- "Add 30 min moderate exercise 3x weekly" = 8 impact, strong evidence
- "Practice 10 min mindfulness daily" = 7 impact, strong evidence
- "Reduce processed food 50%" = 5 impact, strong evidence

---

## 2. EVIDENCE ALIGNMENT IN PRACTITIONER MATCHING (SPRM)

**Location**: `/backend/algorithms/matching/sprm.py`

### Evidence Alignment Score (10% of matching weight)
Part of 5-factor practitioner matching algorithm:
1. Health Need Alignment (40%)
2. Credibility Score (25%)
3. Practical Fit (20%)
4. **Evidence Alignment (10%)**
5. Preference Match (5%)

### Evidence Scoring Formula:
```
evidence_score = 0-100 points

If practitioner.evidence_based = TRUE:
    score += 60 points

For each evidence-based intervention used:
    score += 8 points (max 40 points for 5 interventions)

Final: min(100, 60 + interventions*8)
```

**Interpretation**:
- Practitioners marked as "evidence-based" get 60 baseline points
- Each documented evidence-based intervention adds value
- Maximum 100 points possible

**Example Scenarios**:
- No evidence-based approach = 0 points
- Evidence-based but no interventions listed = 60 points
- Evidence-based + 3 documented interventions = 60 + 24 = 84 points
- Evidence-based + 5+ documented interventions = 100 points

---

## 3. PRACTITIONER CREDIBILITY & OUTCOMES (SANA INDEX)

**Location**: `/backend/algorithms/index/sana_index.py`
**Overall Score**: 0-100

### 5 Components (with weights):

#### 1. Credentials (20%)
- Degree types (PhD=25, Masters=20, Bachelors=15, etc.)
- Professional licenses (Medical=25, HCPC=22, Nursing=20, etc.)
- CAM certifications (Acupuncture=18, Herbalist=15, Naturopath=18)
- Institution reputation multiplier (Oxford/Cambridge=1.2, other universities=1.05-1.1)
- Diversity bonus (up to 10 points for varied qualifications)

**Scoring Example**:
- PhD from Oxford = 25 × 1.2 = 30 points
- + Masters in Herbal Medicine = 20 × 1.0 = 20 points
- + Acupuncture license = 18 × 1.0 = 18 points
- Total raw = 68 points → Score = 75/100 (with diversity bonus)

#### 2. Treatment Volume (20%)
- Total clients treated (logarithmic scale)
  - 10 clients = 25 pts
  - 50 clients = 35 pts
  - 200+ clients = 50 pts
- Total sessions logged (logarithmic)
  - 50 sessions = 15 pts
  - 500 sessions = 25 pts
  - 2000+ sessions = 30 pts
- Active client ratio (current vs historical)
  - 30% active rate = 6 pts
  - 70% active rate = 14 pts

#### 3. Outcomes (40%) - **LARGEST WEIGHT**
The most critical evidence component measuring actual results.

**Factors**:
- **Mean Improvement %** (0-50 points)
  - 50% average improvement = 50 points
  - 25% average improvement = 25 points
  - 0% improvement = 0 points

- **Sample Size Bonus** (0-20 points, logarithmic)
  - Confidence in results increases with more clients
  - 10 clients = 10 pts
  - 100 clients = 15 pts
  - 1000 clients = 20 pts

- **Consistency Bonus** (0-15 points)
  - Coefficient of variation of improvements
  - Low variance (consistent results) = higher score
  - High variance (unpredictable results) = lower score

- **Retention Rate** (0-15 points)
  - % of clients who complete treatment
  - 100% retention = 15 pts
  - 50% retention = 7.5 pts
  - 0% retention = 0 pts

**Example Outcome Calculation**:
```
Practitioner X:
- 50 clients treated
- Average 30% improvement = 30 points
- 50 clients (log₁₀50 ≈ 1.7) = 5 × 1.7 = 8.5 points bonus
- Consistent results (CV=0.3) = 12 points bonus
- 75% retention = 11.25 points bonus
Total = 30 + 8.5 + 12 + 11.25 = 61.75 points → Score = 62/100
```

#### 4. Data Completeness (10%)
- Session note quality (0-40 points)
  - Comprehensive documentation = 40 pts
  - Basic notes = 20 pts
  - Minimal documentation = 5 pts

- Outcome Measure Compliance (0-40 points)
  - % of sessions with PROMs collected
  - 100% compliance = 40 pts
  - 50% compliance = 20 pts
  - 10% compliance = 4 pts

- Data Recency Bonus (0-20 points)
  - Recent activity = higher score
  - Last session <7 days = 20 pts
  - Last session 7-30 days = 15 pts
  - Last session >90 days = 5 pts

#### 5. Client Satisfaction (10%)
- Review ratings (weighted)
  - 5-star average = 10 pts max
  - 3-star average = 6 pts
  - 1-star average = 1 pt

- Rebooking rate
  - % of clients who return
  - 100% rebooking = 5 pts max
  - 50% rebooking = 2.5 pts

- Referral rate
  - % of clients who refer others
  - 50% referral rate = 10 pts max
  - 10% referral rate = 2 pts

---

## 4. EVIDENCE COLLECTION FLOW

### Step-by-Step Process:

```
1. CLIENT BASELINE (SISM)
   ↓
   Completes 35+ question health questionnaire
   Health Score calculated (0-100, 5 domains)
   Weak domains identified
   
2. PRACTITIONER MATCHING (SPRM)
   ↓
   System matches to evidence-based practitioners
   Evidence alignment scores practitioners
   Top 5 recommendations provided
   
3. BOOKING & SESSION
   ↓
   Client books with practitioner
   Payment processed
   Session conducted
   
4. PRACTITIONER DOCUMENTATION
   ↓
   Session notes recorded
   Chief complaint, assessment, treatment, outcomes
   Recommendations documented
   
5. OUTCOME MEASUREMENT (PROMs)
   ↓
   Pre-session PROMs (baseline)
   Post-session PROMs (immediate effect)
   1-week follow-up (short-term)
   1-month follow-up (sustained effect)
   
6. EVIDENCE VALIDATION
   ↓
   Outcomes analyzed for improvement
   Data completeness checked
   Client satisfaction measured
   Safety monitoring for contraindications
   
7. PRACTITIONER CREDIBILITY UPDATE
   ↓
   SANA Index recalculated
   Outcomes component updated
   Future matching influenced by results
   
8. SYSTEM LEARNING
   ↓
   Health graph updated with efficacy data
   Intervention recommendations refined
   Evidence strength classifications updated
```

---

## 5. HOW EVIDENCE VALIDATES TREATMENT EFFECTIVENESS

### Real-Time Measurement:
1. **Immediate Outcomes**: Post-session PROMs
2. **Short-term Tracking**: 1-week follow-up measures
3. **Sustained Improvement**: 1-month checks
4. **Long-term Validation**: 3-month and 6-month assessments

### Statistical Validation:
- **Mean improvement %**: Average improvement across all clients
- **Effect size**: How much improvement relative to baseline
- **Consistency**: Standard deviation of improvements (low = reliable)
- **Sample size**: Larger samples = higher confidence
- **Retention rate**: Do clients stay with treatment? (compliance indicator)

### Safety Validation:
- **Contraindication checking**: Automatic system checks against known interactions
- **Adverse event tracking**: Any negative outcomes reported
- **Medication interactions**: Herb-drug interaction database
- **Population safety**: Special populations (pregnancy, elderly, etc.)

---

## 6. KEY METRICS & FORMULAS

### Evidence Score in SPRM Matching:
```
Evidence_Score = (evidence_based × 60) + (interventions_used × 8)
Score range: 0-100 points
Weight in overall match: 10%
```

### SANA Index Outcomes Component:
```
Outcome_Score = 
    improvement_score (0-50) +
    sample_bonus (0-20) +
    consistency_bonus (0-15) +
    retention_bonus (0-15)

Improvement_Score = min(50, mean_improvement_percent)
Sample_Bonus = min(20, 5 × log₁₀(total_clients))
Consistency_Bonus = 15 × (1 - coefficient_of_variation)
Retention_Bonus = retention_rate × 15

Final_Score = min(100, max(0, total))
```

### SANA Health Score Overall:
```
SANA_Score = 
    physical_score × 0.25 +
    emotional_score × 0.25 +
    social_score × 0.15 +
    cognitive_score × 0.20 +
    spiritual_score × 0.15

Range: 0-100 (higher = better health)
```

### Data Completeness Score:
```
Completeness_Score =
    note_quality × 40% +
    outcome_compliance × 40% +
    data_recency × 20%

Example:
- 80% note quality = 32 points
- 60% outcome compliance = 24 points
- Recent data (<7 days) = 20 points
Total = 76/100
```

---

## 7. EVIDENCE SOURCES & INTEGRATION

### Built-in Evidence Sources:
- **WHO** (World Health Organization)
- **NCCIH** (National Center for Complementary & Integrative Health)
- **Cochrane Reviews** (Systematic evidence reviews)
- **PubMed** (Scientific literature)

### Each Intervention Includes:
- Citation information (author, year, source)
- Research summary
- Evidence strength classification
- Dosage protocols based on research
- Contraindications from studies
- Expected outcomes with timelines
- Success rates from literature

---

## 8. EVIDENCE LAYER INTEGRATION POINTS

### 1. In Matching System
- Practitioners using evidence-based approaches score higher
- Evidence alignment is 10% of total match score
- Users can filter for "evidence-based treatment"

### 2. In Credibility Calculation
- Outcomes component is 40% of SANA Index (largest weight)
- Demonstrates actual patient results
- More reliable than credentials alone

### 3. In Session Planning
- Health graph provides evidence-based interventions
- Practitioners get specific protocols for conditions
- Dosage, duration, and frequency from research

### 4. In Health Tracking
- PROMs provide validated measurement tools
- Trending shows improvement over time
- Alerts if no progress after expected timeline

### 5. In Safety Monitoring
- Automatic contraindication checking
- Drug-herb interaction warnings
- Population-specific safety (pregnancy, elderly, etc.)

---

## 9. KEY STATISTICS FOR INFOGRAPHIC

### SANA Index Component Breakdown:
- **Outcomes**: 40% (Largest weight - actual results)
- **Credentials**: 20% (Qualifications)
- **Volume**: 20% (Experience)
- **Completeness**: 10% (Data quality)
- **Satisfaction**: 10% (Client feedback)

### SPRM Matching Weights:
- **Health Need**: 40% (Match to weak domains)
- **Credibility**: 25% (Trust score)
- **Practical Fit**: 20% (Location, cost)
- **Evidence**: 10% (Treatment approach)
- **Preferences**: 5% (Philosophy, style)

### Evidence Strength Distribution (WHO/Cochrane):
- **Strong**: Multiple RCTs, meta-analyses
- **Moderate**: Some RCTs, systematic reviews
- **Weak**: Observational studies
- **Insufficient**: No quality evidence
- **Conflicting**: Mixed results

### Health Status Levels (SANA Score):
- 0-20: Needs Support
- 21-40: Rebuilding
- 41-60: Balanced
- 61-80: Thriving
- 81-100: Radiant

---

## 10. OUTCOME MEASUREMENT TIMING

```
TIMELINE OF EVIDENCE COLLECTION:

Pre-Session (T-1):
- Client baseline PROMs
- Health assessment
- Condition severity measurement

Day 0:
- Session conducted
- Notes documented
- Treatment provided

Post-Session (T+0):
- Immediate effect measurement (WHO-5, DASS-21, VAS, CAM)
- Client feedback
- Practitioner observations

1-Week (T+7):
- Short-term sustainability check
- Adherence to recommendations
- Emerging results

1-Month (T+30):
- Sustained improvement validation
- Habit formation assessment
- SANA Index partial update

3-Month (T+90):
- Long-term efficacy analysis
- Outcome component fully updated
- Practitioner credibility adjusted

6-Month (T+180):
- Extended outcomes validation
- Trend analysis
- Health graph evidence updated
```

---

## SUMMARY FOR INFOGRAPHIC

### Main Message:
**SANA's Evidence Layer is a comprehensive system that:**
1. **Measures** - Using validated outcome measures (PROMs)
2. **Validates** - Against clinical evidence (health graph)
3. **Tracks** - Client improvements across time
4. **Verifies** - Practitioner effectiveness with actual results
5. **Optimizes** - Matching based on evidence-based practices

### Key Visuals:
- 5-component SANA Index pyramid
- 5-factor SPRM matching breakdown
- PROMs timeline flow
- Evidence strength spectrum
- Outcome measurement dashboard
- 5 wellness domains visualization
- Practitioner credibility scoring formula
