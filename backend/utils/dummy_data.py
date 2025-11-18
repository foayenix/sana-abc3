"""
Dummy data generator for SANA Algorithms Suite testing.
"""

import random
from typing import List, Dict
from uuid import uuid4, UUID
from datetime import datetime, timedelta

from models.user import User, UserProfile
from models.practitioner import Practitioner
from models.intervention import Intervention
from models.health_data import HealthScore
from algorithms.scoring.models import QuestionResponse, QuestionnaireInput


class DummyDataGenerator:
    """Generate realistic dummy data for testing SANA algorithms"""

    # Question templates for each domain
    QUESTIONS = {
        "physical": [
            "PHY_001",  # Sleep quality
            "PHY_002",  # Energy levels
            "PHY_003",  # Pain levels (inverse scored)
            "PHY_004",  # Mobility
            "PHY_005",  # Exercise frequency
        ],
        "emotional": [
            "EMO_001",  # Mood stability
            "EMO_002",  # Stress levels (inverse scored)
            "EMO_003",  # Anxiety levels (inverse scored)
            "EMO_004",  # Emotional regulation
            "EMO_005",  # Life satisfaction
        ],
        "social": [
            "SOC_001",  # Relationship quality
            "SOC_002",  # Social support
            "SOC_003",  # Community connection
            "SOC_004",  # Loneliness (inverse scored)
        ],
        "cognitive": [
            "COG_001",  # Focus/concentration
            "COG_002",  # Memory
            "COG_003",  # Mental clarity
            "COG_004",  # Decision-making ability
            "COG_005",  # Cognitive overwhelm (inverse scored)
        ],
        "spiritual": [
            "SPI_001",  # Sense of purpose
            "SPI_002",  # Meaning in life
            "SPI_003",  # Connection to values
            "SPI_004",  # Inner peace
        ]
    }

    # Inverse scored questions (lower is better)
    INVERSE_QUESTIONS = {
        "PHY_003",  # Pain
        "EMO_002",  # Stress
        "EMO_003",  # Anxiety
        "SOC_004",  # Loneliness
        "COG_005",  # Overwhelm
    }

    @staticmethod
    def generate_user_id() -> UUID:
        """Generate a random user UUID"""
        return uuid4()

    @classmethod
    def generate_questionnaire(
        cls,
        user_id: UUID = None,
        profile: str = "balanced"
    ) -> QuestionnaireInput:
        """
        Generate a complete questionnaire with realistic responses

        Args:
            user_id: User UUID, generates new if not provided
            profile: Response profile type:
                - "balanced": Generally healthy (6-8 scores)
                - "struggling": Low scores in multiple domains (3-5)
                - "thriving": High scores across all domains (8-10)
                - "mixed": Random realistic mix
                - "physical_weak": Strong except physical health
                - "emotional_weak": Strong except emotional health

        Returns:
            Complete QuestionnaireInput
        """
        if user_id is None:
            user_id = cls.generate_user_id()

        responses = []

        # Define score ranges for each profile
        score_ranges = {
            "balanced": (6, 8),
            "struggling": (3, 5),
            "thriving": (8, 10),
            "mixed": (2, 9),
            "physical_weak": None,  # Special handling
            "emotional_weak": None,  # Special handling
        }

        for domain, question_ids in cls.QUESTIONS.items():
            # Determine score range for this domain
            if profile == "physical_weak":
                score_range = (3, 5) if domain == "physical" else (7, 9)
            elif profile == "emotional_weak":
                score_range = (3, 5) if domain == "emotional" else (7, 9)
            else:
                score_range = score_ranges[profile]

            # Generate responses for each question
            for question_id in question_ids:
                # Generate base score
                raw_score = random.randint(*score_range)

                # Add some variation
                variation = random.choice([-1, 0, 0, 1])  # Bias toward no change
                raw_score = max(0, min(10, raw_score + variation))

                # Inverse scoring for certain questions
                if question_id in cls.INVERSE_QUESTIONS:
                    raw_score = 10 - raw_score

                responses.append(QuestionResponse(
                    question_id=question_id,
                    domain=domain,
                    raw_score=raw_score
                ))

        return QuestionnaireInput(
            user_id=user_id,
            responses=responses,
            questionnaire_version="1.0",
            completed_at=datetime.utcnow()
        )

    @classmethod
    def generate_multiple_questionnaires(
        cls,
        count: int = 10,
        profiles: List[str] = None
    ) -> List[QuestionnaireInput]:
        """
        Generate multiple questionnaires with different profiles

        Args:
            count: Number of questionnaires to generate
            profiles: List of profile types to use (cycles through them)
                     If None, uses all profile types

        Returns:
            List of QuestionnaireInput objects
        """
        if profiles is None:
            profiles = ["balanced", "struggling", "thriving", "mixed",
                       "physical_weak", "emotional_weak"]

        questionnaires = []
        for i in range(count):
            profile = profiles[i % len(profiles)]
            questionnaires.append(
                cls.generate_questionnaire(profile=profile)
            )

        return questionnaires

    @classmethod
    def generate_user_journey(
        cls,
        user_id: UUID,
        weeks: int = 12,
        improvement: bool = True
    ) -> List[QuestionnaireInput]:
        """
        Generate a series of questionnaires showing user progress over time

        Args:
            user_id: User UUID to track
            weeks: Number of weeks to simulate
            improvement: Whether scores should improve over time

        Returns:
            List of questionnaires ordered chronologically
        """
        questionnaires = []

        # Start with struggling profile
        current_profile = "struggling"

        for week in range(weeks):
            # Generate questionnaire
            questionnaire = cls.generate_questionnaire(
                user_id=user_id,
                profile=current_profile
            )

            # Set realistic timestamp
            questionnaire.completed_at = datetime.utcnow() - timedelta(weeks=weeks-week)

            questionnaires.append(questionnaire)

            # Progress profile if improvement enabled
            if improvement and week > 0:
                if week < 4:
                    current_profile = "struggling"
                elif week < 8:
                    current_profile = "mixed"
                else:
                    current_profile = "balanced"

        return questionnaires


