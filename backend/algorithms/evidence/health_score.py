"""
SANA Health Score Calculator

Calculates the comprehensive health outputs from the Health Graph:
- SANA Health Score (0-100)
- SANA Status (5 levels)
- Top 3 Levers (personalized action recommendations)
- SANA Age (biological wellness estimate)
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from uuid import UUID
import math
from enum import Enum
from pydantic import BaseModel

from .models import Domain


class SANAStatus(str, Enum):
    """Five-level wellness classification."""
    NEEDS_SUPPORT = "needs_support"  # 0-20
    REBUILDING = "rebuilding"        # 21-40
    BALANCED = "balanced"            # 41-60
    THRIVING = "thriving"           # 61-80
    RADIANT = "radiant"             # 81-100


class WellnessLever(BaseModel):
    """A personalized action recommendation."""
    action: str
    domain: str
    expected_impact: float  # Expected score improvement
    difficulty: str  # easy, moderate, challenging
    time_investment: str
    evidence_strength: str
    priority: int  # 1 = highest


class HealthScoreOutput(BaseModel):
    """Complete SANA Health Score output."""
    # Core outputs
    sana_health_score: float  # 0-100
    sana_status: SANAStatus
    sana_age: float  # Biological age estimate
    chronological_age: int

    # Domain breakdown
    domain_scores: Dict[str, float]
    weak_domains: List[str]
    strong_domains: List[str]

    # Top 3 Levers
    top_levers: List[WellnessLever]

    # Trends
    score_trend: Optional[str] = None  # improving, declining, stable
    status_since: Optional[datetime] = None

    # Additional insights
    percentile: Optional[float] = None  # Where user ranks
    potential_score: float  # Max achievable with improvements


class HealthScoreCalculator:
    """
    Calculates SANA Health Score and related outputs.

    Uses multi-dimensional assessment across 5 wellness domains
    with weighted aggregation and evidence-based action recommendations.
    """

    # Domain weights (sum to 1.0)
    DOMAIN_WEIGHTS = {
        "physical": 0.25,
        "emotional": 0.25,
        "social": 0.15,
        "cognitive": 0.20,
        "spiritual": 0.15
    }

    # Status thresholds
    STATUS_THRESHOLDS = {
        SANAStatus.NEEDS_SUPPORT: (0, 20),
        SANAStatus.REBUILDING: (21, 40),
        SANAStatus.BALANCED: (41, 60),
        SANAStatus.THRIVING: (61, 80),
        SANAStatus.RADIANT: (81, 100)
    }

    # Age impact factors per domain (how much each domain affects biological age)
    AGE_FACTORS = {
        "physical": 3.0,   # Physical health has largest age impact
        "emotional": 2.0,
        "social": 1.5,
        "cognitive": 2.0,
        "spiritual": 1.0
    }

    # Evidence-based levers for each domain
    DOMAIN_LEVERS = {
        "physical": [
            {
                "action": "Add 30 minutes of moderate exercise 3x weekly",
                "impact": 8,
                "difficulty": "moderate",
                "time": "90 min/week",
                "evidence": "strong"
            },
            {
                "action": "Improve sleep hygiene (consistent schedule, no screens before bed)",
                "impact": 6,
                "difficulty": "moderate",
                "time": "daily habit",
                "evidence": "strong"
            },
            {
                "action": "Increase daily water intake to 8 glasses",
                "impact": 3,
                "difficulty": "easy",
                "time": "throughout day",
                "evidence": "moderate"
            },
            {
                "action": "Add 15 minutes of stretching or yoga daily",
                "impact": 4,
                "difficulty": "easy",
                "time": "15 min/day",
                "evidence": "strong"
            },
            {
                "action": "Reduce processed food intake by 50%",
                "impact": 5,
                "difficulty": "challenging",
                "time": "meal planning",
                "evidence": "strong"
            }
        ],
        "emotional": [
            {
                "action": "Practice 10 minutes of mindfulness meditation daily",
                "impact": 7,
                "difficulty": "moderate",
                "time": "10 min/day",
                "evidence": "strong"
            },
            {
                "action": "Journal for 5 minutes each evening",
                "impact": 5,
                "difficulty": "easy",
                "time": "5 min/day",
                "evidence": "moderate"
            },
            {
                "action": "Use 4-7-8 breathing technique during stress",
                "impact": 4,
                "difficulty": "easy",
                "time": "2 min as needed",
                "evidence": "strong"
            },
            {
                "action": "Limit news/social media to 30 minutes daily",
                "impact": 5,
                "difficulty": "moderate",
                "time": "saves time",
                "evidence": "moderate"
            },
            {
                "action": "Schedule one enjoyable activity daily",
                "impact": 4,
                "difficulty": "easy",
                "time": "30 min/day",
                "evidence": "moderate"
            }
        ],
        "social": [
            {
                "action": "Reach out to one friend/family member daily",
                "impact": 6,
                "difficulty": "easy",
                "time": "5-15 min/day",
                "evidence": "strong"
            },
            {
                "action": "Join a group activity or class weekly",
                "impact": 7,
                "difficulty": "moderate",
                "time": "1-2 hours/week",
                "evidence": "strong"
            },
            {
                "action": "Practice active listening in conversations",
                "impact": 4,
                "difficulty": "moderate",
                "time": "ongoing",
                "evidence": "moderate"
            },
            {
                "action": "Volunteer in your community monthly",
                "impact": 5,
                "difficulty": "moderate",
                "time": "2-4 hours/month",
                "evidence": "strong"
            },
            {
                "action": "Have one device-free meal with others daily",
                "impact": 3,
                "difficulty": "easy",
                "time": "30 min/day",
                "evidence": "moderate"
            }
        ],
        "cognitive": [
            {
                "action": "Learn something new for 20 minutes daily",
                "impact": 6,
                "difficulty": "moderate",
                "time": "20 min/day",
                "evidence": "strong"
            },
            {
                "action": "Do brain training exercises or puzzles 3x weekly",
                "impact": 4,
                "difficulty": "easy",
                "time": "15 min/session",
                "evidence": "moderate"
            },
            {
                "action": "Read for 30 minutes before bed",
                "impact": 5,
                "difficulty": "easy",
                "time": "30 min/day",
                "evidence": "moderate"
            },
            {
                "action": "Take regular breaks during focused work (Pomodoro)",
                "impact": 4,
                "difficulty": "easy",
                "time": "5 min/hour",
                "evidence": "strong"
            },
            {
                "action": "Reduce multitasking - single-task important work",
                "impact": 5,
                "difficulty": "challenging",
                "time": "ongoing",
                "evidence": "strong"
            }
        ],
        "spiritual": [
            {
                "action": "Practice gratitude - write 3 things each day",
                "impact": 6,
                "difficulty": "easy",
                "time": "5 min/day",
                "evidence": "strong"
            },
            {
                "action": "Spend 20 minutes in nature daily",
                "impact": 5,
                "difficulty": "easy",
                "time": "20 min/day",
                "evidence": "strong"
            },
            {
                "action": "Define and review personal values monthly",
                "impact": 4,
                "difficulty": "moderate",
                "time": "30 min/month",
                "evidence": "moderate"
            },
            {
                "action": "Engage in acts of kindness weekly",
                "impact": 4,
                "difficulty": "easy",
                "time": "varies",
                "evidence": "moderate"
            },
            {
                "action": "Practice mindful awareness during routine activities",
                "impact": 5,
                "difficulty": "moderate",
                "time": "ongoing",
                "evidence": "strong"
            }
        ]
    }

    def __init__(self):
        """Initialize calculator."""
        pass

    def calculate(
        self,
        domain_scores: Dict[str, float],
        chronological_age: int,
        historical_scores: Optional[List[float]] = None,
        current_activities: Optional[List[str]] = None
    ) -> HealthScoreOutput:
        """
        Calculate complete SANA Health Score output.

        Args:
            domain_scores: Scores for each domain (0-100)
            chronological_age: User's actual age
            historical_scores: Previous overall scores for trend
            current_activities: Activities user already does (to avoid redundant suggestions)

        Returns:
            Complete HealthScoreOutput
        """
        current_activities = current_activities or []

        # 1. Calculate overall health score
        sana_score = self._calculate_overall_score(domain_scores)

        # 2. Determine SANA Status
        sana_status = self._determine_status(sana_score)

        # 3. Calculate SANA Age
        sana_age = self._calculate_biological_age(
            domain_scores, chronological_age
        )

        # 4. Identify weak and strong domains
        weak_domains = [
            domain for domain, score in domain_scores.items()
            if score < 50
        ]
        strong_domains = [
            domain for domain, score in domain_scores.items()
            if score >= 70
        ]

        # 5. Generate Top 3 Levers
        top_levers = self._generate_top_levers(
            domain_scores, weak_domains, current_activities
        )

        # 6. Calculate score trend
        score_trend = None
        if historical_scores and len(historical_scores) >= 3:
            recent = historical_scores[-3:]
            if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
                score_trend = "improving"
            elif all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
                score_trend = "declining"
            else:
                score_trend = "stable"

        # 7. Calculate potential score
        potential_score = self._calculate_potential_score(
            domain_scores, top_levers
        )

        return HealthScoreOutput(
            sana_health_score=round(sana_score, 1),
            sana_status=sana_status,
            sana_age=round(sana_age, 1),
            chronological_age=chronological_age,
            domain_scores={k: round(v, 1) for k, v in domain_scores.items()},
            weak_domains=weak_domains,
            strong_domains=strong_domains,
            top_levers=top_levers,
            score_trend=score_trend,
            potential_score=round(potential_score, 1)
        )

    def _calculate_overall_score(self, domain_scores: Dict[str, float]) -> float:
        """Calculate weighted overall health score."""
        total = 0.0
        total_weight = 0.0

        for domain, weight in self.DOMAIN_WEIGHTS.items():
            if domain in domain_scores:
                total += domain_scores[domain] * weight
                total_weight += weight

        if total_weight == 0:
            return 50.0  # Default neutral score

        return total / total_weight * (1 / max(total_weight, 0.001))

    def _determine_status(self, score: float) -> SANAStatus:
        """Determine SANA Status from score."""
        for status, (low, high) in self.STATUS_THRESHOLDS.items():
            if low <= score <= high:
                return status

        # Edge cases
        if score < 0:
            return SANAStatus.NEEDS_SUPPORT
        return SANAStatus.RADIANT

    def _calculate_biological_age(
        self,
        domain_scores: Dict[str, float],
        chronological_age: int
    ) -> float:
        """
        Calculate biological/wellness age based on health metrics.

        A score of 50 = no adjustment (bio age = chrono age)
        Higher scores reduce bio age (younger than actual)
        Lower scores increase bio age (older than actual)
        """
        # Calculate weighted deviation from neutral (50)
        total_deviation = 0.0
        total_factor = 0.0

        for domain, score in domain_scores.items():
            if domain in self.AGE_FACTORS:
                # Deviation from neutral
                deviation = score - 50

                # Apply domain-specific age factor
                age_adjustment = (deviation / 50) * self.AGE_FACTORS[domain]
                total_deviation += age_adjustment
                total_factor += self.AGE_FACTORS[domain]

        if total_factor == 0:
            return float(chronological_age)

        # Normalize and apply to age
        # Max adjustment is about 10 years either direction
        normalized_deviation = total_deviation / total_factor
        age_adjustment = normalized_deviation * 10

        biological_age = chronological_age - age_adjustment

        # Bound to reasonable range (can't be negative or too extreme)
        return max(18, min(chronological_age + 15, biological_age))

    def _generate_top_levers(
        self,
        domain_scores: Dict[str, float],
        weak_domains: List[str],
        current_activities: List[str]
    ) -> List[WellnessLever]:
        """
        Generate the top 3 personalized action recommendations.

        Prioritizes:
        1. Actions for weakest domains
        2. Highest impact actions
        3. Actions user isn't already doing
        """
        all_levers = []

        # Score each domain by how much it needs improvement
        domain_priority = sorted(
            domain_scores.items(),
            key=lambda x: x[1]
        )

        # Get levers for each domain, prioritizing weak domains
        for domain, score in domain_priority:
            if domain not in self.DOMAIN_LEVERS:
                continue

            # Priority based on how low the score is
            base_priority = 100 - score

            for lever in self.DOMAIN_LEVERS[domain]:
                # Skip if user already does this
                if any(
                    current.lower() in lever["action"].lower()
                    for current in current_activities
                ):
                    continue

                # Calculate total priority score
                impact = lever["impact"]
                difficulty_modifier = {
                    "easy": 1.2,
                    "moderate": 1.0,
                    "challenging": 0.8
                }.get(lever["difficulty"], 1.0)

                evidence_modifier = {
                    "strong": 1.3,
                    "moderate": 1.0,
                    "weak": 0.7
                }.get(lever["evidence"], 1.0)

                priority_score = (
                    base_priority * 0.4 +
                    impact * 5 * difficulty_modifier * evidence_modifier * 0.6
                )

                all_levers.append({
                    "lever": lever,
                    "domain": domain,
                    "priority_score": priority_score
                })

        # Sort by priority and take top 3
        all_levers.sort(key=lambda x: x["priority_score"], reverse=True)
        top_3 = all_levers[:3]

        return [
            WellnessLever(
                action=item["lever"]["action"],
                domain=item["domain"],
                expected_impact=item["lever"]["impact"],
                difficulty=item["lever"]["difficulty"],
                time_investment=item["lever"]["time"],
                evidence_strength=item["lever"]["evidence"],
                priority=idx + 1
            )
            for idx, item in enumerate(top_3)
        ]

    def _calculate_potential_score(
        self,
        domain_scores: Dict[str, float],
        top_levers: List[WellnessLever]
    ) -> float:
        """Calculate potential score if user follows top levers."""
        # Copy current scores
        potential_scores = domain_scores.copy()

        # Apply expected improvements from levers
        for lever in top_levers:
            if lever.domain in potential_scores:
                # Cap improvement at 100
                potential_scores[lever.domain] = min(
                    100,
                    potential_scores[lever.domain] + lever.expected_impact
                )

        return self._calculate_overall_score(potential_scores)

    def get_status_description(self, status: SANAStatus) -> Dict:
        """Get description and guidance for a SANA Status."""
        descriptions = {
            SANAStatus.NEEDS_SUPPORT: {
                "title": "Needs Support",
                "description": "Your wellness scores indicate you may benefit from additional support.",
                "guidance": "Consider reaching out to a healthcare provider or wellness practitioner.",
                "focus": "Build foundational habits in your weakest areas first.",
                "color": "#FF6B6B"
            },
            SANAStatus.REBUILDING: {
                "title": "Rebuilding",
                "description": "You're in a rebuilding phase with room for significant improvement.",
                "guidance": "Focus on consistent small steps rather than major changes.",
                "focus": "Establish routines in 1-2 key areas before expanding.",
                "color": "#FFA94D"
            },
            SANAStatus.BALANCED: {
                "title": "Balanced",
                "description": "You're maintaining a balanced approach to wellness.",
                "guidance": "You have a solid foundation to build on.",
                "focus": "Target specific areas for optimization.",
                "color": "#FFD43B"
            },
            SANAStatus.THRIVING: {
                "title": "Thriving",
                "description": "You're thriving with strong wellness practices.",
                "guidance": "Maintain your current practices and fine-tune.",
                "focus": "Challenge yourself with advanced goals.",
                "color": "#69DB7C"
            },
            SANAStatus.RADIANT: {
                "title": "Radiant",
                "description": "Exceptional wellness across all domains.",
                "guidance": "You're a model of holistic health.",
                "focus": "Consider mentoring others or deepening mastery.",
                "color": "#4DABF7"
            }
        }
        return descriptions.get(status, descriptions[SANAStatus.BALANCED])