# Legacy functions for backwards compatibility
def generate_dummy_user() -> User:
    """Generate a dummy user for testing."""
    return User(
        id=uuid4(),
        email=f"user_{random.randint(1000, 9999)}@example.com",
        full_name=random.choice([
            "Alice Johnson", "Bob Smith", "Carol Williams",
            "David Brown", "Eva Martinez", "Frank Lee"
        ]),
        age=random.randint(25, 65)
    )


def generate_dummy_profile(user_id) -> UserProfile:
    """Generate a dummy user profile."""
    return UserProfile(
        user_id=user_id,
        preferences={
            "preferred_modalities": random.sample(
                ["yoga", "meditation", "herbal", "acupuncture", "massage"],
                k=2
            ),
            "time_preference": random.choice(["morning", "afternoon", "evening"])
        },
        health_goals=random.sample([
            "reduce_stress", "improve_sleep", "increase_energy",
            "manage_pain", "boost_immunity", "improve_focus"
        ], k=3),
        budget_weekly=random.choice([50, 100, 150, 200, 250]),
        time_available_weekly=random.choice([60, 120, 180, 240])
    )


def generate_dummy_practitioner() -> Practitioner:
    """Generate a dummy practitioner for testing."""
    specialties = random.sample([
        "Acupuncture", "Yoga", "Meditation", "Herbal Medicine",
        "Ayurveda", "Naturopathy", "Massage Therapy", "Reiki"
    ], k=random.randint(1, 3))

    credentials = random.sample([
        "RYT-200", "L.Ac", "ND", "RMT", "NCCAOM", "CNHP"
    ], k=random.randint(1, 2))

    return Practitioner(
        id=uuid4(),
        full_name=random.choice([
            "Dr. Sarah Chen", "John Williams, L.Ac",
            "Maria Garcia, ND", "James Kim, RMT"
        ]),
        specialties=specialties,
        credentials=credentials,
        verified=random.choice([True, False]),
        sana_index_score=round(random.uniform(60, 95), 1),
        hourly_rate=random.choice([75, 100, 125, 150, 200])
    )


def generate_dummy_questionnaire_responses() -> Dict[str, Dict[str, int]]:
    """Generate dummy questionnaire responses for all domains."""
    domains = ["physical", "emotional", "social", "cognitive", "spiritual"]
    responses = {}

    for domain in domains:
        responses[domain] = {
            f"q{i}": random.randint(20, 100)
            for i in range(1, 6)
        }

    return responses


def generate_dummy_health_score(user_id) -> HealthScore:
    """Generate a dummy health score for testing."""
    domain_scores = {
        "physical": round(random.uniform(40, 90), 1),
        "emotional": round(random.uniform(40, 90), 1),
        "social": round(random.uniform(40, 90), 1),
        "cognitive": round(random.uniform(40, 90), 1),
        "spiritual": round(random.uniform(40, 90), 1)
    }

    # Calculate weighted overall
    weights = {
        "physical": 0.25,
        "emotional": 0.25,
        "social": 0.15,
        "cognitive": 0.20,
        "spiritual": 0.15
    }
    overall = sum(score * weights[domain] for domain, score in domain_scores.items())

    return HealthScore(
        id=uuid4(),
        user_id=user_id,
        overall_score=round(overall, 1),
        domain_scores=domain_scores
    )


def generate_dummy_intervention() -> Intervention:
    """Generate a dummy intervention for testing."""
    categories = {
        "yoga": ["Hatha Yoga", "Vinyasa Flow", "Yin Yoga", "Restorative Yoga"],
        "meditation": ["Mindfulness", "Guided Meditation", "Body Scan", "Loving Kindness"],
        "herbal": ["Ashwagandha", "Turmeric", "Valerian", "Rhodiola"],
        "acupuncture": ["Traditional Acupuncture", "Auricular", "Electroacupuncture"],
        "massage": ["Swedish Massage", "Deep Tissue", "Trigger Point", "Shiatsu"]
    }

    category = random.choice(list(categories.keys()))
    name = random.choice(categories[category])

    return Intervention(
        id=uuid4(),
        name=name,
        category=category,
        evidence_rating=random.choice(["strong", "moderate", "weak"]),
        target_domains=random.sample(
            ["physical", "emotional", "social", "cognitive", "spiritual"],
            k=random.randint(1, 3)
        ),
        contraindications=random.sample(
            ["pregnancy", "bleeding_disorders", "heart_conditions", "none"],
            k=random.randint(0, 2)
        ),
        typical_duration_minutes=random.choice([15, 30, 45, 60, 90]),
        cost_estimate=random.choice([20, 40, 60, 80, 100])
    )
